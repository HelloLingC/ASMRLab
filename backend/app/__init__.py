from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import ALLOWED_ORIGINS, APP_TITLE, APP_VERSION, setup_logging
from .routers.health import router as health_router
from .routers.models import router as models_router
from .routers.audio import router as audio_router
from .routers.config import router as config_router
from .utils.system_utils import check_cuda
from loguru import logger

# 初始化日志系统
setup_logging()

# 启动时检查CUDA
cuda_info = check_cuda()
if cuda_info["available"]:
    logger.info(f"✅ CUDA可用: {cuda_info['device_count']} 个设备")
else:
    logger.info(f"⚠️ CUDA不可用: {cuda_info.get('error', '未知原因')}")

# 创建FastAPI应用
app = FastAPI(title=APP_TITLE, version=APP_VERSION)

# 配置CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(health_router)
app.include_router(models_router)
app.include_router(audio_router)
app.include_router(config_router)

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "AudioLab API",
        "version": APP_VERSION,
        "endpoints": {
            "health": "/api/health",
            "upload": "/api/upload",
            "process": "/api/process",
            "transcribe": "/api/transcribe",
            "models": "/api/models",
            "model_status": "/api/model/status?model_name=...",
            "download_model": "/api/model/download?model_name=...",
            "delete_model": "/api/model/delete?model_name=..."
        }
    }