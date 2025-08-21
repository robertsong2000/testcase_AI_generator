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
    testspec_coverage: float     # 测试覆盖率 (0-100)
    test_logic_correctness: float   # 测试逻辑正确性 (0-100)
    edge_case_handling: float       # 边界条件处理 (0-100)
    error_handling: float           # 错误处理评估 (0-100)
    code_quality: float            # 代码质量 (0-100)
    missing_functionalities: List[str]  # 缺失的功能点
    redundant_tests: List[str]          # 冗余的测试
    improvement_suggestions: List[str]   # 改进建议
    detailed_analysis: str              # 详细分析
    scoring_basis: Dict[str, str] = None  # 评分依据，可选字段

class CAPLAIEvaluator:
    """CAPL测试用例AI评估器"""
    
    def __init__(self, model_type: str = None, api_url: str = None, model_name: str = None, api_key: str = None, verbose: bool = False):
        # 加载环境变量
        load_dotenv()
        
        # 从环境变量或参数获取配置
        self.model_type = model_type or os.getenv('API_TYPE', 'ollama')
        self.api_url = api_url or self._get_default_api_url()
        self.model_name = model_name or self._get_default_model()
        self.api_key = api_key or os.getenv('API_KEY')
        self.verbose = verbose
        
        # 优化参数以提高一致性
        self.context_length = int(os.getenv('OLLAMA_CONTEXT_LENGTH', '8192'))
        self.max_tokens = int(os.getenv('OLLAMA_MAX_TOKENS', '4096'))
        self.temperature = float(os.getenv('EVALUATOR_TEMPERATURE', '0.05'))  # 极低温度确保一致性
        self.top_p = float(os.getenv('EVALUATOR_TOP_P', '0.8'))
        
        # 打印所有参数值用于调试
        print("📊 AI评估器配置参数:")
        print(f"   模型类型: {self.model_type}")
        print(f"   API地址: {self.api_url}")
        print(f"   模型名称: {self.model_name}")
        print(f"   API密钥: {'已配置' if self.api_key else '未配置'}")
        print(f"   上下文长度: {self.context_length}")
        print(f"   最大token数: {self.max_tokens}")
        print(f"   温度参数: {self.temperature}")
        print(f"   Top-P参数: {self.top_p}")
        print(f"   详细模式: {self.verbose}")
        print("-" * 50)
        
        self.system_prompt = """
        你是一个严格的汽车电子测试专家，专门评估CAPL测试用例的质量。请严格按照以下标准进行评分，确保每次评估的一致性。

        ## 评分标准（严格按照以下标准评分）

        ### 功能完整性评分标准：
        - 100分：完全覆盖所有功能测试，包括主要功能、次要功能、边缘功能
        - 90-99分：基本覆盖所有主要功能，少量次要功能缺失
        - 80-89分：覆盖主要功能，但有明显功能缺失
        - 70-79分：部分主要功能未覆盖
        - 60-69分：大量功能测试缺失
        - <60分：功能覆盖严重不足

        ### 测试覆盖率评分标准：
        - 100分：测试文档中100%功能点都有对应测试
        - 95-99分：测试文档中95-99%功能点有对应测试
        - 90-94分：测试文档中90-94%功能点有对应测试
        - 85-89分：测试文档中85-89%功能点有对应测试
        - 80-84分：测试文档中80-84%功能点有对应测试
        - <80分：测试覆盖率低于80%

        ### 测试逻辑正确性评分标准：
        - 100分：测试逻辑完全符合业务规则，无任何逻辑错误
        - 90-99分：测试逻辑正确，仅存在极轻微缺陷
        - 80-89分：测试逻辑基本正确，存在轻微逻辑缺陷
        - 70-79分：测试逻辑存在明显问题，可能影响测试结果
        - 60-69分：测试逻辑存在较多问题
        - <60分：测试逻辑存在严重错误

        ### 边界条件处理评分标准：
        - 100分：充分考虑所有边界条件（极值、临界值、异常输入）
        - 90-99分：考虑主要边界条件，极少量边界情况未覆盖
        - 80-89分：考虑主要边界条件，少量边界情况未覆盖
        - 70-79分：边界条件考虑不足，存在明显遗漏
        - 60-69分：边界条件考虑严重不足
        - <60分：几乎未考虑边界条件

        ### 错误处理评分标准：
        - 100分：完善的错误处理机制，能优雅处理所有异常情况
        - 90-99分：能处理绝大部分异常情况
        - 80-89分：能处理常见异常情况
        - 70-79分：错误处理存在缺陷，部分异常场景未考虑
        - 60-69分：错误处理严重不足
        - <60分：错误处理机制缺失

        ### 代码质量评分标准：
        - 100分：代码结构清晰，命名规范，注释完善，高度可维护
        - 90-99分：代码结构良好，基本规范，可读性很好
        - 80-89分：代码结构良好，基本规范，可读性较好
        - 70-79分：代码结构一般，可读性有待提高
        - 60-69分：代码结构较差，难以理解
        - <60分：代码结构混乱，无法维护

        ## 评估要求
        1. 严格按照上述标准评分，不要主观判断
        2. 每次评分必须使用相同标准
        3. 先分析再评分，确保评分准确性
        4. 提供具体评分依据和改进建议

        请返回JSON格式结果，包含具体评分依据。
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
    
    def extract_testspecs_from_md(self, md_content: str) -> List[Dict[str, str]]:
        """从测试用例文档提取功能测试
        
        针对测试用例文档的特点：
        1. 包含测试步骤和执行说明
        2. 没有明确的预期结果列
        3. 通过操作描述和验证点体现测试
        """
        import re
        testspecs = []
        
        # 提取测试步骤表中的功能描述
        in_test_steps = False
        lines = md_content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 检测测试步骤表的开始
            if '|' in line and ('测试步骤' in line or 'Test Step' in line or 'Description' in line):
                in_test_steps = True
                continue
                
            # 处理测试步骤表中的行
            if in_test_steps and '|' in line and '---' not in line:
                parts = [part.strip() for part in line.split('|') if part.strip()]
                if len(parts) >= 3:
                    timestamp = parts[0] if len(parts) >= 1 else ""
                    test_step = parts[1] if len(parts) >= 2 else ""
                    description = parts[2] if len(parts) >= 3 else ""
                    
                    # 过滤无效行
                    if (test_step and 
                        test_step not in ['测试步骤', 'Test Step', 'Description'] and
                        '---' not in test_step and
                        not re.match(r'^\d+\.?\d*$', test_step) and
                        not test_step.startswith('[')):
                        
                        # 构建功能测试描述
                        functional_desc = self._build_functional_testspec(test_step, description)
                        
                        testspecs.append({
                            'step': test_step,
                            'expected': description,
                            'functional_testspec': functional_desc
                        })
            
            # 提取独立的测试操作
            elif re.search(r'(TS_|Set|Check|Wait)[A-Z]', line) and '|' not in line:
                # 提取操作描述
                match = re.search(r'([A-Z][a-zA-Z0-9_]+)\s*[:：]?\s*(.+)', line)
                if match:
                    operation = match.group(1)
                    description = match.group(2)
                    
                    functional_desc = self._build_functional_testspec(operation, description)
                    
                    testspecs.append({
                        'step': operation,
                        'expected': description,
                        'functional_testspec': functional_desc
                    })
        
        return testspecs
    
    def _build_functional_testspec(self, test_step: str, description: str = "") -> str:
        """构建功能测试描述
        
        从测试步骤和操作描述中提取核心功能测试
        """
        import re
        
        # 合并测试步骤和描述进行统一分析
        combined_text = f"{test_step} {description}".strip()
        
        # 定义功能关键词映射
        feature_keywords = {
            'wiper_control': ['wiper', '雨刷', 'Wiper'],
            'speed_control': ['speed', '速度', 'Speed'],
            'position_control': ['position', '位置', 'Position', 'stop'],
            'mode_control': ['intermittent', '间歇', 'low', 'high', '低速', '高速'],
            'fault_handling': ['fault', 'failure', '故障', '错误', 'blocked'],
            'timing_control': ['wait', '等待', 'delay', '延时']
        }
        
        # 提取核心功能
        features = []
        for feature, keywords in feature_keywords.items():
            for keyword in keywords:
                if keyword.lower() in combined_text.lower():
                    features.append(feature)
                    break
        
        # 如果没有匹配到功能关键词，使用简化描述
        if not features:
            # 清理测试步骤，移除TS_前缀等
            clean_step = re.sub(r'^TS_', '', test_step)
            clean_step = re.sub(r'([A-Z])', r' \1', clean_step).strip()
            return clean_step
        
        # 构建功能测试描述
        feature_map = {
            'wiper_control': '雨刷控制',
            'speed_control': '速度控制',
            'position_control': '位置控制',
            'mode_control': '模式控制',
            'fault_handling': '故障处理',
            'timing_control': '时序控制'
        }
        
        return " + ".join([feature_map.get(f, f) for f in features])
    
    def create_evaluation_prompt(self, refwritten_content: str, generated_content: str, testspecs: List[str]) -> str:
        """创建AI评估提示"""
        
        testspecs_text = "\n".join([
            f"{i+1}. 步骤: {req['step']} -> 详细步骤: {req['expected']}"
            for i, req in enumerate(testspecs)
        ])
        
        prompt = f"""
        请作为CAPL测试专家，严格按照评分标准评估以下测试用例。请逐项分析后再给出准确评分。

        ## 测试文档（共{len(testspecs)}项测试）
        {testspecs_text}

        ## 参考测试用例
        ```capl
        {refwritten_content}
        ```

        ## 生成测试用例
        ```capl
        {generated_content}
        ```

        ## 评估任务
        请严格按照之前定义的评分标准，从以下6个维度进行评估：

        ### 评估步骤：
        1. **功能完整性分析**：对照测试文档，逐一检查每个测试项目是否被测试
        2. **测试覆盖率统计**：计算被测试项目占总测试的比例
        3. **测试逻辑验证**：验证测试步骤是否符合业务逻辑
        4. **边界条件检查**：检查是否包含边界值测试（如极值、临界值）
        5. **错误处理评估**：检查异常情况的测试覆盖
        6. **代码质量评估**：评估代码可读性、结构清晰度

        ### 评分要求：
        - 每项评分必须有明确依据
        - 评分必须为整数（如85，不是85.5）
        - 严格按照评分标准，不得随意调整

        ## 输出格式（必须严格遵循）
        请以以下JSON格式返回评估结果：
        {{
            "functional_completeness": 整数分数,
            "testspec_coverage": 整数分数,
            "test_logic_correctness": 整数分数,
            "edge_case_handling": 整数分数,
            "error_handling": 整数分数,
            "code_quality": 整数分数,
            "missing_functionalities": ["具体缺失的功能点1", "具体缺失的功能点2", ...],
            "redundant_tests": ["冗余测试1", "冗余测试2", ...],
            "improvement_suggestions": ["具体改进建议1", "具体改进建议2", ...],
            "detailed_analysis": "详细分析文本，包含评分依据",
            "scoring_basis": {{
                "functional_completeness": "评分具体依据",
                "testspec_coverage": "评分具体依据",
                "test_logic_correctness": "评分具体依据",
                "edge_case_handling": "评分具体依据",
                "error_handling": "评分具体依据",
                "code_quality": "评分具体依据"
            }}
        }}

        ## 注意事项
        1. 先分析每个测试项目是否被测试，再给出功能完整性评分
        2. 计算实际覆盖率百分比，再给出测试覆盖率评分
        3. 每项评分必须基于具体事实，不能主观判断
        4. 确保评分的一致性，同样的情况必须给同样的分数
        """
        
        return prompt
    
    def call_ai_model(self, prompt: str) -> Dict[str, Any]:
        """调用AI模型进行评估，增加一致性处理"""
        try:
            print(f"   📡 调用AI模型: {self.model_type}")
            print(f"   🎯 目标模型: {self.model_name}")
            print(f"   🌡️  温度参数: {self.temperature}")
            
            # 根据verbose参数决定是否打印完整的prompt内容
            if self.verbose:
                print("=" * 80)
                print("📋 发送给大模型的完整PROMPT内容:")
                print("=" * 80)
                print(prompt)
                print("=" * 80)
                print("📋 PROMPT内容结束")
                print("=" * 80)
            
            # 使用一致性种子
            import hashlib
            seed = int(hashlib.md5(prompt.encode()).hexdigest(), 16) % 10000
            
            if self.model_type == "ollama":
                print(f"   🔗 连接地址: {self.api_url}")
                result = self._call_ollama(prompt)
            else:  # openai兼容接口
                print(f"   🔗 API地址: {self.api_url}")
                result = self._call_openai_compatible(prompt)
            
            # 标准化处理，确保评分一致性
            normalized_result = self._normalize_scores(result)
            print(f"   📊 响应数据大小: {len(str(normalized_result))} 字符")
            return normalized_result
            
        except Exception as e:
            print(f"AI模型调用失败: {e}")
            return self._get_default_result()
    
    def _normalize_scores(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """标准化评分结果，确保一致性"""
        # 确保所有评分都是有效的数值
        score_fields = [
            'functional_completeness', 'testspec_coverage', 
            'test_logic_correctness', 'edge_case_handling',
            'error_handling', 'code_quality'
        ]
        
        for field in score_fields:
            if field not in result or not isinstance(result[field], (int, float)):
                result[field] = 75.0  # 默认值
            else:
                # 确保评分在合理范围内
                score = float(result[field])
                score = max(0, min(100, score))
                # 标准化为5的倍数，减少波动
                result[field] = round(score / 5) * 5
        
        # 确保列表字段存在
        for list_field in ['missing_functionalities', 'redundant_tests', 'improvement_suggestions']:
            if list_field not in result or not isinstance(result[list_field], list):
                result[list_field] = []
        
        # 确保详细分析字段存在
        if 'detailed_analysis' not in result:
            result['detailed_analysis'] = "AI评估完成"
            
        return result
    
    def _call_openai_compatible(self, prompt: str) -> Dict[str, Any]:
        """调用OpenAI兼容接口"""
        print("   ⏳ 正在连接OpenAI兼容服务...")
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
            print("   📨 发送HTTP请求...")
            response = requests.post(api_url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            
            print("   ✅ 收到API响应")
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # 显示AI的部分分析内容（前500字符）
            preview = content[:500] + "..." if len(content) > 500 else content
            print(f"   🧠 AI分析预览: {preview}")
            
            # 清理可能的markdown代码块标记
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            result = json.loads(content.strip())
            
            # 显示关键分析结果
            if isinstance(result, dict):
                print(f"   📊 功能完整性评分: {result.get('functional_completeness', 'N/A')}")
                print(f"   📊 测试覆盖率评分: {result.get('testspec_coverage', 'N/A')}")
                print(f"   📊 测试逻辑正确性: {result.get('test_logic_correctness', 'N/A')}")
                
                missing_count = len(result.get('missing_functionalities', []))
                suggestions_count = len(result.get('improvement_suggestions', []))
                print(f"   📋 发现缺失功能: {missing_count} 项")
                print(f"   💡 提供改进建议: {suggestions_count} 条")
            
            print("   ✅ JSON解析成功")
            return result
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
            print("   ⏳ 正在连接Ollama服务...")
            ollama_host = self.api_url.rstrip('/')
            client = ollama.Client(host=ollama_host)
            
            print("   📨 发送请求到AI模型...")
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
            
            print("   ✅ 收到AI响应")
            content = response['message']['content']
            
            # 显示AI的部分分析内容（前500字符）
            preview = content[:500] + "..." if len(content) > 500 else content
            print(f"   🧠 AI分析预览: {preview}")
            
            # 清理可能的markdown代码块标记
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            result = json.loads(content.strip())
            
            # 显示关键分析结果
            if isinstance(result, dict):
                print(f"   📊 功能完整性评分: {result.get('functional_completeness', 'N/A')}")
                print(f"   📊 测试覆盖率评分: {result.get('testspec_coverage', 'N/A')}")
                print(f"   📊 测试逻辑正确性: {result.get('test_logic_correctness', 'N/A')}")
                
                missing_count = len(result.get('missing_functionalities', []))
                suggestions_count = len(result.get('improvement_suggestions', []))
                print(f"   📋 发现缺失功能: {missing_count} 项")
                print(f"   💡 提供改进建议: {suggestions_count} 条")
            
            print("   ✅ JSON解析成功")
            return result
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
            "functional_completeness": 75.0,
            "testspec_coverage": 75.0,
            "test_logic_correctness": 75.0,
            "edge_case_handling": 70.0,
            "error_handling": 70.0,
            "code_quality": 75.0,
            "missing_functionalities": ["无法连接AI模型进行详细评估"],
            "redundant_tests": [],
            "improvement_suggestions": [
                "请检查AI模型连接配置",
                "确保Ollama或OpenAI服务正常运行",
                "验证网络连接和API密钥"
            ],
            "detailed_analysis": "由于AI模型调用失败，使用默认评估结果。建议检查网络连接和API配置后重新评估。",
            "scoring_basis": {
                "functional_completeness": "默认中等评分",
                "testspec_coverage": "默认中等评分", 
                "test_logic_correctness": "默认中等评分",
                "edge_case_handling": "默认中等评分",
                "error_handling": "默认中等评分",
                "code_quality": "默认中等评分"
            }
        }
    
    def evaluate_testcase(self, testcase_id: str, refwritten_path: str, generated_path: str, testspec_path: str) -> AIEvaluationResult:
        """评估单个测试用例"""
        
        print(f"\n📋 开始评估测试用例 {testcase_id}")
        
        # 读取文件内容
        print("📖 读取测试文件...")
        refwritten_content = self.read_file_content(refwritten_path)
        generated_content = self.read_file_content(generated_path)
        testspec_content = self.read_file_content(testspec_path)
        
        if not all([refwritten_content, generated_content, testspec_content]):
            print("❌ 部分文件内容为空或无法读取")
            return AIEvaluationResult(**self._get_default_result())
        
        print(f"   ✅ 参考测试用例: {len(refwritten_content)} 字符")
        print(f"   ✅ 生成测试用例: {len(generated_content)} 字符")
        print(f"   ✅ 测试文档: {len(testspec_content)} 字符")
        
        # 提取测试
        print("🔍 分析测试文档...")
        testspecs = self.extract_testspecs_from_md(testspec_content)
        print(f"   ✅ 提取到 {len(testspecs)} 个功能测试")

        # 创建评估提示
        print("📝 生成AI评估提示...")
        prompt = self.create_evaluation_prompt(refwritten_content, generated_content, testspecs)
        prompt_size = len(prompt)
        print(f"   ✅ 提示词长度: {prompt_size} 字符")
        
        # 调用AI模型评估
        print("🤖 调用AI模型...")
        ai_result = self.call_ai_model(prompt)
        print("   ✅ AI模型响应完成")
        
        # 过滤结果，只保留AIEvaluationResult所需的字段
        print("🔧 处理AI响应数据...")
        filtered_result = self._filter_ai_result(ai_result)
        print("   ✅ 数据过滤完成")
        
        return AIEvaluationResult(**filtered_result)
    
    def generate_detailed_report(self, result: AIEvaluationResult, testcase_id: str) -> str:
        """生成详细评估报告"""
        
        # 计算加权综合评分
        weighted_score = (result.functional_completeness * 0.25 + 
                         result.testspec_coverage * 0.25 + 
                         result.test_logic_correctness * 0.20 + 
                         result.edge_case_handling * 0.15 + 
                         result.error_handling * 0.10 + 
                         result.code_quality * 0.05)
        rating = self._get_rating(weighted_score)
        
        report = f"""# CAPL测试用例AI评估报告 - 测试用例 {testcase_id}

## 综合评分
| 评估维度 | 得分 | 评级 |
|----------|------|------|
| 功能完整性 | {result.functional_completeness:.1f}/100 | {self._get_rating(result.functional_completeness)} |
| 测试覆盖率 | {result.testspec_coverage:.1f}/100 | {self._get_rating(result.testspec_coverage)} |
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
    
    def _filter_ai_result(self, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """过滤AI响应，只保留AIEvaluationResult所需的字段"""
        # 定义AIEvaluationResult所需的字段
        required_fields = {
            'functional_completeness', 'testspec_coverage', 'test_logic_correctness',
            'edge_case_handling', 'error_handling', 'code_quality',
            'missing_functionalities', 'redundant_tests', 'improvement_suggestions',
            'detailed_analysis', 'scoring_basis'
        }
        
        # 过滤字段并设置默认值
        filtered = {}
        for field in required_fields:
            if field in ai_result:
                filtered[field] = ai_result[field]
            else:
                # 设置默认值
                if field.endswith('_functionalities') or field.endswith('_tests') or field.endswith('_suggestions'):
                    filtered[field] = []
                elif field == 'detailed_analysis':
                    filtered[field] = "AI评估完成"
                elif field == 'scoring_basis':
                    filtered[field] = None
                else:
                    filtered[field] = 75.0  # 默认评分
        
        # 确保列表字段是列表类型
        list_fields = ['missing_functionalities', 'redundant_tests', 'improvement_suggestions']
        for field in list_fields:
            if not isinstance(filtered[field], list):
                filtered[field] = []
        
        return filtered
    
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
    base_dir = Path(__file__).parent.parent
    
    refwritten_path = base_dir / "test_output" / f"testcase_id_{args.testcase_id}.can"
    generated_path = base_dir / "test_output" / f"qualification_*{args.testcase_id}*.can"
    testspec_path = base_dir / "pdf_converter" / "testcases" / f"qualification_*{args.testcase_id}*.md"
    
    # 查找大模型生成的测试用例文件
    generated_files = list(base_dir.glob(f"test_output/qualification*{args.testcase_id}*.can"))
    testspec_files = list(base_dir.glob(f"pdf_converter/testcases/qualification*{args.testcase_id}*.md"))
    
    if not generated_files:
        print(f"❌ 未找到大模型生成的测试用例文件")
        return
    
    if not testspec_files:
        print(f"❌ 未找到测试文档")
        return
    
    generated_path = generated_files[0]
    testspec_path = testspec_files[0]
    
    if not refwritten_path.exists():
        print(f"❌ 未找到参考测试用例: {refwritten_path}")
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
        str(refwritten_path),
        str(generated_path),
        str(testspec_path)
    )
    
    # 保存结果
    evaluator.save_evaluation_result(result, args.testcase_id)
    
    # 打印简要结果
    print(f"\n📊 AI评估完成!")
    print(f"功能完整性: {result.functional_completeness:.1f}/100")
    print(f"测试覆盖率: {result.testspec_coverage:.1f}/100")
    print(f"测试逻辑正确性: {result.test_logic_correctness:.1f}/100")

if __name__ == "__main__":
    main()