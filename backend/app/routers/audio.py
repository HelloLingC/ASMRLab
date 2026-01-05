import os
import tempfile
import zipfile
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from loguru import logger
from ..dependencies import model_manager
from ..utils.audio_utils import segments_to_srt, parse_srt, segments_to_srt_string
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


@router.post("/api/translate-srt")
async def translate_srt(
    file: UploadFile = File(...),
    target_language: str = Form("en"),
    source_language: str = Form(None),
):
    """使用LLM翻译SRT字幕文件"""
    logger.info(f"开始翻译SRT文件: {file.filename}, 目标语言: {target_language}, 源语言: {source_language}")
    
    try:
        # 检查文件类型
        if not file.filename.endswith('.srt'):
            logger.warning(f"文件类型不正确: {file.filename}")
            raise HTTPException(status_code=400, detail="只支持SRT文件")
        
        # 读取SRT文件内容
        content = await file.read()
        srt_content = content.decode('utf-8')
        logger.debug(f"读取SRT文件: {file.filename}, 大小: {len(srt_content)} 字符")
        
        # 解析SRT文件
        segments = parse_srt(srt_content)
        logger.info(f"解析SRT文件成功: {file.filename}, 字幕段数: {len(segments)}")
        
        if not segments:
            raise HTTPException(status_code=400, detail="SRT文件为空或格式不正确")
        
        # 检查OpenAI API密钥 - 优先使用配置文件
        from ..routers.config import load_config
        config = load_config()
        api_key = config.get("openai_api_key") or os.getenv("OPENAI_API_KEY", "")
        model = config.get("openai_model") or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        base_url = config.get("openai_base_url") or None
        temperature = config.get("openai_temperature", 0.3)
        max_tokens = config.get("openai_max_tokens", 500)
        
        if not api_key:
            logger.error("OpenAI API密钥未配置")
            raise HTTPException(
                status_code=500,
                detail="OpenAI API密钥未配置，请在配置页面设置 API 密钥"
            )
        
        # 使用OpenAI翻译
        try:
            from openai import OpenAI
            client_kwargs = {"api_key": api_key}
            if base_url:
                client_kwargs["base_url"] = base_url
            client = OpenAI(**client_kwargs)
            
            # 翻译所有字幕段
            translated_segments = []
            for i, segment in enumerate(segments, 1):
                text = segment['text'].strip()
                if not text:
                    translated_segments.append(segment)
                    continue
                
                # 构建翻译提示
                source_lang_text = f" from {source_language}" if source_language else ""
                prompt = f"Translate the following subtitle text{source_lang_text} to {target_language}. Only return the translated text, do not add any explanations or notes:\n\n{text}"
                
                logger.debug(f"翻译字幕段 {i}/{len(segments)}: {text[:50]}...")
                
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a professional translator. Translate subtitle text accurately while preserving the meaning and style."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    
                    translated_text = response.choices[0].message.content.strip()
                    translated_segments.append({
                        'start': segment['start'],
                        'end': segment['end'],
                        'text': translated_text
                    })
                    
                    logger.debug(f"翻译完成: {text[:30]}... -> {translated_text[:30]}...")
                    
                except Exception as e:
                    logger.error(f"翻译字幕段失败: {i}, 错误: {str(e)}")
                    # 如果翻译失败，保留原文
                    translated_segments.append(segment)
            
            # 转换为SRT格式
            translated_srt = segments_to_srt_string(translated_segments)
            
            # 保存翻译后的SRT文件
            srt_filename = Path(file.filename).stem + f"_translated_{target_language}.srt"
            srt_path = UPLOAD_DIR / srt_filename
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(translated_srt)
            
            logger.info(f"SRT翻译完成: {file.filename} -> {srt_filename}")
            
            return FileResponse(
                path=srt_path,
                filename=srt_filename,
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename={srt_filename}"}
            )
            
        except ImportError:
            logger.error("OpenAI库未安装")
            raise HTTPException(
                status_code=500,
                detail="OpenAI库未安装，请运行: pip install openai"
            )
        except Exception as e:
            logger.error(f"OpenAI翻译失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"翻译失败: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"翻译SRT失败: {file.filename}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")


@router.post("/api/separate-voice")
async def separate_voice(
    file: UploadFile = File(...),
    model: str = Form("htdemucs"),
    stems: str = Form("vocals,drums,bass,other")
):
    """使用Demucs分离音频中的声音和伴奏"""
    logger.info(f"开始分离音频: {file.filename}, 模型: {model}, 分离轨道: {stems}")
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
            # 导入Demucs
            try:
                from demucs.pretrained import get_model
                from demucs.apply import apply_model
                import torch
                import torchaudio
            except ImportError as e:
                logger.error(f"Demucs库未正确安装: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Demucs库未正确安装，请运行: pip install demucs"
                )

            # 创建输出目录
            output_dir = tempfile.mkdtemp()
            logger.info(f"创建输出目录: {output_dir}")

            # 检测设备
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"使用设备: {device}")

            # 加载模型
            logger.info(f"加载Demucs模型: {model}")
            try:
                demucs_model = get_model(model)
                demucs_model.to(device)
                demucs_model.eval()
            except Exception as e:
                logger.error(f"加载模型失败: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"加载模型失败: {str(e)}。请确保模型已下载。"
                )

            # 加载音频文件
            logger.info(f"加载音频文件: {tmp_file_path}")
            try:
                wav, sr = torchaudio.load(tmp_file_path)
                # 转换为单声道（如果需要）
                if wav.shape[0] > 1:
                    wav = torch.mean(wav, dim=0, keepdim=True)
                # 转换为模型期望的格式
                wav = wav.unsqueeze(0)  # 添加batch维度
            except Exception as e:
                logger.error(f"加载音频文件失败: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"加载音频文件失败: {str(e)}"
                )

            # 分离音频
            logger.info(f"开始分离音频: {file.filename}")
            try:
                with torch.no_grad():
                    sources = apply_model(demucs_model, wav.to(device), device=device)
                # sources shape: [batch, sources, channels, samples]
                sources = sources[0].cpu()  # 移除batch维度
                
                # Demucs默认输出: [drums, bass, other, vocals]
                stem_names = ["drums", "bass", "other", "vocals"]
                
                # 保存分离后的文件
                model_output_dir = Path(output_dir) / model / Path(file.filename).stem
                model_output_dir.mkdir(parents=True, exist_ok=True)
                
                for i, stem_name in enumerate(stem_names):
                    if i < sources.shape[0]:
                        stem_audio = sources[i]
                        # 转换为立体声（如果需要）
                        if stem_audio.shape[0] == 1:
                            stem_audio = stem_audio.repeat(2, 1)
                        
                        output_path = model_output_dir / f"{stem_name}.wav"
                        torchaudio.save(str(output_path), stem_audio, sr)
                        logger.debug(f"保存轨道: {stem_name} -> {output_path}")
                
            except Exception as e:
                logger.error(f"分离音频失败: {str(e)}")
                # 如果CUDA失败，尝试CPU
                if device == "cuda":
                    logger.info("CUDA分离失败，尝试使用CPU进行分离")
                    try:
                        demucs_model = demucs_model.cpu()
                        with torch.no_grad():
                            sources = apply_model(demucs_model, wav, device="cpu")
                        sources = sources[0]
                        
                        stem_names = ["drums", "bass", "other", "vocals"]
                        model_output_dir = Path(output_dir) / model / Path(file.filename).stem
                        model_output_dir.mkdir(parents=True, exist_ok=True)
                        
                        for i, stem_name in enumerate(stem_names):
                            if i < sources.shape[0]:
                                stem_audio = sources[i]
                                if stem_audio.shape[0] == 1:
                                    stem_audio = stem_audio.repeat(2, 1)
                                output_path = model_output_dir / f"{stem_name}.wav"
                                torchaudio.save(str(output_path), stem_audio, sr)
                    except Exception as e2:
                        logger.error(f"CPU分离也失败: {str(e2)}")
                        raise HTTPException(
                            status_code=500,
                            detail=f"音频分离失败: {str(e2)}"
                        )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"音频分离失败: {str(e)}"
                    )

            # 查找分离后的文件
            # Demucs输出结构: output_dir/model_name/track_name/stem.wav
            model_output_dir = Path(output_dir) / model / Path(file.filename).stem
            if not model_output_dir.exists():
                # 尝试查找其他可能的输出结构
                model_dirs = list(Path(output_dir).glob("*"))
                if model_dirs:
                    model_output_dir = model_dirs[0] / Path(file.filename).stem

            if not model_output_dir.exists():
                logger.error(f"找不到输出目录: {model_output_dir}")
                raise HTTPException(
                    status_code=500,
                    detail="分离完成但找不到输出文件"
                )

            # 收集分离后的文件
            stem_files = {}
            requested_stems = [s.strip() for s in stems.split(",")]
            
            for stem_file in model_output_dir.glob("*.wav"):
                stem_name = stem_file.stem
                if stem_name in requested_stems or stems == "all":
                    stem_files[stem_name] = stem_file

            if not stem_files:
                logger.warning(f"未找到请求的轨道: {requested_stems}")
                # 返回所有可用的轨道
                for stem_file in model_output_dir.glob("*.wav"):
                    stem_files[stem_file.stem] = stem_file

            if not stem_files:
                raise HTTPException(
                    status_code=500,
                    detail="分离完成但未找到任何输出文件"
                )

            logger.info(f"分离完成，找到 {len(stem_files)} 个轨道: {list(stem_files.keys())}")

            # 如果只有一个文件，直接返回
            if len(stem_files) == 1:
                stem_name, stem_path = next(iter(stem_files.items()))
                output_filename = f"{Path(file.filename).stem}_{stem_name}.wav"
                output_path = UPLOAD_DIR / output_filename
                
                # 复制文件到上传目录
                import shutil
                shutil.copy2(stem_path, output_path)
                
                logger.info(f"返回单个文件: {output_filename}")
                return FileResponse(
                    path=output_path,
                    filename=output_filename,
                    media_type="audio/wav",
                    headers={"Content-Disposition": f"attachment; filename={output_filename}"}
                )
            else:
                # 多个文件，打包成ZIP
                zip_filename = f"{Path(file.filename).stem}_separated.zip"
                zip_path = UPLOAD_DIR / zip_filename
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for stem_name, stem_path in stem_files.items():
                        output_filename = f"{Path(file.filename).stem}_{stem_name}.wav"
                        zipf.write(stem_path, output_filename)
                        logger.debug(f"添加到ZIP: {output_filename}")

                logger.info(f"返回ZIP文件: {zip_filename}, 包含 {len(stem_files)} 个文件")
                return FileResponse(
                    path=zip_path,
                    filename=zip_filename,
                    media_type="application/zip",
                    headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
                )

        finally:
            # 清理临时文件
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                logger.debug(f"清理临时文件: {tmp_file_path}")
            
            # 清理输出目录
            try:
                import shutil
                if os.path.exists(output_dir):
                    shutil.rmtree(output_dir)
                    logger.debug(f"清理输出目录: {output_dir}")
            except Exception as e:
                logger.warning(f"清理输出目录失败: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分离音频失败: {file.filename}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分离失败: {str(e)}")