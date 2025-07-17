#!/usr/bin/env python3
import os
import re

# 获取 capl 目录路径
capl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capl")

# 确保 capl 目录存在
if not os.path.exists(capl_dir):
    print(f"错误：capl 目录 {capl_dir} 不存在。")
    exit(1)

# 遍历 capl 目录下的所有 md 文件
for root, _, files in os.walk(capl_dir):
    for file in files:
        if file.endswith(".md"):
            md_file_path = os.path.join(root, file)
            try:
                with open(md_file_path, "r", encoding="utf-8") as md_file:
                    content = md_file.read()
                    
                # 使用正则表达式提取 capl 代码块
                capl_matches = re.findall(r"```capl\n(.*?)\n```", content, re.DOTALL)
                
                if capl_matches:
                    # 生成对应的 .can 文件路径
                    base_name = os.path.splitext(file)[0]
                    can_file_path = os.path.join(capl_dir, f"{base_name}.can")
                    
                    # 将提取的 capl 代码写入 .can 文件
                    with open(can_file_path, "w", encoding="utf-8") as can_file:
                        for match in capl_matches:
                            can_file.write(match.strip() + "\n")
                    
                    print(f"已从 {md_file_path} 提取 CAPL 代码到 {can_file_path}")
                else:
                    print(f"警告：{md_file_path} 中未找到 CAPL 代码块。")
            except Exception as e:
                print(f"处理文件 {md_file_path} 时出错：{str(e)}")