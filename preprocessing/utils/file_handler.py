"""
文件处理工具类
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

# 修复导入问题
from preprocessing.utils.logger import Logger

class FileHandler:
    """文件处理工具类"""
    
    def __init__(self, logger: Optional['Logger'] = None):
        """初始化文件处理器
        
        Args:
            logger: 日志器实例，可选
        """
        self.logger = logger or Logger()
    
    def load_json(self, file_path: str) -> Optional[Dict[str, Any]]:
        """加载JSON文件"""
        try:
            path = Path(file_path)
            if not path.exists():
                self.logger.error(f"❌ 文件不存在: {file_path}")
                return None
                
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.logger.info(f"✅ 成功加载文件: {file_path}")
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON解析失败: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ 文件加载失败: {e}")
            return None
    
    def save_json(self, data: Dict[str, Any], file_path: str, indent: int = 2):
        """保存JSON文件"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
                
            self.logger.info(f"✅ 文件保存成功: {file_path}")
            
        except Exception as e:
            self.logger.error(f"❌ 文件保存失败: {e}")
            raise
    
    def get_output_path(self, input_path: str, suffix: str = ".llm_enhanced", 
                       step_index: Optional[int] = None) -> str:
        """生成输出文件路径"""
        input_path = Path(input_path)
        
        if step_index is not None:
            suffix = f"{suffix}_step_{step_index}"
        
        return str(input_path.with_suffix(f"{input_path.suffix}{suffix}"))