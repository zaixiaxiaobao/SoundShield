@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   SoundShield 声隐 - 自动安装脚本
echo ========================================
echo.

REM 创建虚拟环境
if not exist "venv" (
    echo [1/4] 创建虚拟环境...
    python -m venv venv
) else (
    echo [1/4] 虚拟环境已存在，跳过创建
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检测 NVIDIA GPU
echo [2/4] 检测显卡...
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo     检测到 NVIDIA GPU，将安装 CUDA 版本的 PyTorch
    echo     正在安装 PyTorch (CUDA 12.1)...
    pip install torch --index-url https://download.pytorch.org/whl/cu121 -q
) else (
    echo     未检测到 NVIDIA GPU，将安装 CPU 版本的 PyTorch
    echo     正在安装 PyTorch (CPU)...
    pip install torch -q
)

REM 安装 transformers from source
echo [3/4] 安装 transformers (从源码)...
pip install git+https://github.com/huggingface/transformers -q

REM 安装其他依赖
echo [4/4] 安装其他依赖...
pip install PySide6 accelerate soundfile librosa numpy -q

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 运行方式: python main.py
echo.
pause
