from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger
from ..dependencies import model_manager

router = APIRouter()

@router.get("/api/models")
async def list_models():
    """获取所有可用模型列表"""
    logger.info("获取模型列表")
    try:
        models = model_manager.get_available_models()
        logger.info(f"获取模型列表成功，共 {len(models)} 个模型")
        return {
            "models": models,
            "message": "获取模型列表成功"
        }
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")

@router.get("/api/model/status")
async def get_model_status(model_name: str):
    """获取指定模型的状态"""
    logger.info(f"获取模型状态: {model_name}")
    try:
        status = model_manager.get_model_status(model_name)
        logger.info(f"获取模型状态成功: {model_name}, 状态: {status['status']}")
        return status
    except Exception as e:
        logger.error(f"获取模型状态失败: {model_name}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模型状态失败: {str(e)}")

@router.post("/api/model/download")
async def download_model(model_name: str = None, revision: str = None, background_tasks: BackgroundTasks = None):
    """下载指定模型"""
    logger.info(f"开始下载模型: {model_name}, 版本: {revision}")
    try:
        # 检查是否已经在下载或已加载
        status = model_manager.get_model_status(model_name)
        if status["status"] == "loaded":
            logger.info(f"模型已加载: {model_name}")
            return {"message": "模型已加载", "model_name": model_name}
        elif status["status"] == "downloading":
            logger.info(f"模型正在下载中: {model_name}")
            return {"message": "模型正在下载中", "model_name": model_name}

        # 开始异步下载
        background_tasks.add_task(model_manager.download_model_async, model_name, revision)
        logger.info(f"开始异步下载模型: {model_name}")

        return {
            "message": "开始下载模型",
            "model_name": model_name,
            "revision": revision,
            "status": "downloading"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载模型失败: {model_name}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载模型失败: {str(e)}")

@router.delete("/api/model/delete")
async def delete_model(model_name: str):
    """删除指定模型"""
    logger.info(f"开始删除模型: {model_name}")
    try:
        result = model_manager.delete_model(model_name)
        logger.info(f"删除模型成功: {model_name}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除模型失败: {model_name}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除模型失败: {str(e)}")