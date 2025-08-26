# Changelog

## [1.1.0] - 2025-08-26

### Added
- LangChain重构版本，模块化代码结构
- RAG知识库检索功能，支持上下文增强的代码生成
- CLI命令行工具增强，支持多种参数配置
- 支持自定义RAG检索文档数量（-k参数）
- 知识库信息查询和搜索功能
- 示例代码控制选项（--use-example-code/--no-use-example-code）
- 调试模式支持（--debug-prompt）

### Changed
- API类型简化，仅支持ollama和openai两种选项
- 优化RAG检索逻辑，支持动态调整检索数量
- 改进配置系统，支持环境变量和CLI参数优先级
- 更新项目结构，分离核心逻辑到capl_langchain模块

### Fixed
- CLI帮助文本格式问题
- RAG知识库初始化和文档加载稳定性
- 代码生成过程中的异常处理

## [1.0.0] - 2025-08-20

### Added
- Initial release of the testcase_AI_generator project
- CAPL code generation from natural language requirements
- CAPL code extraction and cleaning utilities
- PDF to Markdown testcase conversion tools
- AI model connection testing utility
- Documentation and examples

### Changed
- Optimized AI model response handling with timing and code length metrics

### Fixed
- Parameter priority handling in AI model calls
- Code extraction and cleaning processes