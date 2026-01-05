import json
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger
from ..config import OPENAI_API_KEY, OPENAI_MODEL

router = APIRouter()

# Config file path (save in backend directory)
CONFIG_FILE = Path(__file__).parent.parent.parent / "config.json"

class ConfigModel(BaseModel):
    """Configuration model"""
    whisper_default_model: str = "base"
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    openai_base_url: str = ""  # For custom API endpoints
    openai_temperature: float = 0.3
    openai_max_tokens: int = 500

def load_config() -> dict:
    """Load configuration from file or return defaults"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info(f"加载配置文件: {CONFIG_FILE}")
                return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return get_default_config()
    else:
        logger.info("配置文件不存在，使用默认配置")
        return get_default_config()

def get_default_config() -> dict:
    """Get default configuration"""
    return {
        "whisper_default_model": "base",
        "openai_api_key": OPENAI_API_KEY or "",
        "openai_model": OPENAI_MODEL,
        "openai_base_url": "",
        "openai_temperature": 0.3,
        "openai_max_tokens": 500
    }

def save_config(config: dict) -> None:
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info(f"保存配置文件: {CONFIG_FILE}")
        
        # Update environment variables if needed
        if config.get("openai_api_key"):
            os.environ["OPENAI_API_KEY"] = config["openai_api_key"]
        if config.get("openai_model"):
            os.environ["OPENAI_MODEL"] = config["openai_model"]
    except Exception as e:
        logger.error(f"保存配置文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")

@router.get("/api/config")
async def get_config():
    """获取当前配置"""
    logger.info("获取配置")
    try:
        config = load_config()
        # Don't expose full API key in response, only show if it's set
        config_display = config.copy()
        if config_display.get("openai_api_key"):
            # Show only last 4 characters for security
            api_key = config_display["openai_api_key"]
            if len(api_key) > 4:
                config_display["openai_api_key"] = "*" * (len(api_key) - 4) + api_key[-4:]
            else:
                config_display["openai_api_key"] = "*" * len(api_key)
        return {
            "config": config_display,
            "has_api_key": bool(config.get("openai_api_key")),
            "message": "获取配置成功"
        }
    except Exception as e:
        logger.error(f"获取配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")

@router.post("/api/config")
async def update_config(config_data: ConfigModel):
    """更新配置"""
    logger.info("更新配置")
    try:
        # Load existing config to preserve API key if not provided
        existing_config = load_config()
        
        # Prepare new config
        new_config = {
            "whisper_default_model": config_data.whisper_default_model,
            "openai_model": config_data.openai_model,
            "openai_base_url": config_data.openai_base_url,
            "openai_temperature": config_data.openai_temperature,
            "openai_max_tokens": config_data.openai_max_tokens
        }
        
        # Only update API key if provided (not empty)
        if config_data.openai_api_key:
            new_config["openai_api_key"] = config_data.openai_api_key
        elif existing_config.get("openai_api_key"):
            # Keep existing API key if not provided
            new_config["openai_api_key"] = existing_config["openai_api_key"]
        else:
            new_config["openai_api_key"] = ""
        
        # Save config
        save_config(new_config)
        
        logger.info("配置更新成功")
        return {
            "message": "配置更新成功",
            "config": {
                **new_config,
                "openai_api_key": "*" * len(new_config["openai_api_key"]) if new_config["openai_api_key"] else ""
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")

@router.get("/api/config/validate")
async def validate_config():
    """验证配置（检查API密钥等）"""
    logger.info("验证配置")
    try:
        config = load_config()
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check OpenAI API key if model is set
        if config.get("openai_model") and not config.get("openai_api_key"):
            validation_result["warnings"].append("OpenAI API密钥未设置，翻译功能将不可用")
        
        # Check Whisper model
        if not config.get("whisper_default_model"):
            validation_result["errors"].append("Whisper默认模型未设置")
            validation_result["valid"] = False
        
        if validation_result["errors"]:
            validation_result["valid"] = False
        
        return validation_result
    except Exception as e:
        logger.error(f"验证配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"验证配置失败: {str(e)}")

