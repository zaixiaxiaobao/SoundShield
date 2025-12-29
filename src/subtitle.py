"""
声隐 SoundShield - 字幕生成模块
生成 SRT 格式字幕文件（支持精确时间戳）
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import timedelta


def format_timestamp(seconds: float) -> str:
    """
    将秒数转换为 SRT 时间戳格式
    
    Args:
        seconds: 秒数
        
    Returns:
        SRT 格式时间戳 (HH:MM:SS,mmm)
    """
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = int(td.total_seconds() % 60)
    millis = int((td.total_seconds() % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt_from_timestamps(timestamps: List[Dict[str, Any]]) -> str:
    """
    从时间戳列表生成 SRT 格式字幕
    
    Args:
        timestamps: 时间戳列表 [{"text": str, "start": float, "end": float}, ...]
        
    Returns:
        SRT 格式字符串
    """
    srt_lines = []
    
    for i, segment in enumerate(timestamps, 1):
        text = segment.get("text", "").strip()
        start = segment.get("start", 0)
        end = segment.get("end", 0)
        
        if not text:
            continue
        
        srt_lines.append(str(i))
        srt_lines.append(f"{format_timestamp(start)} --> {format_timestamp(end)}")
        srt_lines.append(text)
        srt_lines.append("")  # 空行分隔
    
    return "\n".join(srt_lines)


def save_srt(srt_content: str, output_path: str) -> bool:
    """
    保存 SRT 字幕文件
    
    Args:
        srt_content: SRT 格式内容
        output_path: 输出文件路径
        
    Returns:
        是否保存成功
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        return True
    except Exception as e:
        print(f"保存字幕失败: {e}")
        return False


def generate_subtitle(
    transcription_result: Dict[str, Any],
    output_path: Optional[str] = None,
    source_path: Optional[str] = None
) -> tuple[str, Optional[str]]:
    """
    从识别结果生成字幕
    
    Args:
        transcription_result: 识别结果（包含 text 和 timestamps）
        output_path: 输出路径（可选）
        source_path: 源文件路径（用于生成默认输出路径）
        
    Returns:
        (SRT 内容, 保存路径) 或 (SRT 内容, None)
    """
    timestamps = transcription_result.get("timestamps", [])
    
    if not timestamps:
        # 如果没有时间戳，返回空
        return "", None
    
    # 生成 SRT
    srt_content = generate_srt_from_timestamps(timestamps)
    
    # 保存文件
    if output_path is None and source_path:
        output_path = str(Path(source_path).with_suffix('.srt'))
    
    saved_path = None
    if output_path:
        if save_srt(srt_content, output_path):
            saved_path = output_path
    
    return srt_content, saved_path


# 保留旧的函数以保持向后兼容
def generate_subtitle_from_text(
    text: str,
    duration: float,
    output_path: Optional[str] = None,
    video_path: Optional[str] = None
) -> tuple[str, Optional[str]]:
    """
    从纯文本生成字幕（无精确时间戳时使用）
    基于文本长度和总时长估算时间
    """
    import re
    
    if not text or duration <= 0:
        return "", None
    
    # 按句子分割
    sentences = re.split(r'([。！？.!?]+)', text)
    
    # 合并标点到句子
    merged = []
    for i in range(0, len(sentences) - 1, 2):
        sentence = sentences[i]
        punct = sentences[i + 1] if i + 1 < len(sentences) else ""
        if sentence.strip():
            merged.append(sentence.strip() + punct)
    
    if len(sentences) % 2 == 1 and sentences[-1].strip():
        merged.append(sentences[-1].strip())
    
    if not merged:
        return "", None
    
    # 估算时间
    total_chars = sum(len(s) for s in merged)
    char_duration = duration / total_chars if total_chars > 0 else 0
    
    timestamps = []
    current_time = 0.0
    
    for sentence in merged:
        segment_duration = len(sentence) * char_duration
        segment_duration = max(1.5, min(segment_duration, 5.0))
        end_time = min(current_time + segment_duration, duration)
        
        timestamps.append({
            "text": sentence,
            "start": current_time,
            "end": end_time
        })
        
        current_time = end_time
        if current_time >= duration:
            break
    
    # 调整最后一段
    if timestamps and timestamps[-1]["end"] < duration:
        timestamps[-1]["end"] = duration
    
    srt_content = generate_srt_from_timestamps(timestamps)
    
    saved_path = None
    if output_path:
        if save_srt(srt_content, output_path):
            saved_path = output_path
    
    return srt_content, saved_path
