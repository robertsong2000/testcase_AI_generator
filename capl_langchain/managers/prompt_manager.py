"""提示模板管理器"""

import re
from pathlib import Path
from ..config.config import CAPLGeneratorConfig


class PromptTemplateManager:
    """提示模板管理器"""
    
    def __init__(self, config: CAPLGeneratorConfig):
        self.config = config
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """加载系统提示模板"""
        try:
            if self.config.prompt_template_file.exists():
                with open(self.config.prompt_template_file, 'r', encoding='utf-8') as f:
                    prompt = f.read()
            else:
                prompt = self._get_default_prompt()
            
            # 根据RAG启用状态和use_example_code配置决定如何处理示例代码
            if self.config.enable_rag and not self.config.use_example_code:
                # 启用RAG但禁用示例代码时，提示使用知识库
                example_placeholder = "# 示例代码已整合到RAG知识库中，将基于知识库内容生成"
            elif self.config.use_example_code:
                # 强制使用示例代码时，无论RAG是否启用
                if self.config.example_code_file.exists():
                    with open(self.config.example_code_file, 'r', encoding='utf-8') as f:
                        example_code = f.read()
                        example_placeholder = example_code
                else:
                    # 文件不存在时的回退提示
                    example_placeholder = "# 示例代码请参考知识库中的CAPL测试用例示例"
            else:
                # 禁用RAG且禁用示例代码时
                example_placeholder = "# 基于测试需求生成CAPL代码，不使用示例代码"
            
            # 替换示例代码占位符（如果存在）
            placeholder_text = "示例代码已移至单独的文件 example_code.txt 中，以保护敏感代码内容。"
            if placeholder_text in prompt:
                prompt = prompt.replace(placeholder_text, example_placeholder)
            elif self.config.enable_rag:
                # 如果提示模板中没有占位符，但启用了RAG，在开头添加提示
                prompt = f"# 使用RAG知识库中的示例代码\n\n{prompt}"
            
            # 转义非变量占位符的花括号
            prompt = self._escape_brackets(prompt)
                    
            return prompt
        except Exception as e:
            print(f"警告: 加载提示模板失败，使用默认模板: {e}")
            return self._get_default_prompt()
    
    def _escape_brackets(self, text: str) -> str:
        """转义非变量占位符的花括号
        
        LangChain使用Jinja2模板引擎，会将单花括号识别为变量占位符。
        此方法会转义所有非变量占位符的花括号，避免解析错误。
        """
        # 定义需要保留的变量占位符模式
        variable_patterns = [
            r'\{requirement\}',
            r'\{context\}',
        ]
        
        # 创建一个临时占位符映射
        temp_placeholders = {}
        placeholder_counter = 0
        
        # 首先保护已知的变量占位符
        protected_text = text
        for pattern in variable_patterns:
            matches = re.finditer(pattern, protected_text)
            for match in matches:
                placeholder = f"___VAR_PLACEHOLDER_{placeholder_counter}___"
                temp_placeholders[placeholder] = match.group()
                protected_text = protected_text.replace(match.group(), placeholder)
                placeholder_counter += 1
        
        # 转义所有剩余的单花括号
        # 将 { 替换为 {{，} 替换为 }}
        protected_text = re.sub(r'(?<!\{)\{(?!\{)', '{{', protected_text)
        protected_text = re.sub(r'(?<!\})\}(?!\})', '}}', protected_text)
        
        # 恢复被保护的变量占位符
        for placeholder, original in temp_placeholders.items():
            protected_text = protected_text.replace(placeholder, original)
        
        return protected_text
    
    def _get_default_prompt(self) -> str:
        """获取默认提示模板"""
        return """你是一个专业的CAPL测试代码生成专家。请根据提供的测试需求，生成高质量的CAPL测试代码。

要求：
1. 代码必须符合CAPL语法规范
2. 包含完整的测试逻辑和断言
3. 添加详细的注释说明
4. 遵循最佳实践和编码规范

测试需求：
{requirement}

请生成对应的CAPL测试代码："""