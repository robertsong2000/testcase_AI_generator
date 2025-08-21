#!/usr/bin/env python3
import ollama
import json

def debug_thinking_format():
    """调试 gpt-oss:latest 的 thinking 格式"""
    
    client = ollama.Client(host='http://192.168.1.2:11434')
    
    print("🔍 调试 gpt-oss:latest 的 thinking 格式...")
    print("=" * 60)
    
    try:
        # 测试流式响应
        response = client.chat(
            model='gpt-oss:latest',
            messages=[{"role": "user", "content": "写一首七言绝句"}],
            stream=True
        )
        
        print("🌊 gpt-oss:latest 流式响应:")
        thinking_found = False
        
        for i, chunk in enumerate(response):
            print(f"\n📦 块 {i+1}:")
            
            # 安全地访问内容
            if hasattr(chunk, 'message') and hasattr(chunk.message, 'content'):
                content = chunk.message.content
                print(f"内容: {repr(content)}")
                
                # 检测 thinking
                if 'thinking' in str(chunk).lower() or '思考' in str(content).lower():
                    thinking_found = True
                    print("🎯 发现 thinking!")
            
            # 打印原始对象属性
            print(f"原始: {chunk}")
            
            if i >= 5:  # 限制输出
                break
                
        return thinking_found
                
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_raw_stream():
    """测试原始流式输出"""
    
    client = ollama.Client(host='http://192.168.1.2:11434')
    
    print("\n🔍 原始流式输出测试...")
    print("=" * 60)
    
    try:
        response = client.chat(
            model='qwen3:1.7b',
            messages=[{"role": "user", "content": "写一首七言绝句"}],
            stream=True
        )
        
        print("📨 开始接收流...")
        for chunk in response:
            print(f"🔍 {repr(chunk)}")
            
    except Exception as e:
        print(f"❌ 流式错误: {e}")

if __name__ == "__main__":
    debug_thinking_format()
    test_raw_stream()