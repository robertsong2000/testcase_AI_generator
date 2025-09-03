#!/usr/bin/env python3
"""
交互式RAG信息查看器
允许用户输入查询并查看所有匹配的RAG信息
"""

import os
import sys
from pathlib import Path
import json
import argparse
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from capl_langchain.config.config import CAPLGeneratorConfig
from capl_langchain.managers.knowledge_manager import KnowledgeManager

class InteractiveRAGViewer:
    """交互式RAG信息查看器"""
    
    def __init__(self, model_type="ollama"):
        """初始化RAG查看器
        
        Args:
            model_type: 使用的模型类型 (ollama/openai)
        """
        self.model_type = model_type
        self.config = CAPLGeneratorConfig()
        self.config.enable_rag = True
        self.knowledge_manager = KnowledgeManager(self.config)
        self.retriever = None
        self.initialized = False
        
    def initialize_knowledge_base(self):
        """初始化知识库
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            print("🔄 正在初始化知识库...")
            
            # 创建配置
            config = CAPLGeneratorConfig()
            config.enable_rag = True  # 强制启用RAG
            
            # 创建知识库管理器
            kb_manager = KnowledgeManager(config)
            
            # 重新初始化知识库（确保检索器可用）
            success = kb_manager.initialize_knowledge_base()
            
            if success:
                self.retriever = kb_manager.get_retriever()
                if self.retriever:
                    self.initialized = True
                    print("✅ 知识库初始化成功")
                    return True
                else:
                    print("❌ 无法获取检索器")
                    return False
            else:
                print("❌ 知识库初始化失败")
                return False
                
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def search_documents(self, query: str, k: int = 6) -> List[Dict[str, Any]]:
        """搜索文档
        
        Args:
            query: 查询关键词
            k: 返回结果数量
            
        Returns:
            包含文档信息的字典列表
        """
        if not self.retriever:
            print("❌ 检索器未初始化")
            return []
        
        try:
            # 使用混合检索器搜索
            docs = self.retriever.invoke(query)[:k]
            
            # 转换为字典格式
            results = []
            for doc in docs:
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source": doc.metadata.get("source", "未知"),
                    "title": doc.metadata.get("title", "无标题")
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def display_document(self, doc: Dict[str, Any], show_content: bool = True, max_content_length: int = 1000):
        """显示单个文档信息"""
        print(f"\n{'='*80}")
        print(f"📄 文档 #{doc['index']}")
        print(f"📁 来源: {doc['source']}")
        print(f"🏷️  标题: {doc['title']}")
        
        if doc['relevance_score'] != "N/A":
            print(f"📊 相关度: {doc['relevance_score']:.3f}")
        
        # 显示元数据
        if doc['metadata']:
            print("\n📋 元数据:")
            for key, value in doc['metadata'].items():
                if key not in ['source', 'title', 'score']:
                    print(f"   {key}: {value}")
        
        # 显示内容
        if show_content:
            content = doc['content']
            if len(content) > max_content_length:
                content = content[:max_content_length] + "... [内容已截断]"
            print(f"\n📝 内容:")
            print(content)
        
        print(f"{'='*80}")
    
    def display_search_results(self, results: List[Dict[str, Any]], query: str, detailed: bool = False):
        """显示搜索结果
        
        Args:
            results: 搜索结果列表
            query: 查询关键词
            detailed: 是否显示详细信息
        """
        if not results:
            print("❌ 未找到相关文档")
            return
        
        print(f"\n✅ 找到 {len(results)} 个相关文档")
        print(f"{'='*80}")
        
        for i, result in enumerate(results, 1):
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            source = result.get("source", "未知")
            title = result.get("title", "无标题")
            
            print(f"\n📄 文档 #{i}")
            print(f"{'='*80}")
            print(f"📁 来源: {source}")
            print(f"🏷️  标题: {title}")
            
            if detailed:
                print(f"\n📋 元数据:")
                for key, value in metadata.items():
                    print(f"   {key}: {value}")
            
            # 显示内容摘要或全文
            if detailed:
                print(f"\n📄 全文内容:")
                print(f"{'-'*80}")
                print(content)
                print(f"{'-'*80}")
            else:
                # 显示摘要
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"\n📄 内容预览:")
                print(f"{'-'*80}")
                print(preview)
            
            print(f"\n📏 内容长度: {len(content)} 字符")
            print(f"{'='*80}")
    
    def display_document(self, result: Dict[str, Any], show_content: bool = True, max_content_length: int = 1000):
        """显示单个文档详细信息
        
        Args:
            result: 文档结果字典
            show_content: 是否显示内容
            max_content_length: 最大内容长度
        """
        content = result.get("content", "")
        metadata = result.get("metadata", {})
        source = result.get("source", "未知")
        title = result.get("title", "无标题")
        
        print(f"\n{'='*100}")
        print(f"📄 文档详情")
        print(f"{'='*100}")
        print(f"📁 来源: {source}")
        print(f"🏷️  标题: {title}")
        
        if metadata:
            print(f"\n📋 元数据:")
            for key, value in metadata.items():
                print(f"   {key}: {value}")
        
        if show_content and content:
            print(f"\n📄 全文内容:")
            print(f"{'-'*100}")
            display_content = content[:max_content_length]
            if len(content) > max_content_length:
                display_content += "... [内容已截断]"
            print(display_content)
            print(f"{'-'*100}")
        
        print(f"\n📊 统计信息:")
        print(f"   内容长度: {len(content)} 字符")
        print(f"{'='*100}")
    
    def display_document_full(self, doc, doc_id):
        """显示单个文档的完整信息
        
        Args:
            doc: 文档对象
            doc_id: 文档编号
        """
        print(f"\n{'='*100}")
        print(f"📄 文档 #{doc_id} - 完整信息")
        print(f"{'='*100}")
        
        # 文档元数据
        metadata = doc.metadata if hasattr(doc, 'metadata') else {}
        
        print(f"📁 来源文件: {metadata.get('source', '未知')}")
        print(f"🏷️  文档标题: {metadata.get('title', '无标题')}")
        print(f"📊 内容长度: {len(doc.page_content)} 字符")
        
        # 显示所有元数据
        if metadata:
            print(f"\n📋 完整元数据:")
            for key, value in metadata.items():
                print(f"   {key}: {value}")
        
        # 全文内容
        print(f"\n📄 全文内容:")
        print(f"{'-'*100}")
        print(doc.page_content)
        print(f"{'-'*100}")
        
        print(f"\n✅ 文档 #{doc_id} 显示完成")
        print(f"{'='*100}")
    
    def export_results(self, query: str, results: List[Dict[str, Any]], output_file: str):
        """导出搜索结果到文件"""
        export_data = {
            "query": query,
            "total_results": len(results),
            "timestamp": "N/A",  # 简化处理
            "results": results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 结果已导出到: {output_file}")
    
    def run_interactive_mode(self):
        """运行交互模式"""
        print("\n" + "="*60)
        print("🎯 交互式RAG信息查看器")
        print("="*60)
        print("💡 提示:")
        print("   • 输入查询关键词查看相关文档")
        print("   • 输入 'detailed' 切换详细模式")
        print("   • 输入 'export <文件名>' 导出结果")
        print("   • 输入 'help' 查看帮助")
        print("   • 输入 'quit' 或 'exit' 退出")
        print("-" * 60)
        
        detailed_mode = False
        
        while True:
            try:
                query = input("\n🔍 请输入查询 (或命令): ").strip()
                
                if not query:
                    continue
                
                # 处理命令
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 感谢使用，再见！")
                    break
                
                elif query.lower() == 'help':
                    self.show_help()
                    continue
                
                elif query.lower() == 'detailed':
                    detailed_mode = not detailed_mode
                    print(f"📋 详细模式: {'开启' if detailed_mode else '关闭'}")
                    continue
                
                elif query.lower().startswith('export '):
                    parts = query.split(' ', 1)
                    if len(parts) == 2 and parts[1]:
                        output_file = parts[1]
                        # 这里需要先有搜索结果才能导出
                        print("⚠️  请先进行一次查询，再使用export命令")
                    else:
                        print("❌ 用法: export <文件名.json>")
                    continue
                
                # 处理查询
                print(f"\n🔍 正在搜索: {query}")
                results = self.search_documents(query)
                
                if results:
                    # 处理导出命令
                    if query.lower().startswith('export '):
                        parts = query.split(' ', 1)
                        if len(parts) == 2:
                            self.export_results(query, results, parts[1])
                        continue
                    
                    # 显示结果 - 修复参数顺序
                    self.display_search_results(results, query, detailed=detailed_mode)
                    
                    # 提供进一步操作
                    self.handle_post_search_options(query, results)
                else:
                    print("❌ 未找到相关文档")
                    
            except KeyboardInterrupt:
                print("\n👋 用户中断，退出程序")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
    
    def handle_post_search_options(self, query: str, results: List[Dict[str, Any]]):
        """处理搜索后的选项"""
        print("\n📋 可选操作:")
        print("   1-9: 查看具体文档详情")
        print("   e: 导出所有结果")
        print("   n: 新的查询")
        print("   q: 退出")
        
        choice = input("请选择操作: ").strip().lower()
        
        if choice == 'q':
            print("👋 再见！")
            exit(0)
        elif choice == 'n':
            return
        elif choice == 'e':
            filename = f"rag_results_{query.replace(' ', '_').replace('/', '_')}.json"
            self.export_results(query, results, filename)
        elif choice.isdigit() and 1 <= int(choice) <= len(results):
            doc_index = int(choice) - 1
            if 0 <= doc_index < len(results):
                self.display_document(results[doc_index], show_content=True, max_content_length=2000)
    
    def show_help(self):
        """显示帮助信息"""
        print("\n📖 帮助信息:")
        print("=" * 40)
        print("查询语法:")
        print("   • 直接输入关键词: 雨刷器测试")
        print("   • 多关键词: CAPL 消息通信")
        print("   • 短语查询: 测试用例设计")
        print()
        print("命令:")
        print("   detailed - 切换详细/简要显示模式")
        print("   export <文件名> - 导出搜索结果到JSON文件")
        print("   help - 显示此帮助信息")
        print("   quit/exit/q - 退出程序")
        print("=" * 40)
    
    def run_batch_mode(self, query: str, detailed: bool = False, export_file: Optional[str] = None):
        """运行批处理模式"""
        if not self.initialized and not self.initialize():
            return False
        
        print(f"🔍 批处理查询: {query}")
        results = self.search_documents(query)
        
        if results:
            self.display_search_results(query, results, detailed=detailed)
            
            if export_file:
                self.export_results(query, results, export_file)
                print(f"✅ 结果已导出到: {export_file}")
        
        return len(results) > 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="交互式RAG信息查看器")
    parser.add_argument("--query", type=str, help="查询关键词")
    parser.add_argument("--model", type=str, default="ollama", choices=["ollama", "openai"], 
                        help="使用的模型类型")
    parser.add_argument("--k", type=int, default=6, help="返回结果数量")
    parser.add_argument("--detailed", action="store_true", help="显示详细信息")
    parser.add_argument("--export", type=str, help="导出结果到JSON文件")
    parser.add_argument("--no-stream", action="store_true", help="禁用流式输出")
    
    args = parser.parse_args()
    
    print("🚀 启动交互式RAG信息查看器...")
    
    # 创建查看器
    viewer = InteractiveRAGViewer(model_type=args.model)
    
    # 初始化知识库
    if not viewer.initialize_knowledge_base():
        print("❌ 知识库初始化失败，程序退出")
        return 1
    
    # 批处理模式
    if args.query:
        print(f"🔍 执行查询: {args.query}")
        results = viewer.search_documents(args.query, k=args.k)
        
        if results:
            viewer.display_search_results(results, args.query, detailed=args.detailed)
            
            if args.export:
                viewer.export_results(args.query, results, args.export)
                print(f"✅ 结果已导出到: {args.export}")
        else:
            print(f"❌ 未找到相关文档")
    else:
        # 交互模式
        viewer.run_interactive_mode()
    
    return 0


if __name__ == "__main__":
    try:
        import pandas as pd
    except ImportError:
        print("⚠️  pandas未安装，时间戳功能将不可用")
    
    exit(main())