#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
声隐 SoundShield - 应用入口
您的隐私听写专家 · 100% 本地运行

Copyright (c) 2024 SoundShield Team
"""

import sys
import os

# 确保能找到 src 模块1
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import create_app


def main():
    """主函数"""
    app, window = create_app()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
