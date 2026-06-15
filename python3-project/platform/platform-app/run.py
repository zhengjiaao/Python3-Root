"""Platform App Application Runner."""
import sys
import uvicorn
from pathlib import Path

# ============================================================
# 关键：确保 platform-admin-app 可被导入
# ============================================================
_admin_app_path = Path(__file__).resolve().parent.parent / "platform-admin-app"
if str(_admin_app_path) not in sys.path:
    sys.path.insert(0, str(_admin_app_path))

from platform_app.config import get_app_settings

settings = get_app_settings()
is_dev = settings.ENVIRONMENT == "development"

if __name__ == "__main__":
    if not is_dev:
        print("[INFO] 生产环境启动: reload 已禁用, 请确保已配置 HTTPS 反向代理")
    uvicorn.run(
        "platform_app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=is_dev,
        workers=1 if is_dev else None,
    )
