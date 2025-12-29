"""
声隐 SoundShield - 语音识别核心模块
使用 FunASR paraformer-zh 模型进行语音转文字（支持时间戳）
"""

import os
from typing import Optional, Callable, List, Dict, Any
from pathlib import Path


class Transcriber:
    """语音识别器类 - 使用 FunASR"""
    
    def __init__(self):
        self.model = None
        self.device = None
        self.is_loaded = False
        
    def load_model(self, progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        加载 FunASR 模型
        
        Args:
            progress_callback: 进度回调函数，接收状态消息
            
        Returns:
            是否加载成功
        """
        try:
            if progress_callback:
                progress_callback("正在导入模型库...")
            
            import torch
            from funasr import AutoModel
            
            if progress_callback:
                progress_callback("正在检测设备...")
            
            # 检测设备
            if torch.cuda.is_available():
                self.device = "cuda"
                device_name = torch.cuda.get_device_name(0)
                if progress_callback:
                    progress_callback(f"检测到 GPU: {device_name}")
            else:
                self.device = "cpu"
                if progress_callback:
                    progress_callback("未检测到 GPU，使用 CPU 模式（速度较慢）")
            
            if progress_callback:
                progress_callback("正在下载/加载模型（首次运行需要下载）...")
            
            # 加载 FunASR 模型
            # paraformer-zh: 中文语音识别
            # fsmn-vad: 语音活动检测
            # ct-punc: 标点预测
            self.model = AutoModel(
                model="paraformer-zh",
                vad_model="fsmn-vad",
                punc_model="ct-punc",
                device=self.device,
            )
            
            self.is_loaded = True
            
            if progress_callback:
                progress_callback("模型加载完成！")
            
            return True
            
        except Exception as e:
            import traceback
            error_msg = f"模型加载失败: {str(e)}"
            print(f"\n{'='*50}")
            print(f"ERROR: {error_msg}")
            print(f"{'='*50}")
            traceback.print_exc()
            print(f"{'='*50}\n")
            if progress_callback:
                progress_callback(error_msg)
            return False
    
    def transcribe(
        self, 
        audio_path: str,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        转写音频文件
        
        Args:
            audio_path: 音频文件路径
            progress_callback: 进度回调函数，接收(状态消息, 进度百分比)
            
        Returns:
            识别结果字典，包含 text 和 timestamps，失败返回 None
        """
        if not self.is_loaded:
            if progress_callback:
                progress_callback("模型未加载", 0)
            return None
        
        try:
            if progress_callback:
                progress_callback("正在处理音频...", 10)
            
            if progress_callback:
                progress_callback("正在识别语音...", 30)
            
            # 使用 FunASR 进行识别
            result = self.model.generate(
                input=audio_path,
                batch_size_s=300,  # 批处理大小（秒）
                sentence_timestamp=True,  # 启用句子时间戳
            )
            
            if progress_callback:
                progress_callback("正在处理结果...", 90)
            
            # 解析结果
            if result and len(result) > 0:
                res = result[0]
                
                # 提取文本
                text = res.get("text", "")
                
                # 提取时间戳
                timestamps = []
                if "sentence_info" in res:
                    for sent in res["sentence_info"]:
                        timestamps.append({
                            "text": sent.get("text", ""),
                            "start": sent.get("start", 0) / 1000.0,  # 转换为秒
                            "end": sent.get("end", 0) / 1000.0,
                        })
                elif "timestamp" in res:
                    # 备用：使用 timestamp 字段
                    for ts in res["timestamp"]:
                        timestamps.append({
                            "start": ts[0] / 1000.0,
                            "end": ts[1] / 1000.0,
                        })
                
                if progress_callback:
                    progress_callback("识别完成！", 100)
                
                return {
                    "text": text,
                    "timestamps": timestamps,
                    "raw": res  # 保留原始结果
                }
            
            return {"text": "", "timestamps": [], "raw": None}
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            if progress_callback:
                progress_callback(f"识别失败: {str(e)}", 0)
            return None


# 全局单例
_transcriber_instance: Optional[Transcriber] = None


def get_transcriber() -> Transcriber:
    """获取转写器单例"""
    global _transcriber_instance
    if _transcriber_instance is None:
        _transcriber_instance = Transcriber()
    return _transcriber_instance
