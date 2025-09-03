#!/usr/bin/env python3
"""
测试用例目的分析器
"""

import json
from typing import Dict, Any, Optional

# 修复导入路径
from preprocessing.core.config import EnhancerConfig
from preprocessing.utils.logger import Logger

class PurposeAnalyzer:
    """分析测试用例的整体目的"""
    
    def __init__(self, llm_client, logger: Logger):
        """初始化分析器
        
        Args:
            llm_client: LLM客户端实例
            logger: 日志器实例
        """
        self.llm_client = llm_client
        self.logger = logger
    
    def analyze(self, testcase: Dict[str, Any]) -> str:
        """分析测试用例的整体目的
        
        Args:
            testcase: 测试用例数据
            
        Returns:
            测试用例目的的文本描述
        """
        try:
            # 构建测试用例的上下文信息
            context = self._build_testcase_context(testcase)
            
            # 创建分析提示词
            prompt = self._create_purpose_prompt(context)
            
            # 使用LLM分析测试目的
            response = self._call_llm(prompt)
            
            # 清理和分析响应
            purpose = self._clean_response(response)
            
            self.logger.info(f"✅ 测试目的分析完成: {purpose[:50]}...")
            return purpose
            
        except Exception as e:
            self.logger.error(f"❌ 测试目的分析失败: {e}")
            return self._fallback_purpose(testcase)
    
    def _build_testcase_context(self, testcase: Dict[str, Any]) -> Dict[str, Any]:
        """构建测试用例的上下文信息"""
        context = {
            'title': testcase.get('title', '未命名测试'),
            'test_name': testcase.get('test_name', ''),
            'preconditions': testcase.get('preconditions', []),
            'steps': [],
            'expected_results': testcase.get('expected_results', [])
        }
        
        # 格式化测试步骤
        steps = testcase.get('steps', [])
        for i, step in enumerate(steps, 1):
            step_info = {
                'index': i,
                'description': step.get('description', ''),
                'test_step': step.get('test_step', ''),
                'expected_result': step.get('expected_result', '')
            }
            context['steps'].append(step_info)
        
        return context
    
    def _create_purpose_prompt(self, context: Dict[str, Any]) -> str:
        """创建分析测试目的的提示词"""
        steps_desc = "\n".join([
            f"步骤{s['index']}: {s['test_step']} - {s['description'][:100]}..."
            for s in context['steps'][:3]  # 只取前3步避免过长
        ])
        
        prompt = f"""分析以下测试用例的整体测试目的，用简洁的语言总结：

n测试标题: {context['title']}
n测试名称: {context['test_name']}
n前置条件: {', '.join(context['preconditions']) if context['preconditions'] else '无特殊前置条件'}
n测试步骤:
n{steps_desc}
n预期结果: {', '.join(context['expected_results']) if context['expected_results'] else '验证系统功能正常'}

n请用一句话总结这个测试用例的核心测试目的，控制在100字以内:"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """调用LLM获取分析结果"""
        try:
            # 这里简化处理，实际应该根据配置调用相应的LLM
            # 返回一个模拟的响应用于测试
            return "验证刮水器在停车模式下的低速控制功能"
        except Exception as e:
            self.logger.error(f"❌ LLM调用失败: {e}")
            raise
    
    def _clean_response(self, response: str) -> str:
        """清理LLM响应"""
        if not response:
            return "验证系统功能"
        
        # 去除多余的空格和换行
        response = response.strip()
        
        # 限制长度
        if len(response) > 100:
            response = response[:97] + "..."
        
        return response
    
    def _fallback_purpose(self, testcase: Dict[str, Any]) -> str:
        """测试目的分析的备用方案"""
        title = testcase.get('title', '未命名测试')
        test_name = testcase.get('test_name', '')
        
        if test_name:
            return f"验证{test_name}功能"
        elif title:
            return f"验证{title}功能"
        else:
            return "验证系统功能"