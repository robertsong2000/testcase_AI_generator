#!/usr/bin/env python3
"""
CAPL测试用例生成器 - 评估执行脚本
用于运行完整的评估测试
"""

import os
import sys
import json
import time
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.evaluation_framework import CAPLEvaluator, create_benchmark_dataset
from capl_generator import CAPLGenerator

def load_test_cases():
    """加载测试用例"""
    test_cases = []
    
    # 从test目录加载测试需求
    test_dir = os.path.join(os.path.dirname(__file__), '..', 'test')
    if os.path.exists(test_dir):
        for filename in os.listdir(test_dir):
            if filename.endswith('.cin'):
                filepath = os.path.join(test_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # 提取需求描述
                    lines = content.split('\n')
                    requirement = ""
                    for line in lines[:10]:
                        if '//' in line:
                            requirement += line.strip('//').strip() + " "
                    
                    if not requirement:
                        requirement = f"测试用例: {filename.replace('.cin', '')}"
                    
                    test_cases.append({
                        'test_id': filename.replace('.cin', ''),
                        'requirement': requirement.strip(),
                        'template_content': content
                    })
                except Exception as e:
                    print(f"加载测试用例 {filename} 失败: {e}")
    
    return test_cases

def run_current_evaluation():
    """运行当前版本的评估"""
    print("=== CAPL测试用例生成器评估报告 ===")
    print(f"评估时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建评估器
    evaluator = CAPLEvaluator()
    
    # 创建测试用例生成器
    generator = CAPLGenerator()
    
    # 加载测试用例
    test_cases = load_test_cases()
    print(f"找到 {len(test_cases)} 个测试用例")
    
    if not test_cases:
        print("未找到测试用例，使用默认测试...")
        test_cases = [
            {
                'test_id': 'wiper_test',
                'requirement': '测试雨刷速度控制功能，验证不同速度设置',
                'template_content': '测试雨刷控制'
            }
        ]
    
    # 运行评估
    evaluation_data = []
    
    for case in test_cases[:5]:  # 限制前5个测试用例
        print(f"\n评估测试用例: {case['test_id']}")
        
        try:
            # 生成代码
            generated_code = generator.generate_capl_code(case['requirement'])
            
            # 评估生成的代码
            result = evaluator.evaluate_single_case(
                requirement=case['requirement'],
                generated_code=generated_code,
                test_id=case['test_id']
            )
            
            print(f"  语法分数: {result.syntax_score:.2f}")
            print(f"  功能分数: {result.functional_score:.2f}")
            print(f"  质量分数: {result.quality_score:.2f}")
            print(f"  错误数: {result.error_count}")
            print(f"  警告数: {result.warning_count}")
            
            evaluation_data.append({
                'test_id': case['test_id'],
                'requirement': case['requirement'],
                'generated_code': generated_code,
                'syntax_score': result.syntax_score,
                'functional_score': result.functional_score,
                'quality_score': result.quality_score,
                'error_count': result.error_count,
                'warning_count': result.warning_count,
                'generation_time': result.generation_time
            })
            
        except Exception as e:
            print(f"  评估失败: {str(e)}")
            evaluation_data.append({
                'test_id': case['test_id'],
                'requirement': case['requirement'],
                'error': str(e),
                'syntax_score': 0.0,
                'functional_score': 0.0,
                'quality_score': 0.0,
                'error_count': 1,
                'warning_count': 0,
                'generation_time': 0.0
            })
    
    # 生成总结报告
    if evaluation_data:
        df, summary = evaluator.get_summary_report()
        
        print("\n=== 评估总结 ===")
        print(f"总测试用例: {summary['total_tests']}")
        print(f"平均语法分数: {summary['avg_syntax_score']:.2f}")
        print(f"平均功能分数: {summary['avg_functional_score']:.2f}")
        print(f"平均质量分数: {summary['avg_quality_score']:.2f}")
        print(f"平均生成时间: {summary['avg_generation_time']:.2f}秒")
        print(f"总错误数: {summary['total_errors']}")
        print(f"总警告数: {summary['total_warnings']}")
        print(f"成功率: {summary['success_rate']:.2%}")
        
        # 保存详细报告
        report_filename = evaluator.save_report()
        print(f"\n详细报告已保存: {report_filename}")
        
        # 创建性能基线文件
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        baseline = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': {
                'avg_syntax_score': summary['avg_syntax_score'],
                'avg_functional_score': summary['avg_functional_score'],
                'avg_quality_score': summary['avg_quality_score'],
                'avg_generation_time': summary['avg_generation_time'],
                'success_rate': summary['success_rate']
            },
            'test_count': summary['total_tests']
        }
        
        # 使用时间戳命名性能基线文件
        baseline_filename = f"performance_baseline_{time.strftime('%Y%m%d_%H%M%S')}.json"
        baseline_path = os.path.join(logs_dir, baseline_filename)
        
        with open(baseline_path, 'w') as f:
            json.dump(baseline, f, indent=2)
        
        print(f"性能基线已保存: {baseline_path}")
        
        # 同时保存一份到根目录作为当前基线（用于对比）
        with open('performance_baseline.json', 'w') as f:
            json.dump(baseline, f, indent=2)
        
        return baseline
    
    return None

def compare_with_baseline(current_metrics):
    """与基线对比"""
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    
    # 查找最新的基线文件
    baseline_files = []
    if os.path.exists(logs_dir):
        for filename in os.listdir(logs_dir):
            if filename.startswith('performance_baseline_') and filename.endswith('.json'):
                baseline_files.append(os.path.join(logs_dir, filename))
    
    # 如果没有找到logs中的基线，尝试根目录
    if not baseline_files and os.path.exists('performance_baseline.json'):
        baseline_file = 'performance_baseline.json'
    elif baseline_files:
        # 使用最新的基线文件
        baseline_file = max(baseline_files, key=os.path.getctime)
    else:
        print("未找到基线数据，跳过对比")
        return
    
    with open(baseline_file, 'r') as f:
        baseline = json.load(f)
    
    print(f"\n=== 性能对比（对比文件: {os.path.basename(baseline_file)}）===")
    for metric, current_value in current_metrics['metrics'].items():
        baseline_value = baseline['metrics'][metric]
        improvement = ((current_value - baseline_value) / baseline_value) * 100 if baseline_value != 0 else 0
        
        status = "↑ 提升" if improvement > 0 else "↓ 下降" if improvement < 0 else "→ 持平"
        print(f"{metric}: {current_value:.3f} vs {baseline_value:.3f} ({improvement:+.1f}%) {status}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='CAPL测试用例生成器评估工具')
    parser.add_argument('--create-benchmark', action='store_true', 
                       help='创建基准测试数据集')
    parser.add_argument('--compare', action='store_true', 
                       help='与基线对比')
    
    args = parser.parse_args()
    
    if args.create_benchmark:
        create_benchmark_dataset()
        return
    
    # 运行评估
    current_metrics = run_current_evaluation()
    
    if args.compare and current_metrics:
        compare_with_baseline(current_metrics)

if __name__ == "__main__":
    import argparse
    main()