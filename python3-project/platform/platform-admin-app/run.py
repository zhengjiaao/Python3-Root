"""Platform Admin Application Runner."""
import sys
import uvicorn
from app.config import get_settings

settings = get_settings()
is_dev = settings.ENVIRONMENT == "development"

if __name__ == "__main__":
    if not is_dev:
        print("[INFO] 生产环境启动: reload 已禁用, 请确保已配置 HTTPS 反向代理")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1" if not is_dev else "0.0.0.0",
        port=8000,
        reload=is_dev,
        workers=1 if is_dev else None,
    )
