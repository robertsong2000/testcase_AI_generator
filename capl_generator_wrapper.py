#!/usr/bin/env python3
"""
CAPL生成器包装器
提供向后兼容的API接口，内部使用新的LangChain实现
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# 导入新的LangChain实现
from capl_generator_langchain import (
    CAPLGeneratorService, 
    CAPLGeneratorConfig,
    CAPLGenerator
)

# 向后兼容的API
class CAPLGeneratorWrapper:
    """向后兼容的包装器类"""
    
    def __init__(self):
        self.config = CAPLGeneratorConfig()
        self.service = CAPLGeneratorService(self.config)
    
    def send_file_to_ollama(self, file_path, **kwargs):
        """向后兼容的API"""
        try:
            # 将旧参数映射到新配置
            if 'api_type' in kwargs:
                self.config.api_type = kwargs['api_type']
            if 'api_url' in kwargs:
                self.config.api_url = kwargs['api_url']
            if 'model' in kwargs:
                self.config.model = kwargs['model']
            if 'output_dir' in kwargs:
                self.config.output_dir = Path(kwargs['output_dir'])
            
            # 处理文件
            result = self.service.process_file(file_path)
            
            if result["status"] == "success":
                return f"\n响应完成"
            else:
                return f"发生错误: {result['error']}"
                
        except Exception as e:
            return f"发生错误: {str(e)}"

def main():
    """向后兼容的主函数"""
    # 使用旧的参数解析方式
    parser = argparse.ArgumentParser(description='CAPL代码生成器 - 基于测试需求生成CAPL代码')
    parser.add_argument('file_path', help='输入的测试需求文件路径')
    parser.add_argument('--api-type', choices=['ollama', 'openai'], 
                       help='API类型 (ollama 或 openai)')
    parser.add_argument('--api-url', help='API服务地址')
    parser.add_argument('--model', help='使用的模型名称')
    parser.add_argument('--context-length', type=int, 
                       help='上下文长度 (tokens)')
    parser.add_argument('--max-tokens', type=int, 
                       help='最大输出tokens数')
    parser.add_argument('--temperature', type=float, 
                       help='生成温度 (0.0-1.0)')
    parser.add_argument('--top-p', type=float, 
                       help='top-p采样参数 (0.0-1.0)')
    parser.add_argument('--no-extract', action='store_true',
                       help='跳过CAPL代码提取步骤')
    parser.add_argument('--output-dir', help='指定测试结果保存的目录')
    parser.add_argument('--debug-prompt', action='store_true',
                       help='启用调试模式，打印完整的prompt信息')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.file_path):
        print(f"错误：文件不存在 - {args.file_path}")
        sys.exit(1)
    
    print(f"正在处理文件: {args.file_path}")
    
    # 创建包装器
    wrapper = CAPLGeneratorWrapper()
    
    # 调用兼容API
    kwargs = {}
    if args.api_type:
        kwargs['api_type'] = args.api_type
    if args.api_url:
        kwargs['api_url'] = args.api_url
    if args.model:
        kwargs['model'] = args.model
    if args.output_dir:
        kwargs['output_dir'] = args.output_dir
    
    result = wrapper.send_file_to_ollama(args.file_path, **kwargs)
    
    if result.startswith("发生错误"):
        print(result)
        sys.exit(1)
    else:
        print(result)

# 向后兼容的类定义
class CAPLGenerator:
    """向后兼容的类定义"""
    
    def __init__(self):
        self.wrapper = CAPLGeneratorWrapper()
    
    def generate_capl_code(self, requirement):
        """向后兼容的方法"""
        # 创建临时文件
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(requirement)
            tmp_file_path = tmp_file.name
        
        try:
            result = self.wrapper.send_file_to_ollama(tmp_file_path)
            
            # 读取生成的CAPL代码
            capl_dir = Path(__file__).parent / "capl"
            if capl_dir.exists():
                capl_files = list(capl_dir.glob("*.md"))
                if capl_files:
                    latest_file = max(capl_files, key=lambda x: x.stat().st_mtime)
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        return f.read()
            
            return "// 生成的CAPL代码将在这里显示"
            
        finally:
            # 清理临时文件
            import os
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

if __name__ == "__main__":
    main()