#!/usr/bin/env python3
"""
基于AI的CAPL测试用例智能评估系统
使用大语言模型从功能完整性角度评估测试用例质量
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import ollama
from dotenv import load_dotenv
from dataclasses import dataclass, asdict

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class AIEvaluationResult:
    """AI评估结果"""
    functional_completeness: float  # 功能完整性评分 (0-100)
    requirement_coverage: float     # 需求覆盖率 (0-100)
    test_logic_correctness: float   # 测试逻辑正确性 (0-100)
    edge_case_handling: float       # 边界条件处理 (0-100)
    error_handling: float           # 错误处理评估 (0-100)
    code_quality: float            # 代码质量 (0-100)
    missing_functionalities: List[str]  # 缺失的功能点
    redundant_tests: List[str]          # 冗余的测试
    improvement_suggestions: List[str]   # 改进建议
    detailed_analysis: str              # 详细分析

class CAPLAIEvaluator:
    """CAPL测试用例AI评估器"""
    
    def __init__(self, model_type: str = None, api_url: str = None, model_name: str = None, api_key: str = None):
        # 加载环境变量
        load_dotenv()
        
        # 从环境变量或参数获取配置
        self.model_type = model_type or os.getenv('API_TYPE', 'ollama')
        self.api_url = api_url or self._get_default_api_url()
        self.model_name = model_name or self._get_default_model()
        self.api_key = api_key or os.getenv('API_KEY')
        
        # 其他配置参数
        self.context_length = int(os.getenv('OLLAMA_CONTEXT_LENGTH', '8192'))
        self.max_tokens = int(os.getenv('OLLAMA_MAX_TOKENS', '4096'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.3'))
        self.top_p = float(os.getenv('TOP_P', '0.5'))
        
        self.system_prompt = """
        你是一个专业的汽车电子测试专家，专门评估CAPL测试用例的质量。
        请从功能完整性角度分析测试用例，重点关注：
        1. 是否覆盖了所有功能需求
        2. 测试逻辑是否正确
        3. 边界条件是否充分考虑
        4. 错误处理是否完善
        5. 测试用例是否冗余
        
        请提供具体的评分和改进建议。
        """
    
    def _get_default_api_url(self) -> str:
        """获取默认API地址"""
        if self.model_type == 'ollama':
            return os.getenv('API_URL', 'http://localhost:11434')
        else:  # openai兼容接口
            return os.getenv('API_URL', 'http://localhost:1234/v1')
    
    def _get_default_model(self) -> str:
        """获取默认模型名称"""
        if self.model_type == 'ollama':
            return os.getenv('OLLAMA_MODEL', 'qwen3:8b')
        else:  # openai兼容接口
            return os.getenv('OPENAI_MODEL', 'qwen/qwen3-8b')
    
    def read_file_content(self, file_path: str) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            return ""
    
    def extract_requirements_from_md(self, md_content: str) -> List[str]:
        """从需求文档提取功能需求"""
        requirements = []
        
        # 提取测试步骤中的功能描述
        lines = md_content.split('\n')
        for line in lines:
            if '|' in line and '测试步骤' not in line and '预期结果' not in line:
                parts = [part.strip() for part in line.split('|')]
                if len(parts) >= 4:
                    test_step = parts[2] if len(parts) > 2 else ""
                    expected_result = parts[3] if len(parts) > 3 else ""
                    if test_step and test_step != '测试步骤':
                        requirements.append({
                            'step': test_step,
                            'expected': expected_result,
                            'functional_requirement': self._extract_functional_requirement(test_step)
                        })
        
        return requirements
    
    def _extract_functional_requirement(self, test_step: str) -> str:
        """提取功能需求"""
        # 简化版本，实际可更复杂
        keywords = [
            '雨刷', 'wiper', '速度', 'speed', '位置', 'position',
            '间歇', 'intermittent', '低速', 'low speed', '高速', 'high speed',
            '停止', 'stop', '启动', 'start', '故障', 'fault'
        ]
        
        functional_req = []
        for keyword in keywords:
            if keyword.lower() in test_step.lower():
                functional_req.append(keyword)
        
        return " ".join(functional_req) if functional_req else test_step
    
    def create_evaluation_prompt(self, handwritten_content: str, generated_content: str, requirements: List[str]) -> str:
        """创建AI评估提示"""
        
        requirements_text = "\n".join([
            f"- {req['step']} -> 预期: {req['expected']}"
            for req in requirements
        ])
        
        prompt = f"""
        请作为CAPL测试专家，从功能完整性角度评估以下测试用例。
        
        ## 需求文档
        {requirements_text}
        
        ## 手写测试用例
        ```capl
        {handwritten_content}
        ```
        
        ## 生成测试用例
        ```capl
        {generated_content}
        ```
        
        请从以下维度进行评估，每项给出0-100的评分：
        
        1. **功能完整性** (functional_completeness): 是否覆盖了所有功能需求
        2. **需求覆盖率** (requirement_coverage): 需求文档中的功能点覆盖程度
        3. **测试逻辑正确性** (test_logic_correctness): 测试逻辑是否符合业务规则
        4. **边界条件处理** (edge_case_handling): 是否考虑了边界值和异常情况
        5. **错误处理** (error_handling): 对错误情况的处理是否完善
        6. **代码质量** (code_quality): 代码可读性、可维护性
        
        请以JSON格式返回评估结果：
        {{
            "functional_completeness": 分数,
            "requirement_coverage": 分数,
            "test_logic_correctness": 分数,
            "edge_case_handling": 分数,
            "error_handling": 分数,
            "code_quality": 分数,
            "missing_functionalities": ["缺失的功能点列表"],
            "redundant_tests": ["冗余的测试列表"],
            "improvement_suggestions": ["改进建议列表"],
            "detailed_analysis": "详细分析文本"
        }}
        """
        
        return prompt
    
    def call_ai_model(self, prompt: str) -> Dict[str, Any]:
        """调用AI模型进行评估"""
        try:
            if self.model_type == "ollama":
                return self._call_ollama(prompt)
            else:  # openai兼容接口
                return self._call_openai_compatible(prompt)
        except Exception as e:
            print(f"AI模型调用失败: {e}")
            return self._get_default_result()
    
    def _call_openai_compatible(self, prompt: str) -> Dict[str, Any]:
        """调用OpenAI兼容接口"""
        # 构建完整的API端点URL
        if self.api_url.endswith('/v1'):
            api_url = f"{self.api_url}/chat/completions"
        elif not self.api_url.endswith('/chat/completions'):
            api_url = f"{self.api_url.rstrip('/')}/chat/completions"
        else:
            api_url = self.api_url
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # 清理可能的markdown代码块标记
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            return json.loads(content.strip())
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"连接失败 - 请确保服务已启动 (运行 'ollama serve' 或启动 LM Studio): {e}")
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"请求超时 - 请检查网络连接和服务状态: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"AI响应格式错误: {e}")
        except Exception as e:
            error_msg = str(e)
            if "Connection" in error_msg or "connect" in error_msg.lower():
                raise ConnectionError(f"连接失败 - 请确保服务已启动并正在监听正确的端口: {e}")
            elif "404" in error_msg:
                raise ValueError(f"模型未找到 - 请确保模型已加载: {e}")
            else:
                raise RuntimeError(f"AI调用失败: {e}")
    
    def _call_ollama(self, prompt: str) -> Dict[str, Any]:
        """调用Ollama本地模型"""
        try:
            # 使用官方 ollama 库
            ollama_host = self.api_url.rstrip('/')
            client = ollama.Client(host=ollama_host)
            
            response = client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "num_ctx": self.context_length,
                    "num_predict": self.max_tokens
                }
            )
            
            content = response['message']['content']
            
            # 清理可能的markdown代码块标记
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            return json.loads(content.strip())
        except Exception as e:
            error_msg = str(e)
            if "Connection" in error_msg or "connect" in error_msg.lower():
                raise ConnectionError(f"连接失败 - 请确保Ollama服务已启动 (运行 'ollama serve'): {e}")
            elif "404" in error_msg:
                raise ValueError(f"模型未找到 - 请运行 'ollama run {self.model_name}' 加载模型: {e}")
            else:
                raise RuntimeError(f"Ollama调用失败: {e}")
    
    def _get_default_result(self) -> Dict[str, Any]:
        """获取默认评估结果"""
        return {
            "functional_completeness": 50.0,
            "requirement_coverage": 50.0,
            "test_logic_correctness": 50.0,
            "edge_case_handling": 50.0,
            "error_handling": 50.0,
            "code_quality": 50.0,
            "missing_functionalities": ["无法连接AI模型进行评估"],
            "redundant_tests": [],
            "improvement_suggestions": ["请检查AI模型配置"],
            "detailed_analysis": "由于AI模型调用失败，无法提供详细分析。请检查网络连接和API配置。"
        }
    
    def evaluate_testcase(self, testcase_id: str, handwritten_path: str, generated_path: str, requirement_path: str) -> AIEvaluationResult:
        """评估单个测试用例"""
        
        # 读取文件内容
        handwritten_content = self.read_file_content(handwritten_path)
        generated_content = self.read_file_content(generated_path)
        requirement_content = self.read_file_content(requirement_path)
        
        if not all([handwritten_content, generated_content, requirement_content]):
            print("❌ 部分文件内容为空或无法读取")
            return AIEvaluationResult(**self._get_default_result())
        
        # 提取需求
        requirements = self.extract_requirements_from_md(requirement_content)
        
        # 创建评估提示
        prompt = self.create_evaluation_prompt(handwritten_content, generated_content, requirements)
        
        # 调用AI模型评估
        ai_result = self.call_ai_model(prompt)
        
        return AIEvaluationResult(**ai_result)
    
    def generate_detailed_report(self, result: AIEvaluationResult, testcase_id: str) -> str:
        """生成详细评估报告"""
        
        # 计算加权综合评分
        weighted_score = (result.functional_completeness * 0.25 + 
                         result.requirement_coverage * 0.25 + 
                         result.test_logic_correctness * 0.20 + 
                         result.edge_case_handling * 0.15 + 
                         result.error_handling * 0.10 + 
                         result.code_quality * 0.05)
        rating = self._get_rating(weighted_score)
        
        report = f"""\# CAPL测试用例AI评估报告 - 测试用例 {testcase_id}

## 综合评分
| 评估维度 | 得分 | 评级 |
|----------|------|------|
| 功能完整性 | {result.functional_completeness:.1f}/100 | {self._get_rating(result.functional_completeness)} |
| 需求覆盖率 | {result.requirement_coverage:.1f}/100 | {self._get_rating(result.requirement_coverage)} |
| 测试逻辑正确性 | {result.test_logic_correctness:.1f}/100 | {self._get_rating(result.test_logic_correctness)} |
| 边界条件处理 | {result.edge_case_handling:.1f}/100 | {self._get_rating(result.edge_case_handling)} |
| 错误处理 | {result.error_handling:.1f}/100 | {self._get_rating(result.error_handling)} |
| 代码质量 | {result.code_quality:.1f}/100 | {self._get_rating(result.code_quality)} |

## 综合评分: {weighted_score:.1f}/100 ({rating})

## 详细分析
{result.detailed_analysis}

"""
        
        if result.missing_functionalities:
            report += f"""
## 缺失的功能点
{chr(10).join([f"- {func}" for func in result.missing_functionalities])}
"""
        
        if result.redundant_tests:
            report += f"""
## 冗余的测试
{chr(10).join([f"- {test}" for test in result.redundant_tests])}
"""
        
        if result.improvement_suggestions:
            report += f"""
## 改进建议
{chr(10).join([f"- {suggestion}" for suggestion in result.improvement_suggestions])}
"""
        
        return report
    
    def _get_rating(self, score: float) -> str:
        """根据分数返回评级"""
        if score >= 90:
            return "优秀"
        elif score >= 80:
            return "良好"
        elif score >= 70:
            return "中等"
        elif score >= 60:
            return "及格"
        else:
            return "需改进"
    
    def save_evaluation_result(self, result: AIEvaluationResult, testcase_id: str, output_dir: str = "results"):
        """保存评估结果"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 生成年月日时分秒格式的时间戳
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 保存JSON结果
        json_file = output_path / f"ai_evaluation_{testcase_id}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(result), f, ensure_ascii=False, indent=2)
        
        # 保存详细报告
        report_file = output_path / f"ai_report_{testcase_id}_{timestamp}.md"
        report = self.generate_detailed_report(result, testcase_id)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📊 AI评估结果已保存:")
        print(f"  JSON文件: {json_file}")
        print(f"  报告文件: {report_file}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CAPL测试用例AI评估系统')
    parser.add_argument('testcase_id', help='测试用例ID')
    parser.add_argument('--model-type', choices=['ollama', 'openai'], default=None, help='AI模型类型 (ollama 或 openai兼容接口)')
    parser.add_argument('--api-url', help='API服务地址')
    parser.add_argument('--model', help='使用的模型名称')
    parser.add_argument('--context-length', type=int, help='上下文长度 (tokens)')
    parser.add_argument('--max-tokens', type=int, help='最大输出tokens数')
    parser.add_argument('--temperature', type=float, help='生成温度 (0.0-1.0)')
    parser.add_argument('--top-p', type=float, help='top-p采样参数 (0.0-1.0)')
    
    args = parser.parse_args()
    
    # 查找测试用例文件
    base_dir = Path("/Users/robertsong/Downloads/code/testcase_AI_generator")
    
    handwritten_path = base_dir / "test_output" / f"testcase_id_{args.testcase_id}.can"
    generated_path = base_dir / "test_output" / f"qualification_*{args.testcase_id}*.can"
    requirement_path = base_dir / "pdf_converter" / "testcases" / f"qualification_*{args.testcase_id}*.md"
    
    # 查找生成的测试用例文件
    generated_files = list(base_dir.glob(f"test_output/qualification*{args.testcase_id}*.can"))
    requirement_files = list(base_dir.glob(f"pdf_converter/testcases/qualification*{args.testcase_id}*.md"))
    
    if not generated_files:
        print(f"❌ 未找到生成的测试用例文件")
        return
    
    if not requirement_files:
        print(f"❌ 未找到需求文档")
        return
    
    generated_path = generated_files[0]
    requirement_path = requirement_files[0]
    
    if not handwritten_path.exists():
        print(f"❌ 未找到手写测试用例: {handwritten_path}")
        return
    
    # 初始化评估器
    evaluator = CAPLAIEvaluator(
        model_type=args.model_type,
        api_url=args.api_url,
        model_name=args.model
    )
    
    # 执行评估
    print(f"🤖 开始AI评估测试用例 {args.testcase_id}...")
    result = evaluator.evaluate_testcase(
        args.testcase_id,
        str(handwritten_path),
        str(generated_path),
        str(requirement_path)
    )
    
    # 保存结果
    evaluator.save_evaluation_result(result, args.testcase_id)
    
    # 打印简要结果
    print(f"\n📊 AI评估完成!")
    print(f"功能完整性: {result.functional_completeness:.1f}/100")
    print(f"需求覆盖率: {result.requirement_coverage:.1f}/100")
    print(f"测试逻辑正确性: {result.test_logic_correctness:.1f}/100")

if __name__ == "__main__":
    main()