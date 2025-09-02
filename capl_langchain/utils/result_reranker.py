"""
轻量级结果重排序器
基于API优先级和关键词匹配度对检索结果进行重排序
"""

from typing import List, Dict, Any
from pathlib import Path
import json
import re
from dataclasses import dataclass


@dataclass
class RerankedResult:
    """重排序后的结果"""
    document: Any
    score: float
    source: str
    api_priority: int
    keyword_match_score: float


class ResultReranker:
    """
    轻量级结果重排序器
    
    功能：
    1. 基于API优先级重排序
    2. 基于关键词匹配度评分
    3. 支持可配置的优先级规则
    4. 保持向后兼容性
    """
    
    def __init__(self, api_files: List[str] = None, priority_mapping_file: str = None):
        """
        初始化重排序器
        
        Args:
            api_files: API定义文件列表，用于确定优先级
            priority_mapping_file: API优先级映射文件路径
        """
        self.api_files = api_files or []
        self.priority_mapping_file = priority_mapping_file
        self.api_priorities = self._load_api_priorities()
        self.high_priority_apis = {
            # CAPL核心API
            "testWaitForTimeout", "testWaitForMessage", "testAssert", "testReportWrite",
            "setTimer", "cancelTimer", "isTimerActive", "testWaitForSignalValue",
            "output", "setPort", "getPort", "setSignal", "getSignal",
            "on message", "on signal", "on timer", "on key",
            
            # 测试相关
            "testcase", "testfunction", "testgroup", "testmodule",
            "testWaitFor", "testCheck", "testVerify", "testStep",
            
            # 常用函数
            "write", "writeLine", "setTimerCyclic", "testWait",
            "testDisableMsg", "testEnableMsg", "testGetLastMsg",
        }
        
    def _load_api_priorities(self) -> Dict[str, int]:
        """从API文件中加载优先级信息"""
        priorities = {}
        
        # 首先尝试加载精确的API优先级映射文件
        if self.priority_mapping_file:
            try:
                mapping_file = Path(self.priority_mapping_file)
                if mapping_file.exists():
                    print(f"正在加载API优先级映射文件: {self.priority_mapping_file}")
                    with open(mapping_file, 'r', encoding='utf-8') as f:
                        priority_mapping = json.load(f)
                    
                    # 使用精确的优先级映射
                    for api_name, priority in priority_mapping.items():
                        priorities[api_name.lower()] = priority
                    
                    print(f"✅ 已加载 {len(priorities)} 个精确的API优先级规则")
                    return priorities
            except Exception as e:
                print(f"⚠️ 加载API优先级映射文件失败: {e}")
        
        # 回退到从API定义文件加载
        for api_file in self.api_files:
            try:
                file_path = Path(api_file)
                if file_path.exists():
                    print(f"正在加载API文件: {api_file}")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # 解析API定义文件
                    if isinstance(data, dict):
                        # 支持两种结构：apis 或 interfaces
                        apis = data.get('apis', data.get('interfaces', []))
                        print(f"  找到 {len(apis)} 个API")
                        for api in apis:
                            name = api.get('name') or api.get('function_name')
                            if name:
                                # 根据API类型设置优先级
                                priority = self._determine_priority(name, api)
                                priorities[name.lower()] = priority
                                print(f"    添加API: {name} -> 优先级 {priority}")
                                
            except Exception as e:
                print(f"⚠️ 加载API优先级失败: {api_file} - {e}")
                
        print(f"总共加载了 {len(priorities)} 个API优先级规则")
        return priorities
    
    def _determine_priority(self, api_name: str, api_info: Dict) -> int:
        """确定API优先级"""
        name_lower = api_name.lower()
        
        # 高优先级（测试相关）
        if any(keyword in name_lower for keyword in ['test', 'assert', 'wait', 'verify']):
            return 10
        
        # 中优先级（消息和信号）
        if any(keyword in name_lower for keyword in ['message', 'signal', 'output', 'set']):
            return 8
            
        # 中低优先级（定时器）
        if 'timer' in name_lower:
            return 6
            
        # 低优先级（其他）
        return 4
    
    def rerank(self, results: List[Any], original_query: str) -> List[Any]:
        """
        对检索结果进行重排序
        
        Args:
            results: 初始检索结果列表
            original_query: 原始查询字符串
            
        Returns:
            重排序后的结果列表
        """
        if not results:
            return results
            
        reranked_results = []
        
        for doc in results:
            if not hasattr(doc, 'page_content') or not hasattr(doc, 'metadata'):
                continue
                
            # 计算各项评分
            api_priority = self._calculate_api_priority(doc)
            keyword_match_score = self._calculate_keyword_match(doc, original_query)
            
            # 综合评分
            total_score = (api_priority * 0.6) + (keyword_match_score * 0.4)
            
            reranked_results.append(RerankedResult(
                document=doc,
                score=total_score,
                source=doc.metadata.get('source', 'unknown'),
                api_priority=api_priority,
                keyword_match_score=keyword_match_score
            ))
        
        # 按分数降序排序
        reranked_results.sort(key=lambda x: x.score, reverse=True)
        
        # 返回重排序后的文档
        return [r.document for r in reranked_results]
    
    def _calculate_api_priority(self, doc) -> int:
        """计算API优先级分数"""
        content = doc.page_content.lower()
        source = doc.metadata.get('source', '').lower()
        
        # 检查内容中的高优先级API
        priority_score = 0
        
        for api in self.high_priority_apis:
            if api.lower() in content:
                priority_score += self.api_priorities.get(api.lower(), 5)
        
        # 检查API文件中的优先级
        for api_name, priority in self.api_priorities.items():
            if api_name in content:
                priority_score += priority
        
        return max(priority_score, 5)  # 最低分数为5
    
    def _calculate_keyword_match(self, doc, query: str) -> float:
        """计算关键词匹配度"""
        query_words = set(query.lower().split())
        
        # 处理不同类型的文档内容
        if hasattr(doc, 'page_content'):
            content = doc.page_content.lower()
        elif isinstance(doc, dict):
            content = doc.get('content', '').lower()
        elif isinstance(doc, str):
            content = doc.lower()
        else:
            content = str(doc).lower()
            
        content_words = set(content.split())
        
        # 计算交集
        intersection = query_words.intersection(content_words)
        
        # 计算匹配度
        if len(query_words) == 0:
            return 0.0
            
        return len(intersection) / len(query_words)
    
    def get_rerank_info(self, results: List[Any], original_query: str) -> Dict[str, Any]:
        """获取重排序的详细信息（用于调试和分析）"""
        if not results:
            return {"total_results": 0, "reranked_results": []}
        
        reranked = []
        for doc in results:
            if not hasattr(doc, 'page_content') or not hasattr(doc, 'metadata'):
                continue
                
            api_priority = self._calculate_api_priority(doc)
            keyword_match = self._calculate_keyword_match(doc, original_query)
            
            reranked.append({
                "source": doc.metadata.get('source', 'unknown'),
                "api_priority": api_priority,
                "keyword_match": keyword_match,
                "content_length": len(doc.page_content),
                "summary": doc.page_content[:100] + "..."
            })
        
        # 按分数排序
        reranked.sort(key=lambda x: (x["api_priority"] * 0.6 + x["keyword_match"] * 0.4), reverse=True)
        
        return {
            "total_results": len(results),
            "reranked_results": reranked
        }