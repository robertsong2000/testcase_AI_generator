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
from capl_langchain.services.generator_service import CAPLGeneratorService
from capl_langchain.services.generator_service import CAPLGenerator
from capl_langchain.config.config import CAPLGeneratorConfig

# 向后兼容的API
class CAPLGeneratorWrapper:
    """向后兼容的包装器类"""
    
    def __init__(self):
        self.config = CAPLGeneratorConfig()
        self.service = CAPLGeneratorService(self.config)
    
    def send_file_to_ollama(self, file_path, **kwargs):
        """向后兼容的API，提供详细日志输出"""
        import time
        
        start_time = time.time()
        
        try:
            # 将旧参数映射到新配置
            if 'api_type' in kwargs:
                self.config.api_type = kwargs['api_type']
                print(f"   API类型: {kwargs['api_type']}")
            if 'api_url' in kwargs:
                self.config.api_url = kwargs['api_url']
                print(f"   API地址: {kwargs['api_url']}")
            if 'model' in kwargs:
                self.config.model = kwargs['model']
                print(f"   模型: {kwargs['model']}")
            if 'output_dir' in kwargs:
                self.config.output_dir = Path(kwargs['output_dir'])
                print(f"   输出目录: {kwargs['output_dir']}")
            
            print("正在初始化生成器...")
            
            # 处理文件
            result = self.service.process_file(file_path)
            
            generation_time = time.time() - start_time
            
            if result["status"] == "success":
                print("\n✅ CAPL代码生成成功")
                print(f"   输出文件: {result['file_path']}")
                print(f"   生成时间: {result['stats']['generation_time']}秒")
                print(f"   代码长度: {result['stats']['code_length']}字符")
                print(f"   估算token: {result['stats']['estimated_tokens']} tokens")
                print(f"   输出速率: {result['stats']['token_rate']} tokens/秒")
                return f"\n响应完成"
            else:
                print(f"❌ 生成失败: {result['error']}")
                return f"发生错误: {result['error']}"
                
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = str(e)
            print(f"❌ 处理失败: {error_msg}")
            if "Connection" in error_msg or "connect" in error_msg.lower():
                return f"发生错误: 连接失败 - 请确保Ollama服务已启动 (运行 'ollama serve')"
            elif "404" in error_msg:
                return f"发生错误: 模型未找到 - 请运行 'ollama run {self.config.model}' 加载模型"
            else:
                return f"发生错误: {error_msg}"

def main():
    """向后兼容的主函数，提供详细日志输出"""
    import subprocess
    import time
    
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
        print(f"❌ 错误：文件不存在 - {args.file_path}")
        sys.exit(1)
    
    print("=" * 50)
    print("CAPL代码生成器 - 包装器模式")
    print("=" * 50)
    print(f"📁 正在处理文件: {args.file_path}")
    
    # 显示参数信息
    if args.api_type:
        print(f"   API类型: {args.api_type}")
    if args.api_url:
        print(f"   API地址: {args.api_url}")
    if args.model:
        print(f"   模型: {args.model}")
    if args.context_length:
        print(f"   上下文长度: {args.context_length}")
    if args.max_tokens:
        print(f"   最大输出tokens: {args.max_tokens}")
    if args.temperature is not None:
        print(f"   生成温度: {args.temperature}")
    if args.top_p is not None:
        print(f"   top-p参数: {args.top_p}")
    if args.output_dir:
        print(f"   输出目录: {args.output_dir}")
    
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
        
        # 如果未跳过提取步骤，运行CAPL提取器
        if not args.no_extract:
            # 确定输出目录
            if args.output_dir:
                capl_dir = Path(args.output_dir).resolve()
            else:
                capl_dir = Path(__file__).parent / "capl"
            
            # 生成对应的文件名
            base_name = Path(args.file_path).stem
            generated_md_file = capl_dir / f"{base_name}.md"
            
            # 检查生成的文件是否存在
            if generated_md_file.exists():
                print(f"\n🔄 正在提取CAPL代码...")
                try:
                    subprocess.run([
                        "python", 
                        str(Path(__file__).parent / "capl_extractor.py"), 
                        str(generated_md_file)
                    ], check=True)
                    print("✅ CAPL代码提取完成")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️  CAPL代码提取失败: {e}")
            else:
                print(f"⚠️  未找到生成的文件 {generated_md_file}")

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