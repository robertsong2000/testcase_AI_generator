#!/usr/bin/env python3
"""
基于LangChain的CAPL代码生成器 - 重构版本

这是capl_generator_langchain.py的重构版本，使用模块化的代码结构。
原文件已被拆分为多个模块，位于capl_langchain/目录下。
"""

import sys
from pathlib import Path

# 将模块路径添加到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from capl_langchain.utils.cli import main

if __name__ == "__main__":
    main()