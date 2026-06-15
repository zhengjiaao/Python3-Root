#!/usr/bin/env bash
# Platform 一键启动脚本 (Bash)
# ============================
# 同时启动 platform-admin-app (8000) 和 platform-app (8001)
#
# 用法:
#   chmod +x start.sh
#   ./start.sh
#   ./start.sh --no-reload
#   ./start.sh --host 0.0.0.0

set -euo pipefail

# 路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADMIN_DIR="$SCRIPT_DIR/platform-admin-app"
APP_DIR="$SCRIPT_DIR/platform-app"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# 参数解析
HOST="127.0.0.1"
RELOAD="--reload"
INSTALL_DEPS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-reload)
            RELOAD=""
            shift
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --install-deps)
            INSTALL_DEPS=true
            shift
            ;;
        -h|--help)
            echo "用法: $0 [--no-reload] [--host HOST] [--install-deps]"
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 查找 Python
find_python() {
    local candidates=()
    local venv_py="$PROJECT_ROOT/.venv/bin/python"
    if [[ -f "$venv_py" ]]; then
        candidates+=("$venv_py")
    fi
    candidates+=("python3" "python" "$(command -v python3 || true)" "$(command -v python || true)")
    for c in "${candidates[@]}"; do
        if [[ -n "$c" ]] && command -v "$c" &>/dev/null; then
            echo "$c"
            return
        fi
    done
}

PYTHON=$(find_python)
if [[ -z "$PYTHON" ]]; then
    echo -e "${RED}[ERROR] 未找到可用的 Python 解释器${NC}"
    exit 1
fi

echo -e "${BOLD}========================================${NC}"
echo -e "${BOLD}         Platform 一键启动脚本${NC}"
echo -e "${CYAN}         Python: $PYTHON${NC}"
echo -e "${BOLD}========================================${NC}"

# 依赖检查
check_deps() {
    $PYTHON -c "import fastapi, uvicorn, sqlalchemy, pydantic, jwt" &>/dev/null
}

if $INSTALL_DEPS || ! check_deps; then
    if ! $INSTALL_DEPS; then
        read -rp "依赖可能未安装，是否现在安装? [y/N]: " resp
        [[ "$resp" =~ ^[Yy]$ ]] || exit 1
    fi
    for dir in "$ADMIN_DIR" "$APP_DIR"; do
        req="$dir/requirements.txt"
        if [[ -f "$req" ]]; then
            echo -e "${YELLOW}[INFO] 安装依赖: $req${NC}"
            $PYTHON -m pip install -r "$req" -q
        fi
    done
fi

# 启动函数
PIDS=()

cleanup() {
    echo -e "\n${YELLOW}[INFO] 正在停止所有服务...${NC}"
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill -TERM "$pid" 2>/dev/null || true
        fi
    done
    sleep 2
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill -KILL "$pid" 2>/dev/null || true
        fi
    done
    echo -e "${GREEN}[OK] 所有服务已停止${NC}\n"
    exit 0
}

trap cleanup INT TERM

echo ""

cd "$ADMIN_DIR"
echo -e "${GREEN}[Admin] 启动中... http://${HOST}:8000${NC}"
$PYTHON -m uvicorn app.main:app --host "$HOST" --port 8000 $RELOAD &
PIDS+=($!)

cd "$APP_DIR"
echo -e "${BLUE}[App  ] 启动中... http://${HOST}:8001${NC}"
$PYTHON -m uvicorn platform_app.main:app --host "$HOST" --port 8001 $RELOAD &
PIDS+=($!)

echo ""
echo -e "${BOLD}----------------------------------------${NC}"
echo -e "  ${GREEN}[Admin]${NC}  ${CYAN}http://${HOST}:8000${NC}"
echo -e "  ${BLUE}[App  ]${NC}  ${CYAN}http://${HOST}:8001${NC}"
echo -e "${BOLD}----------------------------------------${NC}"
echo -e "${YELLOW}\n按 Ctrl+C 停止所有服务\n${NC}"

# 等待子进程
wait
