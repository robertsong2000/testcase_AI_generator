#!/usr/bin/env python3
"""
AI评估系统运行器
简化版命令行工具，快速运行AI评估
"""

import os
import sys
import time
from pathlib import Path
import argparse
import json
from ai_evaluator import CAPLAIEvaluator

def find_testcase_files(testcase_id: str) -> dict:
    """查找测试用例文件"""
    base_dir = Path(__file__).parent.parent
    
    # 手写测试用例
    handwritten = base_dir / "test_output" / f"testcase_id_{testcase_id}.can"
    
    # 生成的测试用例
    generated_files = list(base_dir.glob(f"test_output/qualification*{testcase_id}*.can"))
    generated = generated_files[0] if generated_files else None
    
    # 需求文档
    requirement_files = list(base_dir.glob(f"pdf_converter/testcases/qualification*{testcase_id}*.md"))
    requirement = requirement_files[0] if requirement_files else None
    
    return {
        'handwritten': handwritten,
        'generated': generated,
        'requirement': requirement
    }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='CAPL测试用例AI评估')
    parser.add_argument('testcase_id', help='测试用例ID，如 1336732')
    parser.add_argument('--model-type', choices=['ollama', 'openai'], default=None,
                       help='AI模型类型 (ollama 或 openai兼容接口)')
    parser.add_argument('--api-url', help='API服务地址')
    parser.add_argument('--model', help='使用的模型名称')
    parser.add_argument('--api-key', help='API密钥 (可选)')
    parser.add_argument('--temperature', type=float, default=0.05, 
                       help='模型温度参数，越低越一致 (默认: 0.05)')
    parser.add_argument('--consistent-mode', action='store_true',
                       help='启用一致性模式，确保评分稳定')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细模式，打印发送给AI的完整prompt内容')
    
    args = parser.parse_args()
    
    # 查找文件
    files = find_testcase_files(args.testcase_id)
    
    # 检查文件
    missing = []
    for key, file in files.items():
        if not file or not file.exists():
            missing.append(key)
    
    if missing:
        print(f"❌ 缺少文件: {', '.join(missing)}")
        print("找到的文件:")
        for key, file in files.items():
            if file and file.exists():
                print(f"  ✅ {key}: {file.name}")
            else:
                print(f"  ❌ {key}: 未找到")
        return
    
    # 初始化评估器
    evaluator = CAPLAIEvaluator(
        model_type=args.model_type,
        api_url=args.api_url,
        model_name=args.model,
        api_key=args.api_key,
        verbose=args.verbose
    )
    
    # 设置温度参数以提高一致性
    if args.temperature is not None:
        evaluator.temperature = args.temperature
    
    if args.consistent_mode:
        evaluator.temperature = 0.01  # 极低温度确保最大一致性
    
    # 显示配置信息
    print(f"🤖 开始AI评估测试用例 {args.testcase_id}...")
    print(f"手写文件: {files['handwritten'].name}")
    print(f"生成文件: {files['generated'].name}")
    print(f"需求文件: {files['requirement'].name}")
    print(f"AI配置: 使用{evaluator.model_type}模型 ({evaluator.model_name})")
    
    # 执行评估（带详细过程输出）
    print(f"\n🔄 开始AI分析过程...")
    print("-" * 50)
    
    start_time = time.time()
    
    print(f"\n🤖 调用AI模型进行分析...")
    print(f"   模型: {evaluator.model_name}")
    print(f"   温度: {evaluator.temperature}")
    
    result = evaluator.evaluate_testcase(
        args.testcase_id,
        str(files['handwritten']),
        str(files['generated']),
        str(files['requirement'])
    )
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 保存结果
    print(f"\n💾 保存评估结果...")
    evaluator.save_evaluation_result(result, args.testcase_id)
    print(f"   ✅ 结果已保存到 evaluation/results/ 目录")
    print(f"   ⏱️  总耗时: {elapsed_time:.1f}秒")
    
    # 计算加权综合评分
    weighted_score = (result.functional_completeness * 0.25 + 
                     result.requirement_coverage * 0.25 + 
                     result.test_logic_correctness * 0.20 + 
                     result.edge_case_handling * 0.15 + 
                     result.error_handling * 0.10 + 
                     result.code_quality * 0.05)
    
    # 获取评级
    def get_rating(score):
        if score >= 90:
            return "优秀"
        elif score >= 80:
            return "良好"
        elif score >= 70:
            return "一般"
        else:
            return "需改进"
    
    # 简要结果
    rating = get_rating(weighted_score)
    print(f"\n📊 AI评估完成!")
    print(f"=" * 50)
    print(f"功能完整性: {result.functional_completeness:.1f}/100")
    print(f"需求覆盖率: {result.requirement_coverage:.1f}/100")
    print(f"测试逻辑正确性: {result.test_logic_correctness:.1f}/100")
    print(f"边界条件处理: {result.edge_case_handling:.1f}/100")
    print(f"错误处理: {result.error_handling:.1f}/100")
    print(f"代码质量: {result.code_quality:.1f}/100")
    print(f"-" * 50)
    print(f"综合评分: {weighted_score:.1f}/100 ({rating})")
    print(f"=" * 50)
    
    if result.missing_functionalities:
        print(f"\n⚠️ 缺失功能点 ({len(result.missing_functionalities)}):")
        for func in result.missing_functionalities:
            print(f"  - {func}")
    
    if result.improvement_suggestions:
        print(f"\n💡 改进建议 ({len(result.improvement_suggestions)}):")
        for suggestion in result.improvement_suggestions:
            print(f"  - {suggestion}")

if __name__ == "__main__":
    main()