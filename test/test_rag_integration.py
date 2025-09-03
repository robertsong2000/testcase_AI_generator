#!/usr/bin/env python3
"""
LangChain RAG集成测试文件 - 优化版
演示如何在CAPL代码生成中使用RAG功能，并将结果保存到子目录
"""

import os
import sys
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from capl_langchain.services.generator_service import CAPLGenerator
from capl_langchain.config.config import CAPLGeneratorConfig

def setup_output_directory():
    """设置输出目录结构"""
    test_dir = project_root / "test"
    output_dirs = {
        'rag_tests': test_dir / "rag_output" / "tests",
        'comparisons': test_dir / "rag_output" / "comparisons",
        'custom': test_dir / "rag_output" / "custom"
    }
    
    # 创建所有子目录
    for dir_path in output_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return output_dirs

def test_rag_integration():
    """测试RAG在CAPL代码生成中的集成使用"""
    print("🧪 测试RAG在CAPL代码生成中的集成...")
    
    try:
        # 设置输出目录
        output_dirs = setup_output_directory()
        
        # 创建启用RAG的配置
        config = CAPLGeneratorConfig()
        config.enable_rag = True
        
        # 创建生成器
        generator = CAPLGenerator(config)
        
        print("🔄 初始化生成器（包含RAG）...")
        generator.initialize()
        
        # 测试用例需求
        test_requirements = [
            "创建一个雨刷器间歇模式测试用例",
            "测试CAN消息周期发送功能",
            "验证低功耗模式切换逻辑",
            "测试雨刷器速度调节功能"
        ]
        
        print(f"\n🎯 开始生成测试用例...")
        print(f"📁 输出目录: {output_dirs['rag_tests']}")
        
        generated_files = []
        for i, requirement in enumerate(test_requirements, 1):
            print(f"\n{i}. 需求: {requirement}")
            print("-" * 50)
            
            try:
                # 使用RAG生成CAPL代码
                capl_code = generator.generate_code(requirement)
                
                # 分析生成的代码
                lines = capl_code.count('\n') + 1
                chars = len(capl_code)
                
                print(f"   ✅ 生成成功!")
                print(f"   📊 代码行数: {lines}")
                print(f"   📊 字符数: {chars}")
                
                # 保存代码到子目录
                output_file = output_dirs['rag_tests'] / f"rag_test_{i:02d}_{Path(requirement).stem[:20].replace(' ', '_')}.capl"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"// 需求: {requirement}\n")
                    f.write(f"// 使用RAG生成 - 测试文件 #{i}\n")
                    f.write("=" * 60 + "\n")
                    f.write("// 生成时间: " + __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(capl_code)
                
                generated_files.append(output_file)
                print(f"   💾 已保存: {output_file.name}")
                
            except Exception as e:
                print(f"   ❌ 生成失败: {e}")
        
        return generated_files
                
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_rag_vs_no_rag():
    """对比测试：使用RAG vs 不使用RAG"""
    print("\n🧪 对比测试：RAG vs 无RAG...")
    
    try:
        output_dirs = setup_output_directory()
        requirement = "创建一个雨刷器间歇模式测试用例"
        
        results = {}
        
        # 测试1: 不使用RAG
        print("\n1. 不使用RAG生成...")
        config_no_rag = CAPLGeneratorConfig()
        config_no_rag.enable_rag = False
        
        generator_no_rag = CAPLGenerator(config_no_rag)
        generator_no_rag.initialize()
        
        start_time = __import__('time').time()
        code_no_rag = generator_no_rag.generate_code(requirement)
        no_rag_time = __import__('time').time() - start_time
        
        lines_no_rag = code_no_rag.count('\n') + 1
        chars_no_rag = len(code_no_rag)
        
        results['no_rag'] = {
            'code': code_no_rag,
            'lines': lines_no_rag,
            'chars': chars_no_rag,
            'time': no_rag_time
        }
        
        print(f"   📊 代码行数: {lines_no_rag}")
        print(f"   ⏱️  生成时间: {no_rag_time:.2f}秒")
        
        # 测试2: 使用RAG
        print("\n2. 使用RAG生成...")
        config_rag = CAPLGeneratorConfig()
        config_rag.enable_rag = True
        
        generator_rag = CAPLGenerator(config_rag)
        generator_rag.initialize()
        
        start_time = __import__('time').time()
        code_rag = generator_rag.generate_code(requirement)
        rag_time = __import__('time').time() - start_time
        
        lines_rag = code_rag.count('\n') + 1
        chars_rag = len(code_rag)
        
        results['with_rag'] = {
            'code': code_rag,
            'lines': lines_rag,
            'chars': chars_rag,
            'time': rag_time
        }
        
        print(f"   📊 代码行数: {lines_rag}")
        print(f"   ⏱️  生成时间: {rag_time:.2f}秒")
        
        # 对比结果
        print("\n📊 对比结果:")
        print(f"   无RAG: {lines_no_rag}行, {chars_no_rag}字符, {no_rag_time:.2f}秒")
        print(f"   有RAG: {lines_rag}行, {chars_rag}字符, {rag_time:.2f}秒")
        print(f"   行数差异: +{lines_rag - lines_no_rag} ({((lines_rag-lines_no_rag)/lines_no_rag*100):+.1f}%)")
        print(f"   时间差异: +{rag_time - no_rag_time:.2f}秒")
        
        # 保存对比文件
        timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
        
        no_rag_file = output_dirs['comparisons'] / f"comparison_no_rag_{timestamp}.capl"
        with open(no_rag_file, 'w', encoding='utf-8') as f:
            f.write("// 不使用RAG生成的代码\n")
            f.write("// " + "=" * 50 + "\n")
            f.write(f"// 需求: {requirement}\n")
            f.write(f"// 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(results['no_rag']['code'])
            
        rag_file = output_dirs['comparisons'] / f"comparison_with_rag_{timestamp}.capl"
        with open(rag_file, 'w', encoding='utf-8') as f:
            f.write("// 使用RAG生成的代码\n")
            f.write("// " + "=" * 50 + "\n")
            f.write(f"// 需求: {requirement}\n")
            f.write(f"// 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(results['with_rag']['code'])
            
        # 保存对比报告
        report_file = output_dirs['comparisons'] / f"comparison_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("RAG vs 无RAG对比报告\n")
            f.write("=" * 50 + "\n")
            f.write(f"测试需求: {requirement}\n")
            f.write(f"测试时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"无RAG结果:\n")
            f.write(f"  代码行数: {lines_no_rag}\n")
            f.write(f"  字符数: {chars_no_rag}\n")
            f.write(f"  生成时间: {no_rag_time:.2f}秒\n\n")
            f.write(f"有RAG结果:\n")
            f.write(f"  代码行数: {lines_rag}\n")
            f.write(f"  字符数: {chars_rag}\n")
            f.write(f"  生成时间: {rag_time:.2f}秒\n\n")
            f.write(f"改进幅度:\n")
            f.write(f"  行数: +{lines_rag - lines_no_rag} ({((lines_rag-lines_no_rag)/lines_no_rag*100):+.1f}%)\n")
            f.write(f"  时间: +{rag_time - no_rag_time:.2f}秒\n")
        
        print(f"   💾 对比文件已保存到: {output_dirs['comparisons']}")
        
        return [no_rag_file, rag_file, report_file]
        
    except Exception as e:
        print(f"❌ 对比测试失败: {e}")
        return []

def test_custom_requirement():
    """测试自定义需求"""
    print("\n🧪 测试自定义需求...")
    
    try:
        output_dirs = setup_output_directory()
        
        # 高级自定义需求
        custom_requirement = """
        创建一个完整的测试用例，验证当车速超过30km/h时，
        雨刷器自动从间歇模式切换到连续模式的功能。
        
        前置条件：
        - 车辆电源处于ON状态
        - 雨刷器开关处于间歇模式位置
        - 初始车速为25km/h
        
        测试步骤：
        1. 设置车速信号为25km/h
        2. 激活雨刷器间歇模式（间隔2秒）
        3. 通过CAN总线发送车速增加信号至35km/h
        4. 监控雨刷器状态变化
        5. 验证在3秒内切换到连续模式
        6. 记录切换时间和相关CAN消息
        
        验证条件：
        - 车速超过30km/h时触发切换
        - 切换响应时间不超过3秒
        - 发送正确的状态反馈CAN消息
        - 记录完整的测试日志
        """
        
        print(f"📋 高级自定义需求已加载")
        
        config = CAPLGeneratorConfig()
        config.enable_rag = True
        
        generator = CAPLGenerator(config)
        generator.initialize()
        
        start_time = __import__('time').time()
        capl_code = generator.generate_capl_code(custom_requirement)
        generation_time = __import__('time').time() - start_time
        
        lines = capl_code.count('\n') + 1
        chars = len(capl_code)
        
        # 保存完整代码到自定义目录
        timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dirs['custom'] / f"advanced_custom_test_{timestamp}.capl"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("/*\n")
            f.write(" * 高级自定义需求生成的CAPL测试用例\n")
            f.write(" * " + "=" * 60 + "\n")
            f.write(f" * 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f" * 代码行数: {lines}\n")
            f.write(f" * 字符数: {chars}\n")
            f.write(f" * 生成耗时: {generation_time:.2f}秒\n")
            f.write(" */\n")
            f.write("=" * 80 + "\n\n")
            f.write(capl_code)
        
        print(f"✅ 高级自定义需求生成完成!")
        print(f"📊 代码行数: {lines}")
        print(f"📊 字符数: {chars}")
        print(f"⏱️  生成耗时: {generation_time:.2f}秒")
        print(f"💾 已保存: {output_file.name}")
        
        return [output_file]
        
    except Exception as e:
        print(f"❌ 自定义需求测试失败: {e}")
        return []

def display_directory_structure(output_dirs):
    """显示生成的目录结构"""
    print("\n📁 生成的目录结构:")
    print("test/")
    print("└── rag_output/")
    
    for category, dir_path in output_dirs.items():
        if dir_path.exists():
            files = list(dir_path.glob("*.capl")) + list(dir_path.glob("*.txt"))
            if files:
                print(f"    ├── {category}/")
                for file in sorted(files):
                    print(f"    │   ├── {file.name} ({file.stat().st_size} bytes)")
            else:
                print(f"    ├── {category}/ (空)")

def main():
    """主测试函数"""
    print("=" * 80)
    print("LangChain RAG集成测试 - 优化版")
    print("=" * 80)
    
    # 设置输出目录
    output_dirs = setup_output_directory()
    
    # 清空旧的输出目录（可选）
    rag_output_dir = project_root / "test" / "rag_output"
    if rag_output_dir.exists():
        print("🧹 清理旧的输出文件...")
        for subdir in rag_output_dir.iterdir():
            if subdir.is_dir():
                for file in subdir.glob("*"):
                    file.unlink()
    
    # 运行所有测试
    all_files = []
    
    # 测试1: RAG集成使用
    print("\n🚀 开始测试1: RAG集成使用...")
    files1 = test_rag_integration()
    all_files.extend(files1)
    
    # 测试2: RAG vs 无RAG对比
    print("\n🚀 开始测试2: RAG对比测试...")
    files2 = test_rag_vs_no_rag()
    all_files.extend(files2)
    
    # 测试3: 自定义需求
    print("\n🚀 开始测试3: 高级自定义需求...")
    files3 = test_custom_requirement()
    all_files.extend(files3)
    
    # 显示目录结构
    display_directory_structure(output_dirs)
    
    # 总结
    print("\n" + "=" * 80)
    print("测试结果总结:")
    print(f"总生成文件数: {len(all_files)}")
    print(f"测试目录: {project_root / 'test' / 'rag_output'}")
    
    if all_files:
        total_size = sum(f.stat().st_size for f in all_files)
        print(f"总文件大小: {total_size} bytes")
        print("\n✅ 所有RAG集成测试完成！")
        return 0
    else:
        print("\n⚠️  没有生成任何文件")
        return 1

if __name__ == "__main__":
    exit(main())