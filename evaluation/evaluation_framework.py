#!/usr/bin/env python3
"""
CAPL测试用例生成器 - 评估框架
用于评估代码生成质量和模型性能
"""

import os
import json
import time
import subprocess
import re
import sys
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pandas as pd
except ImportError:
    pd = None
    print("警告: pandas未安装，部分功能将受限")

@dataclass
class EvaluationResult:
    """评估结果数据结构"""
    test_id: str
    requirement: str
    generated_code: str
    syntax_score: float
    functional_score: float
    quality_score: float
    generation_time: float
    error_count: int
    warning_count: int
    timestamp: str

class CAPLEvaluator:
    """CAPL代码评估器"""
    
    def __init__(self, capl_checker_path: str = None):
        if capl_checker_path is None:
            # 使用相对路径
            self.capl_checker_path = os.path.join(
                os.path.dirname(__file__), '..', 'capl_checker', 'capl_checker.py'
            )
        else:
            self.capl_checker_path = capl_checker_path
        
        self.results = []
        
    def evaluate_single_case(self, requirement: str, generated_code: str, 
                           test_id: str = None) -> EvaluationResult:
        """评估单个测试用例"""
        if test_id is None:
            test_id = f"test_{int(time.time())}"
            
        start_time = time.time()
        
        # 1. 语法检查
        syntax_score, errors, warnings = self._check_syntax(generated_code)
        
        # 2. 功能完整性评估
        functional_score = self._evaluate_functional_completeness(requirement, generated_code)
        
        # 3. 代码质量评估
        quality_score = self._evaluate_code_quality(generated_code)
        
        generation_time = time.time() - start_time
        
        result = EvaluationResult(
            test_id=test_id,
            requirement=requirement,
            generated_code=generated_code,
            syntax_score=syntax_score,
            functional_score=functional_score,
            quality_score=quality_score,
            generation_time=generation_time,
            error_count=len(errors),
            warning_count=len(warnings),
            timestamp=datetime.now().isoformat()
        )
        
        self.results.append(result)
        return result
    
    def _check_syntax(self, code: str) -> Tuple[float, List[str], List[str]]:
        """使用CAPL语法检查器检查语法"""
        # 临时保存代码到文件
        temp_file = f"temp_eval_{int(time.time())}.can"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # 运行CAPL语法检查器
            cmd = ["python", self.capl_checker_path, temp_file]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 解析输出
            errors = []
            warnings = []
            
            for line in result.stdout.split('\n'):
                if 'ERROR:' in line:
                    errors.append(line.strip())
                elif 'WARNING:' in line:
                    warnings.append(line.strip())
            
            # 计算语法分数
            syntax_score = max(0.0, 1.0 - (len(errors) * 0.1) - (len(warnings) * 0.05))
            return syntax_score, errors, warnings
            
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def _evaluate_functional_completeness(self, requirement: str, code: str) -> float:
        """评估功能完整性"""
        score = 0.0
        max_score = 1.0
        
        # 检查关键元素
        checks = [
            ('variables', self._count_variables(code)),
            ('testcases', self._count_testcases(code)),
            ('onstart', 'on start' in code.lower()),
            ('onmessage', 'on message' in code.lower()),
            ('output', 'output' in code.lower() or 'write' in code.lower())
        ]
        
        passed_checks = sum(1 for _, check in checks if check)
        return passed_checks / len(checks)
    
    def _evaluate_code_quality(self, code: str) -> float:
        """评估代码质量"""
        score = 0.5  # 基础分
        
        # 代码长度合理性
        lines = code.strip().split('\n')
        if 20 <= len(lines) <= 200:
            score += 0.2
        
        # 注释比例
        comment_lines = sum(1 for line in lines if '//' in line or '/*' in line)
        comment_ratio = comment_lines / len(lines) if lines else 0
        if 0.1 <= comment_ratio <= 0.3:
            score += 0.15
        
        # 命名规范
        if self._check_naming_conventions(code):
            score += 0.15
            
        return min(score, 1.0)
    
    def _count_variables(self, code: str) -> int:
        """统计变量定义数量"""
        variable_pattern = r'\b(int|float|char|byte|word|dword|qword)\s+\w+'
        return len(re.findall(variable_pattern, code, re.IGNORECASE))
    
    def _count_testcases(self, code: str) -> int:
        """统计测试用例数量"""
        testcase_pattern = r'testcase\s+\w+\s*\('
        return len(re.findall(testcase_pattern, code, re.IGNORECASE))
    
    def _check_naming_conventions(self, code: str) -> bool:
        """检查命名规范"""
        # 简单的命名规范检查
        camel_case_pattern = r'\b[a-z][a-zA-Z0-9]*\b'
        variables = re.findall(r'\b(int|float|char|byte|word|dword|qword)\s+(\w+)', code, re.IGNORECASE)
        
        for _, var_name in variables:
            if not re.match(camel_case_pattern, var_name):
                return False
        return True
    
    def batch_evaluate(self, test_cases: List[Dict[str, str]]) -> Any:
        """批量评估多个测试用例"""
        for case in test_cases:
            self.evaluate_single_case(
                requirement=case['requirement'],
                generated_code=case['generated_code'],
                test_id=case.get('test_id', None)
            )
        
        return self.get_summary_report()
    
    def get_summary_report(self) -> Any:
        """生成评估总结报告"""
        if not self.results:
            if pd is not None:
                return pd.DataFrame(), {}
            else:
                return [], {}
        
        if pd is not None:
            df = pd.DataFrame([vars(r) for r in self.results])
        else:
            # 不使用pandas的备选方案
            df = [vars(r) for r in self.results]
        
        # 计算统计信息
        syntax_scores = [r.syntax_score for r in self.results]
        functional_scores = [r.functional_score for r in self.results]
        quality_scores = [r.quality_score for r in self.results]
        generation_times = [r.generation_time for r in self.results]
        error_counts = [r.error_count for r in self.results]
        warning_counts = [r.warning_count for r in self.results]
        
        summary = {
            'total_tests': len(self.results),
            'avg_syntax_score': sum(syntax_scores) / len(syntax_scores) if syntax_scores else 0.0,
            'avg_functional_score': sum(functional_scores) / len(functional_scores) if functional_scores else 0.0,
            'avg_quality_score': sum(quality_scores) / len(quality_scores) if quality_scores else 0.0,
            'avg_generation_time': sum(generation_times) / len(generation_times) if generation_times else 0.0,
            'total_errors': sum(error_counts),
            'total_warnings': sum(warning_counts),
            'success_rate': sum(1 for s in syntax_scores if s > 0.8) / len(syntax_scores) if syntax_scores else 0.0
        }
        
        return df, summary
    
    def save_report(self, filename: str = None):
        """保存评估报告到logs目录"""
        # 确保logs目录存在
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        if filename is None:
            filename = f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 确保保存到logs目录
        if not os.path.isabs(filename):
            filename = os.path.join(logs_dir, filename)
        
        df, summary = self.get_summary_report()
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'detailed_results': [vars(r) for r in self.results]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return filename

def create_benchmark_dataset():
    """创建基准测试数据集"""
    benchmark_cases = [
        {
            'test_id': 'basic_signal_test',
            'requirement': '测试基本信号发送功能，验证CAN消息发送',
            'expected_elements': ['on start', 'output', 'message']
        },
        {
            'test_id': 'condition_check_test',
            'requirement': '测试条件判断功能，验证信号值检查',
            'expected_elements': ['if', 'else', 'condition']
        },
        {
            'test_id': 'timer_test',
            'requirement': '测试定时器功能，验证延时操作',
            'expected_elements': ['msTimer', 'setTimer', 'on timer']
        }
    ]
    
    # 保存基准测试数据集
    benchmark_file = os.path.join(os.path.dirname(__file__), 'benchmark_dataset.json')
    with open(benchmark_file, 'w', encoding='utf-8') as f:
        json.dump(benchmark_cases, f, indent=2, ensure_ascii=False)
    
    print(f"基准测试数据集已创建: {benchmark_file}")
    return benchmark_file

def main():
    """主函数 - 示例用法"""
    evaluator = CAPLEvaluator()
    
    # 示例测试
    sample_code = """
    /* 测试用例: 雨刷速度控制 */
    variables
    {
      int wiperSpeed;
      msTimer wiperTimer;
    }
    
    testcase TC_Wiper_Speed_Control()
    {
      wiperSpeed = 2;
      setTimer(wiperTimer, 1000);
    }
    
    on timer wiperTimer
    {
      output("Wiper speed test completed");
    }
    """
    
    result = evaluator.evaluate_single_case(
        requirement="测试雨刷速度控制功能",
        generated_code=sample_code,
        test_id="sample_test"
    )
    
    print(f"语法分数: {result.syntax_score}")
    print(f"功能分数: {result.functional_score}")
    print(f"质量分数: {result.quality_score}")
    
    # 保存报告
    evaluator.save_report()

if __name__ == "__main__":
    main()