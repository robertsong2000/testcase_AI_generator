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
                    
            return prompt
        except Exception as e:
            print(f"警告: 加载提示模板失败，使用默认模板: {e}")
            return self._get_default_prompt()
    
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
            self.vector_store = Chroma.from_documents(
                documents=splits,
                embedding=embeddings,
                persist_directory=str(self.config.vector_db_dir)
            )
            
            print(f"知识库初始化完成，共加载 {len(documents)} 个文档，{len(splits)} 个文本块")
            return True
            
        except Exception as e:
            print(f"知识库初始化失败: {e}")
            return False
    
    def _load_documents(self) -> List:
        """加载知识库文档"""
        from langchain_community.document_loaders import DirectoryLoader
        
        if not self.config.knowledge_base_dir.exists():
            return []
            
        loader = DirectoryLoader(
            str(self.config.knowledge_base_dir),
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'}
        )
        return loader.load()
    
    def get_retriever(self):
        """获取检索器"""
        if self.vector_store:
            return self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            )
        return None

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
                return "\n\n".join(doc.page_content for doc in docs)
            
            self.chain = (
                {"context": retriever | format_docs, "requirement": RunnablePassthrough()}
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

class CAPLGeneratorService:
    """CAPL生成器服务类，提供完整功能"""
    
    def __init__(self, config: Optional[CAPLGeneratorConfig] = None):
        self.config = config or CAPLGeneratorConfig()
        self.generator = CAPLGenerator(self.config)
        self.start_time = None
        
    def process_file(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """处理单个文件"""
        self.start_time = time.time()
        
        try:
            # 确保输出目录存在
            self.config.output_dir.mkdir(exist_ok=True)
            
            # 初始化生成器
            self.generator.initialize()
            
            # 读取需求文件
            requirement = self._read_file(file_path)
            
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
        """保存生成的CAPL代码"""
        original_name = Path(original_path).stem
        output_file = self.config.output_dir / f"{original_name}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(capl_code)
        
        return output_file
    
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

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='基于LangChain的CAPL代码生成器')
    parser.add_argument('file_path', help='输入的测试需求文件路径')
    parser.add_argument('--api-type', choices=['ollama', 'openai'], help='API类型')
    parser.add_argument('--api-url', help='API服务地址')
    parser.add_argument('--model', help='使用的模型名称')
    parser.add_argument('--output-dir', help='输出目录')
    parser.add_argument('--enable-rag', action='store_true', help='启用RAG功能')
    parser.add_argument('--context-length', type=int, help='上下文长度')
    parser.add_argument('--max-tokens', type=int, help='最大输出tokens')
    parser.add_argument('--temperature', type=float, help='生成温度')
    parser.add_argument('--top-p', type=float, help='top-p采样参数')
    
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
    if args.output_dir:
        config.output_dir = Path(args.output_dir)
    if args.enable_rag:
        config.enable_rag = True
    if args.context_length:
        config.context_length = args.context_length
    if args.max_tokens:
        config.max_tokens = args.max_tokens
    if args.temperature is not None:
        config.temperature = args.temperature
    if args.top_p is not None:
        config.top_p = args.top_p
    
    # 创建服务并处理文件
    service = CAPLGeneratorService(config)
    result = service.process_file(args.file_path)
    
    if result["status"] == "success":
        print("\n✅ CAPL代码生成成功")
        print(f"   输出文件: {result['file_path']}")
        print(f"   生成时间: {result['stats']['generation_time']}秒")
        print(f"   代码长度: {result['stats']['code_length']}字符")
        print(f"   估算token: {result['stats']['estimated_tokens']} tokens")
        print(f"   输出速率: {result['stats']['token_rate']} tokens/秒")
    else:
        print(f"❌ 生成失败: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()