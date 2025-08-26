# CAPL 测试用例生成器

该程序用于向本地 Ollama 或 LM Studio 服务器发送文件，并根据文件内容生成 CAN 的 CAPL 代码。

## 项目结构
本项目包含以下主要组件：
- **CAPL 代码生成器**：根据测试用例生成 CAPL 代码
- **循环检测器**：检测和清理生成代码中的重复循环
- **代码清理器**：移除重复的变量定义
- **CAPL 语法检查器**：集成的 capl_checker 子模块，提供静态语法检查功能
- **VERSION**：项目版本文件
- **CHANGELOG.md**：项目变更日志文件

## 环境准备
确保你已经安装了 Python 3.x，并且本地运行着 Ollama 或 LM Studio 服务器。

## 安装依赖
```bash
pip install -r requirements.txt

# 如果是首次克隆项目，需要初始化子模块
git submodule update --init --recursive
```

## CAPL 语法检查器
本项目集成了 [capl_checker](https://github.com/robertsong2000/capl_checker) 作为子模块，提供 CAPL 代码的静态语法检查功能。

### 功能特性
- **语法检查**：检测基本的语法错误，如括号不匹配、缺少分号等
- **变量分析**：检测未定义变量、变量重复声明等问题
- **函数分析**：检测函数重复声明、参数问题等
- **代码风格**：检查命名规范、行长度、尾随空白等
- **CAPL特定检查**：针对CAPL语言特性的专门检查

### 使用语法检查器
```bash
# 检查生成的 CAPL 文件
python capl_checker/capl_checker.py capl/your_file.can

# 检查多个文件
python capl_checker/capl_checker.py capl/*.can

# 使用 XML 格式输出
python capl_checker/capl_checker.py --format xml capl/your_file.can

# 输出到文件
python capl_checker/capl_checker.py --output report.txt capl/your_file.can
```

## 评估框架

项目包含完整的评估框架，用于评估生成的CAPL代码质量和性能：

### 评估文件夹结构
```
evaluation/
├── evaluation_framework.py   # 评估框架核心代码
├── run_evaluation.py        # 评估执行脚本
└── evaluation_config.json   # 评估配置参数
```

### 使用方法
```bash
# 运行完整评估
python evaluation/run_evaluation.py

# 运行评估框架测试
python evaluation/evaluation_framework.py
```

### 评估指标
- **语法正确性**：检查CAPL语法错误
- **功能完整性**：验证测试用例覆盖度
- **代码质量**：评估代码结构和可读性
- **生成效率**：测量代码生成时间

## 项目结构
本项目包含以下主要组件：
- **CAPL 代码生成器**：根据测试用例生成 CAPL 代码
- **循环检测器**：检测和清理生成代码中的重复循环
- **代码清理器**：移除重复的变量定义
- **CAPL 语法检查器**：集成的 capl_checker 子模块，提供静态语法检查功能

## 环境准备
确保你已经安装了 Python 3.x，并且本地运行着 Ollama 或 LM Studio 服务器。

## 安装依赖
```bash
pip install -r requirements.txt

# 如果是首次克隆项目，需要初始化子模块
git submodule update --init --recursive
```

## CAPL 语法检查器
本项目集成了 [capl_checker](https://github.com/robertsong2000/capl_checker) 作为子模块，提供 CAPL 代码的静态语法检查功能。

### 功能特性
- **语法检查**：检测基本的语法错误，如括号不匹配、缺少分号等
- **变量分析**：检测未定义变量、变量重复声明等问题
- **函数分析**：检测函数重复声明、参数问题等
- **代码风格**：检查命名规范、行长度、尾随空白等
- **CAPL特定检查**：针对CAPL语言特性的专门检查

### 使用语法检查器
```bash
# 检查生成的 CAPL 文件
python capl_checker/capl_checker.py capl/your_file.can

# 检查多个文件
python capl_checker/capl_checker.py capl/*.can

# 使用 XML 格式输出
python capl_checker/capl_checker.py --format xml capl/your_file.can

# 输出到文件
python capl_checker/capl_checker.py --output report.txt capl/your_file.can
```

### 新功能：RAG文档信息显示

现在当使用RAG功能时，系统会自动显示检索到的文档信息：

#### 命令行测试
```bash
# 测试RAG搜索功能
python capl_generator_langchain.py --test-rag "CAPL测试用例"

# 指定检索文档数量
python capl_generator_langchain.py --test-rag "雨刷器测试" --k 5

# 使用特定配置测试
python capl_generator_langchain.py --api-type ollama --model llama3.2 --test-rag "CAN通信"
```

#### 显示内容
- 📄 文档来源路径（相对路径）
- 📝 内容摘要（前200字符）
- 📏 文档长度
- 🔢 检索到的文档数量

#### 正常生成时的显示
当使用RAG功能生成CAPL代码时，会自动显示：
```
📚 RAG状态: 已启用
📁 知识库目录: vector_db/
📊 向量数据库: 已存在 (包含 12 个文档)
🔍 检索到 3 个相关文档:
   📄 1. test_requirements/test_can_communication.txt
      摘要: 测试CAN总线通信功能，包括消息发送和接收...
      长度: 245 字符
   📄 2. test_requirements/test_low_power.txt
      摘要: 测试低功耗模式下的系统行为...
      长度: 189 字符
```

### 配置说明
程序支持两种 API 类型：

1. Ollama API（默认）：
   - 复制配置文件：`cp .env.ollama.sample .env`
   - 配置项说明：
     - `API_TYPE=ollama`：使用 Ollama API
     - `API_URL`：Ollama 服务器地址，默认为 `http://localhost:11434`，如果Ollama运行在远程服务器上，需要修改为相应的地址，例如 `http://192.168.1.2:11434`
     - `OLLAMA_MODEL`：使用的模型名称，默认为 `qwen3:30b-a3b`
     - `OLLAMA_CONTEXT_LENGTH`：上下文长度，默认为 8192
     - `OLLAMA_MAX_TOKENS`：最大输出长度，默认为 4096（防止循环）

### 特殊模型说明

**qwen3-coder 模型**：
- 该模型采用非思考模式（Non-Thinking）架构设计，仅支持非思考模式
- 输出不包含 `<think>` 标记
- 无需手动指定 `enable_thinking=False`
- 在测试中不会生成推理过程内容

2. OpenAI 兼容 API（如 LM Studio）：
   - 复制配置文件：`cp .env.openai.sample .env`
   - 配置项说明：
     - `API_TYPE=openai`：使用 OpenAI 兼容 API
     - `API_URL`：服务器地址，默认为 `http://localhost:1234/v1`，程序会自动添加 `/chat/completions` 端点
     - `OPENAI_MODEL`：使用的模型名称，默认为 `qwen/qwen3-1.7b`

## 提示词配置
程序支持自定义提示词模板，提供更好的灵活性：

### 提示词文件
- `prompt_template.txt`：标准提示词模板（默认）
- `prompt_template_simple.txt`：简化版提示词模板
- `example_code.txt`：示例代码文件，包含CAPL代码示例
- 你可以创建自己的提示词模板文件

### 配置文件
编辑 `prompt_config.ini` 来选择不同的提示词模板：

```ini
# 使用标准模板（默认）
PROMPT_TEMPLATE_FILE=prompt_template.txt

# 使用简化模板
# PROMPT_TEMPLATE_FILE=prompt_template_simple.txt

# 使用自定义模板
# PROMPT_TEMPLATE_FILE=my_custom_prompt.txt
```

### 自定义提示词
1. 创建新的提示词文件（如 `my_prompt.txt`）
2. 在 `prompt_config.ini` 中设置 `PROMPT_TEMPLATE_FILE=my_prompt.txt`
3. 重新运行程序即可使用新的提示词

## 使用方法

### 方法一：完整工作流程（推荐）
使用集成的工作流程脚本，一次性完成代码生成、清理和语法检查：

```bash
# 完整工作流程
python capl_workflow.py /path/to/your/file

# 自定义输出目录
python capl_workflow.py --output-dir my_capl_output /path/to/your/file

# 跳过某些步骤
python capl_workflow.py --skip-cleaning /path/to/your/file
python capl_workflow.py --skip-checking /path/to/your/file

# 指定语法检查器输出格式
python capl_workflow.py --checker-format xml /path/to/your/file
python capl_workflow.py --checker-format json /path/to/your/file

# 只进行清理和检查（跳过生成）
python capl_workflow.py --skip-generation /path/to/existing/file.can
```

### 方法二：分步执行
1. 选择并配置 API 类型（见上方配置说明）

2. 生成 CAPL 代码：
```bash
python capl_generator.py /path/to/your/file
```

如果需要调试并查看完整的prompt信息，可以使用以下命令：
```bash
python capl_generator.py --debug-prompt /path/to/your/file
```

3. 清理生成的代码（可选）：
```bash
python capl_cleaner.py capl/generated_file.can
```

4. 语法检查（可选）：
```bash
python capl_checker/capl_checker.py capl/generated_file.can
```

## 输出说明
- 程序会在当前目录下创建 `capl` 文件夹
- 生成的 CAPL 代码将保存在 `capl` 文件夹中，文件名与输入文件同名，扩展名为 `.md`

## 版本和变更日志

本项目使用 [VERSION](VERSION) 文件来跟踪当前版本号，使用 [CHANGELOG.md](CHANGELOG.md) 文件来记录所有重要的变更历史。

- VERSION: 包含当前项目的版本号
- CHANGELOG.md: 详细记录每个版本的新增功能、变更和修复内容

请定期查看 CHANGELOG.md 以了解项目的最新更新。

```