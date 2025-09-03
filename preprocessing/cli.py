#!/usr/bin/env python3
"""
测试用例增强CLI工具 - 双提示词精简版
仅包含测试用例总体分析和步骤描述增强功能
"""

import argparse
import json
import sys
from pathlib import Path

from preprocessing.core.config import EnhancerConfig
from preprocessing.core.enhancer import TestcaseLLMEnhancer


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="测试用例增强器 - 双提示词版本\n"
                   "功能：\n"
                   "1. 总体分析：一次性调用LLM分析整个测试用例核心目的\n"
                   "2. 步骤增强：对每个测试步骤调用LLM增强描述",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "input_file",
        help="输入的测试用例JSON文件路径"
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        default="ollama",
        help="使用的模型类型 (default: ollama)"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="显示详细处理信息"
    )
    
    parser.add_argument(
        "--suffix", 
        type=str, 
        default=".enhanced",
        help="输出文件后缀 (default: .enhanced)"
    )
    
    parser.add_argument(
        "--step", 
        type=int,
        help="指定增强的步骤索引（从1开始），不指定则增强整个测试用例"
    )
    
    args = parser.parse_args()
    
    # 验证输入文件
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ 错误: 文件 {input_path} 不存在")
        return 1
    
    # 创建配置
    config = EnhancerConfig()
    config.model_type = args.model
    config.enable_rag = False  # 禁用RAG功能
    
    # 创建增强器
    enhancer = TestcaseLLMEnhancer(config, verbose=args.verbose)
    
    # 增强测试用例
    try:
        enhanced_data = enhancer.enhance_testcase(str(input_path), args.step)
        
        if enhanced_data is None:
            print("❌ 增强失败")
            return 1
        
        # 生成输出路径
        if args.step:
            output_path = input_path.with_suffix(f"{args.suffix}_step_{args.step}.json")
        else:
            output_path = input_path.with_suffix(f"{args.suffix}.json")
        
        # 保存增强结果
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
        
        # 显示统计信息
        if args.step:
            print(f"✅ 步骤{args.step}增强完成")
            print(f"📁 输出文件: {output_path}")
        else:
            total_steps = len(enhanced_data.get('steps', []))
            enhanced_steps = sum(1 for step in enhanced_data.get('steps', []) 
                             if 'original_description' in step)
            
            print(f"✅ 测试用例增强完成")
            print(f"📊 总步骤数: {total_steps}")
            print(f"🔄 已增强步骤: {enhanced_steps}")
            print(f"📁 输出文件: {output_path}")
        
        # 显示增强对比（verbose模式）
        if args.verbose:
            if args.step:
                # 显示单个步骤的增强
                step = enhanced_data.get('steps', [None])[0]
                if step and 'original_description' in step:
                    print(f"\n📝 步骤{args.step}增强对比:")
                    print(f"原始: {step.get('original_description', '无原始描述')}")
                    print(f"增强: {step.get('description', '')}")
            else:
                # 显示总体分析结果
                new_purpose = enhanced_data.get('purpose', '')
                print(f"\n🎯 测试用例目的分析:")
                print(f"增强后: {new_purpose}")
                
                # 显示前3个步骤的增强对比
                steps = enhanced_data.get('steps', [])
                for i, step in enumerate(steps[:3]):
                    if 'original_description' in step:
                        print(f"\n📝 步骤{i+1}增强对比:")
                        print(f"原始: {step.get('original_description', '无原始描述')}")
                        print(f"增强: {step.get('description', '')}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())