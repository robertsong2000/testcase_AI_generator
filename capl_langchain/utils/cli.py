"""命令行接口工具"""

import argparse
import sys
from pathlib import Path

from ..generator import CAPLGenerator
from ..config.config import CAPLGeneratorConfig


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="基于LangChain的CAPL代码生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s test_requirements.md
  %(prog)s "测试雨刮器低速功能" --output test_wiper.cin
  %(prog)s requirements.txt --disable-rag
  %(prog)s test.md --force-example
  %(prog)s "测试车门锁功能" --search "车门锁"
        """
    )
    
    parser.add_argument(
        'input',
        nargs='?',  # 让参数变为可选
        help='输入文件路径或测试需求文本'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='输出文件路径（可选）'
    )
    
    parser.add_argument(
        '--disable-rag',
        action='store_true',
        help='禁用RAG知识库检索'
    )
    
    parser.add_argument(
        '--force-example',
        action='store_true',
        default=None,
        help='强制加载示例代码文件（覆盖配置文件设置）'
    )
    
    parser.add_argument(
        '--no-force-example',
        action='store_false',
        dest='force_example',
        help='不强制加载示例代码文件（覆盖配置文件设置）'
    )
    
    parser.add_argument(
        '--search',
        help='搜索知识库并显示结果，不生成代码'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='显示知识库信息'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细输出'
    )
    
    return parser


def load_requirements(input_path: str) -> str:
    """加载测试需求"""
    input_file = Path(input_path)
    
    if input_file.exists():
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            sys.exit(1)
    else:
        # 直接使用输入作为需求文本
        return input_path.strip()


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 检查是否需要input参数
    if not args.input and not (args.info or args.search):
        parser.error("需要提供input参数或使用--info/--search选项")
    
    # 创建配置
    config = CAPLGeneratorConfig()
    
    # 处理命令行参数
    if args.disable_rag:
        config.enable_rag = False
    
    # 创建生成器
    generator = CAPLGenerator(config)
    
    try:
        if args.info:
            # 显示知识库信息
            info = generator.get_knowledge_base_info()
            print("\n📊 知识库信息:")
            print(f"   启用状态: {'✅' if info['enabled'] else '❌'}")
            print(f"   知识库目录: {info['knowledge_base_dir']}")
            print(f"   向量数据库目录: {info['vector_db_dir']}")
            print(f"   已加载文档: {info['documents_loaded']} 个")
            
        elif args.search:
            # 搜索知识库
            if not config.enable_rag:
                print("❌ 错误: 搜索功能需要启用RAG")
                sys.exit(1)
                
            results = generator.search_knowledge_base(args.search)
            if results:
                print(f"\n🔍 搜索结果: 找到 {len(results)} 个相关文档")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. 📄 {result['source']} ({result['length']} 字符)")
                    print(f"   摘要: {result['summary']}")
            else:
                print("🔍 未找到相关文档")
                
        elif args.input:
            # 生成代码
            requirements = load_requirements(args.input)
            
            if args.verbose:
                print(f"\n📋 处理需求: {requirements[:100]}...")
            
            code = generator.generate_code(requirements, args.output)
            
            if args.verbose:
                print(f"\n📄 生成的代码:\n{code[:500]}...")
    
    except KeyboardInterrupt:
        print("\n⏹️  用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()