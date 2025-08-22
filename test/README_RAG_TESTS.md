# LangChain RAG功能测试指南

本目录包含用于测试和验证LangChain RAG功能的测试文件。

## 测试文件说明

### 1. `test_rag_simple.py`
**基础RAG功能测试**
- 测试知识库初始化
- 验证文档加载
- 测试基本检索功能
- 检查向量数据库状态

**使用方法:**
```bash
python test/test_rag_simple.py
```

### 2. `test_rag_simple_v2.py`
**改进版RAG功能测试**
- 修复检索器获取问题
- 增加性能测试
- 更详细的检索结果展示
- 支持现有向量数据库

**使用方法:**
```bash
python test/test_rag_simple_v2.py
```

### 3. `test_rag_integration.py` (优化版)
**RAG集成测试**
- 实际CAPL代码生成测试
- RAG vs 无RAG对比测试
- 自定义需求测试
- **文件自动保存到子目录**: `test/rag_output/`

**使用方法:**
```bash
python test/test_rag_integration.py
```

## 目录结构 (优化后)

```
test/
├── rag_output/                    # 所有测试输出文件
│   ├── tests/                     # RAG集成测试生成的文件
│   │   ├── rag_test_01_*.capl
│   │   ├── rag_test_02_*.capl
│   │   └── ...
│   ├── comparisons/               # 对比测试文件
│   │   ├── comparison_no_rag_*.capl
│   │   ├── comparison_with_rag_*.capl
│   │   └── comparison_report_*.txt
│   └── custom/                    # 自定义需求测试
│       └── advanced_custom_test_*.capl
├── test_rag_simple.py            # 基础测试
├── test_rag_integration.py       # 集成测试
├── README_RAG_TESTS.md          # 本说明文件
└── ...
```

## 测试功能特性

### 知识库支持
- **支持的文件格式**: .txt, .md, .capl, .py
- **默认知识库位置**: `../knowledge_base/`
- **向量数据库位置**: `../vector_db/`

### 测试场景
1. **基础功能测试**
   - 文档加载和分割
   - 向量数据库创建
   - 相似性检索

2. **性能测试**
   - 初始化耗时测量
   - 检索响应时间
   - 内存使用评估

3. **集成测试**
   - 实际代码生成
   - 结果对比分析
   - 文件输出验证

## 预期输出示例

运行测试后，你会看到类似以下的输出：

```
================================================================================
LangChain RAG集成测试 - 优化版
================================================================================

🚀 开始测试1: RAG集成使用...
📁 输出目录: /path/to/test/rag_output/tests

🚀 开始测试2: RAG对比测试...
📁 输出目录: /path/to/test/rag_output/comparisons

🚀 开始测试3: 高级自定义需求...
📁 输出目录: /path/to/test/rag_output/custom

📁 生成的目录结构:
test/
└── rag_output/
    ├── tests/
    │   ├── rag_test_01_创建一个雨刷器间歇模式测试用例.capl (2324 bytes)
    │   ├── rag_test_02_测试CAN消息周期发送功能.capl (2412 bytes)
    │   └── ...
    ├── comparisons/
    │   ├── comparison_no_rag_*.capl
    │   └── ...
    └── custom/
        └── advanced_custom_test_*.capl
```

## 使用方法

### 运行单个测试文件

```bash
# 基础RAG功能测试
python test/test_rag_simple.py

# 改进版RAG功能测试（含性能测试）
python test/test_rag_simple_v2.py

# 完整RAG集成测试（文件保存到test/rag_output/子目录）
python test/test_rag_integration.py
```

### 运行所有测试
```bash
python test/test_rag_simple.py && python test/test_rag_simple_v2.py && python test/test_rag_integration.py
```

## 故障排除

### 常见问题

1. **"无法获取检索器"错误**
   - 确保向量数据库已正确初始化
   - 检查知识库文件是否存在
   - 使用 `--rebuild-rag` 参数重建数据库

2. **知识库文件找不到**
   - 确认 `knowledge_base/` 目录存在
   - 检查文件扩展名是否为支持的格式

3. **内存不足**
   - 减少知识库文件大小
   - 调整文本分割参数

### 调试技巧

1. **查看详细日志**
```bash
python test/test_rag_simple.py --verbose
```

2. **检查向量数据库内容**
```bash
ls -la vector_db/
```

3. **验证知识库文件**
```bash
ls -la knowledge_base/
```

4. **检查输出目录**
```bash
ls -la test/rag_output/
```

## 扩展测试

### 添加新的测试用例

在 `test_rag_integration.py` 中修改 `test_requirements` 列表：

```python
test_requirements = [
    "你的新测试需求",
    "另一个测试需求",
    # 添加更多...
]
```

### 自定义知识库

1. 将新文件放入 `knowledge_base/` 目录
2. 运行测试时会自动加载
3. 使用 `--rebuild-rag` 重建向量数据库

## 相关命令

### 基本使用
```bash
# 运行所有测试
python test/test_rag_integration.py

# 仅运行基础测试
python test/test_rag_simple.py

# 使用特定模型
python test/test_rag_integration.py --model qwen3:14b
```

### 清理和重建
```bash
# 删除向量数据库（需要重建）
rm -rf vector_db/

# 清理测试输出
rm -rf test/rag_output/

# 使用rebuild-rag参数
python capl_generator_langchain.py test.md --enable-rag --rebuild-rag
```