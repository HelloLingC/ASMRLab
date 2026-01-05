"""System and environment utilities"""
import sys
from typing import Dict, Optional, Any
from loguru import logger


def check_cuda() -> Dict[str, Any]:
    """
    检查CUDA可用性
    
    Returns:
        Dict包含CUDA状态信息:
        - available: bool - CUDA是否可用
        - device_count: int - 可用CUDA设备数量
        - devices: list - 设备信息列表
        - cuda_version: str - CUDA版本 (如果有)
        - error: str - 错误信息 (如果有)
    """
    result = {
        "available": False,
        "device_count": 0,
        "devices": [],
        "cuda_version": None,
        "error": None
    }
    
    try:
        import torch
        
        # 检查CUDA是否可用
        if not torch.cuda.is_available():
            result["error"] = "CUDA不可用 (torch.cuda.is_available() = False)"
            logger.warning("CUDA不可用: PyTorch检测到CUDA未安装或未正确配置")
            return result
        
        result["available"] = True
        result["device_count"] = torch.cuda.device_count()
        
        # 获取CUDA版本
        try:
            result["cuda_version"] = torch.version.cuda
        except Exception:
            pass
        
        # 获取每个设备的信息
        devices = []
        for i in range(result["device_count"]):
            try:
                device_name = torch.cuda.get_device_name(i)
                device_props = torch.cuda.get_device_properties(i)
                devices.append({
                    "index": i,
                    "name": device_name,
                    "total_memory_mb": round(device_props.total_memory / (1024 ** 2), 2),
                    "major": device_props.major,
                    "minor": device_props.minor,
                    "multi_processor_count": device_props.multi_processor_count
                })
            except Exception as e:
                devices.append({
                    "index": i,
                    "name": f"Unknown device {i}",
                    "error": str(e)
                })
        
        result["devices"] = devices
        
        logger.info(f"CUDA可用: 检测到 {result['device_count']} 个CUDA设备")
        for device in devices:
            logger.info(f"  - 设备 {device['index']}: {device['name']} ({device.get('total_memory_mb', 'N/A')} MB)")
        
    except ImportError:
        result["error"] = "PyTorch未安装"
        logger.warning("无法检查CUDA: PyTorch未安装")
    except Exception as e:
        result["error"] = f"检查CUDA时出错: {str(e)}"
        logger.error(f"检查CUDA时出错: {str(e)}")
    
    return result


def check_cudnn() -> Dict[str, Any]:
    """
    检查cuDNN可用性
    
    Returns:
        Dict包含cuDNN状态信息:
        - available: bool - cuDNN是否可用
        - enabled: bool - cuDNN是否已启用
        - version: int - cuDNN版本号 (如果有)
        - error: str - 错误信息 (如果有)
    """
    result = {
        "available": False,
        "enabled": False,
        "version": None,
        "error": None
    }
    
    try:
        import torch
        
        # 检查cuDNN是否可用
        try:
            result["available"] = torch.backends.cudnn.is_available()
        except Exception as e:
            result["error"] = f"无法检查cuDNN可用性: {str(e)}"
            logger.warning(f"无法检查cuDNN可用性: {str(e)}")
            return result
        
        if not result["available"]:
            result["error"] = "cuDNN不可用 (torch.backends.cudnn.is_available() = False)"
            logger.warning("cuDNN不可用: PyTorch检测到cuDNN未安装或未正确配置")
            return result
        
        # 检查cuDNN是否已启用
        try:
            result["enabled"] = torch.backends.cudnn.enabled
        except Exception:
            result["enabled"] = False
        
        # 获取cuDNN版本
        try:
            result["version"] = torch.backends.cudnn.version()
        except Exception as e:
            logger.warning(f"无法获取cuDNN版本: {str(e)}")
        
        # 获取其他cuDNN信息
        try:
            result["benchmark"] = torch.backends.cudnn.benchmark
        except Exception:
            pass
        
        try:
            result["deterministic"] = torch.backends.cudnn.deterministic
        except Exception:
            pass
        
        logger.info(f"cuDNN可用: 版本 {result['version']} (启用: {result['enabled']})")
        
    except ImportError:
        result["error"] = "PyTorch未安装"
        logger.warning("无法检查cuDNN: PyTorch未安装")
    except Exception as e:
        result["error"] = f"检查cuDNN时出错: {str(e)}"
        logger.error(f"检查cuDNN时出错: {str(e)}")
    
    return result


def get_system_info() -> Dict[str, Any]:
    """
    获取系统信息
    
    Returns:
        Dict包含系统信息
    """
    info = {
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "cuda": check_cuda()
    }
    
    return info

