"""基于LangChain的CAPL代码生成器"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence, RunnablePassthrough
from langchain.chains import RetrievalQA

from .config.config import CAPLGeneratorConfig
from .factories.llm_factory import LLMFactory
from .managers.prompt_manager import PromptTemplateManager
from .managers.knowledge_manager import KnowledgeBaseManager


class CAPLGenerator:
    """基于LangChain的CAPL代码生成器"""
    
    def __init__(self, config: Optional[CAPLGeneratorConfig] = None):
        self.config = config or CAPLGeneratorConfig()
        self.prompt_manager = PromptTemplateManager(self.config)
        self.kb_manager = KnowledgeBaseManager(self.config)
        self.llm = LLMFactory.create_llm(self.config)
        self.chain = None
        
    def initialize(self):
        """初始化生成器"""
        # 初始化知识库（如果启用RAG）
        if self.config.enable_rag:
            self.kb_manager.initialize_knowledge_base()
        
        # 构建处理链
        self._build_chain()
    
    # 构建LangChain处理链
    def _build_chain(self):
        """构建LangChain处理链"""
        if self.config.enable_rag and self.kb_manager.get_retriever():
            # RAG模式
            retriever = self.kb_manager.get_retriever(self.config.k)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.prompt_manager.system_prompt),
                ("human", """
                基于以下知识库内容生成CAPL代码：
                
                相关上下文：
                {context}
                
                测试需求：
                {requirement}
                """)
            ])
            
            def format_docs(docs):
                return "\n\n".join(str(doc.page_content) for doc in docs)
            
            # 修复：确保输入格式正确，并显示检索信息
            def create_chain_input(requirement_str):
                # 确保requirement是字符串
                if isinstance(requirement_str, dict):
                    requirement_str = str(requirement_str.get('requirement', str(requirement_str)))
                elif not isinstance(requirement_str, str):
                    requirement_str = str(requirement_str)
                
                # 获取相关文档并显示检索信息
                print(f"\n🔍 正在检索知识库...")
                docs = retriever.invoke(requirement_str)
                
                if docs:
                    print(f"✅ 检索完成，找到 {len(docs)} 个相关文档")
                    
                    # 显示每个文档的信息
                    for i, doc in enumerate(docs, 1):
                        # 获取文档来源
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
                        summary = content[:100] + "..." if len(content) > 100 else content
                        
                        print(f"  📄 文档 {i}: {source} ({len(content)} 字符)")
                        print(f"     摘要: {summary}")
                else:
                    print("⚠️  未找到相关文档，将使用通用模板")
                
                return {
                    "context": format_docs(docs),
                    "requirement": requirement_str
                }
            
            # 构建完整的处理链
            self.chain = RunnableSequence(
                create_chain_input,
                prompt,
                self.llm,
                StrOutputParser()
            )
            
        else:
            # 非RAG模式
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.prompt_manager.system_prompt),
                ("human", "{requirement}")
            ])
            
            self.chain = RunnableSequence(
                prompt,
                self.llm,
                StrOutputParser()
            )
    
    def generate_code(self, requirement: str, output_file: Optional[str] = None) -> str:
        """生成CAPL代码"""
        try:
            if self.chain is None:
                self.initialize()
            
            print(f"\n🤖 正在生成CAPL代码...")
            print(f"📋 需求: {requirement[:100]}...")
            
            # 生成代码
            generated_code = self.chain.invoke(requirement)
            
            # 清理生成的代码
            cleaned_code = self._clean_generated_code(generated_code)
            
            # 保存到文件
            if output_file:
                output_path = Path(output_file)
            else:
                # 生成默认文件名
                timestamp = int(os.path.getmtime(__file__) if os.path.exists(__file__) else 0)
                safe_requirement = re.sub(r'[^\w\-_.]', '_', requirement[:50])
                filename = f"capl_test_{safe_requirement}_{timestamp}.cin"
                output_path = self.config.output_dir / filename
            
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_code)
            
            print(f"✅ 代码生成完成！")
            print(f"📁 文件保存至: {output_path}")
            
            return cleaned_code
            
        except Exception as e:
            print(f"❌ 代码生成失败: {e}")
            import traceback
            traceback.print_exc()
            return f"// 代码生成失败: {str(e)}"
    
    def _clean_generated_code(self, code: str) -> str:
        """清理生成的代码"""
        # 移除可能的markdown代码块标记
        code = re.sub(r'^```capl\n', '', code)
        code = re.sub(r'^```\n', '', code)
        code = re.sub(r'\n```$', '', code)
        
        # 移除行尾的空白字符
        lines = code.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        
        # 移除多余的空行
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def get_knowledge_base_info(self) -> Dict[str, Any]:
        """获取知识库信息"""
        info = {
            'enabled': self.config.enable_rag,
            'knowledge_base_dir': str(self.config.knowledge_base_dir),
            'vector_db_dir': str(self.config.vector_db_dir),
            'documents_loaded': 0,
            'search_results': []
        }
        
        if self.config.enable_rag and self.config.knowledge_base_dir.exists():
            # 获取文档数量
            documents = []
            for pattern in ["**/*.txt", "**/*.md", "**/*.capl", "**/*.py"]:
                documents.extend(list(self.config.knowledge_base_dir.glob(pattern)))
            info['documents_loaded'] = len(documents)
        
        return info
    
    def search_knowledge_base(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """搜索知识库"""
        if not self.config.enable_rag:
            return []
        
        return self.kb_manager.search_documents(query, k)