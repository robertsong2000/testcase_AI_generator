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

import copy  # 添加copy模块导入

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from capl_langchain.config.config import CAPLGeneratorConfig
from capl_langchain.managers.knowledge_manager import KnowledgeManager
from capl_langchain.factories.llm_factory import LLMFactory

class TestcaseLLMEnhancer:
    """基于LLM+RAG的测试用例增强器"""
    
    def __init__(self, config: CAPLGeneratorConfig, verbose: bool = False):
        self.config = config
        self.knowledge_manager = KnowledgeManager(config)
        self.llm = LLMFactory.create_llm(config)
        self.verbose = verbose
        self._testcase_purpose_cache = {}  # 缓存测试用例目的
        
    def _get_cached_purpose(self, testcase: Dict[str, Any]) -> str:
        """获取缓存的测试用例目的，如果不存在则分析并缓存"""
        # 使用测试用例ID作为缓存键
        cache_key = testcase.get('id', testcase.get('name', str(hash(str(testcase)))))
        
        if cache_key not in self._testcase_purpose_cache:
            if self.verbose:
                print(f"🔍 首次分析测试用例目的: {testcase.get('title', cache_key)}")
            self._testcase_purpose_cache[cache_key] = self._analyze_testcase_purpose(testcase)
               
        return self._testcase_purpose_cache[cache_key]
        
    def enhance_testcase(self, testcase_path: str, step_index: Optional[int] = None) -> Dict[str, Any]:
        """增强单个测试用例"""
        print(f"🚀 开始增强测试用例: {testcase_path}")
        
        if step_index is not None:
            print(f"📍 指定处理步骤: 第 {step_index + 1} 步")
        
        # 初始化知识库
        if not self.knowledge_manager.initialize_knowledge_base():
            print("❌ 知识库初始化失败")
            return {}
            
        # 加载测试用例
        with open(testcase_path, 'r', encoding='utf-8') as f:
            testcase = json.load(f)
            
        print("🔍 正在分析测试用例结构...")
        
        # 增强测试步骤描述
        enhanced_testcase = self._enhance_with_llm(testcase, step_index)
        
        return enhanced_testcase
        
    def _enhance_with_llm(self, testcase: Dict[str, Any], step_index: Optional[int] = None) -> Dict[str, Any]:
        """使用LLM增强测试用例描述"""
        
        # 获取测试用例的整体目的（使用缓存）
        overall_purpose = self._get_cached_purpose(testcase)
        
        # 创建测试用例的深拷贝以避免修改原始数据
        enhanced_testcase = copy.deepcopy(testcase)
        
        # 确定要处理的步骤范围
        steps_to_process = []
        if step_index is not None:
            if 0 <= step_index < len(enhanced_testcase['steps']):
                steps_to_process = [(step_index, enhanced_testcase['steps'][step_index])]
            else:
                print(f"⚠️ 步骤索引 {step_index} 超出范围，处理所有步骤")
                steps_to_process = list(enumerate(enhanced_testcase['steps']))
        else:
            steps_to_process = list(enumerate(enhanced_testcase['steps']))
        
        # 处理每个步骤
        for i, step in steps_to_process:
            print(f"\n📋 处理步骤 {i+1}/{len(enhanced_testcase['steps'])}")
            if self.verbose:
                print(f"   原始描述: {step.get('description', '无描述')}")
            
            # 获取增强的上下文
            enhanced_context = self._get_enhanced_context(step, enhanced_testcase, i, overall_purpose)
            
            # 使用LLM重写描述
            enhanced_description = self._rewrite_description_with_llm(
                step, enhanced_context, overall_purpose, i, len(enhanced_testcase['steps'])
            )
            
            # 保存原始描述并更新
            if 'original_description' not in step:
                step['original_description'] = step.get('description', '')
            step['description'] = enhanced_description
            
            if self.verbose:
                print(f"   增强描述: {enhanced_description}...")
        
        return enhanced_testcase
        
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
        
    def _rewrite_description_with_llm(self, step: Dict, context: str, overall_purpose: str, step_index: int, total_steps: int) -> str:
        """使用LLM重写步骤描述"""
        
        original_desc = step.get('description', '')
        test_step = step.get('test_step', '')
        
        prompt = f"""你是一位专业的汽车电子测试工程师，请基于以下上下文信息重写测试步骤的描述。

**上下文信息：**
{context}

**需要重写的测试步骤：**
- 步骤名称: {test_step}
- 原始描述: {original_desc}

**重写要求：**
1. **理解整体目的**: 基于上下文信息的整体测试用例目的，明确此步骤在流程中的作用
2. **保持技术准确性**: 确保描述符合汽车电子测试标准
3. **添加具体细节**: 包含具体的测试目的、预期结果和验证方法
4. **步骤关联性**: 考虑与前后步骤的衔接关系
5. **API规范**: 包含相关的API或函数调用信息，但必须严格按照以下规则：
   - 只能使用知识库中提供的API格式
   - 如果API是无参函数，不能添加任何参数
   - 如果API有参数，必须使用正确的参数类型和数量
   - 不能编造不存在的API或参数
6. **语言规范**: 使用清晰的测试语言，不超过200字

**重写后的描述:**"""

        try:
            if self.verbose:
                print(f"📝 发送给LLM的提示词: {prompt}")
            response = self.llm.invoke(prompt)
            enhanced_desc = response.content if hasattr(response, 'content') else str(response)
            
            # 清理响应
            import re
            enhanced_desc = enhanced_desc.strip()
            enhanced_desc = re.sub(r'<think>.*?</think>', '', enhanced_desc, flags=re.DOTALL)
            enhanced_desc = re.sub(r'</?think>', '', enhanced_desc)
            enhanced_desc = re.sub(r'\n\s*\n', ' ', enhanced_desc)
            enhanced_desc = enhanced_desc.strip()
                       
            return enhanced_desc if enhanced_desc else original_desc
            
        except Exception as e:
            print(f"⚠️ LLM重写描述失败: {e}")
            return original_desc
            
    def save_enhanced_testcase(self, enhanced_testcase: Dict[str, Any], output_path: str):
        """保存增强后的测试用例"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_testcase, f, ensure_ascii=False, indent=2)
        print(f"✅ 增强后的测试用例已保存: {output_path}")

    def _analyze_testcase_purpose(self, testcase: Dict[str, Any]) -> str:
        """使用大模型智能分析测试用例的整体目的"""
        
        # 构建测试用例的完整描述
        testcase_info = []
        
        # 测试用例基本信息
        if 'title' in testcase:
            testcase_info.append(f"测试用例标题: {testcase['title']}")
            
        if 'name' in testcase:
            testcase_info.append(f"测试用例名称: {testcase['name']}")
            
        # 前置条件
        if 'preconditions' in testcase:
            preconditions = testcase['preconditions']
            if isinstance(preconditions, list):
                preconditions = '\n'.join(str(p) for p in preconditions if p)
            testcase_info.append(f"前置条件:\n{preconditions}")
            
        # 测试步骤
        if 'steps' in testcase and testcase['steps']:
            steps_info = []
            for i, step in enumerate(testcase['steps'], 1):
                step_desc = f"步骤{i}: {step.get('test_step', '未命名步骤')}"
                if 'description' in step:
                    step_desc += f" - {step['description'][:100]}..."
                steps_info.append(step_desc)
            testcase_info.append(f"测试步骤:\n" + '\n'.join(steps_info))
            
        # 预期结果
        if 'expected_results' in testcase:
            expected = testcase['expected_results']
            if isinstance(expected, list):
                expected = '\n'.join(str(e) for e in expected)
            testcase_info.append(f"预期结果:\n{expected}")
            
        # 如果没有足够信息，返回简化分析
        if not testcase_info:
            title = testcase.get('title', testcase.get('name', '未知测试'))
            return f"测试功能: {title}"
            
        full_context = '\n\n'.join(testcase_info)
        
        # 使用大模型分析测试目的
        purpose_prompt = f"""你是一位专业的汽车测试工程师，请分析以下测试用例并提炼其核心测试目的。

请基于测试用例的完整信息，用简洁的语言总结这个测试用例的核心测试目的和主要验证点。

要求：
1. 用一句话概括测试的核心目的
2. 突出测试的主要功能和验证目标
3. 语言简洁专业，不超过200字
4. 避免冗余的描述性词汇

测试用例信息：
{full_context}

测试目的总结:"""

        try:
            response = self.llm.invoke(purpose_prompt)
            purpose = response.content if hasattr(response, 'content') else str(response)
            
            # 清理响应
            import re
            purpose = purpose.strip()
            purpose = re.sub(r'<think>.*?</think>', '', purpose, flags=re.DOTALL)
            purpose = re.sub(r'</?think>', '', purpose)
            purpose = re.sub(r'\n\s*\n', ' ', purpose)
            purpose = purpose.strip()
                
            # 如果大模型返回空或无效，使用标题兜底
            if not purpose or len(purpose.strip()) < 5:
                title = testcase.get('title', testcase.get('name', '未知测试'))
                title = title.replace('TC_', '').replace('_', ' ')
                return f"测试: {title}"
                
            return purpose
            
        except Exception as e:
            print(f"⚠️ 大模型分析测试目的失败: {e}")
            # 回退到标题
            title = testcase.get('title', testcase.get('name', '未知测试'))
            title = title.replace('TC_', '').replace('_', ' ')
            return f"测试: {title}"
        
    def _get_enhanced_context(self, step: Dict, testcase: Dict, step_index: int, overall_purpose: str) -> str:
        """构建包含整体测试目的的增强上下文"""
        
        # 获取技术上下文
        technical_context = self._get_relevant_context(step)
        
        # 构建步骤上下文信息
        context_parts = []
        
        # 1. 整体测试目的（已缓存）
        context_parts.append(f"测试用例整体目的: {overall_purpose}")
        
        # 2. 当前步骤位置信息
        total_steps = len(testcase['steps'])
        context_parts.append(f"当前步骤: 第 {step_index + 1} 步 (共 {total_steps} 步)")
        
        # 3. 前后步骤关联（如果有）
        if step_index > 0:
            prev_step = testcase['steps'][step_index - 1]
            context_parts.append(f"上一步骤: {prev_step.get('test_step', '未知')}")
        
        if step_index < total_steps - 1:
            next_step = testcase['steps'][step_index + 1]
            context_parts.append(f"下一步骤: {next_step.get('test_step', '未知')}")
        
        # 4. 技术上下文
        if technical_context:
            context_parts.append(f"技术上下文: {technical_context}")
        
        return "\n".join(context_parts)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="基于LLM+RAG的测试用例增强器")
    parser.add_argument("testcase_path", help="测试用例文件路径")
    parser.add_argument("--model", choices=["openai", "ollama"], default="ollama", 
                       help="使用的模型类型")
    parser.add_argument("--suffix", default=".llm_enhanced", 
                       help="输出文件后缀")
    parser.add_argument("--verbose", action="store_true", 
                       help="显示详细的处理过程信息")
    parser.add_argument("--step-index", type=int, 
                       help="指定要处理的步骤索引（从0开始），不指定则处理所有步骤")
    
    args = parser.parse_args()
    
    # 创建配置
    config = CAPLGeneratorConfig()
    config.api_type = args.model
    config.enable_rag = True
    config.use_hybrid_search = True
    config.knowledge_base_dir = project_root / "knowledge_base"
    config.vector_db_dir = project_root / "vector_db"
    
    # 设置使用小模型qwen3:1.7b
    config.model = "qwen3:1.7b"
    
    # 创建增强器（传入verbose参数）
    enhancer = TestcaseLLMEnhancer(config, verbose=args.verbose)
    
    if args.verbose:
        print(f"🔧 详细模式已开启")
        print(f"   使用模型: {config.model}")
        print(f"   知识库目录: {config.knowledge_base_dir}")
        print(f"   向量数据库目录: {config.vector_db_dir}")
        if args.step_index is not None:
            print(f"   指定步骤索引: {args.step_index}")
        print()
    
    # 增强测试用例
    enhanced = enhancer.enhance_testcase(args.testcase_path, args.step_index)
    
    if enhanced:
        # 生成输出路径
        input_path = Path(args.testcase_path)
        
        # 如果指定了步骤索引，修改后缀以区分
        if args.step_index is not None:
            suffix = f"{args.suffix}_step_{args.step_index}"
        else:
            suffix = args.suffix
            
        output_path = input_path.with_suffix(f"{input_path.suffix}{suffix}")
        
        # 保存结果
        enhancer.save_enhanced_testcase(enhanced, str(output_path))
        
        # 打印统计信息
        total_steps = len(enhanced.get('steps', []))
        
        if args.step_index is not None:
            print(f"\n📊 增强完成统计:")
            print(f"   ✅ 总步骤数: {total_steps}")
            print(f"   ✅ 已处理步骤: 第 {args.step_index + 1} 步")
        else:
            enhanced_steps = sum(1 for step in enhanced.get('steps', []) 
                               if 'enhanced_by' in step)
            print(f"\n📊 增强完成统计:")
            print(f"   ✅ 总步骤数: {total_steps}")
            print(f"   ✅ 已增强步骤: {enhanced_steps}")
            print(f"   ✅ 增强比例: {enhanced_steps/total_steps*100:.1f}%")
        
        if args.verbose:
            print(f"   📁 输出文件: {output_path}")
    else:
        print("❌ 增强失败")


if __name__ == "__main__":
    main()