"""知识库管理器，处理RAG相关功能"""

import os
from pathlib import Path
from typing import Any, Dict, List

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.document_loaders.json_loader import JSONLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..config.config import CAPLGeneratorConfig
from ..factories.embedding_factory import EmbeddingFactory


class KnowledgeBaseManager:
    """知识库管理器，处理RAG相关功能"""
    
    def __init__(self, config: CAPLGeneratorConfig):
        self.config = config
        self.vector_store = None
        
    def initialize_knowledge_base(self) -> bool:
        """初始化知识库"""
        if not self.config.enable_rag:
            return False
            
        try:
            # 确保知识库目录存在
            self.config.knowledge_base_dir.mkdir(exist_ok=True)
            self.config.vector_db_dir.mkdir(exist_ok=True)
            
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
            
            # 创建向量存储（Chroma 0.4+自动持久化）
            self.vector_store = Chroma.from_documents(
                documents=splits,
                embedding=embeddings,
                persist_directory=str(self.config.vector_db_dir)
            )
            
            print(f"知识库初始化完成，共加载 {len(documents)} 个文档，{len(splits)} 个文本块")
            return True
            
        except Exception as e:
            print(f"知识库初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_documents(self) -> List:
        """加载知识库文档"""
        knowledge_base_path = Path(self.config.knowledge_base_dir)
        if not knowledge_base_path.exists():
            return []
            
        documents = []
        
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
        
        return documents
    
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
    
    def search_documents(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """搜索相关文档并返回详细信息"""
        if not self.vector_store:
            return []
        
        try:
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k}
            )
            
            docs = retriever.invoke(query)
            
            # 提取文档信息
            results = []
            for doc in docs:
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
                
                results.append({
                    'source': source,
                    'content': content,
                    'summary': summary,
                    'length': len(content)
                })
            
            return results
            
        except Exception as e:
            print(f"文档检索失败: {e}")
            return []