#!/usr/bin/env bash
# Platform 一键停止脚本 (Bash)
# =============================
# 停止 platform-admin-app (8000) 和 platform-app (8001)
#
# 用法:
#   chmod +x stop.sh
#   ./stop.sh
#   ./stop.sh --force
#   ./stop.sh --ports 8000 8001 8002

set -euo pipefail

PORTS=(8000 8001)
FORCE=false

# 参数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        --ports)
            shift
            PORTS=()
            while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do
                PORTS+=("$1")
                shift
            done
            ;;
        -h|--help)
            echo "用法: $0 [--force] [--ports PORT1 PORT2 ...]"
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 颜色
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}========================================${NC}"
echo -e "${BOLD}         Platform 一键停止脚本${NC}"
echo -e "${BOLD}========================================${NC}"

FOUND=false
ALL_PIDS=""

for port in "${PORTS[@]}"; do
    pids=$(lsof -ti:"$port" 2>/dev/null || true)
    if [[ -n "$pids" ]]; then
        FOUND=true
        echo -e "  端口 ${CYAN}$port${NC}  ->  PID: ${YELLOW}$pids${NC}"
        for pid in $pids; do
            ALL_PIDS="$ALL_PIDS $pid"
            if $FORCE; then
                echo -e "  [PID $pid] ${RED}强制终止...${NC}"
                kill -9 "$pid" 2>/dev/null || true
            else
                echo -e "  [PID $pid] ${CYAN}优雅终止...${NC}"
                kill -TERM "$pid" 2>/dev/null || true
            fi
        done
    fi
done

if ! $FOUND; then
    echo -e "\n${YELLOW}[INFO] 未发现占用指定端口的进程，服务可能已经停止。${NC}\n"
    exit 0
fi

if ! $FORCE; then
    echo -e "\n  ${YELLOW}等待 3 秒...${NC}"
    sleep 3

    for pid in $ALL_PIDS; do
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "  [PID $pid] ${RED}未响应，强制终止...${NC}"
            kill -9 "$pid" 2>/dev/null || true
        fi
    done
fi

sleep 1
STILL_ALIVE=false
for port in "${PORTS[@]}"; do
    if lsof -ti:"$port" >/dev/null 2>&1; then
        STILL_ALIVE=true
    fi
done

if $STILL_ALIVE; then
    echo -e "\n${RED}[ERROR] 部分进程未能终止，请手动检查。${NC}\n"
    exit 1
else
    echo -e "\n${GREEN}[OK] 所有服务已停止${NC}\n"
fi
