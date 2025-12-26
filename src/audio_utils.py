"""
声隐 SoundShield - 音频处理工具
支持多种音频格式的加载和预处理
"""

import os
from pathlib import Path
from typing import Optional, Tuple
import numpy as np

# 支持的音频格式
SUPPORTED_FORMATS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.wma', '.aac'}


def is_supported_format(file_path: str) -> bool:
    """检查文件格式是否支持"""
    ext = Path(file_path).suffix.lower()
    return ext in SUPPORTED_FORMATS


def get_supported_formats_filter() -> str:
    """获取文件对话框的格式过滤器"""
    formats = " ".join(f"*{ext}" for ext in SUPPORTED_FORMATS)
    return f"音频文件 ({formats});;所有文件 (*.*)"


def load_audio(file_path: str, target_sr: int = 16000) -> Tuple[Optional[np.ndarray], Optional[int]]:
    """
    加载音频文件并转换为模型需要的格式
    
    Args:
        file_path: 音频文件路径
        target_sr: 目标采样率，GLM-ASR 默认使用 16000Hz
        
    Returns:
        audio_array: 音频数据数组
        sample_rate: 采样率
    """
    try:
        import librosa
        
        # 加载音频并重采样
        audio, sr = librosa.load(file_path, sr=target_sr, mono=True)
        
        return audio, sr
        
    except Exception as e:
        print(f"加载音频失败: {e}")
        return None, None


def get_audio_duration(file_path: str) -> Optional[float]:
    """
    获取音频时长（秒）
    
    Args:
        file_path: 音频文件路径
        
    Returns:
        duration: 音频时长（秒），失败返回 None
    """
    try:
        import librosa
        duration = librosa.get_duration(path=file_path)
        return duration
    except Exception as e:
        print(f"获取音频时长失败: {e}")
        return None


def format_duration(seconds: float) -> str:
    """
    格式化时长显示
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时长字符串，如 "1:23" 或 "1:23:45"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def get_file_info(file_path: str) -> dict:
    """
    获取音频文件信息
    
    Args:
        file_path: 音频文件路径
        
    Returns:
        包含文件信息的字典
    """
    path = Path(file_path)
    
    info = {
        "name": path.name,
        "size": path.stat().st_size if path.exists() else 0,
        "format": path.suffix.lower(),
        "duration": get_audio_duration(file_path),
    }
    
    # 格式化文件大小
    size_mb = info["size"] / (1024 * 1024)
    if size_mb >= 1:
        info["size_str"] = f"{size_mb:.1f} MB"
    else:
        size_kb = info["size"] / 1024
        info["size_str"] = f"{size_kb:.1f} KB"
    
    # 格式化时长
    if info["duration"]:
        info["duration_str"] = format_duration(info["duration"])
    else:
        info["duration_str"] = "未知"
    
    return info
