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

2. OpenAI 兼容 API（如 LM Studio）：
   - 复制配置文件：`cp .env.openai.sample .env`
   - 配置项说明：
     - `API_TYPE=openai`：使用 OpenAI 兼容 API
     - `API_URL`：服务器地址，默认为 `http://localhost:1234/v1/chat/completions`
     - `OPENAI_MODEL`：使用的模型名称，默认为 `qwen/qwen3-1.7b`

## 使用方法
1. 选择并配置 API 类型（见上方配置说明）

2. 运行程序：
```bash
python ollama_file_processor.py /path/to/your/file
```

## 输出说明
- 程序会在当前目录下创建 `capl` 文件夹
- 生成的 CAPL 代码将保存在 `capl` 文件夹中，文件名与输入文件同名，扩展名为 `.md`