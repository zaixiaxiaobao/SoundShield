"""
声隐 SoundShield - 字幕生成模块
生成 SRT 格式字幕文件
"""

import os
import re
from pathlib import Path
from typing import Optional, List, Tuple
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


def split_text_into_segments(
    text: str,
    duration: float,
    max_chars_per_segment: int = 40,
    min_segment_duration: float = 1.5,
    max_segment_duration: float = 5.0
) -> List[Tuple[float, float, str]]:
    """
    将文本分割成字幕段落
    
    Args:
        text: 完整文本
        duration: 音频总时长（秒）
        max_chars_per_segment: 每段最大字符数
        min_segment_duration: 每段最小时长（秒）
        max_segment_duration: 每段最大时长（秒）
        
    Returns:
        列表 [(start_time, end_time, text), ...]
    """
    if not text or duration <= 0:
        return []
    
    # 按句子分割（中文和英文标点）
    sentences = re.split(r'([。！？.!?]+)', text)
    
    # 合并标点符号到句子
    merged_sentences = []
    for i in range(0, len(sentences) - 1, 2):
        sentence = sentences[i]
        punct = sentences[i + 1] if i + 1 < len(sentences) else ""
        if sentence.strip():
            merged_sentences.append(sentence.strip() + punct)
    
    # 处理最后一个可能没有标点的句子
    if len(sentences) % 2 == 1 and sentences[-1].strip():
        merged_sentences.append(sentences[-1].strip())
    
    # 如果没有分割出句子，按字符数分割
    if not merged_sentences:
        merged_sentences = []
        words = text.strip()
        for i in range(0, len(words), max_chars_per_segment):
            segment = words[i:i + max_chars_per_segment].strip()
            if segment:
                merged_sentences.append(segment)
    
    if not merged_sentences:
        return [(0.0, duration, text.strip())]
    
    # 计算每个字符的平均时长
    total_chars = sum(len(s) for s in merged_sentences)
    if total_chars == 0:
        return [(0.0, duration, text.strip())]
    
    char_duration = duration / total_chars
    
    # 生成时间戳
    segments = []
    current_time = 0.0
    
    for sentence in merged_sentences:
        segment_duration = len(sentence) * char_duration
        
        # 限制段落时长
        segment_duration = max(min_segment_duration, min(segment_duration, max_segment_duration))
        
        # 确保不超过总时长
        end_time = min(current_time + segment_duration, duration)
        
        if sentence.strip():
            segments.append((current_time, end_time, sentence.strip()))
        
        current_time = end_time
        
        if current_time >= duration:
            break
    
    # 调整最后一段的结束时间
    if segments and segments[-1][1] < duration:
        last = segments[-1]
        segments[-1] = (last[0], duration, last[2])
    
    return segments


def generate_srt(segments: List[Tuple[float, float, str]]) -> str:
    """
    生成 SRT 格式字幕内容
    
    Args:
        segments: 字幕段落列表 [(start_time, end_time, text), ...]
        
    Returns:
        SRT 格式字符串
    """
    srt_lines = []
    
    for i, (start, end, text) in enumerate(segments, 1):
        srt_lines.append(str(i))
        srt_lines.append(f"{format_timestamp(start)} --> {format_timestamp(end)}")
        srt_lines.append(text)
        srt_lines.append("")  # 空行分隔
    
    return "\n".join(srt_lines)


def save_srt(
    srt_content: str,
    output_path: str
) -> bool:
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


def generate_subtitle_from_text(
    text: str,
    duration: float,
    output_path: Optional[str] = None,
    video_path: Optional[str] = None
) -> Tuple[str, Optional[str]]:
    """
    从识别文本生成字幕
    
    Args:
        text: 识别出的文本
        duration: 音频/视频时长（秒）
        output_path: 输出路径（可选）
        video_path: 视频文件路径（用于生成默认输出路径）
        
    Returns:
        (SRT 内容, 保存路径) 或 (SRT 内容, None)
    """
    # 分割文本
    segments = split_text_into_segments(text, duration)
    
    # 生成 SRT
    srt_content = generate_srt(segments)
    
    # 保存文件
    if output_path is None and video_path:
        output_path = str(Path(video_path).with_suffix('.srt'))
    
    saved_path = None
    if output_path:
        if save_srt(srt_content, output_path):
            saved_path = output_path
    
    return srt_content, saved_path
