#!/usr/bin/env python3
import os
import re
import sys

def extract_capl_from_file(md_file_path):
    """从指定的markdown文件中提取CAPL代码"""
    if not os.path.exists(md_file_path):
        print(f"错误：文件 {md_file_path} 不存在。")
        return False
    
    if not md_file_path.endswith(".md"):
        print(f"错误：文件 {md_file_path} 不是markdown文件。")
        return False
    
    try:
        with open(md_file_path, "r", encoding="utf-8") as md_file:
            content = md_file.read()
            
        # 使用正则表达式提取 capl 代码块
        capl_matches = re.findall(r"```capl\n(.*?)\n```", content, re.DOTALL)
        
        if capl_matches:
            # 获取文件所在目录
            file_dir = os.path.dirname(md_file_path)
            base_name = os.path.splitext(os.path.basename(md_file_path))[0]
            can_file_path = os.path.join(file_dir, f"{base_name}.can")
            
            # 将提取的 capl 代码写入 .can 文件
            with open(can_file_path, "w", encoding="utf-8") as can_file:
                for match in capl_matches:
                    can_file.write(match.strip() + "\n")
            
            print(f"✅ 已从 {md_file_path} 提取 CAPL 代码到 {can_file_path}")
            return True
        else:
            print(f"⚠️  警告：{md_file_path} 中未找到 CAPL 代码块。")
            return False
    except Exception as e:
        print(f"❌ 处理文件 {md_file_path} 时出错：{str(e)}")
        return False

def extract_all_capl_files():
    """提取capl目录下所有markdown文件中的CAPL代码"""
    # 获取 capl 目录路径
    capl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capl")
    
    # 确保 capl 目录存在
    if not os.path.exists(capl_dir):
        print(f"错误：capl 目录 {capl_dir} 不存在。")
        return False
    
    processed_count = 0
    success_count = 0
    
    # 遍历 capl 目录下的所有 md 文件
    for root, _, files in os.walk(capl_dir):
        for file in files:
            if file.endswith(".md"):
                md_file_path = os.path.join(root, file)
                processed_count += 1
                if extract_capl_from_file(md_file_path):
                    success_count += 1
    
    print(f"\n📊 处理完成：共处理 {processed_count} 个文件，成功提取 {success_count} 个文件")
    return success_count > 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 如果提供了文件路径参数，只处理指定文件
        file_path = sys.argv[1]
        extract_capl_from_file(file_path)
    else:
        # 如果没有提供参数，处理所有文件
        extract_all_capl_files()