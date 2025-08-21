# 测试目录说明

此目录包含CAPL测试用例和AI测试相关工具。

## 目录结构

```
test/
├── README.md                           # 本说明文档
├── sample_wiper_test.cin              # 雨刮器测试用例示例
├── ollama_example.py                  # Ollama AI连接测试示例
├── debug_thinking.py                  # AI调试工具
├── test_thinking.py                   # AI思考过程测试
├── test_gpt_oss.py                    # GPT/OSS模型测试工具
```

## 测试用例列表

### CAPL测试用例

#### 示例测试用例
- `sample_wiper_test.cin`
  - 雨刮器功能测试示例
  - 展示标准的CAPL测试用例格式
  - 可作为新测试用例的模板

### AI测试工具

#### 1. AI连接测试
- `ollama_example.vpy`
  - 测试Ollama AI模型的基本连接
  - 支持流式响应测试
  - 可配置模型和API地址

#### 2. AI思考过程测试
- `test_thinking.py`
  - 测试AI的思考过程和分析能力
  - 验证AI对测试用例的理解

#### 3. AI调试工具
- `debug_thinking.py`
  - AI模型调试和诊断工具
  - 用于分析AI响应和调试连接问题

#### 4. GPT/OSS测试
- `test_gpt_oss.py`
  - 测试GPT和开源模型的集成
  - 模型性能对比测试

### AI测试工具

#### 1. AI连接测试
- `ollama_example.py`
  - 测试Ollama AI模型的基本连接
  - 支持流式响应测试
  - 可配置模型和API地址

#### 2. AI模型调试
- `debug_thinking.py`
  - AI模型调试和诊断工具
  - 用于分析AI响应和调试连接问题

#### 3. 通用AI测试
- `test_ai_connection.py`
  - 通用AI模型连接测试
  - 支持多种AI提供商

#### 4. GPT/OSS测试
- `test_gpt_oss.py`
  - 测试GPT和开源模型的集成
  - 模型性能对比测试

## 测试标准

### AI测试标准

AI测试工具遵循以下标准：

1. **环境配置**
   - 使用`.env`文件配置AI模型参数
   - 支持命令行参数覆盖
   - 默认配置安全可靠

2. **连接测试**
   - 提供连接状态反馈
   - 支持错误处理和重试机制
   - 显示配置信息便于调试

3. **响应验证**
   - 验证AI响应格式正确性
   - 检查响应时间性能
   - 提供详细的错误信息

## 使用方法

### CAPL测试用例使用

`sample_wiper_test.cin` 作为示例测试用例，展示了标准的CAPL测试格式，可用作新测试用例的模板。

#### 创建新的CAPL测试用例

1. 复制 `sample_wiper_test.cin` 作为模板
2. 根据实际功能需求修改测试逻辑
3. 调整信号名称和测试条件
4. 在CAPL环境中编译和运行

#### 集成到现有系统

1. 将测试文件复制到CAPL测试环境
2. 确保包含必要的测试框架文件
3. 根据实际CAN信号定义调整信号名称
4. 运行测试用例进行功能验证

### AI测试工具使用

#### 1. Ollama测试
```bash
cd test/
python ollama_example.py
```

#### 2. 通用AI连接测试
```bash
python test_ai_connection.py
```

#### 3. 配置环境变量
复制环境变量模板：
```bash
cp ../.env.ollama.sample ../.env
# 或
cp ../.env.openai.sample ../.env
```

编辑`.env`文件设置AI模型参数：
```
MODEL_TYPE=ollama
API_URL=http://localhost:11434
MODEL_NAME=qwen3-coder:30b
API_KEY=your-api-key
```

## 扩展建议

### CAPL测试扩展
基于 `sample_wiper_test.cin` 模板，可以创建更多功能测试用例：

- **车身控制扩展**
  - 方向盘调节功能测试
  - 后视镜控制测试（电动调节、加热、折叠）
  - 车内照明控制测试（氛围灯、阅读灯）
  - 天窗控制测试

- **安全系统测试**
  - 安全带提醒系统测试
  - 安全气囊系统测试
  - 防盗系统测试
  - 胎压监测系统测试

- **信息娱乐系统**
  - 多媒体系统测试
  - 导航系统测试
  - 语音控制系统测试
  - 蓝牙连接测试

- **高级驾驶辅助**
  - 倒车雷达测试
  - 倒车影像测试
  - 车道保持辅助测试
  - 自适应巡航测试

### AI测试工具扩展

- **模型支持扩展**
  - 支持更多开源模型（Llama、Mistral等）
  - 集成商业API（OpenAI、Claude、Gemini等）
  - 模型性能基准测试

- **功能增强**
  - 批量测试用例生成
  - 测试结果可视化
  - 性能监控和报告

### 文件管理建议

- 将新的CAPL测试用例添加到test/目录
- 保持命名规范：以`tc_`前缀开头
- 使用sample_wiper_test.cin作为模板创建新测试用例
- 为每个新功能创建独立的测试文件

## 注意事项

### 环境要求
- Python 3.7+
- 安装依赖：`pip install -r ../requirements.txt`
- 确保Ollama服务已启动（如果使用本地模型）

### 文件命名规范
- CAPL测试用例：以`tc_`前缀开头，描述功能
- Python测试工具：以`test_`前缀开头，描述测试内容
- 调试工具：以`debug_`前缀开头

### 版本控制
- 所有测试文件已纳入Git版本控制
- 使用有意义的提交信息
- 定期更新文档以反映最新变化

所有新增测试用例和工具应保持与现有标准一致，确保兼容性和可维护性。