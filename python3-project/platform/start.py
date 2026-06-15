#!/usr/bin/env python3
"""
Platform 一键启动脚本
======================
同时启动 platform-admin-app (8000) 和 platform-app (8001)
支持 Windows / Linux / macOS

用法:
    python start.py
    python start.py --no-reload    # 禁用热重载（生产环境建议）
    python start.py --host 0.0.0.0 # 绑定到所有网卡
"""

import argparse
import os
import sys
import subprocess
import time
from pathlib import Path

# ============================================================
# 路径配置
# ============================================================
SCRIPT_DIR = Path(__file__).resolve().parent
ADMIN_DIR = SCRIPT_DIR / "platform-admin-app"
APP_DIR = SCRIPT_DIR / "platform-app"
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent  # Python3-Root

# ============================================================
# 颜色输出
# ============================================================
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    END = "\033[0m"


def colorize(text: str, color: str) -> str:
    """为终端输出添加颜色（Windows 10+ 自动支持）。"""
    if sys.platform == "win32":
        # Windows 10 v1511+ 支持 ANSI，尝试启用
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass
    return f"{color}{text}{Colors.END}"


# ============================================================
# 工具函数
# ============================================================
def get_python_executable() -> str:
    """查找可用的 Python 解释器，优先虚拟环境。"""
    candidates = []

    # 1. 项目根目录虚拟环境
    venv_root = PROJECT_ROOT / ".venv"
    if sys.platform == "win32":
        candidates.append(venv_root / "Scripts" / "python.exe")
    else:
        candidates.append(venv_root / "bin" / "python")

    # 2. 当前 Python
    candidates.append(Path(sys.executable))

    # 3. PATH 中的 python3 / python
    candidates.extend(["python3", "python"])

    for c in candidates:
        if isinstance(c, Path):
            if c.exists():
                return str(c)
        else:
            try:
                result = subprocess.run(
                    [c, "--version"],
                    capture_output=True,
                    check=True,
                    timeout=5,
                )
                return c
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue

    return None


def check_dependencies(python: str) -> bool:
    """检查依赖是否已安装。"""
    try:
        subprocess.run(
            [python, "-c", "import fastapi, uvicorn, sqlalchemy, pydantic, jwt"],
            capture_output=True,
            check=True,
            timeout=10,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_dependencies(python: str, req_file: Path) -> bool:
    """安装依赖。"""
    print(colorize(f"[INFO] 正在安装依赖: {req_file}", Colors.YELLOW))
    try:
        subprocess.run(
            [python, "-m", "pip", "install", "-r", str(req_file), "-q"],
            check=True,
            timeout=120,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(colorize(f"[ERROR] 依赖安装失败: {e}", Colors.RED))
        return False


# ============================================================
# 主逻辑
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Platform 一键启动脚本")
    parser.add_argument("--no-reload", action="store_true", help="禁用热重载")
    parser.add_argument("--host", default="127.0.0.1", help="绑定主机地址 (默认: 127.0.0.1)")
    parser.add_argument("--install-deps", action="store_true", help="启动前自动安装依赖")
    args = parser.parse_args()

    # 查找 Python
    python = get_python_executable()
    if not python:
        print(colorize("[ERROR] 未找到可用的 Python 解释器，请确保已安装 Python 3.10+", Colors.RED))
        sys.exit(1)

    print(colorize("=" * 64, Colors.BOLD))
    print(colorize("         Platform 一键启动脚本", Colors.BOLD))
    print(colorize(f"         Python: {python}", Colors.CYAN))
    print(colorize("=" * 64, Colors.BOLD))

    # 检查 / 安装依赖
    if args.install_deps or not check_dependencies(python):
        if not args.install_deps:
            print(colorize("[WARN] 检测到依赖可能未安装，建议添加 --install-deps 参数", Colors.YELLOW))
            response = input(colorize("是否现在安装依赖? [y/N]: ", Colors.YELLOW)).strip().lower()
            if response in ("y", "yes"):
                args.install_deps = True

        if args.install_deps:
            for name, req in [("Admin", ADMIN_DIR / "requirements.txt"),
                               ("App", APP_DIR / "requirements.txt")]:
                if req.exists():
                    if not install_dependencies(python, req):
                        sys.exit(1)
                else:
                    print(colorize(f"[WARN] 未找到依赖文件: {req}", Colors.YELLOW))

    # 构建启动命令
    reload_flag = [] if args.no_reload else ["--reload"]
    admin_cmd = [
        python, "-m", "uvicorn", "app.main:app",
        "--host", args.host, "--port", "8000",
        *reload_flag,
    ]
    app_cmd = [
        python, "-m", "uvicorn", "platform_app.main:app",
        "--host", args.host, "--port", "8001",
        *reload_flag,
    ]

    # 启动子进程
    processes = []
    services = [
        ("Admin", ADMIN_DIR, admin_cmd, Colors.GREEN, "8000"),
        ("App  ", APP_DIR, app_cmd, Colors.BLUE, "8001"),
    ]

    print()
    for name, cwd, cmd, color, port in services:
        label = colorize(f"[{name}]", color)
        url = colorize(f"http://{args.host}:{port}", Colors.CYAN)
        print(f"{label} 启动中... {url}")
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(cwd),
                # 继承当前终端，方便查看实时日志
                stdout=None,
                stderr=None,
                # Windows: 新建进程组，避免 Ctrl+C 信号互相干扰
                **({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if sys.platform == "win32" else {}),
            )
            processes.append((name, proc, color, port))
        except Exception as e:
            print(colorize(f"[{name}] 启动失败: {e}", Colors.RED))
            sys.exit(1)

    print()
    print(colorize("-" * 64, Colors.BOLD))
    for name, _, color, port in processes:
        url = f"http://{args.host}:{port}"
        print(f"  {colorize(name, color)}  {colorize(url, Colors.CYAN)}")
    print(colorize("-" * 64, Colors.BOLD))
    print(colorize("\n按 Ctrl+C 停止所有服务\n", Colors.YELLOW))

    # 监控循环
    exit_code = 0
    try:
        while True:
            for name, proc, color, port in processes:
                ret = proc.poll()
                if ret is not None:
                    print(colorize(f"\n[{name}] 进程异常退出 (code={ret})", Colors.RED))
                    exit_code = 1
                    raise SystemExit
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print(colorize("\n[INFO] 正在停止所有服务...", Colors.YELLOW))
        for name, proc, color, port in processes:
            if proc.poll() is None:
                print(colorize(f"[{name}] 终止中...", color))
                if sys.platform == "win32":
                    # Windows: 先尝试发送 CTRL_BREAK_EVENT（因为我们用了 CREATE_NEW_PROCESS_GROUP）
                    try:
                        import signal
                        os.kill(proc.pid, signal.CTRL_BREAK_EVENT)
                        proc.wait(timeout=3)
                    except Exception:
                        pass
                else:
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        pass

                # 强制结束
                if proc.poll() is None:
                    proc.kill()
                    proc.wait(timeout=2)

        print(colorize("[OK] 所有服务已停止\n", Colors.GREEN))
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
