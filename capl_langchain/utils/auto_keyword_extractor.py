import json
import re
import configparser
import os
from pathlib import Path
from typing import Dict, List, Set, Any

class AutoKeywordExtractor:
    """零规则自动关键词提取器 - 完全不需要手动定义映射"""
    
    def __init__(self, api_files: List[str] = None, knowledge_base_dir: str = None):
        """
        初始化关键词提取器
        
        Args:
            api_files: 可选的API文件路径列表（优先级最高）
            knowledge_base_dir: 可选的知识库目录路径，默认为项目根目录下的knowledge_base
        """
        # 加载配置文件
        config = self._load_config()
        
        # 设置知识库目录
        if knowledge_base_dir:
            kb_dir = Path(knowledge_base_dir)
        else:
            # 优先使用配置文件中的设置
            config_kb_dir = config.get('DEFAULT', 'KNOWLEDGE_BASE_DIR', fallback='knowledge_base')
            if os.path.isabs(config_kb_dir):
                kb_dir = Path(config_kb_dir)
            else:
                # 相对路径相对于项目根目录
                kb_dir = Path(__file__).parent.parent.parent / config_kb_dir
        
        # 设置API文件
        if api_files:
            # 使用显式指定的文件
            self.api_files = [Path(f) for f in api_files]
        else:
            # 优先使用配置文件中的设置
            config_files = config.get('DEFAULT', 'API_FILES', fallback='')
            if config_files and config_files.strip():
                # 解析配置文件中的文件列表
                file_names = [f.strip() for f in config_files.split(',') if f.strip()]
                self.api_files = []
                for file_name in file_names:
                    if os.path.isabs(file_name):
                        self.api_files.append(Path(file_name))
                    else:
                        # 相对路径相对于知识库目录
                        self.api_files.append(kb_dir / file_name)
            else:
                # 使用默认文件
                self.api_files = [
                    kb_dir / "interfaces_analysis_common-libraries.json",
                    kb_dir / "interfaces_analysis_libraries.json"
                ]
            
        self.keyword_cache = {}
        self._build_keyword_cache()
    
    def _load_config(self):
        """加载配置文件"""
        config = configparser.ConfigParser()
        config_path = Path(__file__).parent.parent.parent / "prompt_config.ini"
        
        if config_path.exists():
            try:
                config.read(config_path, encoding='utf-8')
            except Exception as e:
                print(f"⚠️  读取配置文件失败: {e}，使用默认设置")
        
        return config
    
    def _build_keyword_cache(self):
        """自动从API文档提取关键词 - 零规则"""
        total_apis = 0
        total_files = 0
        
        for api_file in self.api_files:
            if not api_file.exists():
                print(f"⚠️  API文件不存在: {api_file}")
                continue
            
            try:
                with open(api_file, 'r', encoding='utf-8') as f:
                    api_data = json.load(f)
                
                interfaces = api_data.get('interfaces', [])
                file_apis = len(interfaces)
                print(f"📊 正在分析 {api_file.name}: 共找到 {file_apis} 个接口")
                
                # 自动提取所有函数名和描述中的关键词
                api_count = 0
                for interface in interfaces:
                    func_name = interface.get('function_name', '')
                    description = interface.get('description', '')
                    file_path = interface.get('file_path', '')
                    
                    if func_name:  # 只处理有函数名的
                        keywords = self._extract_keywords(func_name, description)
                        constants = self._extract_constants(description)
                        
                        self.keyword_cache[func_name] = {
                            'file_path': str(api_file),
                            'keywords': keywords,
                            'constants': constants,
                            'description': description,
                            'source_file': api_file.name
                        }
                        api_count += 1
                
                print(f"✅ {api_file.name}: 成功提取 {api_count} 个API的关键词")
                total_apis += api_count
                total_files += 1
                
            except Exception as e:
                print(f"❌ 处理 {api_file.name} 时出错: {e}")
        
        print(f"🎯 总计: 从 {total_files} 个文件中提取了 {total_apis} 个API的关键词")
    
    def _extract_keywords(self, func_name: str, description: str) -> List[str]:
        """自动从函数名和描述提取关键词 - 零规则"""
        keywords = set()
        
        # 1. 完整函数名
        keywords.add(func_name.lower())
        
        # 2. 驼峰命名拆分（智能处理）
        if func_name:
            # 处理 SetVeMode -> Set, Ve, Mode
            camel_parts = re.findall(r'[A-Z][a-z]+|[a-z]+|[A-Z]+(?=[A-Z]|$)', func_name)
            keywords.update(part.lower() for part in camel_parts)
            
            # 3. 常见缩写扩展
            abbreviations = {
                've': 'vehicle',
                'pcu': 'power control unit',
                'diag': 'diagnostic',
                'wip': 'wiper',
                'chg': 'charging',
                'ts': 'test step',
                'ssa': 'steering system analysis',
                'fota': 'firmware over the air',
                'escl': 'electronic steering column lock',
                'hmi': 'human machine interface',
                'csi': 'client service interface',
                'psi': 'provider service interface',
                'vdr': 'vehicle data rights',
                'can': 'controller area network',
                'ecu': 'electronic control unit',
                'obd': 'on board diagnostics'
            }
            
            for abbr, full in abbreviations.items():
                if abbr in [part.lower() for part in camel_parts]:
                    keywords.add(full)
        
        # 4. 从描述提取英文关键词（排除常见虚词）
        if description:
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'this', 'that', 'these', 'those'}
            english_words = re.findall(r'\b[a-zA-Z]+\b', description.lower())
            keywords.update(word for word in english_words if word not in stop_words and len(word) > 2)
        
        # 5. 添加测试相关关键词
        test_keywords = ['test', 'set', 'check', 'start', 'config', 'verify', 'validate', 'initialize', 'enable', 'disable', 'create', 'delete', 'read', 'write']
        for keyword in test_keywords:
            if keyword in description.lower() or keyword in func_name.lower():
                keywords.add(keyword)
        
        # 6. 添加功能关键词
        functional_keywords = {
            'mode', 'power', 'diagnostic', 'charging', 'wiper', 'session', 'cable', 
            'vehicle', 'battery', 'engine', 'transmission', 'brake', 'signal', 'message', 'network',
            'timeout', 'campaign', 'firmware', 'update', 'authentication', 'security', 'access',
            'door', 'indicator', 'light', 'headlamp', 'beam', 'horn', 'fan', 'heater', 'windscreen',
            'flasher', 'turn', 'parking', 'speed', 'position', 'climate', 'temperature', 'voltage',
            'current', 'sensor', 'button', 'switch', 'pedal', 'steering', 'lock', 'unlock', 'alarm',
            'warning', 'notification', 'display', 'interface', 'control', 'monitor', 'test', 'verify',
            'wait', 'start', 'stop', 'reset', 'initialize', 'configure', 'enable', 'disable', 'set', 'get',
            'check', 'validate', 'report', 'log', 'trace', 'error', 'failure', 'state', 'status', 'condition'
        }
        
        for keyword in functional_keywords:
            if keyword in func_name.lower() or keyword in description.lower():
                keywords.add(keyword)
        
        return list(keywords)
    
    def _extract_constants(self, description: str) -> List[str]:
        """自动提取描述中的CAPL常量"""
        if not description:
            return []
        
        # 查找CAPL常量模式：kXXX, K_XXX, eXXX
        constants = re.findall(r'\bk[A-Z][a-zA-Z0-9]*\b', description)
        constants.extend(re.findall(r'\bK_[A-Z_]+\b', description))
        constants.extend(re.findall(r'\be[A-Z][a-zA-Z0-9]*\b', description))
        
        return list(set(constants))
    
    def expand_query(self, query: str) -> str:
        """零规则智能扩展查询"""
        if not self.keyword_cache:
            print("⚠️  关键词缓存为空，跳过扩展")
            return query
        
        query_lower = query.lower()
        expanded_terms = [query]  # 保留原始查询
        
        # 智能匹配最相关的API
        matched_apis = []
        for api_name, data in self.keyword_cache.items():
            score = 0
            keywords = data['keywords']
            
            # 计算匹配分数（关键词重叠度）
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
            
            # 如果匹配度高，添加API和常量
            if score >= 1:  # 至少匹配一个关键词
                matched_apis.append((api_name, score, data))
        
        # 按匹配分数排序，取前3个最相关的API
        matched_apis.sort(key=lambda x: x[1], reverse=True)
        top_apis = matched_apis[:3]
        
        # 添加扩展内容
        for api_name, score, data in top_apis:
            expanded_terms.append(api_name)
            expanded_terms.extend(data['constants'])
            
            # 如果匹配分数高，也添加一些相关关键词
            if score >= 2:
                expanded_terms.extend(data['keywords'][:3])  # 添加前3个关键词
        
        # 去重并保持顺序
        seen = set()
        unique_terms = []
        for term in expanded_terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        result = " ".join(unique_terms)
        
        if result != query:
            print(f"🔍 零规则扩展: '{query}' → '{result}'")
        
        return result
    
    def get_api_statistics(self) -> Dict[str, Any]:
        """获取API统计信息"""
        if not self.keyword_cache:
            return {"total_apis": 0, "files": {}, "top_keywords": {}, "sources": {}}
        
        stats = {
            "total_apis": len(self.keyword_cache),
            "files": {},
            "top_keywords": {},
            "sources": {}
        }
        
        # 按源文件分组统计
        for api_name, data in self.keyword_cache.items():
            source_file = data.get('source_file', 'unknown')
            file_name = source_file
            
            if file_name not in stats["files"]:
                stats["files"][file_name] = 0
            stats["files"][file_name] += 1
            
            # 记录源文件信息
            if source_file not in stats["sources"]:
                stats["sources"][source_file] = 0
            stats["sources"][source_file] += 1
        
        # 统计最常用关键词
        keyword_counts = {}
        for data in self.keyword_cache.values():
            for keyword in data['keywords']:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        stats["top_keywords"] = dict(sorted(keyword_counts.items(), 
                                          key=lambda x: x[1], reverse=True)[:10])
        
        return stats

# 测试函数
def test_zero_rule_extraction():
    """测试零规则提取效果"""
    print("🧪 零规则自动关键词提取测试")
    print("=" * 50)
    
    extractor = AutoKeywordExtractor()
    
    if not extractor.keyword_cache:
        print("❌ 未能加载API数据，请检查 interfaces_analysis_common-libraries.json")
        return
    
    # 显示统计信息
    stats = extractor.get_api_statistics()
    print(f"📊 共处理 {stats['total_apis']} 个API")
    print(f"📁 文件分布: {dict(list(stats['files'].items())[:5])}")
    print(f"📂 源文件: {dict(list(stats['sources'].items())[:5])}")
    
    # 测试查询扩展
    test_queries = [
        "Set vehicle mode to power on",
        "Connect charging cable for testing", 
        "Start diagnostic session",
        "Test wiper intermittent mode",
        "Check low power state",
        "Configure CAN message"
    ]
    
    print("\n🎯 Zero-rule query expansion test")
    print("-" * 30)
    
    for query in test_queries:
        expanded = extractor.expand_query(query)
        print(f"原始: {query}")
        print(f"扩展: {expanded}")
        print("-" * 20)
    
    # 显示部分API的关键词提取示例
    print("\n🔍 API关键词提取示例")
    print("-" * 30)
    
    sample_apis = list(extractor.keyword_cache.items())[:3]
    for api_name, data in sample_apis:
        print(f"API: {api_name}")
        print(f"关键词: {data['keywords'][:5]}...")
        print(f"常量: {data['constants']}")
        print("-" * 15)

if __name__ == "__main__":
    test_zero_rule_extraction()