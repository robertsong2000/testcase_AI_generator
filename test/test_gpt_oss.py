#!/usr/bin/env python3
import ollama
import time
import sys

def test_gpt_oss_thinking():
    """测试 gpt-oss:latest 的 thinking 提取"""
    
    client = ollama.Client(host='http://192.168.1.2:11434')
    
    print("🧪 测试 gpt-oss:latest 的 thinking 提取...")
    print("=" * 60)
    
    response = client.chat(
        model='gpt-oss:latest',
        messages=[{"role": "user", "content": "写一首七言绝句"}],
        stream=True
    )
    
    full_response = ""
    thinking_content = ""
    final_content = ""
    
    print("📨 开始接收响应...")
    
    for chunk in response:
        # 检查是否有 thinking 字段
        if hasattr(chunk, 'message') and hasattr(chunk.message, 'thinking'):
            thinking = chunk.message.thinking
            content = chunk.message.content
            
            # 收集 thinking 内容
            if thinking is not None:
                thinking_content += str(thinking)
                print(thinking, end='', flush=True)
            
            # 收集最终内容
            if content is not None:
                final_content += str(content)
                
                # 当开始收到最终内容时，结束 thinking 显示
                if final_content.strip() and thinking_content:
                    print("\n" + "=" * 30)
                    print("✨ 最终响应:")
                    print("-" * 30)
                    
                if content:
                    print(content, end='', flush=True)
        else:
            # 兼容旧格式
            if hasattr(chunk, 'message') and hasattr(chunk.message, 'content'):
                content = chunk.message.content
                if content:
                    final_content += content
                    print(content, end='', flush=True)
    
    print("\n" + "=" * 60)
    print("📊 结果统计:")
    print(f"Thinking 长度: {len(thinking_content)} 字符")
    print(f"最终内容长度: {len(final_content)} 字符")
    
    if thinking_content:
        print(f"\n🧠 完整的 thinking 内容:")
        print(thinking_content)
    
    return {
        'thinking': thinking_content,
        'final': final_content
    }

if __name__ == "__main__":
    result1 = test_gpt_oss_thinking()
