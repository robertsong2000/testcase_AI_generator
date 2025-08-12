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

from evaluation.evaluation_framework import CAPLEvaluator, create_benchmark_dataset, EvaluationResult
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

def load_test_cases_from_file(filepath):
    """从单个文件加载测试用例"""
    test_cases = []
    
    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        return test_cases
    
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
            requirement = f"测试用例: {os.path.basename(filepath).replace('.cin', '').replace('.can', '')}"
        
        test_cases.append({
            'test_id': os.path.basename(filepath).replace('.cin', '').replace('.can', ''),
            'requirement': requirement.strip(),
            'template_content': content,
            'source_file': filepath
        })
        
        print(f"从文件加载测试用例: {os.path.basename(filepath)}")
        
    except Exception as e:
        print(f"加载文件 {filepath} 失败: {e}")
    
    return test_cases

def run_current_evaluation(single_file=None):
    """运行当前版本的评估
    
    Args:
        single_file: 指定单个测试文件路径，如果为None则使用默认测试用例
    """
    print("=== CAPL测试用例生成器评估报告 ===")
    print(f"评估时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if single_file:
        print(f"指定测试文件: {single_file}")
        test_cases = load_test_cases_from_file(single_file)
    else:
        print("使用默认测试用例")
        test_cases = load_test_cases()
    
    if not test_cases:
        print("未找到测试用例，使用默认测试...")
        test_cases = [
            {
                'test_id': 'wiper_test',
                'requirement': '测试雨刷速度控制功能，验证不同速度设置',
                'template_content': '测试雨刷控制'
            }
        ]
    
    print(f"找到 {len(test_cases)} 个测试用例")

    # 创建评估器
    evaluator = CAPLEvaluator()
    
    # 创建测试用例生成器
    generator = CAPLGenerator()
    
    # 运行评估
    evaluation_data = []
    
    for case in test_cases:
        print(f"\n评估测试用例: {case['test_id']}")
        
        try:
            # 记录AI模型生成代码的时间
            start_generation_time = time.time()
            generated_code = generator.generate_capl_code(case['requirement'])
            ai_generation_time = time.time() - start_generation_time
            
            # 评估生成的代码（包括评估时间）
            result = evaluator.evaluate_single_case(
                requirement=case['requirement'],
                generated_code=generated_code,
                test_id=case['test_id']
            )
            
            # 计算总时间 = AI生成时间 + 评估时间
            total_generation_time = ai_generation_time + result.generation_time
            
            print(f"  AI模型生成时间: {ai_generation_time:.2f}秒")
            print(f"  本地评估时间: {result.generation_time:.2f}秒")
            print(f"  总生成时间: {total_generation_time:.2f}秒")
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
                'ai_generation_time': ai_generation_time,
                'evaluation_time': result.generation_time,
                'total_generation_time': total_generation_time
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
                'ai_generation_time': 0.0,
                'evaluation_time': 0.0,
                'total_generation_time': 0.0
            })
    
    # 生成总结报告
    if evaluation_data:
        # 重新计算包含AI生成时间的统计
        total_generation_times = [d['total_generation_time'] for d in evaluation_data]
        syntax_scores = [d['syntax_score'] for d in evaluation_data]
        functional_scores = [d['functional_score'] for d in evaluation_data]
        quality_scores = [d['quality_score'] for d in evaluation_data]
        error_counts = [d['error_count'] for d in evaluation_data]
        warning_counts = [d['warning_count'] for d in evaluation_data]
        
        summary = {
            'total_tests': len(evaluation_data),
            'avg_syntax_score': sum(syntax_scores) / len(syntax_scores) if syntax_scores else 0.0,
            'avg_functional_score': sum(functional_scores) / len(functional_scores) if functional_scores else 0.0,
            'avg_quality_score': sum(quality_scores) / len(quality_scores) if quality_scores else 0.0,
            'avg_generation_time': sum(total_generation_times) / len(total_generation_times) if total_generation_times else 0.0,
            'total_errors': sum(error_counts),
            'total_warnings': sum(warning_counts),
            'success_rate': sum(1 for s in syntax_scores if s > 0.8) / len(syntax_scores) if syntax_scores else 0.0
        }
        
        print("\n=== 评估总结 ===")
        print(f"总测试用例: {summary['total_tests']}")
        print(f"平均语法分数: {summary['avg_syntax_score']:.2f}")
        print(f"平均功能分数: {summary['avg_functional_score']:.2f}")
        print(f"平均质量分数: {summary['avg_quality_score']:.2f}")
        print(f"平均总生成时间: {summary['avg_generation_time']:.2f}秒")
        print(f"总错误数: {summary['total_errors']}")
        print(f"总警告数: {summary['total_warnings']}")
        print(f"成功率: {summary['success_rate']:.2%}")
        
        # 保存详细报告
        evaluator.results = []  # 清空现有结果
        for data in evaluation_data:
            from dataclasses import dataclass
            from datetime import datetime
            
            # 创建新的评估结果
            result = EvaluationResult(
                test_id=data['test_id'],
                requirement=data['requirement'],
                generated_code=data['generated_code'],
                syntax_score=data['syntax_score'],
                functional_score=data['functional_score'],
                quality_score=data['quality_score'],
                generation_time=data['total_generation_time'],  # 使用总时间
                error_count=data['error_count'],
                warning_count=data['warning_count'],
                timestamp=datetime.now().isoformat()
            )
            evaluator.results.append(result)
        
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
            'test_count': len(evaluation_data),
            'time_unit': 'seconds'
        }
        
        baseline_filename = os.path.join(logs_dir, 'performance_baseline.json')
        with open(baseline_filename, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
        
        # 同时保存一份当前基线到根目录用于对比
        current_baseline = os.path.join(os.path.dirname(__file__), 'performance_baseline.json')
        with open(current_baseline, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
        
        print(f"性能基线已保存: {baseline_filename}")
        print(f"当前基线已保存: {current_baseline}")
        
        return summary
    else:
        print("没有可用的评估数据")
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
    parser.add_argument('--file', type=str, 
                       help='指定单个测试文件进行评估')
    
    args = parser.parse_args()
    
    if args.create_benchmark:
        create_benchmark_dataset()
        return
    
    # 运行评估
    current_metrics = run_current_evaluation(single_file=args.file)
    
    if args.compare and current_metrics:
        compare_with_baseline(current_metrics)

if __name__ == "__main__":
    import argparse
    main()