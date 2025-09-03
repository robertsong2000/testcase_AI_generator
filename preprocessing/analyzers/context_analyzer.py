#!/usr/bin/env python3
"""
测试用例上下文分析器
"""

import json
from typing import Dict, Any, Optional, List

# 修复导入路径
from preprocessing.core.config import EnhancerConfig
from preprocessing.utils.logger import Logger

class ContextAnalyzer:
    """分析测试用例的上下文环境"""
    
    def __init__(self, llm_client, logger: Logger):
        """初始化分析器
        
        Args:
            llm_client: LLM客户端实例
            logger: 日志器实例
        """
        self.llm_client = llm_client
        self.logger = logger
    
    def analyze(self, testcase: Dict[str, Any]) -> Dict[str, Any]:
        """分析测试用例的上下文环境
        
        Args:
            testcase: 测试用例数据
            
        Returns:
            上下文分析结果字典
        """
        try:
            # 提取关键上下文信息
            context = self._extract_context(testcase)
            
            # 分析每个上下文元素
            enriched_context = self._enrich_context(context)
            
            self.logger.info("✅ 测试上下文分析完成")
            return enriched_context
            
        except Exception as e:
            self.logger.error(f"❌ 测试上下文分析失败: {e}")
            return self._fallback_context(testcase)
    
    def _extract_context(self, testcase: Dict[str, Any]) -> Dict[str, Any]:
        """提取测试用例的关键上下文信息"""
        context = {
            'environment': self._extract_environment(testcase),
            'variables': self._extract_variables(testcase),
            'conditions': self._extract_conditions(testcase),
            'system_state': self._extract_system_state(testcase)
        }
        return context
    
    def _extract_environment(self, testcase: Dict[str, Any]) -> Dict[str, Any]:
        """提取测试环境信息"""
        env = {}
        
        # 从标题和名称中提取环境信息
        title = testcase.get('title', '').lower()
        test_name = testcase.get('test_name', '').lower()
        
        if 'park' in title or 'park' in test_name:
            env['parking_mode'] = True
        if 'drive' in title or 'drive' in test_name:
            env['driving_mode'] = True
        if 'ignition' in title or 'ignition' in test_name:
            env['ignition_state'] = 'on'
        
        return env
    
    def _extract_variables(self, testcase: Dict[str, Any]) -> List[str]:
        """提取测试中的变量"""
        variables = []
        
        # 从测试步骤中提取变量
        steps = testcase.get('steps', [])
        for step in steps:
            description = step.get('description', '').lower()
            if 'variable' in description or 'parameter' in description:
                # 简单的变量提取逻辑
                words = description.split()
                for word in words:
                    if word.startswith('TC_') or word.isupper():
                        variables.append(word)
        
        return list(set(variables))  # 去重
    
    def _extract_conditions(self, testcase: Dict[str, Any]) -> List[str]:
        """提取测试条件"""
        conditions = []
        
        # 从前置条件中提取
        preconditions = testcase.get('preconditions', [])
        conditions.extend(preconditions)
        
        # 从测试步骤中提取条件
        steps = testcase.get('steps', [])
        for step in steps:
            description = step.get('description', '')
            if 'when' in description.lower() or 'if' in description.lower():
                conditions.append(description)
        
        return conditions
    
    def _extract_system_state(self, testcase: Dict[str, Any]) -> Dict[str, Any]:
        """提取系统状态信息"""
        state = {
            'initial_state': 'unknown',
            'target_state': 'unknown',
            'transitions': []
        }
        
        # 从标题和描述中提取状态信息
        title = testcase.get('title', '').lower()
        
        if 'off' in title:
            state['initial_state'] = 'off'
            state['target_state'] = 'on'
        elif 'on' in title:
            state['initial_state'] = 'on'
            state['target_state'] = 'off'
        
        return state
    
    def _enrich_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """丰富上下文信息"""
        enriched = context.copy()
        
        # 添加测试类型
        enriched['test_type'] = self._determine_test_type(context)
        
        # 添加复杂度评估
        enriched['complexity'] = self._assess_complexity(context)
        
        # 添加风险级别
        enriched['risk_level'] = self._assess_risk(context)
        
        return enriched
    
    def _determine_test_type(self, context: Dict[str, Any]) -> str:
        """确定测试类型"""
        if context['environment'].get('parking_mode'):
            return 'parking_test'
        elif context['environment'].get('driving_mode'):
            return 'driving_test'
        else:
            return 'functional_test'
    
    def _assess_complexity(self, context: Dict[str, Any]) -> str:
        """评估测试复杂度"""
        variable_count = len(context['variables'])
        condition_count = len(context['conditions'])
        
        if variable_count > 3 or condition_count > 5:
            return 'high'
        elif variable_count > 1 or condition_count > 2:
            return 'medium'
        else:
            return 'low'
    
    def _assess_risk(self, context: Dict[str, Any]) -> str:
        """评估测试风险级别"""
        # 简化的风险评估
        return 'medium'
    
    def _fallback_context(self, testcase: Dict[str, Any]) -> Dict[str, Any]:
        """上下文分析的备用方案"""
        return {
            'environment': {'unknown': True},
            'variables': [],
            'conditions': [],
            'system_state': {'initial_state': 'unknown', 'target_state': 'unknown'},
            'test_type': 'unknown',
            'complexity': 'unknown',
            'risk_level': 'unknown'
        }