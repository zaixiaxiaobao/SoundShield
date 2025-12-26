"""
声隐 SoundShield - 语音识别核心模块
使用 GLM-ASR-Nano-2512 模型进行语音转文字
"""

import os
import traceback
from typing import Optional, Callable
from pathlib import Path

# 模型相关
MODEL_ID = "zai-org/GLM-ASR-Nano-2512"


class Transcriber:
    """语音识别器类"""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = None
        self.is_loaded = False
        
    def load_model(self, progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        加载 GLM-ASR 模型
        
        Args:
            progress_callback: 进度回调函数，接收状态消息
            
        Returns:
            是否加载成功
        """
        try:
            if progress_callback:
                progress_callback("正在导入模型库...")
            
            import torch
            from transformers import GlmAsrForConditionalGeneration, AutoProcessor
            
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
                progress_callback("正在下载/加载模型（首次运行需要下载约 3GB）...")
            
            # 加载处理器
            self.processor = AutoProcessor.from_pretrained(MODEL_ID)
            
            if progress_callback:
                progress_callback("正在加载模型权重...")
            
            # 加载模型
            self.model = GlmAsrForConditionalGeneration.from_pretrained(
                MODEL_ID,
                torch_dtype="auto",
                device_map="auto"
            )
            
            self.is_loaded = True
            
            if progress_callback:
                progress_callback("模型加载完成！")
            
            return True
            
        except Exception as e:
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
    ) -> Optional[str]:
        """
        转写音频文件
        
        Args:
            audio_path: 音频文件路径
            progress_callback: 进度回调函数，接收(状态消息, 进度百分比)
            
        Returns:
            识别的文本，失败返回 None
        """
        if not self.is_loaded:
            if progress_callback:
                progress_callback("模型未加载", 0)
            return None
        
        try:
            if progress_callback:
                progress_callback("正在处理音频...", 10)
            
            # 处理输入
            inputs = self.processor.apply_transcription_request(audio_path)
            inputs = inputs.to(self.model.device, dtype=self.model.dtype)
            
            if progress_callback:
                progress_callback("正在识别语音...", 30)
            
            # 生成文本
            import torch
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    do_sample=False,
                    max_new_tokens=2000
                )
            
            if progress_callback:
                progress_callback("正在解码结果...", 90)
            
            # 解码输出
            decoded_outputs = self.processor.batch_decode(
                outputs[:, inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            )
            
            if progress_callback:
                progress_callback("识别完成！", 100)
            
            # 返回第一个结果
            if decoded_outputs:
                return decoded_outputs[0].strip()
            return ""
            
        except Exception as e:
            if progress_callback:
                progress_callback(f"识别失败: {str(e)}", 0)
            return None
    
    def transcribe_audio_array(
        self,
        audio_array,
        sample_rate: int = 16000,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Optional[str]:
        """
        转写音频数组（用于实时录音）
        
        Args:
            audio_array: numpy 音频数组
            sample_rate: 采样率
            progress_callback: 进度回调函数
            
        Returns:
            识别的文本
        """
        if not self.is_loaded:
            return None
        
        try:
            if progress_callback:
                progress_callback("正在处理音频...", 20)
            
            # 处理输入
            inputs = self.processor.apply_transcription_request(audio_array)
            inputs = inputs.to(self.model.device, dtype=self.model.dtype)
            
            if progress_callback:
                progress_callback("正在识别语音...", 50)
            
            # 生成文本
            import torch
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    do_sample=False,
                    max_new_tokens=2000
                )
            
            if progress_callback:
                progress_callback("正在解码结果...", 90)
            
            # 解码输出
            decoded_outputs = self.processor.batch_decode(
                outputs[:, inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            )
            
            if progress_callback:
                progress_callback("识别完成！", 100)
            
            if decoded_outputs:
                return decoded_outputs[0].strip()
            return ""
            
        except Exception as e:
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
