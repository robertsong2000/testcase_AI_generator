#!/usr/bin/env python3
import requests
import sys
import json
import os
from dotenv import load_dotenv


def send_file_to_ollama(file_path):
    try:
        # 加载 .env 文件
        load_dotenv()
        # 获取 API 类型和 URL
        api_type = os.getenv('API_TYPE', 'ollama')  # 可选值：ollama 或 openai
        if api_type == 'ollama':
            default_url = 'http://localhost:11434/api/generate'
        else:  # openai 兼容的 API
            default_url = 'http://localhost:1234/v1/chat/completions'
        
        api_url = os.getenv('API_URL', default_url)

        with open(file_path, "r") as file:
            file_content = file.read()
        # 定义提示模板
        prompt_template = """这是一个 CAN 测试用例，请根据以下内容生成符合 CAN 协议规范的 CAPL 代码。请遵循以下详细要求：

1. 代码结构：
   - 包含必要的变量定义（如报文变量、计时器、状态变量等）
   - 实现相关的事件处理函数（如 on message、on timer 等）
   - 编写完整的测试用例函数，包含测试步骤、期望结果和断言

2. 注释要求：
   - 为每个函数添加详细的文档注释，说明功能、参数和返回值
   - 为关键代码段添加行注释，解释实现逻辑
   - 标注测试用例的目的和预期结果
   - 所有注释必须使用英文编写

3. 代码质量：
   - 使用有意义的变量和函数名称
   - 避免硬编码常量，使用宏定义
   - 确保代码逻辑清晰，易于理解和维护

4. 兼容性：
   - 确保代码可在 CANoe 环境中直接编译和执行
   - 遵循 CAPL 语言的最新标准

内容如下："""

        if api_type == 'ollama':
            payload = {
                "model": os.getenv("OLLAMA_MODEL", "qwen3:30b-a3b"),
                "prompt": f"{prompt_template}\n{file_content}",
                "stream": True,
            }
        else:  # openai 兼容的 API
            payload = {
                "model": os.getenv("OPENAI_MODEL", "qwen/qwen3-1.7b"),
                "messages": [
                    {"role": "system", "content": prompt_template},
                    {"role": "user", "content": file_content}
                ],
                "stream": True,
                "temperature": 0.7
            }
        response = requests.post(api_url, json=payload, stream=True)
        response.raise_for_status()

        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 创建 capl 子目录在脚本所在目录下
        capl_dir = os.path.join(script_dir, "capl")
        os.makedirs(capl_dir, exist_ok=True)
        
        # 生成对应的 capl 文件名
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        capl_file_path = os.path.join(capl_dir, f"{base_name}.md")
        
        with open(capl_file_path, "w", encoding="utf-8") as capl_file:
            for line in response.iter_lines():
                if line:
                    try:
                        data = line.decode('utf-8').lstrip('data: ')
                        if data:
                            json_data = json.loads(data)
                            if api_type == 'ollama':
                                if 'response' in json_data:
                                    response_text = json_data['response']
                                    print(response_text, end='', flush=True)
                                    capl_file.write(response_text)
                            else:  # openai 兼容的 API
                                if 'choices' in json_data and len(json_data['choices']) > 0:
                                    if 'delta' in json_data['choices'][0] and 'content' in json_data['choices'][0]['delta']:
                                        response_text = json_data['choices'][0]['delta']['content']
                                        print(response_text, end='', flush=True)
                                        capl_file.write(response_text)
                    except Exception as e:
                        continue
        return "\n响应完成"
    except Exception as e:
        return f"发生错误: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请提供文件路径作为参数，例如：python ollama_file_processor.py /path/to/your/file")
        sys.exit(1)
    file_path = sys.argv[1]
    result = send_file_to_ollama(file_path)
    if result.startswith("发生错误"):
        print(result)
    else:
        import subprocess
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.run(["python", os.path.join(script_dir, "capl_extractor.py")])