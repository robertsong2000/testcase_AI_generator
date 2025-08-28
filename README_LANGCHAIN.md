# 基于LangChain的CAPL生成器

这是`capl_generator.py`的重构版本，使用LangChain架构实现，支持RAG（检索增强生成）功能。

## 特性

- **模块化架构**: 基于LangChain的链式处理
- **RAG支持**: 可集成知识库进行上下文增强
- **多提供商支持**: 支持Ollama和OpenAI兼容API
- **灵活配置**: 通过环境变量和命令行参数配置
- **类型安全**: 完整的类型注解
- **错误处理**: 完善的异常处理机制

## 安装

1. 安装依赖：
```bash
pip install -r requirements_langchain.txt
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件配置你的参数
```

## 使用方式

### 基本使用

```bash
# 使用默认配置
python capl_generator_langchain.py test_requirements.md

# 指定模型和API
python capl_generator_langchain.py test_requirements.md --model qwen3:8b --api-url http://localhost:11434

# 启用RAG功能
python capl_generator_langchain.py test_requirements.md --enable-rag
```

### 命令行参数

- `file_path`: 输入的测试需求文件路径
- `--api-type`: API类型 (ollama/openai)
- `--api-url`: API服务地址
- `--model`: 使用的模型名称
- `--output-dir`: 输出目录
- `--enable-rag`: 启用RAG功能
- `--context-length`: 上下文长度
- `--max-tokens`: 最大输出tokens
- `--temperature`: 生成温度 (0.0-1.0)
- `--top-p`: top-p采样参数

## RAG功能

### 启用RAG

1. 设置环境变量：
```bash
ENABLE_RAG=true
```

2. 准备知识库文档：
将相关的CAPL代码示例、测试规范等文档放入`knowledge_base/`目录（.txt格式）

3. 运行：
```bash
python capl_generator_langchain.py test_requirements.md --enable-rag
```

### 知识库结构

```
knowledge_base/
├── capl_examples.txt      # CAPL代码示例
├── test_standards.txt     # 测试标准文档
├── best_practices.txt     # 最佳实践
├── capl_api_lists.json  # CAPL API列表（JSON格式）
└── ...
```

### 支持的知识库格式

系统支持以下格式的知识库文档：
- `.txt` - 纯文本文件
- `.md` - Markdown文档
- `.capl` - CAPL代码文件
- `.py` - Python代码文件
- `.json` - JSON文档（包括CAPL API列表等结构化数据）

### JSON文档支持

系统现在支持JSON格式的知识库文档，会自动将JSON数据转换为可搜索的文本格式。例如：
- CAPL API列表 (`capl_api_lists.json`)
- 测试用例数据
- 配置信息
- 其他结构化数据

JSON文档会被格式化为易读的文本格式，保留所有字段和层次结构信息，便于RAG系统检索和使用。

## 编程接口

### 作为库使用

```python
from capl_generator_langchain import CAPLGenerator, CAPLGeneratorConfig

# 创建配置
config = CAPLGeneratorConfig()
config.model = "qwen3:30b-a3b"
config.enable_rag = True

# 创建生成器
generator = CAPLGenerator(config)
generator.initialize()

# 生成代码
requirement = "测试雨刷器低速功能"
capl_code = generator.generate_capl_code(requirement)
print(capl_code)
```

### 批量处理

```python
from capl_generator_langchain import CAPLGeneratorService

service = CAPLGeneratorService()
result = service.process_file("test_requirements.md")

if result["status"] == "success":
    print(f"生成成功: {result['file_path']}")
    print(f"耗时: {result['stats']['generation_time']}s")
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| API_TYPE | API类型 | ollama |
| API_URL | API地址 | http://localhost:11434 |
| OLLAMA_MODEL | Ollama模型 | qwen3:30b-a3b |
| OPENAI_MODEL | OpenAI模型 | gpt-3.5-turbo |
| ENABLE_RAG | 启用RAG | false |
| EMBEDDING_MODEL | 嵌入模型 | nomic-embed-text |

### 配置文件

也可以创建`.env`文件配置所有参数：
```bash
# .env
API_TYPE=ollama
API_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:30b-a3b
ENABLE_RAG=true
EMBEDDING_MODEL=nomic-embed-text
```

## 迁移指南

从旧版本迁移：

1. 保留原有的`prompt_template.txt`和`example_code.txt`
2. 环境变量基本兼容
3. 命令行参数基本一致
4. 输出格式保持不变

## 故障排除

### 常见问题

1. **模型未找到**
   - 确保Ollama服务已启动: `ollama serve`
   - 检查模型是否已安装: `ollama pull qwen3:30b-a3b`

2. **知识库加载失败**
   - 检查`knowledge_base/`目录是否存在
   - 确保文档为UTF-8编码的.txt文件

3. **RAG功能异常**
   - 确认`ENABLE_RAG=true`
   - 检查嵌入模型是否可用

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 架构说明

### 核心组件

- **CAPLGenerator**: 主要的生成器类
- **CAPLGeneratorService**: 服务封装，提供完整功能
- **KnowledgeBaseManager**: RAG知识库管理
- **LLMFactory**: LLM实例工厂
- **PromptTemplateManager**: 提示模板管理

### 处理流程

1. 初始化配置
2. 加载知识库（如果启用RAG）
3. 构建LangChain处理链
4. 处理输入需求
5. 生成CAPL代码
6. 保存结果

这种架构使得后续可以轻松扩展：
- 添加新的LLM提供商
- 集成更多RAG功能
- 支持多模态输入
- 添加代码验证和优化