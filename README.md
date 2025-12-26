# 🛡️ 声隐 SoundShield

> 您的隐私听写专家 - 100% 本地运行的语音转文字工具

## ✨ 特性

- 🔒 **完全离线** - 音频永不上传，数据不出本机
- 💰 **一次购买** - 永久使用，无订阅费
- 🗣️ **方言支持** - 粤语、普通话、英语识别能力强
- 🔊 **低音量优化** - 专门针对轻声说话场景优化
- 📁 **多格式支持** - MP3, WAV, M4A, FLAC, OGG

## 🚀 快速开始

### 环境要求
- Python 3.10+
- 建议有 NVIDIA GPU (6GB+ 显存) 以获得最佳性能
- 无 GPU 也可运行，但速度较慢

### 安装

**方式一：一键安装（推荐）**

```bash
# 克隆项目
git clone https://github.com/zaixiaxiaobao/SoundShield.git
cd SoundShield

# Windows: 双击 install.bat
# macOS/Linux: bash install.sh
```

**方式二：手动安装**

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# GPU 用户 (NVIDIA):
pip install torch --index-url https://download.pytorch.org/whl/cu121

# CPU 用户:
# pip install torch

pip install git+https://github.com/huggingface/transformers
pip install -r requirements.txt
python main.py
```

> ⚠️ **首次运行**会自动下载约 3GB 的模型文件，请保持网络通畅。

## 📖 使用说明

1. 启动应用后，拖拽音频文件到窗口或点击选择文件
2. 等待识别完成
3. 复制或导出识别结果

## 🛠️ 技术栈

- **UI**: PySide6 (Qt for Python)
- **模型**: GLM-ASR-Nano-2512
- **音频处理**: librosa, soundfile

## 📄 许可证

MIT License

---

Made with ❤️ by SoundShield Team
