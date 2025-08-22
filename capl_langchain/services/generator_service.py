"""高级CAPL生成器服务"""

import os
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..generator import CAPLGenerator
from ..config.config import CAPLGeneratorConfig


class CAPLGeneratorService:
    """高级CAPL生成器服务，提供额外功能"""
    
    def __init__(self, config: CAPLGeneratorConfig):
        self.config = config
        self.generator = CAPLGenerator(config)
        self.start_time = None
    
    def process_file(self, 
                    file_path: str, 
                    debug_prompt: bool = False,
                    rebuild_rag: bool = False,
                    show_summary: bool = True) -> Dict[str, Any]:
        """处理单个文件的高级封装"""
        
        try:
            self.start_time = time.time()
            
            # 重建RAG知识库（如果需要）
            if rebuild_rag and self.config.enable_rag:
                print("🔄 正在重建RAG知识库...")
                # 清理向量数据库
                import shutil
                if self.config.vector_db_dir.exists():
                    shutil.rmtree(self.config.vector_db_dir)
                self.config.vector_db_dir.mkdir(parents=True, exist_ok=True)
                
                # 重新初始化知识库
                self.generator.kb_manager.initialize_knowledge_base()
            
            # 读取需求
            requirement = self._read_file(file_path)
            
            if debug_prompt:
                print("🔍 调试模式 - 显示完整prompt:")
                print("=" * 50)
                print(self.generator.prompt_manager.system_prompt)
                print("=" * 50)
            
            # 生成CAPL代码
            capl_code = self.generator.generate_code(requirement)
            
            # 保存结果（多格式）
            result = self._save_result(file_path, capl_code)
            
            # 计算统计信息
            stats = self._calculate_stats(capl_code)
            
            return {
                "status": "success",
                "file_path": str(result),
                "capl_file": str(result).replace('.md', '.can'),
                "stats": stats,
                "error": None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "file_path": None,
                "capl_file": None,
                "stats": {},
                "error": str(e)
            }
    
    def _read_file(self, file_path: str) -> str:
        """读取文件内容"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    def _save_result(self, original_path: str, capl_code: str) -> Path:
        """保存生成的CAPL代码（多格式）"""
        original_name = Path(original_path).stem
        
        # 确保输出目录存在
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 同时生成两种格式的文件
        md_file = self.config.output_dir / f"{original_name}.md"
        can_file = self.config.output_dir / f"{original_name}.can"
        
        # 保存Markdown格式（包含详细说明）
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(capl_code)
        
        # 保存.can格式（纯代码）
        code_blocks = re.findall(r'```(?:capl)?\n(.*?)\n```', capl_code, re.DOTALL)
        
        if code_blocks:
            # 如果有代码块，提取第一个代码块作为.can文件内容
            pure_code = code_blocks[0].strip()
        else:
            # 如果没有找到代码块，使用原始内容
            pure_code = capl_code
        
        with open(can_file, 'w', encoding='utf-8') as f:
            f.write(pure_code)
        
        return md_file
    
    def _calculate_stats(self, capl_code: str) -> Dict[str, Any]:
        """计算生成统计信息"""
        generation_time = time.time() - self.start_time if self.start_time else 0
        code_length = len(capl_code)
        estimated_tokens = max(1, code_length // 4)
        token_rate = estimated_tokens / generation_time if generation_time > 0 else 0
        
        # 计算代码行数
        lines = capl_code.split('\n')
        code_lines = len([line for line in lines if line.strip()])
        
        return {
            "generation_time": round(generation_time, 2),
            "code_length": code_length,
            "code_lines": code_lines,
            "estimated_tokens": estimated_tokens,
            "token_rate": round(token_rate, 2)
        }
    
    def test_rag_search(self, query: str, k: int = 4, show_summary: bool = True) -> List[Dict[str, Any]]:
        """测试RAG搜索功能"""
        if not self.config.enable_rag:
            print("⚠️  RAG功能未启用")
            return []
        
        print(f"\n🔍 测试RAG搜索: '{query}'")
        
        # 确保生成器已初始化
        self.generator.initialize()
        
        # 执行搜索
        documents = self.generator.search_knowledge_base(query, k)
        
        if documents:
            print(f"✅ 找到 {len(documents)} 个相关文档")
            if show_summary:
                for i, doc in enumerate(documents, 1):
                    print(f"\n📄 文档{i}: {doc['source']}")
                    print(f"   摘要: {doc['summary']}")
                    print(f"   长度: {doc['length']} 字符")
            else:
                for i, doc in enumerate(documents, 1):
                    print(f"   📄 文档{i}: {doc['source']}")
        else:
            print("❌ 未找到相关文档")
        
        return documents