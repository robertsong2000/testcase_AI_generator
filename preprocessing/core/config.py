#!/usr/bin/env python3
"""
测试用例增强器配置模块
支持从.env文件读取配置，兼容CAPLGeneratorConfig格式
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List
from dotenv import load_dotenv


@dataclass
class EnhancerConfig:
    """
    测试用例增强器配置类
    
    功能:
    - 从.env文件读取配置
    - 支持LLM配置（OpenAI/Ollama）
    - 支持RAG配置（知识库、向量数据库）
    - 兼容CAPLGeneratorConfig格式
    """
    
    # LLM配置
    api_type: str = "ollama"
    api_url: str = "http://localhost:11434"
    model: str = "qwen3-coder:30b"
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 2000
    context_length: int = 4096
    
    # 嵌入模型配置
    embedding_model: str = "ollama"
    embedding_model_name: str = "nomic-embed-text:latest"
    
    # RAG配置
    knowledge_base_dir: str = "knowledge_base"
    vector_db_dir: str = "vector_db"
    enable_rag: bool = True
    use_hybrid_search: bool = False
    enable_rerank: bool = False
    
    # 文本分割配置
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # 输出配置
    suffix: str = ".llm_enhanced"
    max_description_length: int = 500
    max_purpose_length: int = 200
    
    # 可选配置
    api_files: List[str] = field(default_factory=list)
    api_priority_mapping_file: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理，从环境变量加载配置"""
        load_dotenv()
        
        # 加载LLM配置
        self.api_type = os.getenv('API_TYPE', self.api_type)
        self.api_url = os.getenv('API_URL', self.api_url)
        self.model = os.getenv('MODEL', self.model)
        self.temperature = float(os.getenv('TEMPERATURE', str(self.temperature)))
        self.top_p = float(os.getenv('TOP_P', str(self.top_p)))
        self.max_tokens = int(os.getenv('MAX_TOKENS', str(self.max_tokens)))
        self.context_length = int(os.getenv('CONTEXT_LENGTH', str(self.context_length)))
        
        # 加载嵌入模型配置
        self.embedding_model = os.getenv('EMBEDDING_MODEL', self.embedding_model)
        self.embedding_model_name = os.getenv('EMBEDDING_MODEL_NAME', self.embedding_model_name)
        
        # 加载RAG配置
        self.knowledge_base_dir = os.getenv('KNOWLEDGE_BASE_DIR', self.knowledge_base_dir)
        self.vector_db_dir = os.getenv('VECTOR_DB_DIR', self.vector_db_dir)
        self.enable_rag = os.getenv('ENABLE_RAG', str(self.enable_rag)).lower() == 'true'
        self.use_hybrid_search = os.getenv('USE_HYBRID_SEARCH', str(self.use_hybrid_search)).lower() == 'true'
        self.enable_rerank = os.getenv('ENABLE_RERANK', str(self.enable_rerank)).lower() == 'true'
        
        # 加载文本分割配置
        self.chunk_size = int(os.getenv('CHUNK_SIZE', str(self.chunk_size)))
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', str(self.chunk_overlap)))
        
        # 加载输出配置
        self.suffix = os.getenv('SUFFIX', self.suffix)
        self.max_description_length = int(os.getenv('MAX_DESCRIPTION_LENGTH', str(self.max_description_length)))
        self.max_purpose_length = int(os.getenv('MAX_PURPOSE_LENGTH', str(self.max_purpose_length)))
        
        # 确保目录存在
        Path(self.knowledge_base_dir).mkdir(parents=True, exist_ok=True)
        Path(self.vector_db_dir).mkdir(parents=True, exist_ok=True)
        
        # 同步model参数
        if self.api_type == "ollama":
            self.model = os.getenv('OLLAMA_MODEL', self.model)
        elif self.api_type == "openai":
            self.model = os.getenv('OPENAI_MODEL', self.model)
    
    def __str__(self) -> str:
        """返回配置的字符串表示"""
        return f"""
EnhancerConfig:
  API Type: {self.api_type}
  Model: {self.model}
  Temperature: {self.temperature}
  Knowledge Base: {self.knowledge_base_dir}
  Vector DB: {self.vector_db_dir}
  RAG Enabled: {self.enable_rag}
  Hybrid Search: {self.use_hybrid_search}
        """.strip()