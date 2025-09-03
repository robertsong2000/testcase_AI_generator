#!/usr/bin/env python3
"""
测试用例LLM增强器
基于LLM+RAG的测试用例增强系统
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from capl_langchain.factories.llm_factory import LLMFactory
from capl_langchain.managers.knowledge_manager import KnowledgeManager


class TestcaseLLMEnhancer:
    """
    基于LLM+RAG的测试用例增强器
    
    功能:
    - 智能增强测试用例描述
    - 基于知识库优化测试步骤
    - 生成更详细的预期结果
    """
    
    def __init__(self, config, verbose: bool = False):
        """
        初始化增强器
        
        Args:
            config: EnhancerConfig对象，包含LLM和RAG相关配置
            verbose: 是否显示详细输出
        """
        self.config = config
        self.verbose = verbose
        
        # 初始化LLM客户端
        self.llm_client = LLMFactory.create_llm(config)
        
        # 初始化知识库管理器
        self.knowledge_manager = KnowledgeManager(config)
    
    def enhance_testcase(self, testcase_path: str, step_index: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        增强测试用例
        
        Args:
            testcase_path: 测试用例文件路径
            step_index: 指定要增强的步骤索引，None表示增强所有步骤
            
        Returns:
            增强后的测试用例数据
        """
        try:
            if self.verbose:
                print(f"🚀 开始增强测试用例: {testcase_path}")
            
            # 加载测试用例
            with open(testcase_path, 'r', encoding='utf-8') as f:
                testcase = json.load(f)
            
            # 增强测试用例
            enhanced = self._enhance_testcase(testcase, step_index)
            
            if self.verbose:
                print("✅ 测试用例增强完成")
            
            return enhanced
            
        except Exception as e:
            if self.verbose:
                print(f"❌ 增强测试用例时发生错误: {e}")
            return None
    
    def _enhance_testcase(self, testcase: Dict[str, Any], step_index: Optional[int] = None) -> Dict[str, Any]:
        """
        增强测试用例的核心逻辑
        
        Args:
            testcase: 原始测试用例
            step_index: 指定步骤索引
            
        Returns:
            增强后的测试用例
        """
        enhanced = testcase.copy()
        
        # 增强测试用例描述
        if 'description' in testcase:
            enhanced['description'] = self._enhance_description_with_llm(
                testcase.get('description', ''),
                testcase.get('purpose', ''),
                testcase.get('preconditions', [])
            )
        
        # 增强步骤
        if 'steps' in testcase:
            steps = testcase['steps']
            
            if step_index is not None:
                # 增强指定步骤
                if 0 <= step_index < len(steps):
                    enhanced['steps'][step_index] = self._enhance_step(
                        steps[step_index], 
                        step_index,
                        testcase
                    )
            else:
                # 增强所有步骤
                enhanced_steps = []
                for i, step in enumerate(steps):
                    if self.verbose:
                        print(f"🔄 正在增强步骤 {i+1}/{len(steps)}...")
                    
                    enhanced_step = self._enhance_step(step, i, testcase)
                    enhanced_steps.append(enhanced_step)
                
                enhanced['steps'] = enhanced_steps
        
        return enhanced
    
    def _analyze_testcase_purpose(self, testcase: Dict[str, Any]) -> str:
        """
        分析测试用例的主要目的
        
        Args:
            testcase: 测试用例
            
        Returns:
            测试用例目的的文本描述
        """
        purpose = testcase.get('purpose', '')
        if not purpose:
            # 从测试用例信息推断目的
            title = testcase.get('title', '')
            description = testcase.get('description', '')
            
            prompt = f"""
            基于以下测试用例信息，生成一个简洁的测试目的描述：
            
            标题: {title}
            描述: {description}
            
            请用一句话总结这个测试用例的主要目的。
            """
            
            try:
                response = self.llm_client.invoke(prompt)
                purpose = response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                if self.verbose:
                    print(f"⚠️ 分析测试目的失败: {e}")
                purpose = f"测试{title}功能"
        
        return purpose
    
    def _enhance_step(self, step: Dict[str, Any], step_index: int, testcase: Dict[str, Any]) -> Dict[str, Any]:
        """
        增强单个测试步骤
        
        Args:
            step: 原始步骤
            step_index: 步骤索引
            testcase: 完整测试用例
            
        Returns:
            增强后的步骤
        """
        enhanced_step = step.copy()
        
        # 构建步骤上下文
        context = self._build_step_context(step_index, testcase)
        
        # 增强步骤描述
        if 'description' in step:
            original_description = step['description']
            enhanced_description = self._call_llm_for_step(
                original_description,
                context,
                step_index
            )
            
            if enhanced_description and enhanced_description != original_description:
                enhanced_step['description'] = enhanced_description
                enhanced_step['original_description'] = original_description
        
        # 增强预期结果
        if 'expected_result' in step:
            original_expected = step['expected_result']
            enhanced_expected = self._call_llm_for_expected_result(
                original_expected,
                enhanced_step.get('description', step.get('description', '')),
                context
            )
            
            if enhanced_expected and enhanced_expected != original_expected:
                enhanced_step['expected_result'] = enhanced_expected
                enhanced_step['original_expected_result'] = original_expected
        
        return enhanced_step
    
    def _build_step_context(self, step_index: int, testcase: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建步骤上下文信息
        
        Args:
            step_index: 当前步骤索引
            testcase: 测试用例
            
        Returns:
            上下文信息字典
        """
        context = {
            'testcase_title': testcase.get('title', ''),
            'testcase_purpose': self._analyze_testcase_purpose(testcase),
            'preconditions': testcase.get('preconditions', []),
            'current_step_index': step_index + 1,
            'total_steps': len(testcase.get('steps', [])),
            'previous_steps': [],
            'next_steps': []
        }
        
        # 添加前后步骤信息
        steps = testcase.get('steps', [])
        if step_index > 0:
            context['previous_steps'] = steps[:step_index]
        if step_index < len(steps) - 1:
            context['next_steps'] = steps[step_index + 1:]
        
        return context
    
    def _enhance_description_with_llm(self, original_description: str, purpose: str, preconditions: List[str]) -> str:
        """
        使用LLM增强测试用例描述
        
        Args:
            original_description: 原始描述
            purpose: 测试目的
            preconditions: 前置条件
            
        Returns:
            增强后的描述
        """
        try:
            # 查询相关知识
            knowledge_context = ""
            if self.config.enable_rag:
                try:
                    knowledge_context = self.knowledge_manager.search_documents(
                        query=f"{purpose} {original_description}",
                        k=3
                    )
                except Exception as e:
                    if self.verbose:
                        print(f"⚠️ 知识库查询失败: {e}")
            
            prompt = f"""
            基于以下信息，请增强这个测试用例的描述，使其更清晰、详细：
            
            原始描述: {original_description}
            测试目的: {purpose}
            前置条件: {', '.join(preconditions)}
            
            相关背景知识:
            {knowledge_context}
            
            要求:
            1. 保持原有核心信息不变
            2. 增加必要的细节和解释
            3. 使用更专业的技术语言
            4. 控制在{self.config.max_description_length}字以内
            
            请直接返回增强后的描述，不要添加解释。
            """
            
            response = self.llm_client.invoke(prompt)
            enhanced_description = response.content if hasattr(response, 'content') else str(response)
            
            return enhanced_description.strip()
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️ 描述增强失败: {e}")
            return original_description
    
    def _call_llm_for_step(self, original_description: str, context: Dict[str, Any], step_index: int) -> str:
        """
        调用LLM增强测试步骤
        
        Args:
            original_description: 原始步骤描述
            context: 上下文信息
            step_index: 步骤索引
            
        Returns:
            增强后的步骤描述
        """
        try:
            # 查询相关知识
            knowledge_context = ""
            if self.config.enable_rag:
                try:
                    knowledge_context = self.knowledge_manager.search_documents(
                        query=f"{context['testcase_title']} {original_description}",
                        k=2
                    )
                except Exception as e:
                    if self.verbose:
                        print(f"⚠️ 知识库查询失败: {e}")
            
            prompt = f"""
            基于以下信息，请增强这个测试步骤的描述，使其更清晰、详细：
            
            测试用例: {context['testcase_title']}
            测试目的: {context['testcase_purpose']}
            当前步骤: 第{step_index + 1}步，共{context['total_steps']}步
            原始描述: {original_description}
            
            前置条件: {', '.join(context['preconditions'])}
            
            相关背景知识:
            {knowledge_context}
            
            要求:
            1. 保持原有核心操作不变
            2. 增加必要的细节和解释
            3. 使用更专业的技术语言
            4. 明确指出操作的具体目的和预期行为
            5. 控制在{self.config.max_description_length}字以内
            
            请直接返回增强后的步骤描述，不要添加解释。
            """
            
            response = self.llm_client.invoke(prompt)
            enhanced_description = response.content if hasattr(response, 'content') else str(response)
            
            return enhanced_description.strip()
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️ 步骤增强失败: {e}")
            return original_description
    
    def _call_llm_for_expected_result(self, original_expected: str, step_description: str, context: Dict[str, Any]) -> str:
        """
        调用LLM增强预期结果
        
        Args:
            original_expected: 原始预期结果
            step_description: 步骤描述
            context: 上下文信息
            
        Returns:
            增强后的预期结果
        """
        try:
            prompt = f"""
            基于以下测试步骤，请增强其预期结果，使其更详细、具体：
            
            测试用例: {context['testcase_title']}
            步骤描述: {step_description}
            原始预期结果: {original_expected}
            
            要求:
            1. 保持原有核心预期不变
            2. 增加具体的验证标准和检查点
            3. 明确指出系统应该表现出的具体行为
            4. 使用更专业的技术语言
            5. 控制在{self.config.max_description_length}字以内
            
            请直接返回增强后的预期结果，不要添加解释。
            """
            
            response = self.llm_client.invoke(prompt)
            enhanced_expected = response.content if hasattr(response, 'content') else str(response)
            
            return enhanced_expected.strip()
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️ 预期结果增强失败: {e}")
            return original_expected