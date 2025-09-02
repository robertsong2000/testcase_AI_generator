"""知识库管理器，处理RAG相关功能"""

import os
from pathlib import Path
from typing import Any, Dict, List

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.document_loaders.json_loader import JSONLoader
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..config.config import CAPLGeneratorConfig
from ..factories.embedding_factory import EmbeddingFactory

# 导入重排序器
try:
    from ..utils.result_reranker import ResultReranker
except ImportError:
    ResultReranker = None


class KnowledgeBaseManager:
    """知识库管理器，处理RAG相关功能"""
    
    def __init__(self, config: CAPLGeneratorConfig):
        self.config = config
        self.vector_store = None
        self.reranker = None
        
        # 初始化重排序器
        if ResultReranker is not None:
            # 获取API文件路径
            api_files = []
            if hasattr(config, 'api_files') and config.api_files:
                api_files = config.api_files
            else:
                # 使用默认的API文件
                kb_dir = Path(config.knowledge_base_dir)
                api_files = [
                    str(kb_dir / "interfaces_analysis_common-libraries.json"),
                    str(kb_dir / "interfaces_analysis_libraries.json")
                ]
        
            # 检查是否有优先级映射文件
            priority_mapping_file = None
            if hasattr(config, 'api_priority_mapping_file') and config.api_priority_mapping_file:
                if Path(config.api_priority_mapping_file).exists():
                    priority_mapping_file = str(config.api_priority_mapping_file)
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
        """初始化知识库，支持智能缓存"""
        if not self.config.enable_rag:
            return False
            
        try:
            # 确保知识库目录存在
            self.config.knowledge_base_dir.mkdir(exist_ok=True)
            self.config.vector_db_dir.mkdir(exist_ok=True)
            
            # 检查缓存是否有效
            if self._is_cache_valid():
                print("📦 发现有效缓存，跳过知识库初始化...")
                embeddings = EmbeddingFactory.create_embeddings(self.config)
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
                return True
            
            print("🔄 初始化知识库...")
            
            # 加载文档
            documents = self._load_documents()
            if not documents:
                print("警告: 知识库中没有找到文档")
                return False
                
            # 分割文档 - 使用可配置的参数优化token消耗
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_size,      # 可配置的分块大小
                chunk_overlap=self.config.chunk_overlap,  # 可配置的重叠大小
                length_function=len
            )
            splits = text_splitter.split_documents(documents)
            
            # 创建向量存储
            embeddings = EmbeddingFactory.create_embeddings(self.config)
            
            # 修复Ollama嵌入模型输入格式问题
            # 确保文档内容都是字符串格式
            for doc in splits:
                if hasattr(doc, 'page_content'):
                    # 确保内容不是列表或字典
                    if isinstance(doc.page_content, (list, dict)):
                        doc.page_content = str(doc.page_content)
                    # 确保内容是字符串
                    doc.page_content = str(doc.page_content)
            
            # 创建向量存储（使用langchain-chroma）
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
            
            # 创建缓存标记文件
            self._create_cache_marker()
            
            print(f"✅ 知识库初始化完成，共加载 {len(documents)} 个文档，{len(splits)} 个文本块")
            return True
            
        except Exception as e:
            print(f"知识库初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_documents(self) -> List:
        """加载知识库文档"""
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

    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        cache_marker = self.config.vector_db_dir / ".cache_marker"
        
        # 检查缓存标记文件是否存在
        if not cache_marker.exists():
            return False
        
        # 检查向量数据库是否存在且完整
        if not (self.config.vector_db_dir / "chroma.sqlite3").exists():
            return False
        
        # 检查知识库文件是否有更新
        cache_mtime = cache_marker.stat().st_mtime
        
        # 遍历知识库目录中的所有文件
        knowledge_files = []
        for pattern in ["**/*.txt", "**/*.md", "**/*.capl", "**/*.py", "**/*.json"]:
            knowledge_files.extend(self.config.knowledge_base_dir.glob(pattern))
        
        # 如果有任何知识库文件比缓存新，则缓存无效
        for file_path in knowledge_files:
            if file_path.stat().st_mtime > cache_mtime:
                return False
        
        return True

    def _create_cache_marker(self):
        """创建缓存标记文件"""
        cache_marker = self.config.vector_db_dir / ".cache_marker"
        cache_marker.touch()
        print("📦 缓存标记文件已创建")
    
    def get_retriever(self, k: int = None):
        """获取检索器
        
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
    
    def _load_json_documents(self) -> List:
        """使用JSONLoader专业加载JSON文档"""
        documents = []
        
        # 支持的JSON文件类型
        json_patterns = ["**/*.json"]
        knowledge_base_path = Path(self.config.knowledge_base_dir)
        
        for pattern in json_patterns:
            try:
                json_files = list(knowledge_base_path.glob(pattern))
                for json_file in json_files:
                    try:
                        # 使用JSONLoader处理JSON文档
                        # 对于数组结构的JSON，使用jq_schema='.'加载整个数组
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
    
    def search_documents(self, query: str, k: int = 4, enable_rerank: bool = True) -> List[Dict[str, Any]]:
        """搜索相关文档并返回详细信息
        
        Args:
            query: 查询字符串
            k: 返回的文档数量
            enable_rerank: 是否启用重排序
        """
        if not self.vector_store:
            return []
        
        try:
            # 使用更大的k值进行初始检索，为重排序留出空间
            search_k = max(k * 2, 6) if enable_rerank and self.reranker else k
            
            print(f"🔍 开始文档检索...")
            print(f"   查询: '{query}'")
            print(f"   初始检索数量: {search_k}")
            print(f"   重排序: {'启用' if enable_rerank and self.reranker else '禁用'}")
            
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": search_k}
            )
            
            docs = retriever.invoke(query)
            print(f"   初始检索结果: {len(docs)} 个文档")
            
            # 应用重排序
            if enable_rerank and self.reranker:
                print("⚖️  开始重排序处理...")
                
                # 获取重排序详细信息
                rerank_info = self.reranker.get_rerank_info(docs, query)
                
                # 显示重排序前的文档信息
                print("   📊 重排序前:")
                for i, doc_info in enumerate(rerank_info['reranked_results']):
                    print(f"      {i+1}. {doc_info['source']} (API优先级: {doc_info['api_priority']}, "
                          f"关键词匹配: {doc_info['keyword_match']:.2f})")
                
                # 执行重排序
                docs = self.reranker.rerank(docs, query)
                
                # 获取重排序后的详细信息
                rerank_info_after = self.reranker.get_rerank_info(docs, query)
                
                # 显示重排序后的文档信息
                print("   🎯 重排序后:")
                for i, doc_info in enumerate(rerank_info_after['reranked_results'][:k]):
                    print(f"      {i+1}. {doc_info['source']} (API优先级: {doc_info['api_priority']}, "
                          f"关键词匹配: {doc_info['keyword_match']:.2f})")
                
                # 截取前k个结果
                docs = docs[:k]
                print(f"   最终返回: {len(docs)} 个文档")
            
            # 提取文档信息
            results = []
            print("📋 最终结果:")
            for i, doc in enumerate(docs):
                # 获取文档元信息
                metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                source = metadata.get('source', '未知来源')
                
                # 获取相对路径
                try:
                    if source != '未知来源':
                        source_path = Path(source)
                        if source_path.is_absolute():
                            # 转换为相对于知识库目录的路径
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
                
                print(f"   {i+1}. {source} (长度: {len(content)} 字符)")
                
                results.append({
                    'source': source,
                    'content': content,
                    'summary': summary,
                    'length': len(content)
                })
            
            return results
            
        except Exception as e:
            print(f"❌ 文档检索失败: {e}")
            return []
    
    def get_rerank_info(self, query: str, k: int = 4) -> Dict[str, Any]:
        """获取重排序详细信息（用于调试）"""
        if not self.vector_store or not self.reranker:
            return {"error": "重排序器未初始化"}
        
        try:
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": max(k * 2, 6)}
            )
            
            docs = retriever.invoke(query)
            
            # 获取重排序信息
            rerank_info = self.reranker.get_rerank_info(docs, query)
            reranked_docs = self.reranker.rerank(docs, query)
            
            return {
                "original_count": len(docs),
                "reranked_count": len(reranked_docs),
                "query": query,
                "rerank_details": rerank_info,
                "final_results": [
                    {
                        "source": doc.metadata.get('source', 'unknown'),
                        "content_length": len(doc.page_content)
                    }
                    for doc in reranked_docs[:k]
                ]
            }
            
        except Exception as e:
            return {"error": str(e)}