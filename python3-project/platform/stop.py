#!/usr/bin/env python3
"""
Platform 一键停止脚本
======================
停止 platform-admin-app (8000) 和 platform-app (8001) 对应的服务进程
支持 Windows / Linux / macOS

用法:
    python stop.py
    python stop.py --force    # 强制结束（不等待优雅关闭）
"""

import argparse
import os
import signal
import subprocess
import sys
import time

# ============================================================
# 颜色输出
# ============================================================
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


def colorize(text: str, color: str) -> str:
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass
    return f"{color}{text}{Colors.END}"


# ============================================================
# 核心逻辑
# ============================================================
PORTS = [8000, 8001]


def get_pids_on_port(port: int) -> set[int]:
    """获取占用指定端口的进程 PID 集合（排除系统进程）。"""
    pids = set()

    if sys.platform == "win32":
        # Windows: 通过 PowerShell Get-NetTCPConnection 查询
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f"Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue | "
                    f"Select-Object -ExpandProperty OwningProcess",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if line.isdigit():
                    pid = int(line)
                    if pid > 4:  # 排除系统进程 (0=Idle, 4=System)
                        pids.add(pid)
        except Exception:
            pass
    else:
        # Linux / macOS: 通过 lsof 查询
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if line.isdigit():
                    pid = int(line)
                    if pid > 1:
                        pids.add(pid)
        except Exception:
            pass

        # 备选: ss (Linux)
        if not pids:
            try:
                result = subprocess.run(
                    ["ss", "-tlnp", f"sport = :{port}"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                for line in result.stdout.splitlines():
                    if "pid=" in line:
                        # 解析 pid=1234
                        parts = line.split("pid=")
                        for part in parts[1:]:
                            pid_str = part.split(",")[0].split(")")[0].strip()
                            if pid_str.isdigit():
                                pid = int(pid_str)
                                if pid > 1:
                                    pids.add(pid)
            except Exception:
                pass

    return pids


def is_process_alive(pid: int) -> bool:
    """检查进程是否仍在运行。"""
    if sys.platform == "win32":
        try:
            subprocess.check_output(["tasklist", "/FI", f"PID eq {pid}"], timeout=5)
            return True
        except subprocess.CalledProcessError:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False


def terminate_pid(pid: int, force: bool = False) -> bool:
    """终止指定 PID 的进程。"""
    try:
        if sys.platform == "win32":
            if force:
                subprocess.run(
                    ["taskkill", "/F", "/PID", str(pid)],
                    capture_output=True,
                    timeout=5,
                )
            else:
                subprocess.run(
                    ["taskkill", "/PID", str(pid)],
                    capture_output=True,
                    timeout=5,
                )
        else:
            sig = signal.SIGKILL if force else signal.SIGTERM
            os.kill(pid, sig)
        return True
    except Exception as e:
        print(colorize(f"  [WARN] 终止 PID {pid} 失败: {e}", Colors.YELLOW))
        return False


def main():
    parser = argparse.ArgumentParser(description="Platform 一键停止脚本")
    parser.add_argument("--force", action="store_true", help="强制结束，不等待优雅关闭")
    parser.add_argument("-p", "--ports", nargs="+", type=int, help="自定义端口列表")
    args = parser.parse_args()

    ports = args.ports if args.ports else PORTS
    force = args.force

    print(colorize("=" * 50, Colors.BOLD))
    print(colorize("         Platform 一键停止脚本", Colors.BOLD))
    print(colorize("=" * 50, Colors.BOLD))

    all_pids = set()
    port_map = {}

    # 收集所有 PID
    for port in ports:
        pids = get_pids_on_port(port)
        if pids:
            port_map[port] = pids
            all_pids.update(pids)

    if not all_pids:
        print(colorize("\n[INFO] 未发现占用指定端口的进程，服务可能已经停止。\n", Colors.YELLOW))
        sys.exit(0)

    # 显示待停止的进程
    print()
    for port, pids in sorted(port_map.items()):
        pid_list = ", ".join(str(p) for p in sorted(pids))
        print(f"  端口 {colorize(str(port), Colors.CYAN)}  ->  PID: {colorize(pid_list, Colors.YELLOW)}")

    print()

    # 第一次终止（优雅）
    for pid in sorted(all_pids):
        label = colorize(f"[PID {pid}]", Colors.CYAN)
        action = "强制终止" if force else "优雅终止"
        print(f"{label} {action}中...")
        terminate_pid(pid, force=force)

    # 如果不是强制模式，等待后检查是否存活
    if not force:
        print(colorize("\n  等待 3 秒...", Colors.YELLOW))
        time.sleep(3)

        still_alive = {pid for pid in all_pids if is_process_alive(pid)}
        if still_alive:
            print(colorize("  以下进程未响应，执行强制终止:", Colors.RED))
            for pid in sorted(still_alive):
                print(f"    {colorize(f'[PID {pid}]', Colors.CYAN)} 强制终止...")
                terminate_pid(pid, force=True)
            time.sleep(1)

    # 最终检查
    final_alive = {pid for pid in all_pids if is_process_alive(pid)}
    if final_alive:
        print(colorize("\n[ERROR] 以下进程未能终止，请手动结束:", Colors.RED))
        for pid in sorted(final_alive):
            print(f"  PID {pid}")
        sys.exit(1)
    else:
        print(colorize("\n[OK] 所有服务已停止\n", Colors.GREEN))


if __name__ == "__main__":
    main()
