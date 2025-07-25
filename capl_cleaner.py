#!/usr/bin/env python3
"""
CAPL 代码清理工具
用于检测和修复生成的 CAPL 代码中的重复变量定义问题
"""

import re
import os
import sys

def clean_capl_code(file_path):
    """
    清理 CAPL 代码中的重复变量定义
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 提取 CAPL 代码块
        capl_pattern = r'```capl\s*\n(.*?)\n```'
        capl_matches = re.findall(capl_pattern, content, re.DOTALL)
        
        if not capl_matches:
            print(f"警告：在 {file_path} 中未找到 CAPL 代码块")
            return False
        
        capl_code = capl_matches[0]
        
        # 清理重复的变量定义
        cleaned_code = remove_duplicate_definitions(capl_code)
        
        # 替换原始内容
        new_content = content.replace(f'```capl\n{capl_code}\n```', f'```capl\n{cleaned_code}\n```')
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print(f"✅ 已清理 {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 清理 {file_path} 时出错: {e}")
        return False

def remove_duplicate_definitions(capl_code):
    """
    移除重复的变量和常量定义
    """
    lines = capl_code.split('\n')
    cleaned_lines = []
    defined_variables = set()
    defined_constants = set()
    
    for line in lines:
        stripped_line = line.strip()
        
        # 检测变量定义 (在 variables 块中)
        var_match = re.match(r'\s*(\w+)\s+(\w+)\s*;', stripped_line)
        if var_match:
            var_type, var_name = var_match.groups()
            if var_name in defined_variables:
                print(f"🔍 发现重复变量定义: {var_name}")
                continue  # 跳过重复定义
            defined_variables.add(var_name)
        
        # 检测常量定义 (k开头的常量)
        const_match = re.match(r'\s*(k\w+)\s*=\s*[^;]+;', stripped_line)
        if const_match:
            const_name = const_match.group(1)
            if const_name in defined_constants:
                print(f"🔍 发现重复常量定义: {const_name}")
                continue  # 跳过重复定义
            defined_constants.add(const_name)
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def clean_all_capl_files():
    """
    清理 capl 目录下的所有文件
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    capl_dir = os.path.join(script_dir, "capl")
    
    if not os.path.exists(capl_dir):
        print(f"❌ CAPL 目录不存在: {capl_dir}")
        return
    
    cleaned_count = 0
    total_count = 0
    
    for filename in os.listdir(capl_dir):
        if filename.endswith('.md'):
            file_path = os.path.join(capl_dir, filename)
            total_count += 1
            if clean_capl_code(file_path):
                cleaned_count += 1
    
    print(f"\n📊 清理完成: {cleaned_count}/{total_count} 个文件已处理")

def analyze_capl_code(file_path):
    """
    分析 CAPL 代码，报告重复定义情况
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 提取 CAPL 代码块
        capl_pattern = r'```capl\s*\n(.*?)\n```'
        capl_matches = re.findall(capl_pattern, content, re.DOTALL)
        
        if not capl_matches:
            print(f"警告：在 {file_path} 中未找到 CAPL 代码块")
            return
        
        capl_code = capl_matches[0]
        lines = capl_code.split('\n')
        
        variables = {}
        constants = {}
        
        for i, line in enumerate(lines, 1):
            stripped_line = line.strip()
            
            # 检测变量定义
            var_match = re.match(r'\s*(\w+)\s+(\w+)\s*;', stripped_line)
            if var_match:
                var_type, var_name = var_match.groups()
                if var_name in variables:
                    print(f"🔍 重复变量 '{var_name}': 行 {variables[var_name]} 和 行 {i}")
                else:
                    variables[var_name] = i
            
            # 检测常量定义
            const_match = re.match(r'\s*(k\w+)\s*=\s*[^;]+;', stripped_line)
            if const_match:
                const_name = const_match.group(1)
                if const_name in constants:
                    print(f"🔍 重复常量 '{const_name}': 行 {constants[const_name]} 和 行 {i}")
                else:
                    constants[const_name] = i
        
        print(f"📊 分析完成: 发现 {len(variables)} 个变量, {len(constants)} 个常量")
        
    except Exception as e:
        print(f"❌ 分析 {file_path} 时出错: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--analyze":
            if len(sys.argv) > 2:
                analyze_capl_code(sys.argv[2])
            else:
                print("请提供要分析的文件路径")
        else:
            # 清理指定文件
            clean_capl_code(sys.argv[1])
    else:
        # 清理所有文件
        clean_all_capl_files()