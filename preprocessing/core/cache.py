"""
缓存管理模块
用于缓存测试用例目的分析结果
"""

from typing import Dict, Any
import hashlib
import json

class PurposeCache:
    """测试用例目的缓存管理器"""
    
    def __init__(self):
        self._cache: Dict[str, str] = {}
    
    def get_cache_key(self, testcase: Dict[str, Any]) -> str:
        """生成测试用例的缓存键"""
        # 优先使用ID，其次使用name，最后使用内容哈希
        case_id = testcase.get('id')
        if case_id:
            return str(case_id)
            
        case_name = testcase.get('name')
        if case_name:
            return str(case_name)
            
        # 使用内容哈希作为兜底
        content_str = json.dumps(testcase, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def get(self, testcase: Dict[str, Any]) -> str:
        """获取缓存的测试目的"""
        key = self.get_cache_key(testcase)
        return self._cache.get(key, "")
    
    def set(self, testcase: Dict[str, Any], purpose: str):
        """设置测试目的到缓存"""
        key = self.get_cache_key(testcase)
        self._cache[key] = purpose
    
    def has(self, testcase: Dict[str, Any]) -> bool:
        """检查测试用例是否在缓存中"""
        key = self.get_cache_key(testcase)
        return key in self._cache
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)