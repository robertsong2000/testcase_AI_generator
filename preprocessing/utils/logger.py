"""
日志工具类
"""

from datetime import datetime
from typing import Any

class Logger:
    """日志工具类"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def info(self, message: str):
        """输出信息日志"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"ℹ️  [{timestamp}] {message}")
    
    def warning(self, message: str):
        """输出警告日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"⚠️  [{timestamp}] {message}")
    
    def error(self, message: str):
        """输出错误日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"❌ [{timestamp}] {message}")
    
    def success(self, message: str):
        """输出成功日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"✅ [{timestamp}] {message}")