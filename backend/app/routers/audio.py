import os
import tempfile
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from loguru import logger
from ..dependencies import model_manager
from ..utils.audio_utils import segments_to_srt
from ..config import UPLOAD_DIR

router = APIRouter()

@router.post("/api/upload")
async def upload_audio(file: UploadFile = File(...)):
    """上传音频文件"""
    logger.info(f"开始上传音频文件: {file.filename}, 类型: {file.content_type}")
    try:
        # 检查文件类型
        if not file.content_type or not file.content_type.startswith("audio/"):
            logger.warning(f"文件类型不正确: {file.content_type}")
            raise HTTPException(status_code=400, detail="只支持音频文件")

        # 保存文件
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        logger.info(f"文件上传成功: {file.filename}, 大小: {len(content)} bytes")
        return {
            "message": "文件上传成功",
            "filename": file.filename,
            "size": len(content),
            "file_path": str(file_path)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {file.filename}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@router.post("/api/process")
async def process_audio(file: UploadFile = File(...), operation: str = "analyze"):
    """处理音频文件"""
    logger.info(f"开始处理音频文件: {file.filename}, 操作: {operation}")
    try:
        # 这里可以添加实际的音频处理逻辑
        # 例如：降噪、变调、格式转换等

        # 读取文件
        content = await file.read()

        # 示例处理结果
        result = {
            "message": "音频处理完成",
            "filename": file.filename,
            "operation": operation,
            "file_size": len(content),
            "duration": "00:00:00",  # 实际应该从音频文件读取
            "sample_rate": 44100,  # 实际应该从音频文件读取
            "channels": 2,  # 实际应该从音频文件读取
        }

        logger.info(f"音频处理完成: {file.filename}, 操作: {operation}")
        return result
    except Exception as e:
        logger.error(f"音频处理失败: {file.filename}, 操作: {operation}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@router.post("/api/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    model_name: str = Form("base"),
    language: str = Form(None),
    format: str = Form("json")
):
    """使用Whisper模型转录音频文件"""
    logger.info(f"开始转录音频文件: {file.filename}, 模型: {model_name}, 语言: {language}, 格式: {format}")
    try:
        # 检查文件类型
        if not file.content_type or not file.content_type.startswith("audio/"):
            logger.warning(f"文件类型不正确: {file.content_type}")
            raise HTTPException(status_code=400, detail="只支持音频文件")

        # 读取文件内容
        content = await file.read()
        logger.debug(f"读取音频文件: {file.filename}, 大小: {len(content)} bytes")

        # 创建临时文件保存音频
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            # 获取Whisper模型
            model = model_manager.get_model(model_name)
            if model is None:
                logger.error(f"模型未找到: {model_name}")
                raise HTTPException(status_code=400, detail=f"模型 {model_name} 未下载或加载失败，请先下载模型")

            # 转录音频
            transcribe_options = {}
            if language:
                transcribe_options["language"] = language

            logger.info(f"开始Whisper转录: {file.filename}")
            segments, info = model.transcribe(tmp_file_path, **transcribe_options)
            segments = list(segments)
            logger.info(f"转录完成: {file.filename}, 检测语言: {info.language}, 段落数: {len(segments)}")

            # 转换结果格式以保持兼容性
            result = {
                "text": "",
                "language": info.language,
                "segments": []
            }

            for segment in segments:
                result["text"] += segment.text
                result["segments"].append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                })

            # 根据格式返回结果
            if format.lower() == "srt":
                srt_content = segments_to_srt(result["segments"])
                # 创建临时SRT文件
                srt_filename = Path(file.filename).stem + ".srt"
                srt_path = UPLOAD_DIR / srt_filename
                with open(srt_path, "w", encoding="utf-8") as f:
                    f.write(srt_content)

                logger.info(f"SRT文件生成: {srt_filename}")
                return FileResponse(
                    path=srt_path,
                    filename=srt_filename,
                    media_type="text/plain",
                    headers={"Content-Disposition": f"attachment; filename={srt_filename}"}
                )
            else:
                # 返回JSON结果
                logger.info(f"转录成功: {file.filename}, 文本长度: {len(result['text'])} 字符")
                return {
                    "message": "转录完成",
                    "filename": file.filename,
                    "text": result["text"],
                    "language": result.get("language", "unknown"),
                    "segments": result.get("segments", []),
                    "model_name": model_name
                }
        finally:
            # 清理临时文件
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                logger.debug(f"清理临时文件: {tmp_file_path}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"转录失败: {file.filename}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"转录失败: {str(e)}")