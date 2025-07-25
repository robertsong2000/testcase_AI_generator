#!/usr/bin/env python3
import requests
import sys
import json
import os
from dotenv import load_dotenv
import ollama


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

        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()
       
        # 从配置文件读取提示词模板
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 尝试从配置文件读取提示词模板文件路径
        prompt_template_file = "prompt_template.txt"  # 默认值
        config_path = os.path.join(script_dir, "prompt_config.ini")
        
        if os.path.exists(config_path):
            try:
                import configparser
                config = configparser.ConfigParser()
                config.read(config_path, encoding='utf-8')
                if 'DEFAULT' in config and 'PROMPT_TEMPLATE_FILE' in config['DEFAULT']:
                    prompt_template_file = config['DEFAULT']['PROMPT_TEMPLATE_FILE']
            except Exception as e:
                print(f"警告: 读取配置文件失败，使用默认提示词模板: {str(e)}")
        
        prompt_template_path = os.path.join(script_dir, prompt_template_file)
        
        try:
            with open(prompt_template_path, "r", encoding="utf-8") as prompt_file:
                prompt_template = prompt_file.read()
        except FileNotFoundError:
            return f"错误: 找不到提示词模板文件 {prompt_template_path}"
        except Exception as e:
            return f"错误: 读取提示词模板文件失败: {str(e)}"

        if api_type == 'ollama':
            # 使用官方 ollama 库
            # 从API_URL中提取host地址
            ollama_host = api_url.replace('/api/generate', '').replace('http://', '').replace('https://', '')
            # 创建ollama客户端
            client = ollama.Client(host=f'http://{ollama_host}')
            
            stream = client.chat(
                model=os.getenv("OLLAMA_MODEL", "qwen3:30b-a3b"),
                messages=[
                    {"role": "system", "content": prompt_template},
                    {"role": "user", "content": file_content}
                ],
                stream=True,
                options={
                    "temperature": 0.2,
                    "top_p": 0.5,
                    "num_ctx": int(os.getenv("OLLAMA_CONTEXT_LENGTH", "8192")),  # 默认8192，可通过环境变量配置
                    "num_predict": int(os.getenv("OLLAMA_MAX_TOKENS", "4096")),  # 限制最大输出tokens，防止无限循环
                    "stop": ["```\n\n", "测试用例结束", "TestCase结束", "// End of test case"]  # 停止词，遇到这些词就停止生成
                }
            )
        else:  # openai 兼容的 API
            payload = {
                "model": os.getenv("OPENAI_MODEL", "qwen/qwen3-1.7b"),
                "messages": [
                    {"role": "system", "content": prompt_template},
                    {"role": "user", "content": file_content}
                ],
                "stream": True,
                "temperature": 0.2,
                "top_p": 0.5
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
            if api_type == 'ollama':
                # 处理 ollama 库的流式响应
                for chunk in stream:
                    if 'message' in chunk and 'content' in chunk['message']:
                        response_text = chunk['message']['content']
                        print(response_text, end='', flush=True)
                        capl_file.write(response_text)
            else:
                # 处理 openai 兼容 API 的流式响应
                for line in response.iter_lines():
                    if line:
                        try:
                            data = line.decode('utf-8').lstrip('data: ')
                            if data:
                                json_data = json.loads(data)
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
        print("请提供文件路径作为参数，例如：python capl_generator.py /path/to/your/file")
        sys.exit(1)
    file_path = sys.argv[1]
    result = send_file_to_ollama(file_path)
    if result.startswith("发生错误"):
        print(result)
    else:
        import subprocess
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 运行 CAPL 提取器
        subprocess.run(["python", os.path.join(script_dir, "capl_extractor.py")])
        
        # 运行循环检测器来检测和清理循环
        print("\n🔍 正在检测循环模式...")
        capl_dir = os.path.join(script_dir, "capl")
        if os.path.exists(capl_dir):
            for file in os.listdir(capl_dir):
                if file.endswith('.md'):
                    file_path = os.path.join(capl_dir, file)
                    subprocess.run(["python", os.path.join(script_dir, "loop_detector.py"), file_path, "--clean"])
        
        # 运行 CAPL 清理器来修复重复定义
        print("\n🔧 正在清理重复的变量定义...")
        subprocess.run(["python", os.path.join(script_dir, "capl_cleaner.py")])