#!/bin/bash
echo ""
echo "========================================"
echo "  SoundShield 声隐 - 自动安装脚本"
echo "========================================"
echo ""

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "[1/4] 创建虚拟环境..."
    python3 -m venv venv
else
    echo "[1/4] 虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境
source venv/bin/activate

# 检测 NVIDIA GPU
echo "[2/4] 检测显卡..."
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
    echo "    检测到 NVIDIA GPU，将安装 CUDA 版本的 PyTorch"
    echo "    正在安装 PyTorch (CUDA 12.1)..."
    pip install torch --index-url https://download.pytorch.org/whl/cu121 -q
else
    echo "    未检测到 NVIDIA GPU，将安装 CPU 版本的 PyTorch"
    echo "    正在安装 PyTorch (CPU)..."
    pip install torch -q
fi

# 安装 transformers from source
echo "[3/4] 安装 transformers (从源码)..."
pip install git+https://github.com/huggingface/transformers -q

# 安装其他依赖
echo "[4/4] 安装其他依赖..."
pip install PySide6 accelerate soundfile librosa numpy -q

echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo ""
echo "运行方式: python main.py"
echo ""
