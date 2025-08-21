from ollama import Client
import json
import os
from dotenv import load_dotenv

def test_ollama_connection():
    """测试 Ollama 连接和基本对话功能"""
    try:
        # 加载环境变量
        load_dotenv()
        
        # 获取配置信息
        api_url = os.getenv('API_URL', 'http://localhost:11434')
        model_name = os.getenv('MODEL_NAME', 'qwen3:1.7b')
        
        # 打印当前配置
        print("=== 当前配置信息 ===")
        print(f"API URL: {api_url}")
        print(f"Model: {model_name}")
        print("=" * 30)
        
        # 创建客户端
        client = Client(host=api_url)
        
        # 发送简单的测试消息
        response = client.chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': 'Why is the sky blue?',
            },
        ])
        
        # 打印响应
        print("Response:", response['message']['content'])
        return True
        
    except Exception as e:
        print(f"连接失败: {e}")
        return False

def test_ollama_stream():
    """测试 Ollama 流式响应"""
    try:
        # 加载环境变量
        load_dotenv()
        
        # 获取配置信息
        api_url = os.getenv('API_URL', 'http://localhost:11434')
        model_name = os.getenv('MODEL_NAME', 'qwen3:1.7b')
        
        # 打印当前配置
        print("=== 流式测试配置 ===")
        print(f"API URL: {api_url}")
        print(f"Model: {model_name}")
        print("=" * 30)
        
        client = Client(host=api_url)
        
        stream = client.chat(
            model=model_name,
            messages=[
                {
                    'role': 'system',
                    'content': '你是一个有用的助手，请用日语回答。'
                },
                {
                    'role': 'user',
                    'content': '请简单介绍一下人工智能。'
                }
            ],
            stream=True
        )
        
        print("流式响应:")
        for chunk in stream:
            if 'message' in chunk and 'content' in chunk['message']:
                print(chunk['message']['content'], end='', flush=True)
        print("\n")
        return True
        
    except Exception as e:
        print(f"流式响应测试失败: {e}")
        return False

if __name__ == "__main__":
    ##print("=== Ollama 连接测试 ===")
    ##test_ollama_connection()
    
    print("\n=== Ollama 流式响应测试 ===")
    test_ollama_stream()