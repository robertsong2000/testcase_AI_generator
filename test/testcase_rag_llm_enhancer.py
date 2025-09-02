#!/usr/bin/env python3
"""
基于LLM+RAG的测试用例增强器
使用大模型结合RAG分析测试用例的description字段并智能重写
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from capl_langchain.config.config import CAPLGeneratorConfig
from capl_langchain.managers.knowledge_manager import KnowledgeManager
from capl_langchain.factories.llm_factory import LLMFactory


class TestcaseLLMEnhancer:
    """基于LLM+RAG的测试用例增强器"""
    
    def __init__(self, config: CAPLGeneratorConfig):
        self.config = config
        self.knowledge_manager = KnowledgeManager(config)
        self.llm = LLMFactory.create_llm(config)
        
    def enhance_testcase(self, testcase_path: str) -> Dict[str, Any]:
        """增强单个测试用例"""
        print(f"🚀 开始增强测试用例: {testcase_path}")
        
        # 初始化知识库
        if not self.knowledge_manager.initialize_knowledge_base():
            print("❌ 知识库初始化失败")
            return {}
            
        # 加载测试用例
        with open(testcase_path, 'r', encoding='utf-8') as f:
            testcase = json.load(f)
            
        print("🔍 正在分析测试用例结构...")
        
        # 增强测试步骤描述
        enhanced_testcase = self._enhance_with_llm(testcase)
        
        return enhanced_testcase
        
    def _enhance_with_llm(self, testcase: Dict[str, Any]) -> Dict[str, Any]:
        """使用LLM智能重写description字段"""
        enhanced = testcase.copy()
        
        # 增强测试步骤描述
        if 'steps' in testcase:
            enhanced_steps = []
            for i, step in enumerate(testcase['steps']):
                enhanced_step = step.copy()
                if 'description' in step and 'test_step' in step:
                    print(f"🤖 正在处理第 {i+1} 个步骤: {step['test_step']}")
                    
                    # 获取相关上下文
                    context = self._get_relevant_context(step)
                    
                    # 使用LLM重写描述
                    enhanced_description = self._rewrite_description_with_llm(
                        step['description'],
                        step['test_step'],
                        context
                    )
                    enhanced_step['description'] = enhanced_description
                    enhanced_step['original_description'] = step['description']
                    
                    # 添加处理标记
                    enhanced_step['enhanced_by'] = f"llm_{self.config.api_type}"
                    
                enhanced_steps.append(enhanced_step)
            enhanced['steps'] = enhanced_steps
            
        return enhanced
        
    def _get_relevant_context(self, step: Dict) -> str:
        """获取相关的技术上下文"""
        query = f"{step['test_step']} - {step['description']}"
        
        # 搜索相关知识
        relevant_docs = self.knowledge_manager.search_documents(
            query=query,
            k=3,
            enable_rerank=True
        )
        
        if not relevant_docs:
            return ""
            
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(f"相关技术文档: {doc['source']}")
            context_parts.append(f"内容摘要: {doc['summary']}")
            context_parts.append("")
            
        return "\n".join(context_parts)
        
    def _rewrite_description_with_llm(self, original_desc: str, test_step: str, context: str) -> str:
        """使用LLM重写描述"""
        
        prompt = f"""你是一位专业的汽车测试工程师，负责增强测试用例的描述。

原始测试步骤: {test_step}
原始描述: {original_desc}

相关技术上下文:
{context}

请基于以上信息，用更专业、详细的方式重写这个测试步骤的描述。
要求：
1. 保持技术准确性
2. 添加具体的测试目的和预期结果
3. 包含相关的API或函数调用信息
4. 使用清晰的测试语言
5. 不超过200字

重写后的描述:"""

        try:
            response = self.llm.invoke(prompt)
            enhanced_desc = response.content if hasattr(response, 'content') else str(response)
            
            # 清理响应
            enhanced_desc = enhanced_desc.strip()
            if enhanced_desc.startswith('"') and enhanced_desc.endswith('"'):
                enhanced_desc = enhanced_desc[1:-1]
                
            return enhanced_desc or original_desc
            
        except Exception as e:
            print(f"⚠️ LLM处理失败: {e}")
            return original_desc
            
    def save_enhanced_testcase(self, enhanced_testcase: Dict[str, Any], output_path: str):
        """保存增强后的测试用例"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_testcase, f, ensure_ascii=False, indent=2)
        print(f"✅ 增强后的测试用例已保存: {output_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="基于LLM+RAG的测试用例增强器")
    parser.add_argument("testcase_path", help="测试用例文件路径")
    parser.add_argument("--model", choices=["openai", "ollama"], default="ollama", 
                       help="使用的模型类型")
    parser.add_argument("--suffix", default=".llm_enhanced", 
                       help="输出文件后缀")
    
    args = parser.parse_args()
    
    # 创建配置
    config = CAPLGeneratorConfig()
    config.api_type = args.model
    config.enable_rag = True
    config.use_hybrid_search = False
    config.knowledge_base_dir = project_root / "knowledge_base"
    config.vector_db_dir = project_root / "vector_db"
    
    # 设置使用小模型qwen3:1.7b
    config.model = "qwen3:1.7b"
    
    # 创建增强器
    enhancer = TestcaseLLMEnhancer(config)
    
    # 增强测试用例
    enhanced = enhancer.enhance_testcase(args.testcase_path)
    
    if enhanced:
        # 生成输出路径
        input_path = Path(args.testcase_path)
        output_path = input_path.with_suffix(f"{input_path.suffix}{args.suffix}")
        
        # 保存结果
        enhancer.save_enhanced_testcase(enhanced, str(output_path))
        
        # 打印统计信息
        total_steps = len(enhanced.get('steps', []))
        enhanced_steps = sum(1 for step in enhanced.get('steps', []) 
                           if 'enhanced_by' in step)
        
        print(f"\n📊 增强完成统计:")
        print(f"   ✅ 总步骤数: {total_steps}")
        print(f"   ✅ 已增强步骤: {enhanced_steps}")
        print(f"   ✅ 增强比例: {enhanced_steps/total_steps*100:.1f}%")
    else:
        print("❌ 增强失败")


if __name__ == "__main__":
    main()