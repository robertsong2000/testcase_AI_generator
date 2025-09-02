#!/usr/bin/env python3
"""
API优先级分析工具
基于实际的API文件内容来定义和验证优先级规则
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

class APIPriorityAnalyzer:
    def __init__(self):
        # 使用相对路径基于当前工程目录
        base_dir = Path(__file__).parent.parent
        self.api_files = [
            base_dir / "knowledge_base" / "interfaces_analysis_common-libraries.json",
            base_dir / "knowledge_base" / "interfaces_analysis_libraries.json"
        ]
        self.apis = []
        self.load_apis()
    
    def load_apis(self):
        """加载所有API数据"""
        for file_path in self.api_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    interfaces = data.get('interfaces', [])
                    self.apis.extend(interfaces)
                    print(f"✅ 加载 {len(interfaces)} 个API从 {Path(file_path).name}")
            except Exception as e:
                print(f"❌ 加载失败 {file_path}: {e}")
    
    def analyze_naming_patterns(self):
        """分析API命名模式"""
        print("\n" + "="*60)
        print("🔍 API命名模式分析")
        print("="*60)
        
        # 关键词统计
        keywords = {
            'test': [], 'check': [], 'verify': [], 'wait': [], 'set': [],
            'get': [], 'is': [], 'ts': [], 'verdict': [], 'configure': [],
            'service': [], 'callback': [], 'simulate': [], 'enable': [],
            'disable': [], 'start': [], 'stop': [], 'state': [], 'status': []
        }
        
        for api in self.apis:
            name = api.get('function_name', '').lower()
            for keyword in keywords:
                if keyword in name:
                    keywords[keyword].append(name)
        
        for keyword, apis in keywords.items():
            if apis:
                print(f"{keyword.upper():12} ({len(apis):3d}个): {apis[:3]}...")
    
    def classify_by_priority(self):
        """基于实际内容分类优先级"""
        print("\n" + "="*60)
        print("🏷️ 基于实际内容的优先级分类")
        print("="*60)
        
        # 重新定义优先级规则
        priority_rules = {
            10: {  # 最高优先级 - 测试核心函数
                'patterns': [
                    'test', 'assert', 'verify', 'verdict', 'check',
                    'testwait', 'testcheck', 'testverify'
                ],
                'apis': []
            },
            9: {   # 高优先级 - 测试辅助函数
                'patterns': [
                    'wait', 'timeout', 'delay', 'sleep', 'pause',
                    'starttest', 'stoptest', 'setup', 'teardown'
                ],
                'apis': []
            },
            8: {   # 中高优先级 - 状态检查
                'patterns': [
                    'ischeck', 'isverify', 'isstate', 'getstate', 'getstatus',
                    'checkstate', 'checkstatus', 'verdictstate'
                ],
                'apis': []
            },
            7: {   # 中优先级 - 配置和控制
                'patterns': [
                    'configure', 'setup', 'set', 'enable', 'disable',
                    'init', 'reset', 'clear', 'create', 'delete'
                ],
                'apis': []
            },
            6: {   # 中低优先级 - 获取数据
                'patterns': [
                    'get', 'read', 'fetch', 'retrieve', 'receive',
                    'collect', 'extract', 'parse'
                ],
                'apis': []
            },
            5: {   # 低优先级 - 回调和事件
                'patterns': [
                    'callback', 'onmessage', 'onsignal', 'ontimer', 'onkey',
                    'event', 'handler', 'listener'
                ],
                'apis': []
            },
            4: {   # 最低优先级 - 其他
                'patterns': [],
                'apis': []
            }
        }
        
        # 分类API
        unclassified = []
        for api in self.apis:
            name = api.get('function_name', '').lower()
            classified = False
            
            for priority, rule in priority_rules.items():
                for pattern in rule['patterns']:
                    if pattern in name:
                        rule['apis'].append({
                            'name': api.get('function_name'),
                            'description': api.get('description', ''),
                            'priority': priority
                        })
                        classified = True
                        break
                if classified:
                    break
            
            if not classified:
                priority_rules[4]['apis'].append({
                    'name': api.get('function_name'),
                    'description': api.get('description', ''),
                    'priority': 4
                })
        
        # 输出分类结果
        total_classified = 0
        for priority in sorted(priority_rules.keys(), reverse=True):
            apis = priority_rules[priority]['apis']
            if apis:
                print(f"\n🔸 优先级 {priority} ({len(apis)}个)")
                for api in apis[:5]:  # 显示前5个示例
                    print(f"   {api['name']}: {api['description']}")
                if len(apis) > 5:
                    print(f"   ... 共{len(apis)}个")
                total_classified += len(apis)
        
        print(f"\n📊 总计: {total_classified}个API已分类")
        
        return priority_rules
    
    def generate_priority_mapping(self):
        """生成优先级映射配置"""
        print("\n" + "="*60)
        print("⚙️ 生成优先级映射配置")
        print("="*60)
        
        # 使用相对路径基于当前工程目录
        base_dir = Path(__file__).parent.parent
        priority_mapping = {}
        
        for api in self.apis:
            name = api.get('function_name', '')
            name_lower = name.lower()
            
            # 基于函数名的精确匹配规则
            if any(kw in name_lower for kw in ['testwait', 'testassert', 'testcheck', 'testverify']):
                priority = 10
            elif any(kw in name_lower for kw in ['assert', 'verdict', 'test']):
                priority = 10
            elif any(kw in name_lower for kw in ['wait', 'timeout', 'delay']):
                priority = 9
            elif any(kw in name_lower for kw in ['checkstate', 'getstate', 'isstate']):
                priority = 8
            elif any(kw in name_lower for kw in ['configure', 'setup', 'set', 'enable', 'disable']):
                priority = 7
            elif any(kw in name_lower for kw in ['get', 'read', 'fetch']):
                priority = 6
            elif any(kw in name_lower for kw in ['callback', 'onmessage', 'onsignal']):
                priority = 5
            else:
                priority = 4
            
            priority_mapping[name] = priority
        
        # 保存映射文件到当前工程目录
        output_file = base_dir / "test" / "api_priority_mapping.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(priority_mapping, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 优先级映射已保存到: {output_file}")
        
        # 统计分布
        priority_counts = Counter(priority_mapping.values())
        print("\n📈 优先级分布:")
        for priority in sorted(priority_counts.keys(), reverse=True):
            count = priority_counts[priority]
            percentage = (count / len(priority_mapping)) * 100
            print(f"   优先级 {priority}: {count}个 ({percentage:.1f}%)")
        
        return priority_mapping
    
    def validate_current_rules(self):
        """验证当前规则的有效性"""
        print("\n" + "="*60)
        print("🔍 验证当前优先级规则")
        print("="*60)
        
        # 当前规则
        current_rules = {
            10: ['test', 'assert'],
            8: ['message', 'signal', 'output'],
            6: ['timer'],
            4: []  # 其他
        }
        
        matches = defaultdict(list)
        for api in self.apis:
            name = api.get('function_name', '').lower()
            
            for priority, keywords in current_rules.items():
                for keyword in keywords:
                    if keyword in name:
                        matches[priority].append(name)
                        break
        
        for priority in sorted(matches.keys(), reverse=True):
            apis = matches[priority]
            print(f"\n当前规则 优先级{priority} ({len(apis)}个匹配):")
            for api in apis[:5]:
                print(f"   {api}")
            if len(apis) > 5:
                print(f"   ... 共{len(apis)}个")

def main():
    analyzer = APIPriorityAnalyzer()
    analyzer.analyze_naming_patterns()
    analyzer.validate_current_rules()
    priority_rules = analyzer.classify_by_priority()
    analyzer.generate_priority_mapping()

if __name__ == "__main__":
    main()