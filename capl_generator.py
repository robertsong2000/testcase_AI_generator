#!/usr/bin/env python3
import requests
import sys
import json
import os
import argparse
from dotenv import load_dotenv
import ollama


def send_file_to_ollama(file_path, api_type=None, api_url=None, model=None, context_length=None, max_tokens=None, temperature=None, top_p=None, output_dir=None, debug_prompt=False):
    try:
        # 加载 .env 文件
        load_dotenv()
        
        # 命令行参数优先，其次环境变量，最后默认值
        api_type = api_type or os.getenv('API_TYPE', 'ollama')
        if api_type == 'ollama':
            default_url = 'http://localhost:11434'
        else:  # openai 兼容的 API
            default_url = 'http://localhost:1234/v1'
        
        api_url = api_url or os.getenv('API_URL', default_url)
        model = model or (os.getenv("OLLAMA_MODEL") if api_type == 'ollama' else os.getenv("OPENAI_MODEL"))
        context_length = context_length or int(os.getenv("OLLAMA_CONTEXT_LENGTH", "8192"))
        max_tokens = max_tokens or int(os.getenv("OLLAMA_MAX_TOKENS", "4096"))
        temperature = temperature or float(os.getenv("TEMPERATURE", "0.2"))
        top_p = top_p or float(os.getenv("TOP_P", "0.5"))

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
                
            # 检查是否存在示例代码文件，如果存在则读取并合并
            example_code_file = "example_code.txt"
            example_code_path = os.path.join(script_dir, example_code_file)
            if os.path.exists(example_code_path):
                with open(example_code_path, "r", encoding="utf-8") as example_file:
                    example_code_content = example_file.read()
                    # 将示例代码内容合并到提示词模板中
                    prompt_template = prompt_template.replace("示例代码已移至单独的文件 example_code.txt 中，以保护敏感代码内容。", example_code_content)
        except FileNotFoundError:
            return f"错误: 找不到提示词模板文件 {prompt_template_path}"
        except Exception as e:
            return f"错误: 读取提示词模板文件失败: {str(e)}"

        # 如果启用调试模式，打印完整的prompt信息
        if debug_prompt:
            print("=" * 50)
            print("完整的Prompt信息:")
            print("=" * 50)
            print(f"System Prompt:\n{prompt_template}\n")
            print(f"User Content:\n{file_content}\n")
            print("=" * 50)
            print("Prompt信息打印完成")
            print("=" * 50)

        if api_type == 'ollama':
            # 使用官方 ollama 库
            # 直接使用API_URL作为host地址
            ollama_host = api_url.rstrip('/')
            # 创建ollama客户端
            client = ollama.Client(host=ollama_host)
            
            # 根据api_type设置模型名称
            if api_type == 'ollama':
                actual_model = model or os.getenv("OLLAMA_MODEL", "qwen3:30b-a3b")
            else:
                actual_model = model or os.getenv("OPENAI_MODEL", "qwen/qwen3-1.7b")
                
            stream = client.chat(
                model=actual_model,
                messages=[
                    {"role": "system", "content": prompt_template},
                    {"role": "user", "content": file_content}
                ],
                stream=True,
                options={
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_ctx": context_length,
                    "num_predict": max_tokens
                }
            )
        else:  # openai 兼容的 API
            # 构建完整的API端点URL
            if api_url.endswith('/v1'):
                api_url = f"{api_url}/chat/completions"
            elif not api_url.endswith('/chat/completions'):
                api_url = f"{api_url.rstrip('/')}/chat/completions"
            
            # 根据api_type设置模型名称
            actual_model = model or os.getenv("OPENAI_MODEL", "qwen/qwen3-1.7b")
            
            payload = {
                "model": actual_model,
                "messages": [
                    {"role": "system", "content": prompt_template},
                    {"role": "user", "content": file_content}
                ],
                "stream": True,
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens
            }
            response = requests.post(api_url, json=payload, stream=True)
            response.raise_for_status()

        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 创建输出目录，支持自定义目录
        if output_dir:
            capl_dir = os.path.abspath(output_dir)
        else:
            capl_dir = os.path.join(script_dir, "capl")
        os.makedirs(capl_dir, exist_ok=True)
        
        # 生成对应的 capl 文件名
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        capl_file_path = os.path.join(capl_dir, f"{base_name}.md")
        
        with open(capl_file_path, "w", encoding="utf-8") as capl_file:
            if api_type == 'ollama':
                # 处理 ollama 库的流式响应
                think_started = False
                think_ended = False
                
                # 获取模型名称（从环境变量，避免在循环中判断）
                model_name = os.getenv("OLLAMA_MODEL", "qwen3:30b-a3b")
                is_gpt_oss = 'gpt-oss' in model_name.lower()
                print(f"模型名称: {model_name}, 是否为 gpt-oss: {is_gpt_oss}")
                for chunk in stream:
                    if 'message' in chunk:
                        message = chunk['message']
                        
                        if is_gpt_oss and 'thinking' in message and message['thinking'] is not None:
                            thinking_content = message['thinking']
                            if thinking_content and not think_ended:
                                if not think_started:
                                    print("<think>\n", end='', flush=True)
                                    capl_file.write("<think>\n")
                                    think_started = True
                                print(thinking_content, end='', flush=True)
                                capl_file.write(thinking_content)
                        
                        if 'content' in message and message['content']:
                            content = message['content']
                            if think_started and not think_ended:
                                print("</think>\n", end='', flush=True)
                                capl_file.write("</think>\n")
                                think_ended = True
                            print(content, end='', flush=True)
                            capl_file.write(content)
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
    except requests.exceptions.ConnectionError as e:
        return f"发生错误: 连接失败 - 请确保Ollama服务已启动 (运行 'ollama serve')"
    except requests.exceptions.Timeout as e:
        return f"发生错误: 请求超时 - 请检查网络连接和服务状态"
    except Exception as e:
        error_msg = str(e)
        if "Connection" in error_msg or "connect" in error_msg.lower():
            return f"发生错误: 连接失败 - 请确保Ollama服务已启动并正在监听正确的端口"
        elif "404" in error_msg:
            return f"发生错误: 模型未找到 - 请运行 'ollama run qwen3:30b-a3b' 加载模型"
        else:
            return f"发生错误: {error_msg}"

def main():
    import os
    import sys
    
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
    if args.api_type:
        print(f"API类型: {args.api_type}")
    if args.api_url:
        print(f"API地址: {args.api_url}")
    if args.model:
        print(f"模型: {args.model}")
    if args.context_length:
        print(f"上下文长度: {args.context_length}")
    if args.max_tokens:
        print(f"最大输出tokens: {args.max_tokens}")
    if args.output_dir:
        print(f"输出目录: {args.output_dir}")
    
    result = send_file_to_ollama(
        args.file_path,
        api_type=args.api_type,
        api_url=args.api_url,
        model=args.model,
        context_length=args.context_length,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        output_dir=args.output_dir,
        debug_prompt=args.debug_prompt
    )
    
    if result.startswith("发生错误") or result.startswith("错误:"):
        print(result)
        sys.exit(1)
    else:
        print(result)
        
        if not args.no_extract:
            import subprocess
            
            # 确定输出目录
            if args.output_dir:
                capl_dir = os.path.abspath(args.output_dir)
            else:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                capl_dir = os.path.join(script_dir, "capl")
            
            # 生成对应的文件名
            base_name = os.path.splitext(os.path.basename(args.file_path))[0]
            generated_md_file = os.path.join(capl_dir, f"{base_name}.md")
            
            # 运行 CAPL 提取器 - 只提取当前生成的文件
            if os.path.exists(generated_md_file):
                subprocess.run(["python", os.path.join(os.path.dirname(os.path.abspath(__file__)), "capl_extractor.py"), generated_md_file])
            else:
                print(f"警告：未找到生成的文件 {generated_md_file}")

if __name__ == "__main__":
    main()


class CAPLGenerator:
    """CAPL代码生成器类，用于评估框架"""
    
    def __init__(self):
        pass
    
    def generate_capl_code(self, requirement):
        """根据需求生成CAPL代码"""
        from capl_generator import send_file_to_ollama
        
        # 创建一个临时文件来存储需求
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cin', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(f"// {requirement}\n")
            tmp_file.write("// 测试用例需求\n")
            tmp_file.write("variables\n")
            tmp_file.write("{\n")
            tmp_file.write("  // 变量定义\n")
            tmp_file.write("}\n")
            tmp_file.write("\n")
            tmp_file.write("on start\n")
            tmp_file.write("{\n")
            tmp_file.write("  // 测试逻辑\n")
            tmp_file.write("}\n")
            tmp_file_path = tmp_file.name
        
        try:
            # 使用现有的send_file_to_ollama函数
            result = send_file_to_ollama(tmp_file_path)
            
            # 检查send_file_to_ollama的返回值
            if result.startswith("发生错误") or result.startswith("错误:"):
                # 提取错误信息
                error_msg = result.replace("发生错误: ", "").replace("错误: ", "")
                raise RuntimeError(f"AI模型调用失败: {error_msg}")
            
            # 读取生成的CAPL代码
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            capl_dir = os.path.join(script_dir, "capl")
            
            # 找到最新的生成的文件
            capl_files = []
            if os.path.exists(capl_dir):
                for f in os.listdir(capl_dir):
                    if f.endswith('.md'):
                        capl_files.append(os.path.join(capl_dir, f))
            
            if capl_files:
                latest_file = max(capl_files, key=os.path.getmtime)
                with open(latest_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查生成内容是否有效
                if not content.strip() or content.strip() == "// 生成的CAPL代码将在这里显示":
                    raise RuntimeError("AI模型未返回有效内容，可能服务未启动或模型未加载")
                    
                return content
            else:
                raise RuntimeError("未找到生成的CAPL文件，AI模型可能未成功调用")
                
        finally:
            # 清理临时文件
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)