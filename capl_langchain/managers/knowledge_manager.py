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
                
            # 分割文档
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
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
        if not self.config.knowledge_base_dir.exists():
            return []
            
        documents = []
        
        # 支持的文件格式和对应的加载器
        file_configs = [
            {"pattern": "**/*.txt", "loader": TextLoader},
            {"pattern": "**/*.md", "loader": TextLoader},
            {"pattern": "**/*.capl", "loader": TextLoader},
            {"pattern": "**/*.py", "loader": TextLoader},
            {"pattern": "**/*.json", "loader": JSONLoader}
        ]
        
        for config in file_configs:
            pattern = config["pattern"]
            loader_cls = config["loader"]
            
            try:
                loader_kwargs = {'encoding': 'utf-8', 'autodetect_encoding': True}
                
                # 为JSON文件配置特殊的加载器参数
                if loader_cls == JSONLoader:
                    # 使用JSONLoader处理JSON文件，提取内容作为文本
                    loader = DirectoryLoader(
                        str(self.config.knowledge_base_dir),
                        glob=pattern,
                        loader_cls=TextLoader,  # 先作为文本加载，然后处理
                        loader_kwargs=loader_kwargs
                    )
                else:
                    loader = DirectoryLoader(
                        str(self.config.knowledge_base_dir),
                        glob=pattern,
                        loader_cls=loader_cls,
                        loader_kwargs=loader_kwargs
                    )
                
                docs = loader.load()
                
                # 为JSON文件进行特殊处理
                if pattern == "**/*.json":
                    docs = self._process_json_documents(docs)
                
                # 确保文档内容格式正确
                for doc in docs:
                    if hasattr(doc, 'page_content'):
                        # 确保内容是字符串，不是复杂对象
                        content = doc.page_content
                        if isinstance(content, (list, dict, tuple)):
                            doc.page_content = self._format_json_content(content)
                        elif not isinstance(content, str):
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
    
    def _process_json_documents(self, docs: List) -> List:
        """处理JSON文档，将其转换为可搜索的文本格式"""
        processed_docs = []
        
        for doc in docs:
            if hasattr(doc, 'page_content'):
                try:
                    import json
                    content = doc.page_content
                    
                    # 尝试解析JSON内容
                    try:
                        json_data = json.loads(content)
                    except json.JSONDecodeError:
                        # 如果不是有效的JSON，保持原样
                        processed_docs.append(doc)
                        continue
                    
                    # 将JSON数据转换为格式化的文本
                    formatted_content = self._format_json_content(json_data)
                    
                    # 更新文档内容
                    doc.page_content = formatted_content
                    
                    # 添加元数据标记这是JSON文档
                    if hasattr(doc, 'metadata'):
                        doc.metadata['document_type'] = 'json'
                    
                    processed_docs.append(doc)
                    
                except Exception as e:
                    print(f"处理JSON文档时出错: {e}")
                    processed_docs.append(doc)
        
        return processed_docs
    
    def _format_json_content(self, data: Any) -> str:
        """将JSON数据格式化为可搜索的文本"""
        def _format_object(obj, indent=0):
            """递归格式化对象"""
            result = []
            spaces = "  " * indent
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        result.append(f"{spaces}{key}:")
                        result.append(_format_object(value, indent + 1))
                    else:
                        result.append(f"{spaces}{key}: {value}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, (dict, list)):
                        result.append(f"{spaces}[{i}]:")
                        result.append(_format_object(item, indent + 1))
                    else:
                        result.append(f"{spaces}[{i}]: {item}")
            else:
                result.append(f"{spaces}{obj}")
            
            return "\n".join(result)
        
        try:
            # 如果是列表或字典，使用自定义格式化
            if isinstance(data, (dict, list)):
                return _format_object(data)
            else:
                return str(data)
        except Exception as e:
            print(f"格式化JSON内容时出错: {e}")
            return str(data)
    
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