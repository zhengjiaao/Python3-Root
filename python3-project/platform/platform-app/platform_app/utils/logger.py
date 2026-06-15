"""平台应用端的集中日志配置。

提供结构化日志输出（控制台和文件）、请求追踪
以及按模块创建日志工厂。

用法:
    from platform_app.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("应用启动")
"""

import json
import logging
import logging.handlers
import sys
from pathlib import Path

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_log_dir: Path | None = None
_log_level: int = logging.INFO
_configured_apps: set[str] = set()


class JSONFormatter(logging.Formatter):
    """JSON 结构化日志格式化器（供生产环境 ELK/Loki 采集）。"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    level: str = "INFO",
    log_dir: str | None = None,
    log_file: str = "app.log",
    app_name: str = "default",
    json_format: bool = False,
) -> None:
    """初始化根日志器，包含控制台和可选的文件处理器。"""
    global _log_dir, _log_level, _configured_apps

    if app_name in _configured_apps:
        return

    _configured_apps.add(app_name)
    _log_level = getattr(logging, level.upper(), logging.INFO)

    # 根日志器
    root = logging.getLogger()
    root.setLevel(_log_level)

    # 移除已有处理器以避免重复
    root.handlers.clear()

    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # 控制台处理器
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(_log_level)
    console.setFormatter(formatter)
    root.addHandler(console)

    # 文件处理器（可选）
    if log_dir:
        _log_dir = Path(log_dir)
        _log_dir.mkdir(parents=True, exist_ok=True)
        file_path = _log_dir / log_file
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(_log_level)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    # 静默嘈杂的第三方日志器
    for name in ("uvicorn.access", "sqlalchemy.engine", "sqlalchemy.pool"):
        logging.getLogger(name).setLevel(logging.WARNING)
    for name in list(logging.Logger.manager.loggerDict):
        if name.startswith("sqlalchemy."):
            logging.getLogger(name).setLevel(logging.WARNING)

    get_logger(__name__).info(
        "日志已初始化 | 应用=%s | 级别=%s | 格式=%s | 文件=%s",
        app_name,
        level,
        "JSON" if json_format else "TEXT",
        log_dir or "已禁用",
    )


def get_logger(name: str) -> logging.Logger:
    """返回指定名称的日志器，遵循已配置的级别。"""
    logger = logging.getLogger(name)
    if _configured_apps:
        logger.setLevel(_log_level)
    return logger
