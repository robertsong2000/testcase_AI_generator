#!/usr/bin/env python3
"""
测试用例LLM增强器 - 双提示词精简版
仅包含测试用例总体分析和步骤描述增强两个核心功能
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

from capl_langchain.factories.llm_factory import LLMFactory
from capl_langchain.managers.knowledge_manager import KnowledgeManager


class TestcaseLLMEnhancer:
    """
    基于LLM的测试用例增强器 - 双提示词版本
    
    功能:
    - 智能分析测试用例总体目的（一次性）
    - 增强每个测试步骤的描述（对每个包含steps的测试用例）
    """
    
    def __init__(self, config, verbose: bool = False):
        """
        初始化增强器
        
        Args:
            config: EnhancerConfig对象，包含LLM配置
            verbose: 是否显示详细输出
        """
        self.config = config
        self.verbose = verbose
        
        # 初始化LLM客户端
        self.llm_client = LLMFactory.create_llm(config)
        
        # 缓存测试用例目的
        self._testcase_purpose_cache = {}
    
    def enhance_testcase(self, testcase_path: str, step_index: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        增强测试用例 - 支持步骤选择
        
        Args:
            testcase_path: 测试用例文件路径
            step_index: 指定增强的步骤索引（从1开始），None表示增强整个测试用例
            
        Returns:
            增强后的测试用例数据
        """
        try:
            if self.verbose:
                print(f"🚀 [阶段1] 开始增强测试用例")
                print(f"   📁 文件路径: {testcase_path}")
                if step_index:
                    print(f"   🎯 指定步骤: 步骤{step_index}")
                else:
                    print(f"   🎯 增强模式: 完整测试用例")
                print()
            
            # 加载测试用例
            if self.verbose:
                print(f"📖 [阶段2] 加载测试用例文件...")
            
            with open(testcase_path, 'r', encoding='utf-8') as f:
                testcase = json.load(f)
            
            if self.verbose:
                print(f"   ✅ 加载成功: {len(testcase)}个顶级字段")
                if 'steps' in testcase:
                    print(f"   ✅ 发现步骤: {len(testcase['steps'])}个测试步骤")
                print()
            
            # 增强测试用例
            enhanced = self._enhance_testcase(testcase, step_index)
            
            if self.verbose:
                print("✅ [阶段7] 测试用例增强完成")
            
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
            step_index: 指定增强的步骤索引，None表示增强整个测试用例
            
        Returns:
            增强后的测试用例
        """
        enhanced = testcase.copy()
        
        if step_index is not None:
            # 仅增强指定步骤
            return self._enhance_single_step(testcase, step_index)
        else:
            # 增强整个测试用例
            return self._enhance_full_testcase(testcase)
    
    def _enhance_full_testcase(self, testcase: Dict[str, Any]) -> Dict[str, Any]:
        """
        增强整个测试用例
        
        Args:
            testcase: 原始测试用例
            
        Returns:
            增强后的完整测试用例
        """
        enhanced = testcase.copy()
        
        # 1. 一次性分析测试用例总体目的
        if self.verbose:
            print(f"🎯 [阶段3] 开始分析测试用例总体目的...")
        
        overall_purpose = self._analyze_testcase_purpose(testcase)
        enhanced['purpose'] = overall_purpose
        
        if self.verbose:
            print(f"   📝 分析结果: {overall_purpose}")
            print()
        
        # 2. 增强每个测试步骤的描述
        if 'steps' in testcase and testcase['steps']:
            if self.verbose:
                print(f"🔄 [阶段4] 开始增强测试步骤描述...")
                print(f"   📊 总计: {len(testcase['steps'])}个步骤")
                print()
            
            enhanced_steps = []
            for i, step in enumerate(testcase['steps']):
                if self.verbose:
                    print(f"   🔧 [阶段4.{i+1}] 处理步骤{i+1}/{len(testcase['steps'])}...")
                
                enhanced_step = self._enhance_step_description(
                    step, i, overall_purpose, testcase
                )
                enhanced_steps.append(enhanced_step)
                
                if self.verbose:
                    print(f"   ✅ 步骤{i+1}处理完成")
                    print()
            
            enhanced['steps'] = enhanced_steps
            
            if self.verbose:
                enhanced_count = sum(1 for s in enhanced_steps if 'original_description' in s)
                print(f"   📊 增强统计: {enhanced_count}/{len(enhanced_steps)}个步骤已增强")
                print()
        else:
            if self.verbose:
                print(f"⚠️ [阶段4] 测试用例中没有步骤需要增强")
                print()
        
        return enhanced
    
    def _enhance_single_step(self, testcase: Dict[str, Any], step_index: int) -> Dict[str, Any]:
        """
        仅增强指定步骤
        
        Args:
            testcase: 原始测试用例
            step_index: 步骤索引（从1开始）
            
        Returns:
            只包含增强后指定步骤的测试用例
        """
        enhanced = testcase.copy()
        
        # 验证步骤索引
        if 'steps' not in testcase or not testcase['steps']:
            raise ValueError("测试用例中没有步骤")
        
        if step_index < 1 or step_index > len(testcase['steps']):
            raise ValueError(f"步骤索引无效，有效范围: 1-{len(testcase['steps'])}")
        
        if self.verbose:
            print(f"🎯 [阶段3] 分析测试用例上下文...")
        
        # 分析测试用例总体目的（用于上下文）
        overall_purpose = self._analyze_testcase_purpose(testcase)
        enhanced['purpose'] = overall_purpose
        
        if self.verbose:
            print(f"   📝 测试目的: {overall_purpose}")
            print(f"🔄 [阶段4] 增强指定步骤...")
            print(f"   🎯 目标步骤: 步骤{step_index}")
            print()
        
        # 仅增强指定步骤
        original_step = testcase['steps'][step_index - 1]
        enhanced_step = self._enhance_step_description(
            original_step, step_index - 1, overall_purpose, testcase
        )
        
        # 只返回增强后的指定步骤
        enhanced['steps'] = [enhanced_step]
        
        if self.verbose:
            print(f"   ✅ 步骤{step_index}增强完成")
            print()
        
        return enhanced
    
    def _get_cached_purpose(self, testcase: Dict[str, Any]) -> str:
        """获取缓存的测试用例目的，如果不存在则分析并缓存"""
        # 使用测试用例ID作为缓存键
        cache_key = testcase.get('id', testcase.get('name', str(hash(str(testcase)))))
        
        if cache_key not in self._testcase_purpose_cache:
            if self.verbose:
                print(f"   🔍 首次分析测试用例目的...")
            self._testcase_purpose_cache[cache_key] = self._analyze_testcase_purpose(testcase)
        
        return self._testcase_purpose_cache[cache_key]
    
    def _analyze_testcase_purpose(self, testcase: Dict[str, Any]) -> str:
        """
        使用LLM分析测试用例的主要目的 - 一次性调用
        
        Args:
            testcase: 测试用例
            
        Returns:
            测试用例目的的文本描述
        """
        try:
            # 获取缓存的目的（如果已存在）
            cache_key = testcase.get('id', testcase.get('name', str(hash(str(testcase)))))
            if cache_key in self._testcase_purpose_cache:
                return self._testcase_purpose_cache[cache_key]
            
            # 构建测试用例信息
            testcase_info = []
            
            if 'title' in testcase:
                testcase_info.append(f"测试用例标题: {testcase['title']}")
            
            if 'name' in testcase:
                testcase_info.append(f"测试用例名称: {testcase['name']}")
                
            if 'description' in testcase:
                testcase_info.append(f"描述: {testcase['description']}")
                
            if 'preconditions' in testcase:
                preconditions = testcase['preconditions']
                if isinstance(preconditions, list):
                    preconditions = '\n'.join(str(p) for p in preconditions if p)
                testcase_info.append(f"前置条件:\n{preconditions}")
                
            if 'steps' in testcase and testcase['steps']:
                steps_info = []
                for i, step in enumerate(testcase['steps'], 1):
                    step_desc = f"步骤{i}: {step.get('test_step', '未命名步骤')}"
                    if 'description' in step:
                        step_desc += f" - {step['description'][:100]}..."
                    steps_info.append(step_desc)
                testcase_info.append(f"测试步骤:\n" + '\n'.join(steps_info))
            
            if 'expected_results' in testcase:
                expected = testcase['expected_results']
                if isinstance(expected, list):
                    expected = '\n'.join(str(e) for e in expected)
                testcase_info.append(f"预期结果:\n{expected}")
            
            full_context = '\n\n'.join(testcase_info)
            
            prompt = f"""你是一位专业的汽车测试工程师，请分析以下测试用例并提炼其核心测试目的。

请基于测试用例的完整信息，用简洁的语言总结这个测试用例的核心测试目的和主要验证点。

要求：
1. 用一句话概括测试的核心目的
2. 突出测试的主要功能和验证目标
3. 语言简洁专业，不超过200字
4. 避免冗余的描述性词汇

测试用例信息：
{full_context}

测试目的总结:"""

            if self.verbose:
                print(f"   📝 调用LLM分析测试目的...")
                print(f"   📊 上下文长度: {len(full_context)}字符")
            
            response = self.llm_client.invoke(prompt)
            purpose = response.content if hasattr(response, 'content') else str(response)
            
            # 清理响应
            purpose = purpose.strip()
            purpose = re.sub(r'<think>.*?</think>', '', purpose, flags=re.DOTALL)
            purpose = re.sub(r'</?think>', '', purpose)
            purpose = re.sub(r'\n\s*\n', ' ', purpose)
            purpose = purpose.strip()
            
            # 如果返回空或无效，使用标题兜底
            if not purpose or len(purpose.strip()) < 5:
                title = testcase.get('title', testcase.get('name', '未知测试'))
                title = title.replace('TC_', '').replace('_', ' ')
                purpose = f"测试: {title}"
            
            # 缓存结果
            self._testcase_purpose_cache[cache_key] = purpose
            
            return purpose
            
        except Exception as e:
            if self.verbose:
                print(f"   ⚠️ 分析测试目的失败: {e}")
            # 回退到标题
            title = testcase.get('title', testcase.get('name', '未知测试'))
            title = title.replace('TC_', '').replace('_', ' ')
            return f"测试: {title}"
    
    def _enhance_step_description(self, step: Dict[str, Any], step_index: int, 
                                overall_purpose: str, testcase: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用LLM增强单个测试步骤的描述 - 对每个步骤调用
        
        Args:
            step: 原始步骤
            step_index: 步骤索引
            overall_purpose: 测试用例总体目的
            testcase: 完整测试用例上下文
            
        Returns:
            增强后的步骤
        """
        try:
            # 保存原始描述
            enhanced_step = step.copy()
            enhanced_step['original_description'] = step.get('description', '')
            
            # 构建步骤上下文
            step_context = self._build_step_context(step, step_index, overall_purpose, testcase)
            
            prompt = f"""你是一位专业的汽车测试工程师，请基于测试用例上下文增强以下测试步骤的描述。

当前测试用例目的：{overall_purpose}

步骤信息：
{step_context}

要求：
1. 用更详细、专业的语言描述测试步骤
2. 包含具体的操作细节和预期行为
3. 语言清晰准确，便于测试人员执行
4. 保持原有含义不变，仅增强描述
5. 不超过150字

增强后的步骤描述:"""

            if self.verbose:
                print(f"   📝 调用LLM增强步骤描述...")
                print(f"   📊 上下文长度: {len(step_context)}字符")
                print(f"   📝 原始描述: {step.get('description', '无描述')}")
            
            response = self.llm_client.invoke(prompt)
            enhanced_description = response.content if hasattr(response, 'content') else str(response)
            
            # 清理响应
            enhanced_description = enhanced_description.strip()
            enhanced_description = re.sub(r'<think>.*?</think>', '', enhanced_description, flags=re.DOTALL)
            enhanced_description = re.sub(r'</?think>', '', enhanced_description)
            enhanced_description = re.sub(r'\n\s*\n', ' ', enhanced_description)
            enhanced_description = enhanced_description.strip()
            
            # 如果返回空或无效，使用原始描述
            if not enhanced_description or len(enhanced_description.strip()) < 5:
                enhanced_description = step.get('description', '')
            
            enhanced_step['description'] = enhanced_description
            
            if self.verbose:
                print(f"   ✅ 增强完成")
                print(f"   📝 增强描述: {enhanced_description}")
            
            return enhanced_step
            
        except Exception as e:
            if self.verbose:
                print(f"   ⚠️ 增强步骤描述失败: {e}")
            # 回退到原始描述
            enhanced_step = step.copy()
            enhanced_step['original_description'] = step.get('description', '')
            enhanced_step['description'] = step.get('description', '')
            return enhanced_step
    
    def _build_step_context(self, step: Dict[str, Any], step_index: int, 
                          overall_purpose: str, testcase: Dict[str, Any]) -> str:
        """
        构建步骤的上下文信息
        
        Args:
            step: 当前步骤
            step_index: 步骤索引
            overall_purpose: 测试用例总体目的
            testcase: 完整测试用例
            
        Returns:
            步骤上下文字符串
        """
        context_parts = []
        
        # 步骤基本信息
        step_number = step_index + 1
        test_step = step.get('test_step', f"步骤{step_number}")
        description = step.get('description', '')
        
        context_parts.append(f"步骤编号: {step_number}")
        context_parts.append(f"步骤名称: {test_step}")
        context_parts.append(f"原始描述: {description}")
        
        # 添加前置步骤信息（如果有）
        if 'steps' in testcase and testcase['steps']:
            if step_index > 0:
                prev_step = testcase['steps'][step_index - 1]
                prev_desc = prev_step.get('description', '')
                if prev_desc:
                    context_parts.append(f"前置步骤: {prev_desc[:100]}...")
        
        # 添加预期结果
        if 'expected_results' in step:
            expected = step['expected_results']
            if isinstance(expected, list):
                expected = '\n'.join(str(e) for e in expected)
            context_parts.append(f"预期结果: {expected}")
        
        return '\n'.join(context_parts)