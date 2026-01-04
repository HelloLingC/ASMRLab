from fastapi import APIRouter
from loguru import logger

router = APIRouter()

@router.get("/api/health")
async def health_check():
    """健康检查端点"""
    logger.debug("健康检查请求")
    return {"status": "healthy", "service": "AudioLab API"}