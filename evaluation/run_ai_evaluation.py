#!/usr/bin/env python3
"""
AI评估系统运行器
简化版命令行工具，快速运行AI评估
"""

import os
import sys
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
        api_key=args.api_key
    )
    
    # 显示配置信息
    print(f"🤖 开始AI评估测试用例 {args.testcase_id}...")
    print(f"手写文件: {files['handwritten'].name}")
    print(f"生成文件: {files['generated'].name}")
    print(f"需求文件: {files['requirement'].name}")
    print(f"AI配置: 使用{evaluator.model_type}模型 ({evaluator.model_name})")
    
    # 执行评估
    result = evaluator.evaluate_testcase(
        args.testcase_id,
        str(files['handwritten']),
        str(files['generated']),
        str(files['requirement'])
    )
    
    # 保存并显示结果
    evaluator.save_evaluation_result(result, args.testcase_id)
    
    # 计算加权综合评分
    weighted_score = (result.functional_completeness * 0.25 + 
                     result.requirement_coverage * 0.25 + 
                     result.test_logic_correctness * 0.20 + 
                     result.edge_case_handling * 0.15 + 
                     result.error_handling * 0.10 + 
                     result.code_quality * 0.05)
    
    # 简要结果
    print(f"\n📊 AI评估完成!")
    print(f"=" * 40)
    print(f"功能完整性: {result.functional_completeness:.1f}/100")
    print(f"需求覆盖率: {result.requirement_coverage:.1f}/100")
    print(f"测试逻辑正确性: {result.test_logic_correctness:.1f}/100")
    print(f"边界条件处理: {result.edge_case_handling:.1f}/100")
    print(f"错误处理: {result.error_handling:.1f}/100")
    print(f"代码质量: {result.code_quality:.1f}/100")
    print(f"综合评分: {weighted_score:.1f}/100")
    print(f"=" * 40)
    
    if result.missing_functionalities:
        print(f"\n⚠️ 缺失功能点 ({len(result.missing_functionalities)}):")
        for func in result.missing_functionalities[:3]:
            print(f"  - {func}")
    
    if result.improvement_suggestions:
        print(f"\n💡 主要改进建议 ({len(result.improvement_suggestions)}):")
        for suggestion in result.improvement_suggestions[:3]:
            print(f"  - {suggestion}")

if __name__ == "__main__":
    main()