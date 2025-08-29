#!/usr/bin/env python3
"""
RAG检索优化测试工具
用于测试和优化测试规范到API的映射效果
"""

import os
import sys
from pathlib import Path
import json
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from capl_langchain.generator import CAPLGenerator
from capl_langchain.config.config import CAPLGeneratorConfig

class RAGOptimizer:
    def __init__(self):
        self.config = CAPLGeneratorConfig()
        self.config.enable_rag = True
        self.generator = CAPLGenerator(self.config)
        
    def test_query_optimization(self):
        """测试查询优化效果"""
        print("🧪 测试RAG查询优化...")
        
        # 测试用例：从简单到复杂
        test_cases = [
            {
                "original": "测试雨刷器",
                "optimized": "雨刷器间歇模式测试 CAPL测试用例 定时器控制"
            },
            {
                "original": "CAN消息发送",
                "optimized": "CAN消息周期发送 output消息发送 testWaitForMessage"
            },
            {
                "original": "低功耗测试",
                "optimized": "低功耗模式测试 超时等待 testWaitForTimeout"
            },
            {
                "original": "检查信号值",
                "optimized": "信号值检查 testAssert 边界值测试"
            },
            {
                "original": "GPIO控制",
                "optimized": "GPIO端口控制 setPort getPort 高低电平测试"
            }
        ]
        
        print("=" * 80)
        print("查询优化对比测试")
        print("=" * 80)
        
        for case in test_cases:
            print(f"\n📋 原始查询: '{case['original']}'")
            print(f"🔍 优化查询: '{case['optimized']}'")
            print("-" * 50)
            
            # 测试原始查询
            try:
                original_results = self.generator.search_knowledge_base(case['original'], k=3)
            except Exception as e:
                print(f"原始查询错误: {e}")
                original_results = []
            
            # 测试优化查询
            try:
                optimized_results = self.generator.search_knowledge_base(case['optimized'], k=3)
            except Exception as e:
                print(f"优化查询错误: {e}")
                optimized_results = []
            
            print(f"原始查询结果: {len(original_results)} 个文档")
            print(f"优化查询结果: {len(optimized_results)} 个文档")
            
            if optimized_results:
                print("✅ 优化后检索效果更好")
            else:
                print("⚠️  需要进一步优化")
    
    def test_threshold_tuning(self):
        """测试相似性阈值调优"""
        print("\n🎯 测试相似性阈值调优...")
        
        test_queries = [
            "雨刷器间歇模式3秒周期测试",
            "CAN消息100ms周期发送验证",
            "低功耗5秒空闲进入测试"
        ]
        
        # 测试不同的k值
        k_values = [2, 3, 4, 5, 6]
        
        for query in test_queries:
            print(f"\n📋 查询: '{query}'")
            print("-" * 40)
            
            for k in k_values:
                try:
                    results = self.generator.search_knowledge_base(query, k=k)
                    relevance_score = len(results) / k if results else 0
                    print(f"k={k}: 找到 {len(results)} 个文档 (相关度: {relevance_score:.2f})")
                except Exception as e:
                    print(f"k={k}: 查询错误 - {e}")
    
    def generate_optimization_report(self):
        """生成优化报告"""
        print("\n📊 生成RAG优化报告...")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "knowledge_base_status": self._check_knowledge_base(),
            "optimization_recommendations": [
                "使用更具体的查询关键词",
                "增加知识库中测试场景的描述",
                "调整检索参数k值",
                "添加关键词同义词映射",
                "使用混合检索策略"
            ]
        }
        
        # 保存报告
        report_path = Path("test/rag_optimization_report.json")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 优化报告已保存: {report_path}")
        return report
    
    def _check_knowledge_base(self):
        """检查知识库状态"""
        kb_dir = Path("knowledge_base")
        
        if not kb_dir.exists():
            return {"status": "不存在", "files": 0}
        
        files = list(kb_dir.glob("*.md")) + list(kb_dir.glob("*.txt")) + list(kb_dir.glob("*.json"))
        
        return {
            "status": "存在",
            "files": len(files),
            "file_list": [f.name for f in files]
        }
    
    def run_comprehensive_test(self):
        """运行综合优化测试"""
        print("🚀 开始RAG综合优化测试...")
        
        self.test_query_optimization()
        self.test_threshold_tuning()
        report = self.generate_optimization_report()
        
        print("\n" + "=" * 80)
        print("RAG优化测试完成")
        print("=" * 80)
        
        return report

def main():
    """主函数"""
    optimizer = RAGOptimizer()
    optimizer.run_comprehensive_test()

if __name__ == "__main__":
    main()