from fastapi import APIRouter
from loguru import logger
from ..utils.system_utils import check_cuda

router = APIRouter()

@router.get("/api/health")
async def health_check():
    """健康检查端点"""
    logger.debug("健康检查请求")
    cuda_info = check_cuda()
    return {
        "status": "healthy",
        "service": "AudioLab API",
        "cuda": cuda_info
    }