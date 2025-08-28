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
                    force_rebuild: bool = False,
                    show_summary: bool = True,
                    stream: bool = False) -> Dict[str, Any]:
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
                print("✅ RAG知识库重建完成")
            
            # 读取需求
            requirement = self._read_file(file_path)
            
            if debug_prompt:
                print("🔍 调试模式 - 显示完整prompt:")
                print("=" * 50)
                print(self.generator.prompt_manager.system_prompt)
                print("=" * 50)
            
            # 根据模式选择生成方式
            if stream:
                return self._process_file_stream(file_path, requirement, show_summary)
            else:
                # 传统阻塞式生成
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
    
    def _process_file_stream(self, file_path: str, requirement: str, show_summary: bool = True) -> Dict[str, Any]:
        """流式处理单个文件"""
        try:
            # 生成输出文件路径
            original_name = Path(file_path).stem
            output_file = self.config.output_dir / f"{original_name}.md"
            
            # 确保输出目录存在
            self.config.output_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"📁 输出文件: {output_file}")
            
            # 使用流式生成
            capl_code = ""
            with open(output_file, 'w', encoding='utf-8') as f:
                print("\n" + "="*50)
                print("🔄 开始流式生成代码...")
                print("="*50)
                
                # 流式输出到控制台和文件
                for chunk in self.generator.generate_code_stream(requirement):
                    print(chunk, end='', flush=True)
                    f.write(chunk)
                    capl_code += chunk
                
                print("\n" + "="*50)
                print("✅ 流式生成完成！")
            
            # 同时生成.can文件
            can_file = self.config.output_dir / f"{original_name}.can"
            code_blocks = re.findall(r'```(?:capl)?\n(.*?)\n```', capl_code, re.DOTALL)
            
            if code_blocks:
                pure_code = code_blocks[0].strip()
            else:
                pure_code = capl_code
            
            with open(can_file, 'w', encoding='utf-8') as f:
                f.write(pure_code)
            
            # 计算统计信息
            stats = self._calculate_stats(capl_code)
            
            return {
                "status": "success",
                "file_path": str(output_file),
                "capl_file": str(can_file),
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
    
    def calculate_prompt_tokens(self, requirement: str, include_rag_context: bool = True) -> Dict[str, Any]:
        """计算prompt的token数量"""
        system_prompt = self.generator.prompt_manager.system_prompt
        
        # 基础prompt
        base_prompt = system_prompt + "\n\n" + requirement
        base_length = len(base_prompt)
        base_tokens = max(1, base_length // 4)
        
        # 如果启用RAG，计算上下文token
        rag_context_tokens = 0
        rag_context_length = 0
        if include_rag_context and self.config.enable_rag:
            # 确保生成器初始化
            self.generator.initialize()
            
            # 获取相关文档
            try:
                retriever = self.generator.kb_manager.get_retriever(self.config.k)
                if retriever:
                    # 获取文档内容
                    docs = retriever.invoke(requirement)
                    if docs:
                        for doc in docs:
                            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                            rag_context_length += len(content)
                        rag_context_tokens = max(1, rag_context_length // 4)
            except Exception as e:
                print(f"⚠️  获取RAG上下文时出错: {e}")
        
        # 总prompt
        total_length = base_length + rag_context_length
        total_tokens = base_tokens + rag_context_tokens
        
        return {
            "system_prompt_length": len(system_prompt),
            "system_prompt_tokens": max(1, len(system_prompt) // 4),
            "requirement_length": len(requirement),
            "requirement_tokens": max(1, len(requirement) // 4),
            "base_prompt_length": base_length,
            "base_prompt_tokens": base_tokens,
            "rag_context_length": rag_context_length,
            "rag_context_tokens": rag_context_tokens,
            "total_prompt_length": total_length,
            "total_prompt_tokens": total_tokens
        }
    
    def test_rag_search(self, query: str, k: int = None, show_summary: bool = True) -> List[Dict[str, Any]]:
        """测试RAG搜索功能"""
        if not self.config.enable_rag:
            print("⚠️  RAG功能未启用")
            return []
        
        # 使用config中的k值作为默认值
        search_k = k if k is not None else self.config.k
        
        print(f"\n🔍 测试RAG搜索: '{query}' (k={search_k})")
        
        # 确保生成器已初始化
        self.generator.initialize()
        
        # 执行搜索
        documents = self.generator.search_knowledge_base(query, search_k)
        
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