"""
轻量级混合检索实现
基于Chroma向量存储 + 关键词检索的混合方案
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
import numpy as np


@dataclass
class HybridSearchResult:
    """混合检索结果"""
    document: Document
    vector_score: float
    keyword_score: float
    combined_score: float
    match_type: str  # 'vector', 'keyword', 'hybrid'


class LightweightHybridSearch:
    """轻量级混合检索器
    
    特点：
    1. 基于现有Chroma向量存储
    2. 简单关键词匹配，无需额外依赖
    3. 轻量级融合算法
    4. 与现有配置完全兼容
    """
    
    def __init__(
        self,
        vector_store: Chroma,
        embeddings: Embeddings,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
        keyword_threshold: float = 0.1
    ):
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
        self.keyword_threshold = keyword_threshold
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        fetch_k: int = 20  # 先获取更多候选
    ) -> List[HybridSearchResult]:
        """执行混合检索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            filter_dict: 过滤条件
            fetch_k: 初始获取的候选数量
        """
        # 1. 向量检索
        vector_results = self._vector_search(query, fetch_k, filter_dict)
        
        # 2. 关键词检索
        keyword_results = self._keyword_search(query, vector_results)
        
        # 3. 融合结果
        combined_results = self._fuse_results(vector_results, keyword_results)
        
        # 4. 排序并返回前k个
        combined_results.sort(key=lambda x: x.combined_score, reverse=True)
        return combined_results[:k]
    
    def _vector_search(
        self,
        query: str,
        k: int,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """向量检索"""
        try:
            docs_with_scores = self.vector_store.similarity_search_with_score(
                query, k=k, filter=filter_dict
            )
            return [(doc, score) for doc, score in docs_with_scores]
        except Exception as e:
            print(f"向量检索失败: {e}")
            return []
    
    def _keyword_search(
        self,
        query: str,
        vector_results: List[Tuple[Document, float]]
    ) -> Dict[str, float]:
        """关键词检索
        
        实现特点：
        1. 只在向量检索结果中进行关键词匹配
        2. 使用简单TF-IDF风格评分
        3. 支持模糊匹配
        """
        if not vector_results:
            return {}
        
        # 预处理查询
        query_words = self._preprocess_text(query)
        if not query_words:
            return {}
        
        keyword_scores = {}
        
        for doc, _ in vector_results:
            content = doc.page_content.lower()
            doc_words = self._preprocess_text(content)
            
            if not doc_words:
                continue
            
            # 计算关键词匹配分数
            score = self._calculate_keyword_score(query_words, doc_words)
            if score >= self.keyword_threshold:
                keyword_scores[doc.page_content] = score
        
        return keyword_scores
    
    def _preprocess_text(self, text: str) -> List[str]:
        """文本预处理"""
        # 移除特殊字符，分词
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # 移除停用词（简化版）
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def _calculate_keyword_score(
        self,
        query_words: List[str],
        doc_words: List[str]
    ) -> float:
        """计算关键词匹配分数"""
        if not query_words or not doc_words:
            return 0.0
        
        # 计算匹配的词数
        matches = sum(1 for word in query_words if word in doc_words)
        
        # 使用Jaccard相似度的变体
        intersection = len(set(query_words) & set(doc_words))
        union = len(set(query_words) | set(doc_words))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _fuse_results(
        self,
        vector_results: List[Tuple[Document, float]],
        keyword_results: Dict[str, float]
    ) -> List[HybridSearchResult]:
        """融合向量和关键词结果"""
        
        # 标准化向量分数（反转距离分数，使其越高越好）
        max_vector_score = max([score for _, score in vector_results]) if vector_results else 1.0
        
        # 创建文档到分数的映射
        vector_scores = {}
        doc_map = {}  # 用内容作为键，文档作为值
        
        for doc, score in vector_results:
            # 将距离分数转换为相似度分数
            normalized_score = 1.0 - (score / max_vector_score) if max_vector_score > 0 else 0.0
            content_key = doc.page_content
            vector_scores[content_key] = max(0.0, normalized_score)
            doc_map[content_key] = doc
        
        # 标准化关键词分数
        max_keyword_score = max(keyword_results.values()) if keyword_results else 1.0
        normalized_keyword_scores = {
            content: score / max_keyword_score 
            for content, score in keyword_results.items()
        }
        
        # 合并所有文档
        all_content_keys = set(vector_scores.keys())
        all_content_keys.update(normalized_keyword_scores.keys())
        
        # 计算融合分数
        results = []
        for content_key in all_content_keys:
            doc = doc_map.get(content_key)
            if not doc:
                # 如果只有关键词匹配，找到对应的文档
                for d, _ in vector_results:
                    if d.page_content == content_key:
                        doc = d
                        break
                if not doc:
                    continue
            
            vector_score = vector_scores.get(content_key, 0.0)
            keyword_score = normalized_keyword_scores.get(content_key, 0.0)
            
            # 融合分数
            combined_score = (
                self.vector_weight * vector_score + 
                self.keyword_weight * keyword_score
            )
            
            # 确定匹配类型
            if vector_score > 0 and keyword_score > 0:
                match_type = "hybrid"
            elif vector_score > 0:
                match_type = "vector"
            else:
                match_type = "keyword"
            
            results.append(HybridSearchResult(
                document=doc,
                vector_score=vector_score,
                keyword_score=keyword_score,
                combined_score=combined_score,
                match_type=match_type
            ))
        
        return results
    
    def add_documents(self, documents: List[Document]) -> None:
        """添加文档到向量存储"""
        if hasattr(self.vector_store, 'add_documents'):
            self.vector_store.add_documents(documents)
        else:
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            self.vector_store.add_texts(texts, metadatas=metadatas)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            # 尝试获取集合大小
            count = len(self.vector_store.get())
            return {
                "total_documents": count,
                "vector_weight": self.vector_weight,
                "keyword_weight": self.keyword_weight,
                "keyword_threshold": self.keyword_threshold
            }
        except Exception:
            return {
                "total_documents": "unknown",
                "vector_weight": self.vector_weight,
                "keyword_weight": self.keyword_weight,
                "keyword_threshold": self.keyword_threshold
            }