from pathlib import Path
import threading
from typing import Dict, Optional
from loguru import logger
from faster_whisper import WhisperModel


class WhisperModelManager:
    def __init__(self):
        self.models: Dict[str, WhisperModel] = {}
        self.download_status: Dict[str, Dict] = {}
        self.lock = threading.Lock()

    def get_available_models(self):
        """获取常用模型信息"""
        models_info = {
            "tiny": {
                "name": "Tiny",
                "description": "最快速度，精度较低 (~39 MB)",
                "size_mb": 39,
                "speed": "最快",
                "accuracy": "较低"
            },
            "base": {
                "name": "Base",
                "description": "平衡速度和精度 (~74 MB)",
                "size_mb": 74,
                "speed": "中等",
                "accuracy": "中等"
            },
            "small": {
                "name": "Small",
                "description": "较好精度 (~244 MB)",
                "size_mb": 244,
                "speed": "较慢",
                "accuracy": "良好"
            },
            "medium": {
                "name": "Medium",
                "description": "高精度 (~769 MB)",
                "size_mb": 769,
                "speed": "慢",
                "accuracy": "高"
            },
            "large-v1": {
                "name": "Large v1",
                "description": "最高精度 (~1550 MB)",
                "size_mb": 1550,
                "speed": "最慢",
                "accuracy": "最高"
            },
            "large-v2": {
                "name": "Large v2",
                "description": "最新最高精度 (~1550 MB)",
                "size_mb": 1550,
                "speed": "最慢",
                "accuracy": "最高"
            },
            "large-v3": {
                "name": "Large v3",
                "description": "最新最高精度 (~1550 MB)",
                "size_mb": 1550,
                "speed": "最慢",
                "accuracy": "最高"
            },
            "openai/whisper-tiny": {
                "name": "OpenAI Tiny",
                "description": "OpenAI官方Tiny模型 (~39 MB)",
                "size_mb": 39,
                "speed": "最快",
                "accuracy": "较低"
            },
            "openai/whisper-base": {
                "name": "OpenAI Base",
                "description": "OpenAI官方Base模型 (~74 MB)",
                "size_mb": 74,
                "speed": "中等",
                "accuracy": "中等"
            },
            "openai/whisper-small": {
                "name": "OpenAI Small",
                "description": "OpenAI官方Small模型 (~244 MB)",
                "size_mb": 244,
                "speed": "较慢",
                "accuracy": "良好"
            },
            "openai/whisper-medium": {
                "name": "OpenAI Medium",
                "description": "OpenAI官方Medium模型 (~769 MB)",
                "size_mb": 769,
                "speed": "慢",
                "accuracy": "高"
            },
            "openai/whisper-large-v3": {
                "name": "OpenAI Large v3",
                "description": "OpenAI官方最新Large模型 (~1550 MB)",
                "size_mb": 1550,
                "speed": "最慢",
                "accuracy": "最高"
            }
        }
        return models_info

    def is_model_downloaded(self, model_name: str) -> bool:
       """检查模型是否已下载到磁盘"""
       # 处理模型名称映射
       model_name_mapping = {
           "tiny": "Systran/faster-whisper-tiny",
           "base": "Systran/faster-whisper-base",
           "small": "Systran/faster-whisper-small",
           "medium": "Systran/faster-whisper-medium",
           "large-v1": "Systran/faster-whisper-large-v1",
           "large-v2": "Systran/faster-whisper-large-v2",
           "large-v3": "Systran/faster-whisper-large-v3",
       }
       # 如果是简短名称，转换为完整名称
       full_model_name = model_name_mapping.get(model_name, model_name)
       model_dir = Path("models") / f"models--{full_model_name.replace('/', '--')}"
       return model_dir.exists() and model_dir.is_dir()

    def get_model_status(self, model_name: str) -> Dict:
        """获取模型状态"""
        with self.lock:
            if model_name in self.models:
                return {
                    "status": "loaded",
                    "model_name": model_name,
                    "message": "模型已加载"
                }
            elif model_name in self.download_status:
                status_info = self.download_status[model_name]
                return {
                    "status": status_info.get("status", "unknown"),
                    "model_name": model_name,
                    "progress": status_info.get("progress", 0),
                    "message": status_info.get("message", "")
                }
            else:
                if self.is_model_downloaded(model_name):
                    return {
                        "status": "downloaded",
                        "model_name": model_name,
                        "message": "模型已下载"
                    }
                else:
                    return {
                        "status": "not_downloaded",
                        "model_name": model_name,
                        "message": "模型未下载"
                    }

    def download_model_async(self, model_name: str, revision: str = None):
        """异步下载模型"""
        def download_worker():
            logger.info(f"开始下载模型: {model_name}, 版本: {revision}")
            try:
                with self.lock:
                    self.download_status[model_name] = {
                        "status": "downloading",
                        "progress": 0,
                        "message": "开始下载模型..."
                    }

                # 下载并加载模型
                kwargs = {"download_root": "models"}
                if revision:
                    kwargs["revision"] = revision
                logger.debug(f"下载参数: {kwargs}")
                model = WhisperModel(model_name, **kwargs)

                with self.lock:
                    self.models[model_name] = model
                    self.download_status.pop(model_name, None)

                logger.info(f"模型下载并加载成功: {model_name}")

            except Exception as e:
                logger.error(f"模型下载失败: {model_name}, 错误: {str(e)}")
                with self.lock:
                    self.download_status[model_name] = {
                        "status": "error",
                        "progress": 0,
                        "message": f"下载失败: {str(e)}"
                    }

        thread = threading.Thread(target=download_worker, daemon=True)
        thread.start()

    def get_model(self, model_name: str) -> Optional[WhisperModel]:
        """获取模型，如果不存在则尝试加载已下载的模型"""
        with self.lock:
            # 如果模型已在内存中，直接返回
            if model_name in self.models:
                return self.models[model_name]

            # 如果模型已下载但未加载，尝试加载它
            if self.is_model_downloaded(model_name):
                logger.info(f"模型 {model_name} 已下载但未加载，正在加载...")
                try:
                    # 处理模型名称映射
                    model_name_mapping = {
                        "tiny": "Systran/faster-whisper-tiny",
                        "base": "Systran/faster-whisper-base",
                        "small": "Systran/faster-whisper-small",
                        "medium": "Systran/faster-whisper-medium",
                        "large-v1": "Systran/faster-whisper-large-v1",
                        "large-v2": "Systran/faster-whisper-large-v2",
                        "large-v3": "Systran/faster-whisper-large-v3",
                    }
                    full_model_name = model_name_mapping.get(model_name, model_name)

                    # 加载模型到内存
                    model = WhisperModel(full_model_name, download_root="models")
                    self.models[model_name] = model
                    logger.info(f"模型 {model_name} 加载成功")
                    return model
                except Exception as e:
                    logger.error(f"加载模型失败: {model_name}, 错误: {str(e)}")
                    return None

            # 模型未下载
            return None

    def delete_model(self, model_name: str) -> Dict[str, str]:
        """删除指定的模型"""
        logger.info(f"开始删除模型: {model_name}")
        with self.lock:
            # 检查模型是否正在下载
            if model_name in self.download_status:
                status = self.download_status[model_name]
                if status.get("status") == "downloading":
                    logger.warning(f"模型正在下载中，无法删除: {model_name}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"模型 {model_name} 正在下载中，无法删除"
                    )

            # 检查模型是否已加载
            if model_name in self.models:
                # 从内存中移除模型
                del self.models[model_name]
                logger.info(f"从内存中移除模型: {model_name}")

            # 删除模型文件
            try:
                import shutil
                from pathlib import Path

                # 处理模型名称映射
                # faster-whisper使用简短名称，但实际下载的是完整名称
                model_name_mapping = {
                    "tiny": "Systran/faster-whisper-tiny",
                    "base": "Systran/faster-whisper-base",
                    "small": "Systran/faster-whisper-small",
                    "medium": "Systran/faster-whisper-medium",
                    "large-v1": "Systran/faster-whisper-large-v1",
                    "large-v2": "Systran/faster-whisper-large-v2",
                    "large-v3": "Systran/faster-whisper-large-v3",
                }

                # 如果是简短名称，转换为完整名称
                full_model_name = model_name_mapping.get(model_name, model_name)

                model_dir = Path("models") / f"models--{full_model_name.replace('/', '--')}"
                if model_dir.exists():
                    shutil.rmtree(model_dir)
                    logger.info(f"删除模型文件成功: {model_name}")
                    return {
                        "message": f"模型 {model_name} 已成功删除",
                        "model_name": model_name
                    }
                else:
                    logger.info(f"模型文件不存在: {model_name}")
                    return {
                        "message": f"模型 {model_name} 的文件不存在，可能已被删除",
                        "model_name": model_name
                    }
            except Exception as e:
                logger.error(f"删除模型文件失败: {model_name}, 错误: {str(e)}")
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=500,
                    detail=f"删除模型文件失败: {str(e)}"
                )