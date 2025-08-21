#!/usr/bin/env python3
import ollama
import os

def test_thinking_display():
    """测试 ollama qwen3-coder:30b 是否显示 thinking 过程"""
    try:
        # 创建客户端
        client = ollama.Client(host='http://192.168.1.2:11434')
        
        model_name = 'qwen3-coder:30b'
        is_qwen3_coder = 'qwen3-coder' in model_name.lower()
        
        print(f"🧪 测试 ollama {model_name} thinking 过程...")
        print("=" * 60)
        
        # 发送一个简单的测试问题
        response = client.chat(
            model=model_name,
            messages=[{"role": "user", "content": "特朗普是马基雅维利主义者吗？"}],
            stream=True
        )
        
        print("📊 原始响应数据:")
        print("-" * 30)
        
        full_response = ""
        thinking_content = ""
        for chunk in response:
            if 'message' in chunk:
                if 'thinking' in chunk['message'] and chunk['message']['thinking'] is not None:
                    thinking_content += chunk['message']['thinking']
                    print(f"[Thinking] {chunk['message']['thinking']}", end='', flush=True)
                if 'content' in chunk['message'] and chunk['message']['content']:
                    content = chunk['message']['content']
                    full_response += content
                    ## print(content, end='', flush=True)
        
        print("\n" + "=" * 60)
        print("📋 完整响应:")
        print(full_response)
        
        # 打印收集到的推理内容
        if thinking_content:
            print(f"\n🧠 收集到的推理内容 ({len(thinking_content)} 字符):")
            print(thinking_content)
        else:
            print("\n💭 未收集到推理内容")
        
        # 检查是否包含 thinking 标签
        # qwen3-coder 模型不生成<think>标签，这是预期行为
        if '<think>' in full_response:
            print("\n✅ 检测到 thinking 标签!")
            start = full_response.find('think>') + 7
            end = full_response.find('</think>')
            thinking = full_response[start:end]
            print(f"🧠 Thinking 标签内容: {thinking}")
        else:
            if is_qwen3_coder:
                print("\n✅ 未检测到 thinking 标签 (qwen3-coder 模型预期行为)")
            else:
                print("\n❌ 未检测到 thinking 标签")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_thinking_display()