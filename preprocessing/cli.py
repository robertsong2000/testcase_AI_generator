#!/usr/bin/env python3
"""
预处理CLI工具
用于增强测试用例的CLI入口
"""

import argparse
import sys
from pathlib import Path

from preprocessing.core.config import EnhancerConfig
from preprocessing.core.enhancer import TestcaseLLMEnhancer
from preprocessing.utils.file_handler import FileHandler


def main():
    """CLI主函数"""
    parser = argparse.ArgumentParser(description="使用LLM+RAG增强测试用例")
    parser.add_argument("input", help="输入测试用例文件路径")
    parser.add_argument("--api-type", choices=["openai", "ollama", "azure"], 
                       default="ollama", help="LLM API类型")
    parser.add_argument("--api-url", help="LLM API URL")
    parser.add_argument("--model", help="模型名称")
    parser.add_argument("--suffix", default=".llm_enhanced", 
                       help="输出文件后缀")
    parser.add_argument("--step", type=int, help="指定增强的步骤索引")
    parser.add_argument("--verbose", action="store_true", 
                       help="显示详细输出")
    parser.add_argument("--enable-rag", action="store_true", default=True,
                       help="启用RAG知识库")
    parser.add_argument("--disable-rag", action="store_true",
                       help="禁用RAG知识库")
    
    args = parser.parse_args()
    
    # 创建配置
    config = EnhancerConfig()
    config.api_type = args.api_type
    if args.api_url:
        config.api_url = args.api_url
    if args.model:
        config.model = args.model
    config.enable_rag = not args.disable_rag
    
    # 创建文件处理器
    file_handler = FileHandler()
    
    # 检查输入文件
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 文件不存在: {args.input}")
        sys.exit(1)
    
    # 初始化增强器
    enhancer = TestcaseLLMEnhancer(config, verbose=args.verbose)
    
    try:
        # 增强测试用例
        enhanced = enhancer.enhance_testcase(str(input_path), args.step)
        
        if enhanced:
            # 生成输出路径
            output_path = file_handler.get_output_path(
                str(input_path), 
                args.suffix, 
                args.step
            )
            
            # 保存增强后的测试用例
            file_handler.save_json(enhanced, output_path)
            
            print(f"✅ 增强完成！")
            print(f"📁 输出文件: {output_path}")
            
            # 统计信息
            original_steps = len(file_handler.load_json(str(input_path)).get('steps', []))
            enhanced_steps = len(enhanced.get('steps', []))
            
            print(f"📊 统计信息:")
            print(f"   原始步骤: {original_steps}")
            print(f"   增强步骤: {enhanced_steps}")
            
        else:
            print("❌ 增强失败")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()