# 🛡️ 声隐 SoundShield

> 您的隐私听写专家 - 100% 本地运行的语音转文字工具

## ✨ 特性

- 🔒 **完全离线** - 音频永不上传，数据不出本机
- 💰 **一次购买** - 永久使用，无订阅费
- 🗣️ **方言支持** - 粤语、普通话、英语识别能力强
- 🔊 **低音量优化** - 专门针对轻声说话场景优化
- 🎙️ **音频格式** - MP3, WAV, M4A, FLAC, OGG, AAC, WMA
- 🎬 **视频格式** - MP4, MKV, AVI, MOV, WMV, FLV, WebM

## 🚀 快速开始

### 环境要求
- Python 3.10+
- 建议有 NVIDIA GPU (6GB+ 显存) 以获得最佳性能
- 无 GPU 也可运行，但速度较慢
- **FFmpeg** (用于视频音频提取，可选)
  - Windows: `winget install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

### 安装

```bash
# 克隆项目
git clone https://github.com/zaixiaxiaobao/SoundShield.git
cd SoundShield

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# GPU 用户先安装 CUDA 版 PyTorch (可选，大幅提升速度):
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

> ⚠️ **首次运行**会自动下载约 1GB 的模型文件，请保持网络通畅。

## 📖 使用说明

1. 启动应用后，拖拽音频/视频文件到窗口或点击选择文件
2. 等待识别完成
3. 复制文本/导出 TXT/导出字幕(SRT)

## 🛠️ 技术栈

- **UI**: PySide6 (Qt for Python)
- **语音识别**: FunASR paraformer-zh (阿里达摩院)
- **音频处理**: librosa, soundfile
- **字幕生成**: 支持 SRT 格式，精确时间戳

## 📄 许可证

MIT License

---

Made with ❤️ by SoundShield Team
