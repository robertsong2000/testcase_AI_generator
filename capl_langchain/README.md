# CAPL LangChain 生成器

基于LangChain的CAPL测试代码生成器，采用模块化架构设计。

## 目录结构

```
capl_langchain/
├── __init__.py              # 包初始化
├── generator.py             # 主要的CAPL生成器类
├── config/                  # 配置模块
│   ├── __init__.py
│   └── config.py           # CAPLGeneratorConfig配置类
├── factories/               # 工厂类模块
│   ├── __init__.py
│   ├── llm_factory.py      # LLM工厂类
│   └── embedding_factory.py # 嵌入模型工厂类
├── managers/                # 管理器模块
│   ├── __init__.py
│   ├── prompt_manager.py   # 提示模板管理器
│   └── knowledge_manager.py # 知识库管理器
├── utils/                   # 工具模块
│   ├── __init__.py
│   └── cli.py              # 命令行接口
└── README.md               # 本文件
```

## 快速开始

### 1. 作为库使用

```python
from capl_langchain import CAPLGenerator, CAPLGeneratorConfig

# 使用默认配置
config = CAPLGeneratorConfig()
generator = CAPLGenerator(config)

# 生成代码
code = generator.generate_code("测试雨刮器低速功能")
print(code)
```

### 2. 命令行使用

```bash
# 显示帮助
python3 capl_generator_langchain_new.py --help

# 显示知识库信息
python3 capl_generator_langchain_new.py --info

# 搜索知识库
python3 capl_generator_langchain_new.py --search "CAPL测试"

# 生成代码
python3 capl_generator_langchain_new.py "测试车门锁功能"
python3 capl_generator_langchain_new.py test_requirements.md --output test.cin
```

## 配置

### 环境变量

- `API_TYPE`: API类型 (ollama, openai)，默认：ollama
- `API_URL`: API地址，默认：http://localhost:11434
- `OLLAMA_MODEL`: 模型名称，默认：qwen3:30b-a3b
- `ENABLE_RAG`: 是否启用RAG，默认：true
- `KNOWLEDGE_BASE_DIR`: 知识库目录路径
- `VECTOR_DB_DIR`: 向量数据库目录路径

### 配置文件

使用 `prompt_config.ini` 文件进行配置：

```ini
[DEFAULT]
PROMPT_TEMPLATE_FILE = prompt_template.txt
KNOWLEDGE_BASE_DIR = knowledge_base
VECTOR_DB_DIR = vector_db
```

## API 参考

### CAPLGenerator

主要生成器类，提供代码生成功能。

#### 方法

- `generate_code(requirement, output_file=None)`: 生成CAPL代码
- `get_knowledge_base_info()`: 获取知识库信息
- `search_knowledge_base(query, k=4)`: 搜索知识库

### CAPLGeneratorConfig

配置类，管理所有配置选项。

## 迁移指南

从旧的 `capl_generator_langchain.py` 迁移到新的模块化版本：

1. **导入路径变化**:
   ```python
   # 旧版本
   from capl_generator_langchain import CAPLGenerator
   
   # 新版本
   from capl_langchain import CAPLGenerator
   ```

2. **配置方式**:
   ```python
   # 旧版本
   config = CAPLGeneratorConfig()
   
   # 新版本（相同）
   config = CAPLGeneratorConfig()
   ```

3. **命令行使用**:
   ```bash
   # 旧版本
   python3 capl_generator_langchain.py ...
   
   # 新版本
   python3 capl_generator_langchain_new.py ...
   ```

## 开发指南

### 添加新功能

1. **新的工厂类**: 添加到 `factories/` 目录
2. **新的管理器**: 添加到 `managers/` 目录
3. **新的工具**: 添加到 `utils/` 目录

### 测试

```bash
# 测试命令行接口
python3 -m capl_langchain.utils.cli --info

# 测试生成功能
python3 -m capl_langchain.utils.cli "测试需求" --verbose
```

## 注意事项

- 新的模块化版本与旧版本功能完全兼容
- 所有配置选项保持不变
- 命令行参数保持不变
- 支持向后兼容