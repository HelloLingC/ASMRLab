def format_timestamp(seconds: float) -> str:
    """将秒数转换为SRT格式的时间戳 (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def segments_to_srt(segments) -> str:
    """将转录段转换为SRT格式"""
    srt_content = []
    for i, segment in enumerate(segments, 1):
        start_time = format_timestamp(segment.start)
        end_time = format_timestamp(segment.end)
        text = segment.text.strip()

        srt_entry = f"{i}\n{start_time} --> {end_time}\n{text}\n"
        srt_content.append(srt_entry)

    return "\n".join(srt_content)


def parse_srt(srt_content: str) -> list:
    """解析SRT文件内容，返回字幕段列表"""
    lines = srt_content.split('\n')
    segments = []
    current_segment = None
    
    for line in lines:
        line = line.strip()
        
        # 空行表示一个字幕段结束
        if not line:
            if current_segment:
                segments.append(current_segment)
                current_segment = None
            continue
        
        # 检查是否是时间戳行 (包含 -->)
        if '-->' in line:
            parts = line.split('-->')
            if len(parts) == 2:
                start_str = parts[0].strip()
                end_str = parts[1].strip()
                current_segment = {
                    'start': srt_time_to_seconds(start_str),
                    'end': srt_time_to_seconds(end_str),
                    'text': ''
                }
        # 如果是数字（序号），跳过
        elif line.isdigit():
            continue
        # 否则是文本内容
        elif current_segment is not None:
            if current_segment['text']:
                current_segment['text'] += ' ' + line
            else:
                current_segment['text'] = line
    
    # 添加最后一个段
    if current_segment:
        segments.append(current_segment)
    
    return segments


def srt_time_to_seconds(time_str: str) -> float:
    """将SRT时间格式 (HH:MM:SS,mmm) 转换为秒数"""
    # 处理逗号或点作为毫秒分隔符
    if ',' in time_str:
        time_part, ms_part = time_str.split(',')
    elif '.' in time_str:
        time_part, ms_part = time_str.split('.')
    else:
        time_part = time_str
        ms_part = '0'
    
    # 解析时:分:秒
    time_parts = time_part.split(':')
    hours = int(time_parts[0]) if len(time_parts) > 0 else 0
    minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
    seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
    
    # 解析毫秒（最多3位）
    milliseconds = int(ms_part[:3].ljust(3, '0'))
    
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0


def segments_to_srt_string(segments: list) -> str:
    """将字幕段列表转换为SRT格式字符串"""
    srt_content = []
    for i, segment in enumerate(segments, 1):
        start_time = format_timestamp(segment['start'])
        end_time = format_timestamp(segment['end'])
        text = segment['text'].strip()
        
        srt_entry = f"{i}\n{start_time} --> {end_time}\n{text}\n"
        srt_content.append(srt_entry)
    
    return "\n".join(srt_content)