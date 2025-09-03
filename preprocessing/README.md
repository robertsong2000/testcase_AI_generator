# 测试用例预处理系统

基于LLM+RAG的测试用例增强系统，将原有的单体脚本重构为模块化架构。

## 🏗️ 架构设计

### 目录结构
```
preprocessing/
├── __init__.py           # 主入口
├── cli.py               # CLI工具
├── core/                # 核心模块
│   ├── __init__.py
│   ├── enhancer.py      # 主增强器类
│   ├── config.py        # 配置管理
│   └── cache.py         # 缓存管理
├── analyzers/           # 分析器模块
│   ├── __init__.py
│   ├── purpose_analyzer.py   # 测试目的分析
│   └── context_analyzer.py   # 上下文分析
├── enhancers/           # 增强器模块
│   ├── __init__.py
│   └── description_enhancer.py  # 描述增强
└── utils/               # 工具模块
    ├── __init__.py
    ├── file_handler.py  # 文件处理
    └── logger.py        # 日志工具
```

## 🚀 使用方式

### 1. CLI工具
```bash
# 增强整个测试用例
python -m preprocessing.cli testcases/testcase.json

# 增强特定步骤
python -m preprocessing.cli testcases/testcase.json --step-index 5

# 使用OpenAI模型
python -m preprocessing.cli testcases/testcase.json --model openai

# 详细输出模式
python -m preprocessing.cli testcases/testcase.json --verbose
```

### 2. 编程接口
```python
from preprocessing import TestcaseLLMEnhancer, EnhancerConfig

# 创建配置
config = EnhancerConfig(
    api_type="ollama",
    max_purpose_length=200,
    max_description_length=500
)

# 创建增强器
enhancer = TestcaseLLMEnhancer(config, verbose=True)

# 增强测试用例
enhanced = enhancer.enhance_testcase("testcase.json")

# 保存结果
enhancer.save_enhanced_testcase(enhanced, "testcase_enhanced.json")
```

## ⚙️ 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api_type` | str | "ollama" | API类型 (openai/ollama) |
| `model` | str | "qwen3:1.7b" | 模型名称 |
| `max_purpose_length` | int | 200 | 测试目的最大长度 |
| `max_description_length` | int | 500 | 描述最大长度 |
| `suffix` | str | ".llm_enhanced" | 输出文件后缀 |

## 🎯 功能特性

### ✅ 已优化
- **模块化架构**: 单一职责原则，每个模块功能明确
- **缓存机制**: 测试目的分析结果缓存，避免重复计算
- **配置管理**: 统一的配置管理，支持灵活定制
- **错误处理**: 完善的异常处理和回退机制
- **日志系统**: 详细的操作日志和调试信息

### 📊 性能改进
- **缓存优化**: 测试目的只分析一次，后续复用
- **内存管理**: 使用深拷贝避免数据污染
- **错误恢复**: 失败时回退到原始描述

### 🔧 扩展性
- **插件化设计**: 易于添加新的分析器或增强器
- **配置驱动**: 通过配置控制行为
- **接口抽象**: 清晰的模块接口定义

## 🧪 测试验证

运行测试脚本验证重构效果：
```bash
cd preprocessing
python test_restructure.py
```

## 🔄 迁移指南

### 从旧版本迁移
原命令：
```bash
python test/testcase_rag_llm_enhancer.py test.json
```

新命令：
```bash
python -m preprocessing.cli test.json
```

### 向后兼容
- 保持相同的输出格式
- 支持原有的CLI参数
- 相同的文件命名规则

## 📈 未来扩展

### 计划功能
- [ ] 批量处理多个测试用例
- [ ] 支持更多模型类型
- [ ] 自定义增强模板
- [ ] 结果验证和质量评分
- [ ] 并行处理优化

### 扩展点
- 添加新的`Analyzer`子类
- 实现自定义的`Enhancer`
- 扩展`Config`配置选项
- 集成新的知识库