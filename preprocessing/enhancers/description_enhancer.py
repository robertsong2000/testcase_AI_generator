#!/usr/bin/env python3
"""
测试用例描述增强器 - 实际调用LLM进行智能增强
"""

import json
import re
from typing import Dict, Any, List

class DescriptionEnhancer:
    """增强测试用例描述"""
    
    def __init__(self, llm_client, logger):
        """初始化增强器"""
        self.llm_client = llm_client  # 这是LangChain的LLM客户端
        self.logger = logger
    
    def enhance(self, testcase: Dict[str, Any], context: Dict[str, Any], 
                purpose: str) -> Dict[str, Any]:
        """增强测试用例描述"""
        try:
            enhanced = testcase.copy()
            
            # 增强标题
            enhanced['title'] = self._enhance_title(testcase, purpose)
            
            # 增强描述
            enhanced['description'] = self._enhance_description(testcase, context, purpose)
            
            # 增强测试步骤
            enhanced['steps'] = self._enhance_steps(testcase.get('steps', []), context, purpose)
            
            # 添加增强元数据
            enhanced['_enhanced'] = True
            enhanced['_purpose'] = purpose
            enhanced['_context'] = context
            
            self.logger.info("✅ 测试用例描述增强完成")
            return enhanced
            
        except Exception as e:
            self.logger.error(f"❌ 测试用例增强失败: {e}")
            return testcase
    
    def _enhance_title(self, testcase: Dict[str, Any], purpose: str) -> str:
        """增强测试用例标题"""
        original_title = testcase.get('title', '')
        
        # 如果已经有合适的标题，保持不变
        if original_title and len(original_title) > 5:
            return original_title
        
        # 基于测试名称生成标题
        test_name = testcase.get('name', '')
        if test_name:
            # 清理测试名称
            clean_name = test_name.replace('TC_', '').replace('_', ' ')
            return f"{clean_name}功能测试"
        
        # 基于目的生成标题
        return purpose.replace('验证', '').replace('测试', '').strip() + "功能验证"
    
    def _enhance_description(self, testcase: Dict[str, Any], 
                          context: Dict[str, Any], purpose: str) -> str:
        """增强测试用例描述"""
        original_desc = testcase.get('description', '')
        
        # 使用LLM生成详细描述
        enhanced_desc = self._call_llm_for_description(testcase, context, purpose)
        
        return enhanced_desc if enhanced_desc else original_desc
    
    def _enhance_steps(self, steps: List[Dict[str, Any]], 
                      context: Dict[str, Any], purpose: str) -> List[Dict[str, Any]]:
        """增强测试步骤"""
        enhanced_steps = []
        enhanced_count = 0
        
        for i, step in enumerate(steps, 1):
            enhanced_step = step.copy()
            
            # 使用LLM增强步骤描述
            enhanced_description = self._call_llm_for_step(
                step, i, len(steps), context, purpose
            )
            if enhanced_description and enhanced_description != step.get('description', ''):
                enhanced_step['description'] = enhanced_description
                enhanced_count += 1
            
            # 增强预期结果
            original_expected = step.get('expected_result', '')
            if not original_expected or original_expected == f"验证第{i}步操作结果正确":
                enhanced_expected = self._call_llm_for_expected_result(
                    step, i, context, purpose
                )
                if enhanced_expected:
                    enhanced_step['expected_result'] = enhanced_expected
                    enhanced_count += 1
            
            # 确保步骤编号
            enhanced_step['step_number'] = i
            
            # 标记为已增强
            enhanced_step['enhanced_by'] = "llm"
            
            enhanced_steps.append(enhanced_step)
        
        # 记录增强统计
        self.logger.info(f"📊 已增强 {enhanced_count} 个步骤")
        
        return enhanced_steps
    
    def _call_llm_for_description(self, testcase: Dict[str, Any], 
                                context: Dict[str, Any], purpose: str) -> str:
        """调用LLM生成测试用例描述"""
        
        # 构建测试步骤信息
        steps_summary = []
        for i, step in enumerate(testcase.get('steps', [])[:5], 1):  # 取前5步作为摘要
            steps_summary.append(f"步骤{i}: {step.get('test_step', '')}")
        
        prompt = f"""你是一位专业的汽车电子测试工程师，请基于以下信息生成一个详细且专业的测试用例描述。

测试目的: {purpose}

测试用例基本信息:
- 名称: {testcase.get('name', '')}
- 主要步骤: {', '.join(steps_summary)}

上下文信息:
{json.dumps(context, ensure_ascii=False, indent=2)}

要求:
1. 用简洁专业的语言描述测试的核心目的
2. 说明测试的重要性和应用场景
3. 概述测试覆盖的关键功能点
4. 语言清晰，不超过150字

测试用例描述:"""

        try:
            # 使用LangChain LLM的invoke方法
            response = self.llm_client.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            
            return self._clean_llm_response(result)
            
        except Exception as e:
            self.logger.error(f"❌ LLM描述增强失败: {e}")
            return ""
    
    def _call_llm_for_step(self, step: Dict[str, Any], step_num: int, 
                          total_steps: int, context: Dict[str, Any], 
                          purpose: str) -> str:
        """调用LLM增强步骤描述"""
        
        prompt = f"""你是一位专业的汽车电子测试工程师，请重写以下测试步骤的描述，使其更清晰和专业。

测试步骤:
- 步骤名称: {step.get('test_step', '')}
- 原始描述: {step.get('description', '')}

测试整体目的: {purpose}
步骤位置: 第{step_num}步/共{total_steps}步

要求:
1. 明确此步骤在整体测试中的作用
2. 使用专业的测试术语
3. 描述具体的操作内容和目的
4. 语言简洁，不超过100字

重写后的步骤描述:"""

        try:
            response = self.llm_client.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            
            return self._clean_llm_response(result)
            
        except Exception as e:
            self.logger.error(f"❌ LLM步骤增强失败: {e}")
            return step.get('description', '')
    
    def _call_llm_for_expected_result(self, step: Dict[str, Any], 
                                    step_num: int, context: Dict[str, Any], 
                                    purpose: str) -> str:
        """调用LLM生成预期结果"""
        
        prompt = f"""你是一位专业的汽车电子测试工程师，请为以下测试步骤生成准确且可验证的预期结果。

测试步骤:
- 步骤名称: {step.get('test_step', '')}
- 步骤描述: {step.get('description', '')}

要求:
1. 描述具体的验证条件和标准
2. 使用可量化的指标
3. 语言明确无歧义
4. 不超过80字

预期结果:"""

        try:
            response = self.llm_client.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            
            return self._clean_llm_response(result)
            
        except Exception as e:
            self.logger.error(f"❌ LLM预期结果生成失败: {e}")
            return f"验证第{step_num}步操作结果符合预期"
    
    def _clean_llm_response(self, response: str) -> str:
        """清理LLM响应"""
        if not response:
            return ""
        
        # 移除可能的HTML标签和特殊字符
        response = re.sub(r'<[^>]+>', '', response)
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)  # 移除think标签
        response = re.sub(r'\n+', '\n', response)
        response = re.sub(r'\s+', ' ', response)
        response = response.strip()
        
        return response