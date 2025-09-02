"""
统一知识库管理器，支持可配置的混合检索
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.document_loaders.json_loader import JSONLoader
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..config.config import CAPLGeneratorConfig
from ..factories.embedding_factory import EmbeddingFactory

# 可选的混合检索支持
try:
    from ..utils.hybrid_search import LightweightHybridSearch
    HYBRID_SEARCH_AVAILABLE = True
except ImportError:
    LightweightHybridSearch = None
    HYBRID_SEARCH_AVAILABLE = False

# 导入重排序器
try:
    from ..utils.result_reranker import ResultReranker
except ImportError:
    ResultReranker = None


class UnifiedKnowledgeBaseManager:
    """统一知识库管理器，支持混合检索和纯向量检索"""
    
    def __init__(self, config: CAPLGeneratorConfig):
        self.config = config
        self.vector_store = None
        self.hybrid_search = None
        self.reranker = None
        
        # 初始化重排序器
        self._init_reranker()
        
        # 根据配置初始化混合检索
        if config.use_hybrid_search and HYBRID_SEARCH_AVAILABLE:
            print("🔄 混合检索已启用")
        elif config.use_hybrid_search and not HYBRID_SEARCH_AVAILABLE:
            print("⚠️ 混合检索不可用，将使用纯向量检索")
    
    def _init_reranker(self):
        """初始化重排序器"""
        if ResultReranker is not None:
            # 获取API文件路径
            api_files = []
            if hasattr(self.config, 'api_files') and self.config.api_files:
                api_files = self.config.api_files
            else:
                # 使用默认的API文件
                kb_dir = Path(self.config.knowledge_base_dir)
                api_files = [
                    str(kb_dir / "interfaces_analysis_common-libraries.json"),
                    str(kb_dir / "interfaces_analysis_libraries.json")
                ]
        
            # 检查是否有优先级映射文件
            priority_mapping_file = None
            if hasattr(self.config, 'api_priority_mapping_file') and self.config.api_priority_mapping_file:
                if Path(self.config.api_priority_mapping_file).exists():
                    priority_mapping_file = str(self.config.api_priority_mapping_file)
                    print(f"📊 使用API优先级映射文件: {priority_mapping_file}")
            
            # 只使用存在的API文件
            valid_api_files = [f for f in api_files if Path(f).exists()]
            if priority_mapping_file:
                # 使用优先级映射文件
                self.reranker = ResultReranker(
                    api_files=valid_api_files,
                    priority_mapping_file=priority_mapping_file
                )
            elif valid_api_files:
                # 使用API文件
                self.reranker = ResultReranker(api_files=valid_api_files)
            else:
                # 使用空API文件列表创建重排序器（使用默认行为）
                self.reranker = ResultReranker(api_files=[])
    
    def initialize_knowledge_base(self) -> bool:
        """初始化知识库，支持混合检索配置"""
        if not self.config.enable_rag:
            return False
            
        try:
            # 确保目录存在
            self.config.knowledge_base_dir.mkdir(exist_ok=True)
            self.config.vector_db_dir.mkdir(exist_ok=True)
            
            # 检查缓存
            if self._is_cache_valid():
                print("📦 发现有效缓存，跳过知识库初始化...")
                return self._load_from_cache()
            
            if self.config.use_hybrid_search:
                print("🔄 初始化知识库和混合检索器...")
            else:
                print("🔄 初始化知识库（纯向量检索）...")
            
            # 加载文档
            documents = self._load_documents()
            if not documents:
                print("警告: 知识库中没有找到文档")
                return False
            
            # 分割文档
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
                length_function=len
            )
            splits = text_splitter.split_documents(documents)
            
            # 创建嵌入模型
            embeddings = EmbeddingFactory.create_embeddings(self.config)
            
            # 修复内容格式
            for doc in splits:
                if hasattr(doc, 'page_content'):
                    if isinstance(doc.page_content, (list, dict)):
                        doc.page_content = str(doc.page_content)
                    doc.page_content = str(doc.page_content)
            
            # 创建向量存储
            try:
                from langchain_chroma import Chroma
                self.vector_store = Chroma.from_documents(
                    documents=splits,
                    embedding=embeddings,
                    persist_directory=str(self.config.vector_db_dir)
                )
            except ImportError:
                from langchain_community.vectorstores import Chroma
                self.vector_store = Chroma.from_documents(
                    documents=splits,
                    embedding=embeddings,
                    persist_directory=str(self.config.vector_db_dir)
                )
            
            # 如果需要混合检索且可用，创建混合检索器
            if self.config.use_hybrid_search and HYBRID_SEARCH_AVAILABLE:
                self.hybrid_search = LightweightHybridSearch(
                    vector_store=self.vector_store,
                    embeddings=embeddings,
                    vector_weight=0.7,
                    keyword_weight=0.3
                )
                print("✅ 混合检索器已创建")
            
            # 创建缓存标记
            self._create_cache_marker()
            
            print(f"✅ 知识库初始化完成")
            print(f"   📊 文档数量: {len(documents)}")
            print(f"   🧩 文本块数量: {len(splits)}")
            if self.hybrid_search:
                print(f"   🔍 混合检索器已就绪")
            else:
                print(f"   📊 向量检索器已就绪")
            
            return True
            
        except Exception as e:
            print(f"❌ 知识库初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_from_cache(self) -> bool:
        """从缓存加载"""
        try:
            embeddings = EmbeddingFactory.create_embeddings(self.config)
            
            # 加载向量存储
            try:
                from langchain_chroma import Chroma
                self.vector_store = Chroma(
                    persist_directory=str(self.config.vector_db_dir),
                    embedding_function=embeddings
                )
            except ImportError:
                from langchain_community.vectorstores import Chroma
                self.vector_store = Chroma(
                    persist_directory=str(self.config.vector_db_dir),
                    embedding_function=embeddings
                )
            
            # 如果需要混合检索且可用，创建混合检索器
            if self.config.use_hybrid_search and HYBRID_SEARCH_AVAILABLE:
                self.hybrid_search = LightweightHybridSearch(
                    vector_store=self.vector_store,
                    embeddings=embeddings,
                    vector_weight=0.7,
                    keyword_weight=0.3
                )
                print("✅ 从缓存成功加载知识库和混合检索器")
            else:
                print("✅ 从缓存成功加载知识库")
            
            return True
            
        except Exception as e:
            print(f"⚠️ 缓存加载失败，将重新初始化: {e}")
            return False
    
    def search_documents(
        self,
        query: str,
        k: int = 4,
        enable_rerank: bool = True,
        use_hybrid: bool = None
    ) -> List[Dict[str, Any]]:
        """搜索相关文档，支持混合检索和重排序
        
        Args:
            query: 查询字符串
            k: 返回的文档数量
            enable_rerank: 是否启用重排序
            use_hybrid: 是否使用混合检索，None表示使用配置默认值
        """
        if not self.vector_store:
            return []
        
        # 确定是否使用混合检索
        if use_hybrid is None:
            use_hybrid = self.config.use_hybrid_search and self.hybrid_search is not None
        
        # 检查混合检索可用性
        if use_hybrid and not self.hybrid_search:
            print("⚠️ 混合检索不可用，将使用纯向量检索")
            use_hybrid = False
        
        try:
            print(f"🔍 开始文档检索...")
            print(f"   查询: {query}")
            print(f"   混合检索: {'启用' if use_hybrid else '禁用'}")
            print(f"   重排序: {'启用' if enable_rerank and self.reranker else '禁用'}")
            
            # 确定初始检索数量
            search_k = max(k * 2, 6) if enable_rerank and self.reranker else k
            
            if use_hybrid and self.hybrid_search:
                # 使用混合检索
                print(f"   🔍 使用混合检索，初始检索数量: {search_k}")
                hybrid_results = self.hybrid_search.search(
                    query=query,
                    k=search_k,
                    fetch_k=search_k * 2
                )
                
                # 转换为Document对象
                docs = [result.document for result in hybrid_results]
                
                # 存储混合检索的分数信息
                hybrid_scores = {
                    result.document.page_content: {
                        'vector_score': result.vector_score,
                        'keyword_score': result.keyword_score,
                        'combined_score': result.combined_score,
                        'match_type': result.match_type
                    }
                    for result in hybrid_results
                }
                
            else:
                # 使用纯向量检索
                print(f"   📊 使用向量检索，检索数量: {search_k}")
                retriever = self.vector_store.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": search_k}
                )
                docs = retriever.invoke(query)
                hybrid_scores = {}
            
            print(f"   初始检索结果: {len(docs)} 个文档")
            
            # 应用重排序
            if enable_rerank and self.reranker:
                print("⚖️  开始重排序处理...")
                
                # 获取重排序信息
                rerank_info = self.reranker.get_rerank_info(docs, query)
                
                # 显示重排序前的信息
                if use_hybrid and hybrid_scores:
                    print("   📊 重排序前（混合检索分数）:")
                    for i, doc in enumerate(docs[:min(3, len(docs))]):
                        score_info = hybrid_scores.get(doc.page_content, {})
                        print(f"      {i+1}. {doc.metadata.get('source', '未知')} - "
                              f"组合分数: {score_info.get('combined_score', 0):.3f}, "
                              f"类型: {score_info.get('match_type', 'unknown')}")
                
                # 执行重排序
                docs = self.reranker.rerank(docs, query)
                
                # 截取前k个结果
                docs = docs[:k]
                print(f"   重排序后: {len(docs)} 个文档")
            
            elif len(docs) > k:
                # 如果没有重排序，简单截取前k个
                docs = docs[:k]
            
            # 提取文档信息
            results = []
            print("📋 最终结果:")
            for i, doc in enumerate(docs):
                metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                source = metadata.get('source', '未知来源')
                
                # 获取相对路径
                try:
                    if source != '未知来源':
                        source_path = Path(source)
                        if source_path.is_absolute():
                            try:
                                source = str(source_path.relative_to(self.config.knowledge_base_dir))
                            except ValueError:
                                source = source_path.name
                        else:
                            source = str(source_path)
                except Exception:
                    source = str(source)
                
                # 内容摘要
                content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                summary = content[:200] + "..." if len(content) > 200 else content
                
                # 获取混合检索分数信息
                score_info = {}
                if hybrid_scores and doc.page_content in hybrid_scores:
                    score_info = hybrid_scores[doc.page_content]
                
                print(f"   {i+1}. {source} (长度: {len(content)} 字符)")
                if score_info:
                    print(f"      混合分数: {score_info.get('combined_score', 0):.3f}, "
                          f"类型: {score_info.get('match_type', 'unknown')}")
                
                results.append({
                    'source': source,
                    'content': content,
                    'summary': summary,
                    'length': len(content),
                    'metadata': metadata,
                    'hybrid_scores': score_info if score_info else None,
                    'search_method': 'hybrid' if use_hybrid else 'vector'
                })
            
            return results
            
        except Exception as e:
            print(f"❌ 文档检索失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_search_stats(self) -> Dict[str, Any]:
        """获取搜索统计信息"""
        stats = {
            "knowledge_base_ready": self.vector_store is not None,
            "hybrid_search_available": HYBRID_SEARCH_AVAILABLE,
            "hybrid_search_enabled": self.config.use_hybrid_search,
            "hybrid_search_ready": self.hybrid_search is not None,
            "reranker_ready": self.reranker is not None
        }
        
        if self.hybrid_search:
            stats.update(self.hybrid_search.get_stats())
        
        return stats
    
    def get_retriever(self, k: int = None):
        """获取检索器（兼容性方法）
        
        Args:
            k: 返回的文档数量，如果为None则使用配置中的默认值
        """
        if self.vector_store:
            search_k = k if k is not None else self.config.k
            return self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": search_k}
            )
        return None
    
    def is_hybrid_available(self) -> bool:
        """检查混合检索是否可用"""
        return HYBRID_SEARCH_AVAILABLE and self.hybrid_search is not None
    
    def switch_search_mode(self, use_hybrid: bool):
        """动态切换检索模式"""
        if use_hybrid and HYBRID_SEARCH_AVAILABLE and self.vector_store:
            if not self.hybrid_search:
                embeddings = EmbeddingFactory.create_embeddings(self.config)
                self.hybrid_search = LightweightHybridSearch(
                    vector_store=self.vector_store,
                    embeddings=embeddings,
                    vector_weight=0.7,
                    keyword_weight=0.3
                )
            print("✅ 已切换到混合检索模式")
        elif use_hybrid and not HYBRID_SEARCH_AVAILABLE:
            print("⚠️ 混合检索不可用，保持当前模式")
        else:
            print("✅ 已切换到纯向量检索模式")
    
    # 以下方法保持统一实现
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        cache_marker = self.config.vector_db_dir / ".cache_valid"
        if not cache_marker.exists():
            return False
        
        cache_time = cache_marker.stat().st_mtime
        kb_time = max(
            (f.stat().st_mtime for f in Path(self.config.knowledge_base_dir).rglob("*") if f.is_file()),
            default=0
        )
        
        return cache_time > kb_time
    
    def _create_cache_marker(self):
        """创建缓存标记文件"""
        cache_marker = self.config.vector_db_dir / ".cache_valid"
        cache_marker.touch()
    
    def _load_documents(self) -> List:
        """加载知识库文档（统一实现）"""
        documents = []
        knowledge_base_path = Path(self.config.knowledge_base_dir)
        if not knowledge_base_path.exists():
            print(f"⚠️ 知识库目录不存在: {knowledge_base_path}")
            return []
        
        print(f"📁 正在加载知识库: {knowledge_base_path}")
        
        # 支持的文件格式和对应的加载器
        file_configs = [
            {"pattern": "**/*.txt", "loader": TextLoader},
            {"pattern": "**/*.md", "loader": TextLoader},
            {"pattern": "**/*.capl", "loader": TextLoader},
            {"pattern": "**/*.py", "loader": TextLoader}
        ]
        
        # 加载非JSON文档
        for config in file_configs:
            pattern = config["pattern"]
            loader_cls = config["loader"]
            
            try:
                loader_kwargs = {'encoding': 'utf-8', 'autodetect_encoding': True}
                
                loader = DirectoryLoader(
                    str(knowledge_base_path),
                    glob=pattern,
                    loader_cls=loader_cls,
                    loader_kwargs=loader_kwargs
                )
                
                docs = loader.load()
                
                # 确保文档内容格式正确
                for doc in docs:
                    if hasattr(doc, 'page_content'):
                        content = doc.page_content
                        if not isinstance(content, str):
                            doc.page_content = str(content)
                        
                        # 清理内容
                        doc.page_content = doc.page_content.strip()
                        
                        # 确保内容不为空
                        if not doc.page_content:
                            continue
                
                # 过滤掉空文档
                valid_docs = [doc for doc in docs if doc.page_content and doc.page_content.strip()]
                documents.extend(valid_docs)
                
                if valid_docs:
                    print(f"📁 加载 {pattern} 格式: {len(valid_docs)} 个有效文档")
                    
            except Exception as e:
                print(f"⚠️  加载 {pattern} 格式失败: {e}")
                continue
        
        # 加载JSON文档
        json_docs = self._load_json_documents()
        documents.extend(json_docs)
        
        print(f"📊 总共加载 {len(documents)} 个文档")
        return documents
    
    def _load_json_documents(self) -> List:
        """使用JSONLoader专业加载JSON文档"""
        documents = []
        
        # 支持的JSON文件类型
        json_patterns = ["**/*.json", "**/*.jsonl"]
        knowledge_base_path = Path(self.config.knowledge_base_dir)
        
        for pattern in json_patterns:
            try:
                json_files = list(knowledge_base_path.glob(pattern))
                for json_file in json_files:
                    try:
                        # 使用JSONLoader处理JSON文档
                        loader = JSONLoader(
                            file_path=str(json_file),
                            jq_schema='.',
                            text_content=False,
                            content_key=None
                        )
                        docs = loader.load()
                        
                        # 为JSON文档添加丰富的元数据
                        for doc in docs:
                            if hasattr(doc, 'metadata'):
                                doc.metadata.update({
                                    'document_type': 'json',
                                    'source': str(json_file.relative_to(knowledge_base_path)),
                                    'file_path': str(json_file),
                                    'format': 'structured_json'
                                })
                        
                        documents.extend(docs)
                        print(f"📁 JSONLoader加载: {json_file.name} ({len(docs)} 个文档)")
                        
                    except Exception as e:
                        # JSONLoader失败时的回退处理
                        fallback_docs = self._fallback_json_processing(json_file)
                        documents.extend(fallback_docs)
                        print(f"⚠️ JSONLoader失败，使用回退模式: {json_file.name} - {e}")
                        
            except Exception as e:
                print(f"⚠️ 查找JSON文件失败: {e}")
                continue
                
        return documents
    
    def _fallback_json_processing(self, json_file: Path) -> List:
        """JSONLoader失败时的回退处理"""
        documents = []
        try:
            import json
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 将JSON数据转换为结构化的文本表示
            content = json.dumps(data, ensure_ascii=False, indent=2)
            
            # 创建文档对象
            doc = type('Document', (), {})()
            doc.page_content = content
            doc.metadata = {
                'document_type': 'json',
                'source': str(json_file.name),
                'file_path': str(json_file),
                'format': 'fallback_text'
            }
            documents.append(doc)
            
        except Exception as e:
            print(f"回退处理JSON失败: {json_file.name} - {e}")
        
        return documents