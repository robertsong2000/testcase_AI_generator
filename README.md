# Ollama 文件处理器

该程序用于向本地 Ollama 服务器发送文件，并根据文件内容生成 CAN 的 CAPL 代码。

## 环境准备
确保你已经安装了 Python 3.x，并且本地运行着 Ollama 服务器。

## 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法
1. 运行程序：
```bash
python ollama_file_processor.py
```
2. 根据提示输入要发送的文件路径。

## 配置说明
默认的 Ollama 服务器地址为 `http://192.168.1.2:11434`，如果需要修改，可以在代码中调整 `ollama_url` 参数。同时，需要将 `your_model_name` 替换为实际使用的模型名称。