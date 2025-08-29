"""CAPL生成器配置类"""

import os
import configparser
from pathlib import Path
from dotenv import load_dotenv


class CAPLGeneratorConfig:
    """CAPL生成器配置类"""
    
    def __init__(self):
        load_dotenv()
        
        # API配置 - 主模型
        self.api_type = os.getenv('API_TYPE', 'ollama')  # ollama, openai
        self.api_url = os.getenv('API_URL', 'http://localhost:11434')
        
        # 嵌入模型独立配置
        self.embedding_api_type = os.getenv('EMBEDDING_API_TYPE', self.api_type)  # 默认跟随主模型
        self.embedding_api_url = os.getenv('EMBEDDING_API_URL', self.api_url)   # 默认跟随主模型
        
        # 根据API类型选择正确的模型环境变量
        if self.api_type == "openai":
            self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        else:
            self.model = os.getenv("OLLAMA_MODEL", "qwen3:30b-a3b")
        self.context_length = int(os.getenv("OLLAMA_CONTEXT_LENGTH", "8192"))
        self.max_tokens = int(os.getenv("OLLAMA_MAX_TOKENS", "4096"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.2"))
        self.top_p = float(os.getenv("TOP_P", "0.5"))
        
        # 路径配置
        self.project_root = Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "capl"
        
        # 从配置文件读取提示词模板路径
        self.prompt_template_file = self._get_prompt_template_path()
        self.example_code_file = self.project_root / "example_code.txt"
        
        # RAG配置
        self.enable_rag = os.getenv("ENABLE_RAG", "true").lower() == "true"
        self.k = int(os.getenv("RAG_K", "6"))  # RAG检索返回的文档数量 - 优化为6，适合复杂测试用例
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "400"))  # 文档分块大小 - 高精度场景默认值
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))  # 文档分块重叠大小 - 高精度场景默认值
        
        # 从配置文件读取知识库和向量数据库目录
        config_kb_dir, config_vector_dir = self._get_knowledge_base_config()
        
        # 环境变量优先级最高，配置文件次之，最后使用默认值
        custom_kb_dir = os.getenv("KNOWLEDGE_BASE_DIR")
        if custom_kb_dir:
            self.knowledge_base_dir = Path(custom_kb_dir)
        else:
            self.knowledge_base_dir = config_kb_dir
            
        custom_vector_dir = os.getenv("VECTOR_DB_DIR")
        if custom_vector_dir:
            self.vector_db_dir = Path(custom_vector_dir)
        else:
            self.vector_db_dir = config_vector_dir
            
        # 嵌入模型配置 - 独立于主模型
        if self.embedding_api_type == "openai":
            self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        else:
            self.embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
        
        # 显示配置
        self.show_doc_summary = os.getenv("SHOW_DOC_SUMMARY", "true").lower() == "true"
        
        # 示例代码配置
        self.use_example_code = os.getenv("USE_EXAMPLE_CODE", "true").lower() == "true"
    
    def _get_knowledge_base_config(self) -> tuple[Path, Path]:
        """从配置文件读取知识库目录配置"""
        config_path = self.project_root / "prompt_config.ini"
        default_kb_dir = self.project_root / "knowledge_base"
        default_vector_dir = self.project_root / "vector_db"
        
        if config_path.exists():
            try:
                config = configparser.ConfigParser()
                config.read(config_path, encoding='utf-8')
                
                kb_dir_str = config['DEFAULT'].get('KNOWLEDGE_BASE_DIR', 'knowledge_base')
                vector_dir_str = config['DEFAULT'].get('VECTOR_DB_DIR', 'vector_db')
                
                # 转换为绝对路径
                kb_dir = Path(kb_dir_str) if Path(kb_dir_str).is_absolute() else self.project_root / kb_dir_str
                vector_dir = Path(vector_dir_str) if Path(vector_dir_str).is_absolute() else self.project_root / vector_dir_str
                
                return kb_dir, vector_dir
                
            except Exception as e:
                print(f"警告: 读取知识库配置失败，使用默认配置: {e}")
        
        return default_kb_dir, default_vector_dir
    
    def _get_prompt_template_path(self) -> Path:
        """从配置文件读取提示词模板路径"""
        config_path = self.project_root / "prompt_config.ini"
        default_template = "prompt_template.txt"
        
        if config_path.exists():
            try:
                config = configparser.ConfigParser()
                config.read(config_path, encoding='utf-8')
                if 'DEFAULT' in config and 'PROMPT_TEMPLATE_FILE' in config['DEFAULT']:
                    template_file = config['DEFAULT']['PROMPT_TEMPLATE_FILE']
                    return self.project_root / template_file
            except Exception as e:
                print(f"警告: 读取配置文件失败，使用默认提示词模板: {e}")
        
        return self.project_root / default_template