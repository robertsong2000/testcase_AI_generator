# CAPL测试用例AI智能评估系统 - 使用指南

## 🎯 系统概述

这个AI评估系统使用大语言模型从**功能完整性**角度评估CAPL测试用例，而非简单的字符串相似度比较。它能：

- ✅ 评估功能需求覆盖度
- ✅ 分析测试逻辑正确性
- ✅ 识别缺失的测试场景
- ✅ 检测冗余测试用例
- ✅ 提供具体改进建议

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install ollama requests python-dotenv
```

### 2. 配置文件设置

#### 方法一：使用现有配置文件
项目根目录已提供配置文件模板：
```bash
# 使用Ollama配置
cp .env.ollama.sample .env

# 或使用OpenAI配置
cp .env.openai.sample .env
```

#### 方法二：手动创建配置文件
创建 `.env` 文件：
```bash
# API类型: ollama 或 openai
API_TYPE=ollama

# API服务地址
API_URL=http://localhost:11434

# 模型名称
OLLAMA_MODEL=qwen3:8b
OPENAI_MODEL=qwen/qwen3-8b

# OpenAI API密钥（如使用OpenAI）
OPENAI_API_KEY=sk-xxx
```

### 3. 使用方法

#### 基础用法
```bash
# 使用默认配置（Ollama + qwen3:8b）
python run_ai_evaluation.py 1336732

# 指定测试用例ID和模型
python run_ai_evaluation.py 1336732 --model-type ollama --model qwen3:8b

# 使用OpenAI
python run_ai_evaluation.py 1336732 --model-type openai --api-key sk-xxx --model gpt-4

# 使用LM Studio
python run_ai_evaluation.py 1336732 --model-type openai --api-url http://localhost:1234/v1 --model qwen/qwen3-8b
```

#### 高级参数
```bash
# 自定义温度和token限制
python run_ai_evaluation.py 1336732 --temperature 0.2 --max-tokens 4000

# 使用不同的提示词模板
python run_ai_evaluation.py 1336732 --prompt-template detailed

# 启用调试模式
python run_ai_evaluation.py 1336732 --debug
```

## 📊 评估维度

### 核心评估指标

| 维度 | 权重 | 评分标准 | 优秀标准 |
|------|------|----------|----------|
| **功能完整性** | 25% | 是否覆盖所有功能需求 | ≥85分 |
| **需求覆盖率** | 25% | 需求文档功能点覆盖程度 | ≥90分 |
| **测试逻辑正确性** | 20% | 测试逻辑是否符合业务规则 | ≥80分 |
| **边界条件处理** | 15% | 边界值和异常情况考虑 | ≥75分 |
| **错误处理** | 10% | 错误情况处理完善程度 | ≥70分 |
| **代码质量** | 5% | 可读性、可维护性 | ≥80分 |

### 评估等级说明

- **优秀 (90-100分)**: 测试用例完整覆盖需求，逻辑严谨，边界条件充分考虑
- **良好 (80-89分)**: 基本覆盖需求，逻辑正确，主要边界条件已考虑
- **一般 (70-79分)**: 部分需求未覆盖，逻辑存在小问题，边界条件考虑不足
- **需改进 (<70分)**: 需求覆盖不完整，逻辑有明显缺陷，需大幅修改

## 📁 输出文件

运行后会生成以下文件：

### 1. JSON结果文件
**路径**: `results/ai_evaluation_{testcase_id}_{timestamp}.json`
**内容**:
- 6项评估指标得分
- 缺失功能点列表
- 改进建议
- 详细对比数据

### 2. 详细报告
**路径**: `results/ai_report_{testcase_id}_{timestamp}.md`
**内容**:
- 评估摘要
- 缺失功能分析
- 具体改进建议
- 测试用例对比

### 3. 示例输出
```
📊 AI评估完成! 测试用例: 1336732
========================================
综合评分: 80.75/100 (良好)
功能完整性: 85.0/100
需求覆盖率: 90.0/100
测试逻辑正确性: 75.0/100
边界条件处理: 65.0/100
错误处理: 70.0/100
代码质量: 85.0/100
========================================

⚠️ 缺失功能点 (3):
  - 未测试雨刷在极低温度下的工作情况
  - 缺少电源波动时的稳定性测试
  - 未验证连续工作状态下的性能

💡 主要改进建议 (3):
  - 增加低温环境测试用例 (-40°C)
  - 添加电源电压变化测试场景 (9V-16V)
  - 补充长时间运行压力测试 (连续工作4小时)
```

## 🔍 评估结果示例

### 实际评估结果示例

```json
{
  "testcase_id": "1336732",
  "overall_score": 80.75,
  "scores": {
    "functional_completeness": 85.0,
    "requirement_coverage": 90.0,
    "test_logic_correctness": 75.0,
    "boundary_condition_handling": 65.0,
    "error_handling": 70.0,
    "code_quality": 85.0
  },
  "missing_features": [
    "未测试雨刷在极低温度下的工作情况",
    "缺少电源波动时的稳定性测试",
    "未验证连续工作状态下的性能"
  ],
  "improvement_suggestions": [
    "增加低温环境测试用例 (-40°C)",
    "添加电源电压变化测试场景 (9V-16V)",
    "补充长时间运行压力测试 (连续工作4小时)"
  ],
  "analysis": {
    "strengths": [
      "需求覆盖率优秀 (90.0/100)",
      "代码质量良好 (85.0/100)",
      "功能完整性较好 (85.0/100)"
    ],
    "weaknesses": [
      "边界条件处理不足 (65.0/100)",
      "错误处理需要改进 (70.0/100)",
      "测试逻辑正确性待提升 (75.0/100)"
    ]
  }
}
```

### 详细报告示例

#### 评估摘要
测试用例1336732的综合评分为**80.75/100**，属于**良好**等级。

#### 详细分析

**强项分析：**
- ✅ **需求覆盖率**: 90.0/100 - 基本覆盖了所有功能需求
- ✅ **代码质量**: 85.0/100 - 代码结构清晰，命名规范
- ✅ **功能完整性**: 85.0/100 - 主要功能测试完整

**待改进项：**
- ⚠️ **边界条件处理**: 65.0/100 - 缺少极端条件测试
- ⚠️ **错误处理**: 70.0/100 - 异常场景覆盖不足
- ⚠️ **测试逻辑正确性**: 75.0/100 - 部分测试逻辑需要验证

#### 具体改进建议

1. **边界条件优化** (优先级：高)
   - 添加低温测试：-40°C环境测试
   - 添加高温测试：85°C环境测试
   - 添加电压边界：9V-16V电源波动测试

2. **错误处理增强** (优先级：中)
   - 添加传感器故障模拟
   - 添加通信中断测试
   - 添加执行器故障测试

3. **测试逻辑完善** (优先级：中)
   - 验证测试步骤的正确性
   - 确保预期结果与实际需求匹配
   - 添加状态转换验证

#### 优化后预期得分

完成上述改进后，预计综合评分可提升至**88-93分**区间。

## 🛠️ 高级用法

### 1. 自定义提示词模板

可以自定义评估提示词模板：

```python
from evaluation.ai_evaluator import CAPLAIEvaluator

# 创建自定义提示词模板
CUSTOM_PROMPT = """
你是一位专业的CAPL测试工程师，请评估以下测试用例的质量。

**评估标准：**
- 功能完整性：是否覆盖所有需求点
- 需求覆盖率：需求文档中的功能点是否都被测试
- 测试逻辑正确性：测试步骤是否符合逻辑
- 边界条件处理：是否测试了边界值和异常情况
- 错误处理：是否处理了可能的错误场景
- 代码质量：代码的可读性和规范性

**测试用例信息：**
- 测试用例ID: {testcase_id}
- 功能需求: {requirements}

**手写测试用例:**
```capl
{handwritten}
```

**AI生成测试用例:**
```capl
{generated}
```

请按照以下JSON格式返回评估结果：
{{
    "overall_score": <0-100>,
    "functional_completeness": <0-100>,
    "requirement_coverage": <0-100>,
    "test_logic_correctness": <0-100>,
    "boundary_condition_handling": <0-100>,
    "error_handling": <0-100>,
    "code_quality": <0-100>,
    "missing_features": ["..."],
    "improvement_suggestions": ["..."],
    "detailed_analysis": "..."
}}
"""

# 使用自定义模板
evaluator = CAPLAIEvaluator(prompt_template=CUSTOM_PROMPT)
```

### 2. 批量评估多个测试用例

#### 基础批量评估
```python
import os
import json
from evaluation.ai_evaluator import CAPLAIEvaluator

def batch_evaluate_testcases(testcase_ids, model_type="ollama"):
    """批量评估测试用例"""
    evaluator = CAPLAIEvaluator(model_type=model_type)
    results = []
    
    for testcase_id in testcase_ids:
        try:
            result = evaluator.evaluate_testcase(
                testcase_id=testcase_id,
                handwritten_path=f"test_output/testcase_id_{testcase_id}.can",
                generated_path=f"test_output/qualification_{testcase_id}.can",
                requirement_path=f"pdf_converter/testcases/qualification_{testcase_id}.md"
            )
            
            results.append({
                "testcase_id": testcase_id,
                "result": result,
                "status": "success"
            })
            
            print(f"✅ {testcase_id}: {result['overall_score']}/100")
            
        except Exception as e:
            results.append({
                "testcase_id": testcase_id,
                "error": str(e),
                "status": "failed"
            })
            print(f"❌ {testcase_id}: 失败 - {str(e)}")
    
    return results

# 使用示例
testcase_ids = ["1336732", "1336763", "1336764"]
results = batch_evaluate_testcases(testcase_ids)
```

#### 带统计分析的批量评估
```python
import pandas as pd
import matplotlib.pyplot as plt

def analyze_evaluation_results(results):
    """分析批量评估结果"""
    
    # 提取成功评估的结果
    successful_results = [r for r in results if r['status'] == 'success']
    
    if not successful_results:
        print("没有成功评估的结果")
        return
    
    # 创建DataFrame
    scores_data = []
    for r in successful_results:
        scores = r['result']['scores']
        scores['testcase_id'] = r['testcase_id']
        scores_data.append(scores)
    
    df = pd.DataFrame(scores_data)
    
    # 统计信息
    print("=== 评估统计 ===")
    print(f"总测试用例: {len(results)}")
    print(f"成功评估: {len(successful_results)}")
    print(f"失败评估: {len(results) - len(successful_results)}")
    print()
    
    print("=== 得分统计 ===")
    print(df.describe())
    print()
    
    # 找出需要改进的测试用例
    low_scores = df[df['overall_score'] < 75]
    if not low_scores.empty:
        print("=== 需要改进的测试用例 ===")
        for _, row in low_scores.iterrows():
            print(f"{row['testcase_id']}: {row['overall_score']}/100")
    
    return df

# 使用示例
df = analyze_evaluation_results(results)
```

### 3. 性能优化

#### 并行评估（需要安装joblib）
```python
from joblib import Parallel, delayed
from evaluation.ai_evaluator import CAPLAIEvaluator

def parallel_evaluate(testcase_id):
    """单个测试用例评估函数"""
    try:
        evaluator = CAPLAIEvaluator()
        result = evaluator.evaluate_testcase(
            testcase_id=testcase_id,
            handwritten_path=f"test_output/testcase_id_{testcase_id}.can",
            generated_path=f"test_output/qualification_{testcase_id}.can",
            requirement_path=f"pdf_converter/testcases/qualification_{testcase_id}.md"
        )
        return {
            "testcase_id": testcase_id,
            "result": result,
            "status": "success"
        }
    except Exception as e:
        return {
            "testcase_id": testcase_id,
            "error": str(e),
            "status": "failed"
        }

# 并行评估
testcase_ids = ["1336732", "1336763", "1336764"]
results = Parallel(n_jobs=3)(delayed(parallel_evaluate)(tid) for tid in testcase_ids)
```

### 4. 结果可视化

#### 生成评估报告图表
```python
import matplotlib.pyplot as plt
import seaborn as sns

def create_evaluation_report(df):
    """生成评估报告图表"""
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. 整体得分分布
    axes[0,0].hist(df['overall_score'], bins=10, edgecolor='black', alpha=0.7)
    axes[0,0].set_title('整体得分分布')
    axes[0,0].set_xlabel('得分')
    axes[0,0].set_ylabel('测试用例数量')
    
    # 2. 各指标平均分
    metrics = ['functional_completeness', 'requirement_coverage', 'test_logic_correctness', 
               'boundary_condition_handling', 'error_handling', 'code_quality']
    avg_scores = df[metrics].mean()
    
    axes[0,1].bar(range(len(metrics)), avg_scores.values)
    axes[0,1].set_title('各指标平均分')
    axes[0,1].set_xticks(range(len(metrics)))
    axes[0,1].set_xticklabels([m.replace('_', '\n') for m in metrics], rotation=45)
    axes[0,1].set_ylim(0, 100)
    
    # 3. 测试用例得分排名
    df_sorted = df.sort_values('overall_score', ascending=False)
    axes[1,0].barh(df_sorted['testcase_id'], df_sorted['overall_score'])
    axes[1,0].set_title('测试用例得分排名')
    axes[1,0].set_xlabel('得分')
    
    # 4. 热力图
    sns.heatmap(df[metrics].corr(), annot=True, fmt='.2f', ax=axes[1,1])
    axes[1,1].set_title('指标相关性热力图')
    
    plt.tight_layout()
    plt.savefig('evaluation_report.png', dpi=300, bbox_inches='tight')
    plt.show()

# 使用示例
create_evaluation_report(df)
```

## 🎯 与传统比较的区别

| 传统字符串比较 | AI智能评估 |
|----------------|------------|
| 基于文本相似度 | 基于功能理解 |
| 表面形式比较 | 深层逻辑分析 |
| 无法识别业务逻辑 | 理解测试目的 |
| 给出模糊评分 | 提供具体建议 |
| 忽略业务场景 | 考虑实际需求 |

## 📝 注意事项

1. **API配额**: OpenAI有调用频率限制，大量评估请使用本地Ollama
2. **网络连接**: 使用OpenAI需要稳定网络，Ollama可离线运行
3. **模型选择**: 
   - GPT-4更准确但成本高
   - Llama2免费但精度略低
4. **结果解释**: AI评估是辅助工具，最终决策仍需人工确认

## 🔧 故障排除

### 常见问题

**Q: Ollama连接失败**
```bash
# 检查Ollama服务
ollama serve

# 重新拉取模型
ollama pull llama2
```

**Q: OpenAI API错误**
```bash
# 检查API密钥
export OPENAI_API_KEY="your-valid-key"

# 检查配额
curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Q: 文件找不到**
```bash
# 检查文件路径
ls test_output/
ls pdf_converter/testcases/
```

### 1. API连接失败
**问题描述**: 无法连接到AI模型API

**解决方案**:
```bash
# 检查Ollama服务状态
ollama ps

# 如果服务未启动，启动Ollama
ollama serve

# 检查模型是否存在
ollama list

# 如果模型不存在，拉取模型
ollama pull qwen3:8b
```

**Python调试**:
```python
import requests

# 测试Ollama连接
try:
    response = requests.get("http://localhost:11434/api/tags")
    print("Ollama连接正常")
    print("可用模型:", response.json())
except Exception as e:
    print("Ollama连接失败:", e)
```

### 2. 评估结果异常
**问题描述**: 评估结果不准确或异常

**排查步骤**:
1. **检查输入文件**:
   ```bash
   # 验证文件存在
   ls -la test_output/testcase_id_1336732.can
   ls -la test_output/qualification_1336732.can
   ls -la pdf_converter/testcases/qualification_1336732.md
   
   # 检查文件内容
   head -20 test_output/testcase_id_1336732.can
   ```

2. **验证测试用例格式**:
   ```python
   def validate_testcase_files(testcase_id):
       files = [
           f"test_output/testcase_id_{testcase_id}.can",
           f"test_output/qualification_{testcase_id}.can",
           f"pdf_converter/testcases/qualification_{testcase_id}.md"
       ]
       
       for file_path in files:
           if not os.path.exists(file_path):
               print(f"❌ 文件不存在: {file_path}")
               return False
           
           if os.path.getsize(file_path) == 0:
               print(f"❌ 文件为空: {file_path}")
               return False
       
       print("✅ 所有文件验证通过")
       return True
   ```

### 3. 性能问题
**问题描述**: 评估过程缓慢或超时

**优化方案**:

1. **使用本地模型**:
   ```python
   # 推荐使用Ollama本地模型
   evaluator = CAPLAIEvaluator(
       model_type="ollama",
       model_name="qwen3:8b",
       timeout=300  # 5分钟超时
   )
   ```

2. **调整并发数**:
   ```python
   # 减少并行任务数
   from joblib import Parallel, delayed
   results = Parallel(n_jobs=2)(delayed(evaluate_single)(tid) for tid in testcase_ids)
   ```

3. **优化批处理大小**:
   ```python
   def batch_evaluate_with_size_limit(testcase_ids, batch_size=5):
       """分批评估，避免一次处理过多"""
       results = []
       for i in range(0, len(testcase_ids), batch_size):
           batch = testcase_ids[i:i+batch_size]
           batch_results = batch_evaluate_testcases(batch)
           results.extend(batch_results)
           print(f"完成批次 {i//batch_size + 1}/{(len(testcase_ids)-1)//batch_size + 1}")
       return results
   ```

### 4. 内存问题
**问题描述**: 内存不足或程序崩溃

**解决方案**:
```python
import gc

def memory_safe_evaluate(testcase_ids):
    """内存安全的评估方式"""
    results = []
    
    for testcase_id in testcase_ids:
        # 每次创建新的评估器实例
        evaluator = CAPLAIEvaluator()
        
        try:
            result = evaluator.evaluate_testcase(
                testcase_id=testcase_id,
                handwritten_path=f"test_output/testcase_id_{testcase_id}.can",
                generated_path=f"test_output/qualification_{testcase_id}.can",
                requirement_path=f"pdf_converter/testcases/qualification_{testcase_id}.md"
            )
            results.append(result)
            
        except Exception as e:
            print(f"评估 {testcase_id} 时出错: {e}")
        
        # 强制垃圾回收
        del evaluator
        gc.collect()
    
    return results
```

### 5. 调试模式

**启用调试日志**:
```python
import logging

# 设置调试日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evaluation_debug.log'),
        logging.StreamHandler()
    ]
)

# 在调试模式下运行评估
evaluator = CAPLAIEvaluator(debug=True)
result = evaluator.evaluate_testcase("1336732")
```

### 6. 错误恢复

**自动重试机制**:
```python
import time
from functools import wraps

def retry_on_failure(max_attempts=3, delay=5):
    """失败重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    print(f"尝试 {attempt + 1} 失败，{delay}秒后重试...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry_on_failure(max_attempts=3, delay=10)
def safe_evaluate(testcase_id):
    evaluator = CAPLAIEvaluator()
    return evaluator.evaluate_testcase(testcase_id)
```

## 🚀 下一步

### 即将推出的功能

#### 1. 多模型对比评估
- 支持同时对比多个AI模型的评估结果
- 提供模型性能排行榜
- 自动选择最优模型

#### 2. 智能改进建议
- 基于评估结果自动生成改进代码
- 一键应用改进建议
- 改进效果追踪

#### 3. 实时监控面板
- Web界面实时查看评估进度
- 交互式结果分析
- 历史数据趋势图

#### 4. 团队协作功能
- 评估结果共享
- 评论和讨论功能
- 改进建议投票系统

### 参与开发

欢迎提交Issue和Pull Request来改进AI评估系统！

#### 开发路线图
- **v3.1**: 多模型对比功能
- **v3.2**: 智能代码修复
- **v3.3**: Web界面
- **v3.4**: 团队协作功能

#### 如何贡献
1. Fork项目代码
2. 创建功能分支
3. 提交改进代码
4. 创建Pull Request

### 联系我们

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至开发团队
- 加入社区讨论群组

---

**最后更新时间**: 2024年12月20日  
**文档版本**: v3.0  
**系统版本**: AI智能评估系统 v3.0