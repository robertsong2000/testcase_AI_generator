# CAPL 测试用例生成器

该程序用于向本地 Ollama 或 LM Studio 服务器发送文件，并根据文件内容生成 CAN 的 CAPL 代码。

## 环境准备
确保你已经安装了 Python 3.x，并且本地运行着 Ollama 或 LM Studio 服务器。

## 安装依赖
```bash
pip install -r requirements.txt
```

## 配置说明
程序支持两种 API 类型：

1. Ollama API（默认）：
   - 复制配置文件：`cp .env.ollama.sample .env`
   - 配置项说明：
     - `API_TYPE=ollama`：使用 Ollama API
     - `API_URL`：Ollama 服务器地址，默认为 `http://localhost:11434/api/generate`
     - `OLLAMA_MODEL`：使用的模型名称，默认为 `qwen3:30b-a3b`
     - `OLLAMA_CONTEXT_LENGTH`：上下文长度，默认为 8192
     - `OLLAMA_MAX_TOKENS`：最大输出长度，默认为 4096（防止循环）

2. OpenAI 兼容 API（如 LM Studio）：
   - 复制配置文件：`cp .env.openai.sample .env`
   - 配置项说明：
     - `API_TYPE=openai`：使用 OpenAI 兼容 API
     - `API_URL`：服务器地址，默认为 `http://localhost:1234/v1/chat/completions`
     - `OPENAI_MODEL`：使用的模型名称，默认为 `qwen/qwen3-1.7b`

## 提示词配置
程序支持自定义提示词模板，提供更好的灵活性：

### 提示词文件
- `prompt_template.txt`：标准提示词模板（默认）
- `prompt_template_simple.txt`：简化版提示词模板
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
1. 选择并配置 API 类型（见上方配置说明）

2. 运行程序：
```bash
python ollama_file_processor.py /path/to/your/file
```

## 输出说明
- 程序会在当前目录下创建 `capl` 文件夹
- 生成的 CAPL 代码将保存在 `capl` 文件夹中，文件名与输入文件同名，扩展名为 `.md`