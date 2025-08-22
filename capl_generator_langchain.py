#!/usr/bin/env python3
"""
基于LangChain的CAPL代码生成器
重构版本，支持RAG和更灵活的架构
"""

import os
import sys
import json
import argparse
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# LangChain imports - 使用最新版本
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

# 配置类
class CAPLGeneratorConfig:
    """CAPL生成器配置类"""
    
    def __init__(self):
        load_dotenv()
        
        # API配置
        self.api_type = os.getenv('API_TYPE', 'ollama')  # ollama, openai
        self.api_url = os.getenv('API_URL', 'http://localhost:11434')
        self.model = os.getenv("OLLAMA_MODEL", "qwen3:30b-a3b")
        self.context_length = int(os.getenv("OLLAMA_CONTEXT_LENGTH", "8192"))
        self.max_tokens = int(os.getenv("OLLAMA_MAX_TOKENS", "4096"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.2"))
        self.top_p = float(os.getenv("TOP_P", "0.5"))
        
        # 路径配置
        self.project_root = Path(__file__).parent
        self.output_dir = self.project_root / "capl"
        
        # 从配置文件读取提示词模板路径
        self.prompt_template_file = self._get_prompt_template_path()
        self.example_code_file = self.project_root / "example_code.txt"
        
        # RAG配置
        self.enable_rag = os.getenv("ENABLE_RAG", "false").lower() == "true"
        self.knowledge_base_dir = self.project_root / "knowledge_base"
        self.vector_db_dir = self.project_root / "vector_db"
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    
    def _get_prompt_template_path(self) -> Path:
        """从配置文件读取提示词模板路径"""
        config_path = self.project_root / "prompt_config.ini"
        default_template = "prompt_template_simple.txt"
        
        if config_path.exists():
            try:
                import configparser
                config = configparser.ConfigParser()
                config.read(config_path, encoding='utf-8')
                if 'DEFAULT' in config and 'PROMPT_TEMPLATE_FILE' in config['DEFAULT']:
                    template_file = config['DEFAULT']['PROMPT_TEMPLATE_FILE']
                    return self.project_root / template_file
            except Exception as e:
                print(f"警告: 读取配置文件失败，使用默认提示词模板: {e}")
        
        return self.project_root / default_template

class LLMFactory:
    """LLM工厂类，统一管理不同提供商的LLM"""
    
    @staticmethod
    def create_llm(config: CAPLGeneratorConfig) -> Any:
        """根据配置创建LLM实例"""
        if config.api_type == "ollama":
            return OllamaLLM(
                base_url=config.api_url,
                model=config.model,
                temperature=config.temperature,
                top_p=config.top_p,
                num_ctx=config.context_length,
                num_predict=config.max_tokens
            )
        elif config.api_type == "openai":
            return ChatOpenAI(
                base_url=config.api_url,
                model=config.model,
                temperature=config.temperature,
                top_p=config.top_p,
                max_tokens=config.max_tokens
            )
        else:
            raise ValueError(f"不支持的API类型: {config.api_type}")

class EmbeddingFactory:
    """嵌入模型工厂类"""
    
    @staticmethod
    def create_embeddings(config: CAPLGeneratorConfig) -> Embeddings:
        """根据配置创建嵌入模型"""
        if config.api_type == "ollama":
            return OllamaEmbeddings(
                base_url=config.api_url,
                model=config.embedding_model
            )
        elif config.api_type == "openai":
            return OpenAIEmbeddings(
                base_url=config.api_url,
                model=config.embedding_model
            )
        else:
            raise ValueError(f"不支持的嵌入类型: {config.api_type}")

class PromptTemplateManager:
    """提示模板管理器"""
    
    def __init__(self, config: CAPLGeneratorConfig):
        self.config = config
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """加载系统提示模板"""
        try:
            if self.config.prompt_template_file.exists():
                with open(self.config.prompt_template_file, 'r', encoding='utf-8') as f:
                    prompt = f.read()
            else:
                prompt = self._get_default_prompt()
                
            # 加载示例代码
            if self.config.example_code_file.exists():
                with open(self.config.example_code_file, 'r', encoding='utf-8') as f:
                    example_code = f.read()
                    prompt = prompt.replace("示例代码已移至单独的文件 example_code.txt 中，以保护敏感代码内容。", example_code)
            
            # 转义非变量占位符的花括号
            prompt = self._escape_brackets(prompt)
                    
            return prompt
        except Exception as e:
            print(f"警告: 加载提示模板失败，使用默认模板: {e}")
            return self._get_default_prompt()
    
    def _escape_brackets(self, text: str) -> str:
        """转义非变量占位符的花括号
        
        LangChain使用Jinja2模板引擎，会将单花括号识别为变量占位符。
        此方法会转义所有非变量占位符的花括号，避免解析错误。
        """
        import re
        
        # 定义需要保留的变量占位符模式
        variable_patterns = [
            r'\{requirement\}',
            r'\{context\}',
        ]
        
        # 创建一个临时占位符映射
        temp_placeholders = {}
        placeholder_counter = 0
        
        # 首先保护已知的变量占位符
        protected_text = text
        for pattern in variable_patterns:
            matches = re.finditer(pattern, protected_text)
            for match in matches:
                placeholder = f"___VAR_PLACEHOLDER_{placeholder_counter}___"
                temp_placeholders[placeholder] = match.group()
                protected_text = protected_text.replace(match.group(), placeholder)
                placeholder_counter += 1
        
        # 转义所有剩余的单花括号
        # 将 { 替换为 {{，} 替换为 }}
        protected_text = re.sub(r'(?<!\{)\{(?!\{)', '{{', protected_text)
        protected_text = re.sub(r'(?<!\})\}(?!\})', '}}', protected_text)
        
        # 恢复被保护的变量占位符
        for placeholder, original in temp_placeholders.items():
            protected_text = protected_text.replace(placeholder, original)
        
        return protected_text
    
    def _get_default_prompt(self) -> str:
        """获取默认提示模板"""
        return """你是一个专业的CAPL测试代码生成专家。请根据提供的测试需求，生成高质量的CAPL测试代码。

要求：
1. 代码必须符合CAPL语法规范
2. 包含完整的测试逻辑和断言
3. 添加详细的注释说明
4. 遵循最佳实践和编码规范

测试需求：
{requirement}

请生成对应的CAPL测试代码："""

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
        from langchain_community.document_loaders import DirectoryLoader, TextLoader
        
        if not self.config.knowledge_base_dir.exists():
            return []
            
        documents = []
        
        # 支持的文件格式
        file_patterns = ["**/*.txt", "**/*.md", "**/*.capl", "**/*.py"]
        
        for pattern in file_patterns:
            try:
                loader = DirectoryLoader(
                    str(self.config.knowledge_base_dir),
                    glob=pattern,
                    loader_cls=TextLoader,
                    loader_kwargs={'encoding': 'utf-8', 'autodetect_encoding': True}
                )
                docs = loader.load()
                
                # 确保文档内容格式正确
                for doc in docs:
                    if hasattr(doc, 'page_content'):
                        # 确保内容是字符串，不是复杂对象
                        content = doc.page_content
                        if isinstance(content, (list, dict, tuple)):
                            doc.page_content = str(content)
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
    
    def get_retriever(self):
        """获取检索器"""
        if self.vector_store:
            return self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            )
        return None
    
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
    
    def _build_chain(self):
        """构建LangChain处理链"""
        if self.config.enable_rag and self.kb_manager.get_retriever():
            # RAG模式
            retriever = self.kb_manager.get_retriever()
            
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
                        summary = content[:150] + "..." if len(content) > 150 else content
                        
                        print(f"   📄 文档{i}: {source}")
                        print(f"      摘要: {summary}")
                        print(f"      长度: {len(content)} 字符")
                        print()
                else:
                    print("⚠️  未找到相关文档，将基于通用知识生成")
                
                context_str = format_docs(docs)
                
                return {
                    "context": context_str,
                    "requirement": requirement_str
                }
            
            # 使用自定义的链构建
            self.chain = (
                create_chain_input
                | prompt
                | self.llm
                | StrOutputParser()
            )
        else:
            # 标准模式
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.prompt_manager.system_prompt),
                ("human", "{requirement}")
            ])
            
            self.chain = prompt | self.llm | StrOutputParser()
    
    def generate_capl_code(self, requirement: str, context: Optional[str] = None) -> str:
        """生成CAPL代码"""
        try:
            if not self.chain:
                self.initialize()
            
            # 准备输入
            if context:
                full_requirement = f"{context}\n\n{requirement}"
            else:
                full_requirement = requirement
            
            # 生成代码
            response = self.chain.invoke({"requirement": full_requirement})
            
            return response
            
        except Exception as e:
            raise RuntimeError(f"CAPL代码生成失败: {str(e)}")
    
    def generate_from_file(self, file_path: str) -> str:
        """从文件读取需求并生成CAPL代码"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                requirement = f.read()
            
            return self.generate_capl_code(requirement)
            
        except Exception as e:
            raise RuntimeError(f"读取文件失败: {str(e)}")
    
    def get_document_info(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """获取文档检索信息（用于调试和显示）"""
        if not self.config.enable_rag:
            print("⚠️  RAG功能未启用")
            return []
        
        if not self.kb_manager.vector_store:
            print("⚠️  知识库未初始化")
            return []
        
        return self.kb_manager.search_documents(query, k)

class CAPLGeneratorService:
    """CAPL生成器服务类，提供完整功能"""
    
    def __init__(self, config: Optional[CAPLGeneratorConfig] = None):
        self.config = config or CAPLGeneratorConfig()
        self.generator = CAPLGenerator(self.config)
        self.start_time = None
        
    def process_file(self, file_path: str, debug_prompt: bool = False, rebuild_rag: bool = False, **kwargs) -> Dict[str, Any]:
        """处理单个文件"""
        self.start_time = time.time()
        
        try:
            # 确保输出目录存在
            self.config.output_dir.mkdir(exist_ok=True)
            
            # 处理RAG重构选项
            if rebuild_rag and self.config.enable_rag:
                print("🔄 检测到RAG重构选项，正在删除旧向量数据库...")
                vector_db_path = self.config.vector_db_dir
                if vector_db_path.exists():
                    import shutil
                    shutil.rmtree(vector_db_path)
                    print(f"✅ 已删除旧向量数据库: {vector_db_path}")
                else:
                    print("ℹ️  向量数据库不存在，无需删除")
            
            # 初始化生成器
            self.generator.initialize()
            
            # 读取需求文件
            requirement = self._read_file(file_path)
            
            # 调试模式：打印完整的prompt
            if debug_prompt:
                print("\n🔍 调试模式：完整Prompt内容")
                print("=" * 60)
                print("系统提示词:")
                print(self.generator.prompt_manager.system_prompt)
                print("\n" + "=" * 60)
                print("用户输入:")
                print(requirement)
                print("=" * 60)
                print("\n")
            
            # 显示RAG状态
            if self.config.enable_rag:
                print(f"\n📚 RAG功能已启用")
                print(f"📁 知识库目录: {self.config.knowledge_base_dir}")
                print(f"📁 向量数据库目录: {self.config.vector_db_dir}")
                
                # 检查向量数据库状态
                vector_db_exists = self.config.vector_db_dir.exists() and \
                                 any(self.config.vector_db_dir.glob("*"))
                
                if vector_db_exists:
                    print("✅ 向量数据库已存在")
                    # 列出数据库文件
                    for item in self.config.vector_db_dir.rglob("*"):
                        if item.is_file():
                            size = item.stat().st_size
                            print(f"   📄 {item.relative_to(self.config.vector_db_dir)} ({size} bytes)")
                else:
                    print("ℹ️  向量数据库不存在，将创建新的")
            else:
                print("ℹ️  RAG功能未启用，使用通用知识生成")
            
            # 生成CAPL代码
            capl_code = self.generator.generate_capl_code(requirement)
            
            # 保存结果
            result = self._save_result(file_path, capl_code)
            
            # 计算统计信息
            stats = self._calculate_stats(capl_code)
            
            return {
                "status": "success",
                "file_path": str(result),
                "stats": stats,
                "error": None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "file_path": None,
                "stats": {},
                "error": str(e)
            }
    
    def _read_file(self, file_path: str) -> str:
        """读取文件内容"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _save_result(self, original_path: str, capl_code: str) -> Path:
        """保存生成的CAPL代码
        
        支持两种输出格式：
        - .md 格式：Markdown格式的详细说明文档
        - .can 格式：纯CAPL代码文件，可直接用于CANoe/CANalyzer
        """
        original_name = Path(original_path).stem
        
        # 同时生成两种格式的文件
        md_file = self.config.output_dir / f"{original_name}.md"
        can_file = self.config.output_dir / f"{original_name}.can"
        
        # 保存Markdown格式（包含详细说明）
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(capl_code)
        
        # 保存.can格式（纯代码）
        # 从生成的内容中提取代码块
        import re
        code_blocks = re.findall(r'```(?:capl)?\n(.*?)\n```', capl_code, re.DOTALL)
        
        if code_blocks:
            # 如果有代码块，提取第一个代码块作为.can文件内容
            pure_code = code_blocks[0].strip()
        else:
            # 如果没有找到代码块，使用原始内容
            pure_code = capl_code
        
        with open(can_file, 'w', encoding='utf-8') as f:
            f.write(pure_code)
        
        return md_file  # 返回主输出文件路径
    
    def _calculate_stats(self, capl_code: str) -> Dict[str, Any]:
        """计算生成统计信息"""
        generation_time = time.time() - self.start_time if self.start_time else 0
        code_length = len(capl_code)
        estimated_tokens = max(1, code_length // 4)
        token_rate = estimated_tokens / generation_time if generation_time > 0 else 0
        
        return {
            "generation_time": round(generation_time, 2),
            "code_length": code_length,
            "estimated_tokens": estimated_tokens,
            "token_rate": round(token_rate, 2)
        }
    
    def test_rag_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """测试RAG搜索功能"""
        if not self.config.enable_rag:
            print("⚠️  RAG功能未启用")
            return []
        
        print(f"\n🔍 测试RAG搜索: '{query}'")
        
        # 初始化知识库
        self.generator.initialize()
        
        # 执行搜索
        results = self.generator.get_document_info(query, k)
        
        if results:
            print(f"✅ 找到 {len(results)} 个相关文档")
            for i, result in enumerate(results, 1):
                print(f"\n📄 文档{i}: {result['source']}")
                print(f"   摘要: {result['summary']}")
                print(f"   长度: {result['length']} 字符")
        else:
            print("❌ 未找到相关文档")
        
        return results

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='基于LangChain的CAPL代码生成器')
    parser.add_argument('file_path', nargs='?', help='输入的测试需求文件路径')
    parser.add_argument('--api-type', choices=['ollama', 'openai'], help='API类型')
    parser.add_argument('--api-url', help='API服务地址')
    parser.add_argument('--model', help='模型名称')
    parser.add_argument('--enable-rag', action='store_true', help='启用RAG功能')
    parser.add_argument('--disable-rag', action='store_true', help='禁用RAG功能')
    parser.add_argument('--debug-prompt', action='store_true', help='调试模式，显示完整prompt')
    parser.add_argument('--rebuild-rag', action='store_true', help='重新构建RAG知识库')
    parser.add_argument('--test-rag', help='测试RAG搜索功能，输入查询内容')
    parser.add_argument('--k', type=int, default=4, help='RAG检索返回的文档数量')
    
    args = parser.parse_args()
    
    # 创建配置
    config = CAPLGeneratorConfig()
    
    # 应用命令行参数
    if args.api_type:
        config.api_type = args.api_type
    if args.api_url:
        config.api_url = args.api_url
    if args.model:
        config.model = args.model
    if args.enable_rag:
        config.enable_rag = True
    if args.disable_rag:
        config.enable_rag = False
    
    # 创建服务
    service = CAPLGeneratorService(config)
    
    # 处理不同的操作模式
    if args.test_rag:
        # 测试RAG搜索模式
        service.test_rag_search(args.test_rag, args.k)
        return
    
    if not args.file_path:
        print("错误: 请提供输入文件路径或使用 --test-rag 测试RAG功能")
        parser.print_help()
        return
    
    # 正常处理文件
    print("=" * 60)
    print("CAPL代码生成器")
    print("=" * 60)
    
    result = service.process_file(
        args.file_path,
        debug_prompt=args.debug_prompt,
        rebuild_rag=args.rebuild_rag
    )
    
    if result["status"] == "success":
        print(f"✅ 生成成功！")
        print(f"📁 输出文件: {result['file_path']}")
        print(f"📁 CAPL代码文件: {result['file_path'].replace('.md', '.can')}")
        print(f"ℹ️  说明: .md文件包含详细说明和代码，.can文件为纯CAPL代码可直接导入CANoe/CANalyzer")
        print(f"⏱️  生成时间: {result['stats']['generation_time']}秒")
        print(f"📊 代码长度: {result['stats']['code_length']}字符")
        print(f"🔢 估算tokens: {result['stats']['estimated_tokens']}")
        print(f"⚡ 生成速度: {result['stats']['token_rate']} tokens/秒")
    else:
        print(f"❌ 生成失败: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()