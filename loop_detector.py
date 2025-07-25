#!/usr/bin/env python3
"""
循环检测器 - 检测和处理CAPL代码生成中的重复循环
"""
import re
import sys
import os
from collections import Counter, deque

class LoopDetector:
    def __init__(self, max_repetitions=3, window_size=10):
        """
        初始化循环检测器
        
        Args:
            max_repetitions: 允许的最大重复次数
            window_size: 检测窗口大小
        """
        self.max_repetitions = max_repetitions
        self.window_size = window_size
        self.step_history = deque(maxlen=window_size)
        self.pattern_counter = Counter()
        
    def detect_step_loop(self, content):
        """
        检测测试步骤中的循环模式
        
        Args:
            content: 要检测的内容
            
        Returns:
            dict: 检测结果
        """
        # 提取步骤编号和内容
        step_pattern = r'// Step (\d+):\s*(.+)'
        steps = re.findall(step_pattern, content)
        
        if not steps:
            return {"has_loop": False, "message": "未找到测试步骤"}
        
        # 检查步骤编号是否过大
        max_step_num = max(int(step[0]) for step in steps)
        if max_step_num > 200:
            return {
                "has_loop": True, 
                "message": f"步骤编号过大 ({max_step_num})，可能陷入循环",
                "max_step": max_step_num
            }
        
        # 检查重复的步骤内容
        step_contents = [step[1].strip() for step in steps]
        content_counter = Counter(step_contents)
        
        repeated_steps = {content: count for content, count in content_counter.items() 
                         if count > self.max_repetitions}
        
        if repeated_steps:
            return {
                "has_loop": True,
                "message": f"发现重复步骤: {list(repeated_steps.keys())[:3]}...",
                "repeated_steps": repeated_steps
            }
        
        # 检查连续重复的模式
        consecutive_patterns = self._find_consecutive_patterns(step_contents)
        if consecutive_patterns:
            return {
                "has_loop": True,
                "message": f"发现连续重复模式: {consecutive_patterns[:3]}...",
                "patterns": consecutive_patterns
            }
        
        return {"has_loop": False, "message": "未检测到循环"}
    
    def _find_consecutive_patterns(self, steps):
        """查找连续重复的模式"""
        patterns = []
        
        # 检查长度为2-5的重复模式
        for pattern_length in range(2, 6):
            for i in range(len(steps) - pattern_length * 2):
                pattern = steps[i:i + pattern_length]
                next_pattern = steps[i + pattern_length:i + pattern_length * 2]
                
                if pattern == next_pattern:
                    # 检查这个模式重复了多少次
                    repeat_count = 1
                    start_pos = i + pattern_length
                    
                    while (start_pos + pattern_length <= len(steps) and 
                           steps[start_pos:start_pos + pattern_length] == pattern):
                        repeat_count += 1
                        start_pos += pattern_length
                    
                    if repeat_count >= self.max_repetitions:
                        patterns.append({
                            "pattern": pattern,
                            "repeat_count": repeat_count,
                            "start_index": i
                        })
        
        return patterns
    
    def clean_loops(self, content):
        """
        清理内容中的循环
        
        Args:
            content: 原始内容
            
        Returns:
            str: 清理后的内容
        """
        detection_result = self.detect_step_loop(content)
        
        if not detection_result["has_loop"]:
            return content
        
        print(f"🔍 检测到循环: {detection_result['message']}")
        
        # 提取所有步骤
        step_pattern = r'(// Step \d+:.*?)(?=// Step \d+:|$)'
        steps = re.findall(step_pattern, content, re.DOTALL)
        
        if not steps:
            return content
        
        # 移除重复的步骤，保留前几次出现
        seen_contents = {}
        cleaned_steps = []
        
        for step in steps:
            # 提取步骤内容（去除步骤编号）
            step_content_match = re.search(r'// Step \d+:\s*(.+)', step)
            if step_content_match:
                step_content = step_content_match.group(1).strip()
                
                if step_content not in seen_contents:
                    seen_contents[step_content] = 0
                
                seen_contents[step_content] += 1
                
                # 只保留前几次出现的步骤
                if seen_contents[step_content] <= self.max_repetitions:
                    cleaned_steps.append(step)
                else:
                    print(f"  ❌ 移除重复步骤: {step_content[:50]}...")
        
        # 重新组合内容
        cleaned_content = '\n'.join(cleaned_steps)
        
        # 添加结束标记
        if not re.search(r'}\s*$', cleaned_content):
            cleaned_content += '\n\n    // Test case completed\n    TestStopLogging();\n}'
        
        print(f"✅ 循环清理完成，从 {len(steps)} 个步骤减少到 {len(cleaned_steps)} 个步骤")
        
        return cleaned_content

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python loop_detector.py <file_path> [--clean]")
        print("  --clean: 自动清理检测到的循环")
        sys.exit(1)
    
    file_path = sys.argv[1]
    should_clean = "--clean" in sys.argv
    
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        sys.exit(1)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        detector = LoopDetector()
        
        if should_clean:
            cleaned_content = detector.clean_loops(content)
            
            # 保存清理后的内容
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📁 原文件已备份到: {backup_path}")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"✅ 清理后的内容已保存到: {file_path}")
        else:
            # 只检测，不清理
            result = detector.detect_step_loop(content)
            if result["has_loop"]:
                print(f"⚠️  检测到循环: {result['message']}")
                print("   使用 --clean 参数来自动清理循环")
            else:
                print(f"✅ {result['message']}")
    
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()