"""命令行接口工具"""

import argparse
import sys
from pathlib import Path

from ..generator import CAPLGenerator
from ..config.config import CAPLGeneratorConfig


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="CAPL代码生成器 - 基于LangChain的AI驱动CAPL脚本生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s requirements.txt                          # 默认流式输出
  %(prog)s requirements.txt --no-stream            # 禁用流式输出
  %(prog)s requirements.txt --output ./generated/
  %(prog)s requirements.txt --disable-rag
  %(prog)s requirements.txt -k 8                   # 设置RAG检索返回8个文档
  %(prog)s --info
  %(prog)s --search "CAPL message handling"
  %(prog)s --test-rag "message filter"
  %(prog)s requirements.txt --debug-prompt
  %(prog)s requirements.txt --rebuild-rag
  %(prog)s requirements.txt --no-use-example-code  # 禁用示例代码
  %(prog)s requirements.txt --use-example-code     # 强制使用示例代码
  %(prog)s requirements.txt --chunk-size 600       # 平衡场景配置
  %(prog)s requirements.txt --chunk-overlap 100    # 平衡场景配置
  %(prog)s requirements.txt --chunk-size 800 --chunk-overlap 150  # 完整上下文配置
        """
    )
    
    # 输入参数（可选）
    parser.add_argument(
        'input', 
        nargs='?',
        help='输入需求文件路径或直接输入需求文本'
    )
    
    # 输出配置
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='./generated',
        help='输出目录路径 (默认: ./generated)'
    )
    
    # LLM配置
    parser.add_argument(
        '--api-type',
        type=str,
        default='ollama',
        choices=['ollama', 'openai'],
        help='API类型 (ollama/openai)'
    )
    
    parser.add_argument(
        '--api-url',
        type=str,
        help='API基础URL (用于自定义或本地API)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        help='使用的模型名称'
    )
    
    # RAG配置
    parser.add_argument(
        '--disable-rag',
        action='store_true',
        help='禁用RAG功能'
    )
    
    parser.add_argument(
        '-k', '--k',
        type=int,
        default=8,
        metavar='K',
        help='RAG检索返回的文档数量 (默认: 8)'
    )
    
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=400,
        metavar='SIZE',
        help='文档分块大小，单位字符 (默认: 400 - 高精度场景)'
    )
    
    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=50,
        metavar='OVERLAP',
        help='文档分块重叠大小，单位字符 (默认: 50 - 高精度场景)'
    )
    
    parser.add_argument(
        '--rebuild-rag',
        action='store_true',
        help='强制重建RAG知识库'
    )
    
    # 调试和测试
    parser.add_argument(
        '--debug-prompt',
        action='store_true',
        help='显示完整的prompt内容（调试用）'
    )
    
    parser.add_argument(
        '--test-rag',
        type=str,
        metavar='QUERY',
        help='测试RAG搜索功能'
    )
    
    # 示例代码配置
    parser.add_argument(
        '--use-example-code',
        action='store_true',
        default=True,
        help='强制使用示例CAPL代码，无论RAG是否启用 (默认: 开启)'
    )
    
    parser.add_argument(
        '--no-use-example-code',
        action='store_false',
        dest='use_example_code',
        help='禁用示例CAPL代码，仅基于需求生成'
    )
    
    parser.add_argument(
        '--no-force-example',
        action='store_false',
        dest='force_example',
        help='不强制加载示例CAPL代码'
    )
    
    # 统计和摘要
    parser.add_argument(
        '--show-summary',
        action='store_true',
        default=True,
        help='显示生成摘要 (默认: 开启)'
    )
    
    parser.add_argument(
        '--hide-summary',
        action='store_false',
        dest='show_summary',
        help='隐藏生成摘要'
    )
    
    # 流式输出控制
    parser.add_argument(
        '--no-stream',
        action='store_true',
        help='禁用流式输出，使用传统阻塞式生成'
    )
    
    # 信息查询
    parser.add_argument(
        '--info',
        action='store_true',
        help='显示知识库信息'
    )
    
    parser.add_argument(
        '--search',
        type=str,
        metavar='QUERY',
        help='搜索知识库内容'
    )
    
    parser.add_argument(
        '--count-tokens',
        action='store_true',
        help='计算输入需求的token数量（包括prompt模板和RAG上下文）'
    )
    
    return parser


def load_config(args) -> CAPLGeneratorConfig:
    """根据命令行参数加载配置"""
    config = CAPLGeneratorConfig()
    
    # 应用命令行参数
    if args.disable_rag:
        config.enable_rag = False
    
    if args.k is not None:
        config.k = args.k
        
    if args.chunk_size is not None:
        config.chunk_size = args.chunk_size
        
    if args.chunk_overlap is not None:
        config.chunk_overlap = args.chunk_overlap
    
    if args.output:
        config.output_dir = Path(args.output)
    
    if args.api_type:
        config.api_type = args.api_type
    
    if args.api_url:
        config.api_base = args.api_url
    
    if args.model:
        config.model_name = args.model
    
    if args.use_example_code is not None:
        config.use_example_code = args.use_example_code
    
    return config

def load_requirements(input_source: str) -> str:
    """加载需求内容"""
    if not input_source:
        return ""
    
    # 检查是否为文件路径
    input_path = Path(input_source)
    if input_path.exists():
        with open(input_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    else:
        # 直接作为需求文本
        return input_source.strip()

def show_knowledge_base_info(config: CAPLGeneratorConfig):
    """显示知识库信息"""
    from ..generator import CAPLGenerator
    generator = CAPLGenerator(config)
    
    info = generator.get_knowledge_base_info()
    print("\n📊 知识库信息:")
    print(f"   启用状态: {'✅' if info['enabled'] else '❌'}")
    print(f"   知识库目录: {info['knowledge_base_dir']}")
    print(f"   向量数据库目录: {info['vector_db_dir']}")
    print(f"   已加载文档: {info['documents_loaded']} 个")

def search_knowledge_base(config: CAPLGeneratorConfig, query: str):
    """搜索知识库"""
    from ..generator import CAPLGenerator
    generator = CAPLGenerator(config)
    
    if not config.enable_rag:
        print("❌ 错误: 搜索功能需要启用RAG")
        return
    
    results = generator.search_knowledge_base(query)
    if results:
        print(f"\n🔍 搜索结果: 找到 {len(results)} 个相关文档")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. 📄 {result['source']} ({result['length']} 字符)")
            print(f"   摘要: {result['summary']}")
    else:
        print("🔍 未找到相关文档")

def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 检查输入参数
    if not args.input and not args.info and not args.search and not args.test_rag:
        parser.error("the following arguments are required: input (or use --info/--search/--test-rag)")
    
    try:
        # 加载配置
        config = load_config(args)
        
        # 信息查询模式
        if args.info:
            show_knowledge_base_info(config)
            return
        
        if args.search:
            search_knowledge_base(config, args.search)
            return
            
        # Token计数模式
        if args.count_tokens:
            if not args.input:
                print("❌ 错误: --count-tokens 需要指定输入文件")
                return 1
            
            requirement = load_requirements(args.input)
            
            from ..services.generator_service import CAPLGeneratorService
            service = CAPLGeneratorService(config)
            
            print("📊 计算prompt token数量...")
            tokens_info = service.calculate_prompt_tokens(requirement)
            
            print(f"\n📋 Token统计:")
            print(f"   系统提示词: {tokens_info['system_prompt_tokens']} tokens ({tokens_info['system_prompt_length']} 字符)")
            print(f"   需求内容: {tokens_info['requirement_tokens']} tokens ({tokens_info['requirement_length']} 字符)")
            print(f"   基础prompt: {tokens_info['base_prompt_tokens']} tokens ({tokens_info['base_prompt_length']} 字符)")
            
            if config.enable_rag:
                print(f"   RAG上下文: {tokens_info['rag_context_tokens']} tokens ({tokens_info['rag_context_length']} 字符)")
                print(f"   总prompt: {tokens_info['total_prompt_tokens']} tokens ({tokens_info['total_prompt_length']} 字符)")
            else:
                print(f"   总prompt: {tokens_info['base_prompt_tokens']} tokens (RAG未启用)")
            
            return
        
        # 使用高级服务
        from ..services.generator_service import CAPLGeneratorService
        service = CAPLGeneratorService(config)

        # 测试RAG搜索
        if args.test_rag:
            service.test_rag_search(args.test_rag, show_summary=True)
            return

        # 重建RAG知识库
        if args.rebuild_rag:
            service.process_file("dummy", rebuild_rag=True)
            return
        
        # 处理输入
        requirement = load_requirements(args.input)
        
        # 生成CAPL代码
        print(f"🚀 开始生成CAPL代码...")
        result = service.process_file(
            file_path=args.input,
            debug_prompt=args.debug_prompt,
            rebuild_rag=args.rebuild_rag,
            show_summary=args.show_summary,
            stream=not args.no_stream  # 默认启用流式输出，除非指定--no-stream
        )
        
        if result["status"] == "success":
            print(f"✅ 生成完成！")
            print(f"📁 Markdown文件: {result['file_path']}")
            print(f"📁 CAPL文件: {result['capl_file']}")
            
            if args.show_summary and result["stats"]:
                stats = result["stats"]
                print(f"\n📊 生成统计:")
                print(f"   用时: {stats['generation_time']} 秒")
                print(f"   代码长度: {stats['code_length']} 字符")
                print(f"   代码行数: {stats['code_lines']} 行")
                print(f"   估计Token: {stats['estimated_tokens']}")
                print(f"   Token速率: {stats['token_rate']} tokens/秒")
        else:
            print(f"❌ 生成失败: {result['error']}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  用户中断")
        return 0
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0