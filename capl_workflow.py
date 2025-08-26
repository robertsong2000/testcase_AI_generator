#!/usr/bin/env python3
"""
CAPL 工作流程脚本
集成代码生成、清理和语法检查的完整工作流程
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """运行命令并处理错误"""
    print(f"正在执行: {description}")
    print(f"命令: {' '.join(command)}")
    print("-" * 40)
    
    try:
        # 使用 Popen 来实现实时输出
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 实时读取并输出
        output_lines = []
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # 只去除行尾换行符，保留缩进
                print(output.rstrip('\n\r'))
                output_lines.append(output)
        
        # 等待进程完成
        return_code = process.poll()
        
        if return_code == 0:
            print("-" * 40)
            print(f"✅ {description} 完成")
            return True
        else:
            print("-" * 40)
            print(f"❌ {description} 失败 (退出码: {return_code})")
            return False
            
    except FileNotFoundError:
        print(f"❌ 错误: 找不到命令 {command[0]}")
        return False
    except Exception as e:
        print(f"❌ 执行命令时发生错误: {str(e)}")
        return False

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if not os.path.exists(file_path):
        print(f"错误: {description} 不存在: {file_path}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description='CAPL 完整工作流程')
    parser.add_argument('input_file', help='输入文件路径')
    parser.add_argument('--skip-generation', action='store_true', 
                       help='跳过代码生成步骤，直接处理现有的 CAPL 文件')
    parser.add_argument('--skip-cleaning', action='store_true',
                       help='跳过代码清理步骤')
    parser.add_argument('--skip-checking', action='store_true',
                       help='跳过语法检查步骤')
    parser.add_argument('--checker-format', default='txt', 
                       choices=['txt', 'xml', 'json'],
                       help='语法检查器输出格式')
    parser.add_argument('--output-dir', default='capl',
                       help='输出目录（默认: capl）')
    parser.add_argument('--use-langchain', action='store_true',
                       help='使用LangChain模式生成代码')
    parser.add_argument('--disable-rag', action='store_true',
                       help='在LangChain模式下禁用RAG')
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not check_file_exists(args.input_file, "输入文件"):
        return 1
    
    input_path = Path(args.input_file)
    output_dir = Path(args.output_dir)
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True)
    
    # 步骤1: 生成 CAPL 代码
    if not args.skip_generation:
        print("\n" + "="*50)
        print("步骤 1: 生成 CAPL 代码")
        print("="*50)
        
        if args.use_langchain:
            # 使用LangChain模式生成代码
            command = [sys.executable, 'capl_generator_langchain.py', str(input_path)]
            if args.disable_rag:
                command.append('--disable-rag')
            if args.output_dir:
                command.extend(['--output', str(args.output_dir)])
        else:
            # 使用默认模式生成代码
            command = [sys.executable, 'capl_generator.py', str(input_path)]
        
        if not run_command(command, "CAPL 代码生成"):
            print("❌ 代码生成失败，停止执行后续步骤")
            return 1
    
    # 查找生成的 CAPL 文件
    capl_files = []
    if output_dir.exists():
        # 只查找与输入需求文件对应的 CAPL 文件
        input_stem = input_path.stem
        capl_files = list(output_dir.glob(f"{input_stem}*.can"))
        if not capl_files:
            # 也检查 .md 文件（如果生成器输出为 markdown）
            md_files = list(output_dir.glob(f"{input_stem}*.md"))
            if md_files:
                print(f"发现 {len(md_files)} 个 Markdown 文件，但需要 .can 文件进行语法检查")
    
    # 如果使用LangChain模式，可能生成的文件在不同的目录结构中
    if args.use_langchain and not capl_files:
        # LangChain模式可能直接在output_dir中生成.can文件
        input_stem = input_path.stem
        langchain_capl_files = list(Path(args.output_dir).glob(f"{input_stem}*.can"))
        if langchain_capl_files:
            capl_files = langchain_capl_files
    
    if not capl_files and not args.skip_generation:
        print("❌ 未找到生成的 CAPL 文件，停止执行")
        return 1
    
    # 步骤2: 清理代码（如果有 CAPL 文件）
    if capl_files and not args.skip_cleaning:
        print("\n" + "="*50)
        print("步骤 2: 清理 CAPL 代码")
        print("="*50)
        
        for capl_file in capl_files:
            print(f"\n清理文件: {capl_file}")
            
            # 运行代码清理器
            if not run_command([
                sys.executable, 'capl_cleaner.py', str(capl_file)
            ], f"代码清理 - {capl_file.name}"):
                print(f"❌ 代码清理失败: {capl_file.name}，停止执行后续步骤")
                return 1
    
    # 步骤3: 语法检查
    if capl_files and not args.skip_checking:
        print("\n" + "="*50)
        print("步骤 3: CAPL 语法检查")
        print("="*50)
        
        # 检查 capl_checker 是否存在
        checker_path = Path("capl_checker/capl_checker.py")
        if not check_file_exists(checker_path, "CAPL 语法检查器"):
            print("❌ CAPL 语法检查器不存在，停止执行")
            print("提示: 请确保已初始化子模块: git submodule update --init --recursive")
            return 1
        
        for capl_file in capl_files:
            print(f"\n检查文件: {capl_file}")
            
            # 生成检查报告文件名
            report_file = output_dir / f"{capl_file.stem}_check_report.{args.checker_format}"
            
            command = [
                sys.executable, str(checker_path),
                '--format', args.checker_format,
                '--output', str(report_file),
                str(capl_file)
            ]
            
            if run_command(command, f"语法检查 - {capl_file.name}"):
                print(f"检查报告已保存到: {report_file}")
            else:
                print(f"❌ 语法检查失败: {capl_file.name}，停止执行后续步骤")
                return 1
    
    # 总结
    print("\n" + "="*50)
    print("工作流程完成")
    print("="*50)
    
    print("✅ 所有步骤都成功完成")
    if capl_files:
        print(f"\n生成的文件:")
        for capl_file in capl_files:
            print(f"  - CAPL 代码: {capl_file}")
            
            # 列出相关的报告文件
            for fmt in ['text', 'xml', 'json']:
                report_file = output_dir / f"{capl_file.stem}_check_report.{fmt}"
                if report_file.exists():
                    print(f"  - 检查报告 ({fmt}): {report_file}")
    return 0

if __name__ == "__main__":
    sys.exit(main())