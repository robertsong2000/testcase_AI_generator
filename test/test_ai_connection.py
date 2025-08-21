#!/usr/bin/env python3
"""
测试AI模型连接状态的脚本
用于验证大模型调用是否正常
"""

import sys
import os
import requests
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from capl_generator import CAPLGenerator

def test_ollama_connection():
    """测试Ollama连接状态"""
    print("=== 测试AI模型连接状态 ===")
    
    try:
        # 测试Ollama API连接
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        api_type = os.getenv('API_TYPE', 'ollama')
        if api_type == 'ollama':
            api_url = os.getenv('API_URL', 'http://localhost:11434')
            test_url = f"{api_url.rstrip('/')}/api/tags"
        else:
            api_url = os.getenv('API_URL', 'http://localhost:1234/v1')
            test_url = f"{api_url.rstrip('/')}/chat/completions"
        
        print(f"测试连接: {test_url}")
        
        try:
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                print("✅ API服务连接正常")
                if api_type == 'ollama':
                    try:
                        data = response.json()
                        models = data.get('models', [])
                        if models:
                            print(f"✅ 已加载的模型: {[m.get('name', 'unknown') for m in models]}")
                        else:
                            print("⚠️  未检测到已加载的模型")
                            print("   请运行: ollama run qwen3:30b-a3b")
                    except:
                        print("✅ Ollama服务响应正常")
            else:
                print(f"❌ API服务响应异常: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到AI服务")
            print("   请确保运行: ollama serve")
            return False
        except requests.exceptions.Timeout:
            print("❌ 连接超时")
            print("   请检查服务状态和网络连接")
            return False
        
        # 测试实际的代码生成
        print("\n=== 测试代码生成功能 ===")
        generator = CAPLGenerator()
        
        start_time = time.time()
        try:
            test_code = generator.generate_capl_code("测试雨刷控制功能")
            generation_time = time.time() - start_time
            
            if generation_time > 0.01 and test_code.strip() and "// 生成的CAPL代码将在这里显示" not in test_code:
                print(f"✅ AI模型调用成功")
                print(f"   生成时间: {generation_time:.2f}秒")
                print(f"   代码长度: {len(test_code)}字符")
                return True
            else:
                print(f"❌ AI模型调用失败")
                print(f"   生成时间: {generation_time:.2f}秒")
                print(f"   代码长度: {len(test_code)}字符")
                return False
                
        except Exception as e:
            print(f"❌ 代码生成失败: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def print_usage_instructions():
    """打印使用说明"""
    print("\n=== 使用说明 ===")
    print("1. 启动Ollama服务:")
    print("   ollama serve")
    print("2. 加载模型:")
    print("   ollama run qwen3:30b-a3b")
    print("3. 检查服务状态:")
    print("   curl http://localhost:11434/api/tags")
    print("4. 运行评估:")
    print("   python evaluation/run_evaluation.py")

if __name__ == "__main__":
    success = test_ollama_connection()
    
    if not success:
        print_usage_instructions()
        sys.exit(1)
    else:
        print("\n✅ 所有测试通过，可以运行评估程序")
        sys.exit(0)