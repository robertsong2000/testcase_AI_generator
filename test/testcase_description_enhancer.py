#!/usr/bin/env python3
"""
测试用例描述增强器
使用零规则关键词提取器增强JSON测试用例文件中的description字段
"""

import json
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from capl_langchain.utils.auto_keyword_extractor import AutoKeywordExtractor

class TestcaseDescriptionEnhancer:
    """测试用例描述增强器"""
    
    def __init__(self):
        self.extractor = AutoKeywordExtractor()
    
    def enhance_description(self, test_step: str, description: str) -> str:
        """使用零规则扩展增强描述，结合test_step和description"""
        if not description and not test_step:
            return description or ""
        
        # 清理输入
        test_step_clean = test_step.strip() if test_step else ""
        description_clean = description.strip() if description else ""
        
        # 避免重复：如果test_step和description内容相似或相同，只使用一个
        combined_text = ""
        if test_step_clean and description_clean:
            # 检查是否内容相似（简单检查：一个包含另一个）
            if test_step_clean.lower() in description_clean.lower() or description_clean.lower() in test_step_clean.lower():
                combined_text = description_clean  # 优先使用description
            else:
                combined_text = f"{test_step_clean} - {description_clean}"
        elif test_step_clean:
            combined_text = test_step_clean
        elif description_clean:
            combined_text = description_clean
        else:
            return description or ""
        
        try:
            enhanced = self.extractor.expand_query(combined_text)
            # 将增强内容追加到原description最后，前面添加"enhanced info："前缀
            if enhanced and enhanced.strip():
                if description_clean:
                    return f"{description_clean} enhanced info：{enhanced}"
                else:
                    return f"enhanced info：{enhanced}"
            else:
                return description or ""
        except Exception as e:
            print(f"⚠️  扩展失败: {e}")
            return description or ""
    
    def process_json_file(self, file_path: str, backup: bool = True) -> bool:
        """处理单个JSON测试用例文件，增强后保存到新文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            modified = False
            original_data = json.loads(json.dumps(data))  # 深拷贝原始数据
            
            # 处理steps中的description
            if 'steps' in data and isinstance(data['steps'], list):
                for step in data['steps']:
                    if 'description' in step:
                        original_desc = step['description'] or ""
                        test_step = step.get('test_step', '') or ""
                        enhanced_desc = self.enhance_description(test_step, original_desc)
                        
                        if enhanced_desc != original_desc:
                            step['description'] = enhanced_desc
                            modified = True
                            print(f"✅ 增强: '{original_desc[:50]}...' -> '{enhanced_desc[:50]}...'")
                        elif test_step and original_desc:
                            print(f"ℹ️  无变化: '{original_desc[:50]}...'")
            
            if modified:
                # 创建增强文件路径
                enhanced_path = f"{file_path}.enhanced"
                
                # 写入增强后的文件到新文件
                with open(enhanced_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"✅ 增强文件已创建: {enhanced_path}")
                
                # 保留原文件不变，无需备份
                return True
            else:
                print(f"ℹ️  无需增强: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ 处理文件失败 {file_path}: {e}")
            return False
    
    def process_directory(self, directory_path: str, pattern: str = "*.json") -> dict:
        """处理整个目录中的JSON文件，增强后保存到.enhanced文件"""
        directory = Path(directory_path)
        results = {
            'processed': 0,
            'enhanced': 0,
            'failed': 0,
            'files': [],
            'enhanced_files': []
        }
        
        if not directory.exists():
            print(f"❌ 目录不存在: {directory_path}")
            return results
        
        json_files = list(directory.glob(pattern))
        print(f"📁 找到 {len(json_files)} 个JSON文件")
        
        for json_file in json_files:
            print(f"\n🔄 处理: {json_file.name}")
            success = self.process_json_file(str(json_file))
            
            if success:
                results['enhanced'] += 1
                enhanced_file = f"{json_file}.enhanced"
                results['enhanced_files'].append(enhanced_file)
                print(f"📝 增强文件: {json_file.name}.enhanced")
            elif success is False:  # 无需增强也算成功处理
                results['processed'] += 1
            else:
                results['failed'] += 1
            
            results['files'].append(str(json_file))
        
        return results

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python testcase_description_enhancer.py <json_file_or_directory>")
        print("示例:")
        print("  python testcase_description_enhancer.py testcases_head_lamps/testcase.json")
        print("  python testcase_description_enhancer.py testcases_head_lamps/")
        return
    
    target_path = sys.argv[1]
    enhancer = TestcaseDescriptionEnhancer()
    
    if os.path.isfile(target_path):
        # 处理单个文件
        print(f"🎯 处理单个文件: {target_path}")
        enhancer.process_json_file(target_path)
    elif os.path.isdir(target_path):
        # 处理整个目录
        print(f"📂 处理目录: {target_path}")
        results = enhancer.process_directory(target_path)
        
        print(f"\n📊 处理结果:")
        print(f"  总文件数: {len(results['files'])}")
        print(f"  已增强: {results['enhanced']}")
        print(f"  已处理: {results['processed']}")
        print(f"  失败: {results['failed']}")
        if results['enhanced_files']:
            print(f"  增强文件列表:")
            for enhanced_file in results['enhanced_files']:
                print(f"    - {Path(enhanced_file).name}")
    else:
        print(f"❌ 路径不存在: {target_path}")

if __name__ == "__main__":
    main()