from pathlib import Path
from loguru import logger

# CORS origins
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:3000",  # Alternative dev port
]

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Models directory
MODELS_DIR = Path("models")

# Logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# App configuration
APP_TITLE = "AudioLab API"
APP_VERSION = "1.0.0"

# Logging configuration
def setup_logging():
    """配置日志系统"""
    # 移除默认的handler
    logger.remove()

    # 控制台日志 - INFO级别及以上
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )

    # 文件日志 - DEBUG级别及以上，带轮转
    logger.add(
        LOGS_DIR / "audiolab_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="00:00",  # 每天轮转
        retention="30 days",  # 保留30天
        encoding="utf-8"
    )

    # 错误日志单独文件
    logger.add(
        LOGS_DIR / "audiolab_error_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="00:00",
        retention="30 days",
        encoding="utf-8"
    )

    logger.info("日志系统初始化完成")