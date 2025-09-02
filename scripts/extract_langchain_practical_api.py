#!/usr/bin/env python3
"""
LangChain实用API提取脚本 - 提取可直接使用的类和方法
"""

import sys
from pathlib import Path
import importlib
import inspect

# 添加虚拟环境路径
venv_path = Path(__file__).parent.parent / ".venv"
site_packages = venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
sys.path.insert(0, str(site_packages))

def get_practical_apis():
    """获取实用的LangChain API"""
    
    practical_apis = {
        'LLMs': {
            'OpenAI': 'langchain.llms.OpenAI',
            'ChatOpenAI': 'langchain.chat_models.ChatOpenAI',
            'HuggingFaceHub': 'langchain.llms.HuggingFaceHub',
            'Ollama': 'langchain.llms.Ollama'
        },
        'Chains': {
            'LLMChain': 'langchain.chains.LLMChain',
            'RetrievalQA': 'langchain.chains.RetrievalQA',
            'ConversationalRetrievalChain': 'langchain.chains.ConversationalRetrievalChain'
        },
        'Prompts': {
            'PromptTemplate': 'langchain.prompts.PromptTemplate',
            'ChatPromptTemplate': 'langchain.prompts.ChatPromptTemplate',
            'FewShotPromptTemplate': 'langchain.prompts.FewShotPromptTemplate'
        },
        'VectorStores': {
            'Chroma': 'langchain.vectorstores.Chroma',
            'FAISS': 'langchain.vectorstores.FAISS',
            'Pinecone': 'langchain.vectorstores.Pinecone'
        },
        'Embeddings': {
            'OpenAIEmbeddings': 'langchain.embeddings.OpenAIEmbeddings',
            'HuggingFaceEmbeddings': 'langchain.embeddings.HuggingFaceEmbeddings',
            'OllamaEmbeddings': 'langchain.embeddings.OllamaEmbeddings'
        },
        'DocumentLoaders': {
            'TextLoader': 'langchain.document_loaders.TextLoader',
            'DirectoryLoader': 'langchain.document_loaders.DirectoryLoader',
            'PyPDFLoader': 'langchain.document_loaders.PyPDFLoader'
        },
        'TextSplitters': {
            'RecursiveCharacterTextSplitter': 'langchain.text_splitter.RecursiveCharacterTextSplitter',
            'CharacterTextSplitter': 'langchain.text_splitter.CharacterTextSplitter'
        },
        'Memory': {
            'ConversationBufferMemory': 'langchain.memory.ConversationBufferMemory',
            'ConversationBufferWindowMemory': 'langchain.memory.ConversationBufferWindowMemory'
        },
        'Agents': {
            'initialize_agent': 'langchain.agents.initialize_agent',
            'create_react_agent': 'langchain.agents.create_react_agent'
        },
        'Retrievers': {
            'VectorStoreRetriever': 'langchain.vectorstores.base.VectorStoreRetriever',
            'MultiQueryRetriever': 'langchain.retrievers.MultiQueryRetriever'
        }
    }
    
    extracted_apis = {}
    
    for category, items in practical_apis.items():
        extracted_apis[category] = {}
        
        for name, import_path in items.items():
            try:
                module_path, class_name = import_path.rsplit('.', 1)
                module = importlib.import_module(module_path)
                cls = getattr(module, class_name)
                
                # 获取构造函数签名
                try:
                    sig = str(inspect.signature(cls.__init__))
                except:
                    sig = "()"
                
                # 获取文档
                doc = inspect.getdoc(cls) or "无文档"
                
                extracted_apis[category][name] = {
                    'import_path': import_path,
                    'signature': sig,
                    'doc': doc,
                    'example': generate_example(category, name, import_path)
                }
                
                print(f"✅ 提取了 {category}.{name}")
                
            except Exception as e:
                print(f"❌ 无法提取 {category}.{name}: {e}")
                extracted_apis[category][name] = {
                    'import_path': import_path,
                    'signature': "不可用",
                    'doc': f"导入错误: {e}",
                    'example': "# 导入失败，请检查依赖"
                }
    
    return extracted_apis

def generate_example(category, name, import_path):
    """生成使用示例"""
    
    examples = {
        'LLMs': {
            'OpenAI': """from langchain.llms import OpenAI

llm = OpenAI(temperature=0.7)
response = llm("Hello, how are you?")""",
            'ChatOpenAI': """from langchain.chat_models import ChatOpenAI

chat = ChatOpenAI(model="gpt-3.5-turbo")
response = chat.invoke([{"role": "user", "content": "Hello!"}])"""
        },
        'Chains': {
            'LLMChain': """from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

prompt = PromptTemplate(template="Say {adjective} to {name}!", input_variables=["adjective", "name"])
chain = LLMChain(llm=OpenAI(), prompt=prompt)
result = chain.run({"adjective": "hello", "name": "world"})""",
            'RetrievalQA': """from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

vectorstore = Chroma.from_texts(["Hello world"], OpenAIEmbeddings())
qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=vectorstore.as_retriever())
result = qa.run("What is the text about?")"""
        },
        'Prompts': {
            'PromptTemplate': """from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    template="Tell me a {adjective} story about {topic}.",
    input_variables=["adjective", "topic"]
)"""
        },
        'VectorStores': {
            'Chroma': """from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# 创建向量存储
vectorstore = Chroma.from_texts(
    ["Hello world", "Machine learning is fun"],
    OpenAIEmbeddings()
)

# 相似性搜索
results = vectorstore.similarity_search("hello", k=1)"""
        },
        'Embeddings': {
            'OpenAIEmbeddings': """from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
text_embedding = embeddings.embed_query("Hello world")"""
        },
        'DocumentLoaders': {
            'TextLoader': """from langchain.document_loaders import TextLoader

loader = TextLoader("path/to/file.txt")
documents = loader.load()""",
            'DirectoryLoader': """from langchain.document_loaders import DirectoryLoader

loader = DirectoryLoader("path/to/directory", glob="**/*.txt")
documents = loader.load()"""
        },
        'TextSplitters': {
            'RecursiveCharacterTextSplitter': """from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = splitter.split_text("Your long text here...")"""
        },
        'Memory': {
            'ConversationBufferMemory': """from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory()
memory.save_context({"input": "Hi"}, {"output": "Hello!"})
memory.load_memory_variables({})"""
        }
    }
    
    return examples.get(category, {}).get(name, f"# 使用 {import_path}")

def generate_markdown(apis):
    """生成markdown文档"""
    
    md = """# LangChain 实用API参考手册

> 这份文档包含了LangChain最常用的核心API，可以直接复制使用

## 📋 目录

"""
    
    for category in apis.keys():
        md += f"- [{category}](#{category.lower()})\n"
    
    for category, items in apis.items():
        md += f"\n## {category}\n\n"
        
        for name, info in items.items():
            md += f"### {name}\n"
            md += f"**导入**: `from {info['import_path'].rsplit('.', 1)[0]} import {name}`\n\n"
            md += f"**构造函数**: `{name}{info['signature']}`\n\n"
            md += f"**说明**: {info['doc'][:200]}...\n\n"
            md += "**使用示例**:\n```python\n"
            md += f"{info['example']}\n"
            md += "```\n\n"
            md += "---\n\n"
    
    return md

def main():
    """主函数"""
    print("🔍 开始提取LangChain实用API...")
    
    apis = get_practical_apis()
    
    # 生成markdown
    md_content = generate_markdown(apis)
    
    output_file = Path("knowledge_base/LANGCHAIN_PRACTICAL_API.md")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ 实用API文档已保存到: {output_file}")
    
    # 统计信息
    total_apis = sum(len(items) for items in apis.values())
    print(f"📊 总计提取了 {total_apis} 个实用API")

if __name__ == "__main__":
    main()