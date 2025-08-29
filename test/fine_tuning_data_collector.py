#!/usr/bin/env python3
"""
测试规范到CAPL API映射数据收集工具
为模型微调准备训练数据
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

class FineTuningDataCollector:
    """收集测试规范到API的映射数据，用于模型微调"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "test" / "fine_tuning_data"
        self.data_dir.mkdir(exist_ok=True)
        
    def collect_from_generated_tests(self) -> List[Dict[str, str]]:
        """从生成的测试文件中收集映射数据"""
        generated_dir = self.project_root / "head_lamps_generated"
        mappings = []
        
        for file in generated_dir.glob("*.md"):
            if "TC_" in file.name:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取测试规范描述
                    spec_match = re.search(r'# (.*?)\n', content)
                    if spec_match:
                        test_spec = spec_match.group(1).strip()
                        
                        # 找到对应的.can文件
                        can_file = file.with_suffix('.can')
                        if can_file.exists():
                            with open(can_file, 'r', encoding='utf-8') as f:
                                capl_content = f.read()
                            
                            # 提取API调用
                            api_calls = re.findall(r'test[A-Z][a-zA-Z0-9_]*\(', capl_content)
                            if api_calls:
                                for api in set(api_calls):
                                    api_name = api.rstrip('(')
                                    mappings.append({
                                        "test_spec": test_spec,
                                        "api": api_name,
                                        "source_file": str(file.name)
                                    })
                                    
                except Exception as e:
                    print(f"处理文件 {file} 时出错: {e}")
        
        return mappings
    
    def collect_from_knowledge_base(self) -> List[Dict[str, str]]:
        """从知识库中提取映射关系"""
        kb_dir = self.project_root / "knowledge_base"
        mappings = []
        
        # 从增强测试模板收集
        template_file = kb_dir / "enhanced_test_templates.md"
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取测试场景和API映射
            sections = re.findall(r'### (.*?)\n(.*?)\n\*\*CAPL API:\*\* `(.*?)`', 
                                content, re.DOTALL)
            
            for section in sections:
                scenario = section[0].strip()
                description = section[1].strip()
                api = section[2].strip()
                
                mappings.append({
                    "test_spec": f"{scenario}: {description}",
                    "api": api,
                    "source_file": "enhanced_test_templates.md"
                })
        
        return mappings
    
    def generate_synthetic_data(self) -> List[Dict[str, str]]:
        """生成合成训练数据"""
        synthetic_data = [
            {
                "test_spec": "验证雨刷器间歇模式功能是否正常",
                "api": "testWaitForWiperIntermittentMode",
                "type": "synthetic"
            },
            {
                "test_spec": "检查CAN消息发送周期是否符合规范要求",
                "api": "testCanMsgCycleCheck",
                "type": "synthetic"
            },
            {
                "test_spec": "测试低功耗模式下GPIO引脚状态",
                "api": "testGPIOLowPowerMode",
                "type": "synthetic"
            },
            {
                "test_spec": "验证网络管理消息超时处理机制",
                "api": "testNetworkTimeoutHandling",
                "type": "synthetic"
            },
            {
                "test_spec": "测试诊断服务响应时间",
                "api": "testDiagnosticServiceResponseTime",
                "type": "synthetic"
            },
            {
                "test_spec": "检查车门锁状态切换延迟",
                "api": "testDoorLockStateTransitionDelay",
                "type": "synthetic"
            },
            {
                "test_spec": "验证座椅位置传感器校准",
                "api": "testSeatPositionSensorCalibration",
                "type": "synthetic"
            },
            {
                "test_spec": "测试环境光照传感器灵敏度",
                "api": "testAmbientLightSensorSensitivity",
                "type": "synthetic"
            }
        ]
        
        return synthetic_data
    
    def create_training_dataset(self) -> Dict[str, any]:
        """创建完整的训练数据集"""
        
        # 收集各类数据
        generated_data = self.collect_from_generated_tests()
        kb_data = self.collect_from_knowledge_base()
        synthetic_data = self.generate_synthetic_data()
        
        # 合并并去重
        all_data = []
        seen = set()
        
        for item in generated_data + kb_data + synthetic_data:
            key = (item["test_spec"], item["api"])
            if key not in seen:
                seen.add(key)
                all_data.append(item)
        
        # 分割训练集和验证集
        split_index = int(len(all_data) * 0.8)
        train_data = all_data[:split_index]
        val_data = all_data[split_index:]
        
        dataset = {
            "metadata": {
                "total_samples": len(all_data),
                "train_samples": len(train_data),
                "val_samples": len(val_data),
                "data_sources": {
                    "generated": len(generated_data),
                    "knowledge_base": len(kb_data),
                    "synthetic": len(synthetic_data)
                }
            },
            "train": train_data,
            "validation": val_data
        }
        
        # 保存数据集
        with open(self.data_dir / "training_dataset.json", 'w', 
                  encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        # 创建Hugging Face格式
        hf_format = {
            "train": [
                {
                    "instruction": "根据测试规范找出对应的CAPL API函数",
                    "input": item["test_spec"],
                    "output": item["api"]
                }
                for item in train_data
            ],
            "validation": [
                {
                    "instruction": "根据测试规范找出对应的CAPL API函数", 
                    "input": item["test_spec"],
                    "output": item["api"]
                }
                for item in val_data
            ]
        }
        
        with open(self.data_dir / "hf_training_data.json", 'w', 
                  encoding='utf-8') as f:
            json.dump(hf_format, f, ensure_ascii=False, indent=2)
        
        return dataset
    
    def generate_training_script(self):
        """生成模型微调脚本"""
        script_content = '''#!/usr/bin/env python3
"""
测试规范到CAPL API映射模型微调脚本
"""

from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)
from datasets import Dataset
import json
import torch
from pathlib import Path

def load_training_data(data_path):
    """加载训练数据"""
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def prepare_dataset(data):
    """准备Hugging Face数据集"""
    return Dataset.from_list(data["train"])

def tokenize_function(examples, tokenizer):
    """tokenize函数"""
    inputs = [f"测试规范: {inp} 对应的API是:" for inp in examples["input"]]
    targets = [out for out in examples["output"]]
    
    model_inputs = tokenizer(
        inputs, 
        max_length=256, 
        truncation=True, 
        padding="max_length"
    )
    
    labels = tokenizer(
        targets, 
        max_length=64, 
        truncation=True, 
        padding="max_length"
    )
    
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

def main():
    # 配置参数
    model_name = "meta-llama/Llama-3.2-3B-Instruct"
    data_path = "test/fine_tuning_data/hf_training_data.json"
    output_dir = "./fine_tuned_test_mapper"
    
    # 加载数据
    data = load_training_data(data_path)
    train_data = prepare_dataset(data)
    
    # 加载模型和tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # tokenize数据
    tokenized_dataset = train_data.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=train_data.column_names
    )
    
    # 训练参数
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        gradient_accumulation_steps=4,
        warmup_steps=100,
        learning_rate=2e-5,
        fp16=True,
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=100,
        save_steps=500,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
    )
    
    # 数据收集器
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True,
    )
    
    # 创建trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )
    
    # 开始训练
    trainer.train()
    
    # 保存模型
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print(f"模型微调完成，保存在: {output_dir}")

if __name__ == "__main__":
    main()
'''
        
        with open(self.data_dir / "fine_tune_model.py", 'w', 
                  encoding='utf-8') as f:
            f.write(script_content)
        
        # 创建运行脚本
        run_script = '''#!/bin/bash
# 模型微调运行脚本

echo "开始收集训练数据..."
python3 -c "
from test.fine_tuning_data_collector import FineTuningDataCollector
collector = FineTuningDataCollector('.')
dataset = collector.create_training_dataset()
print(f'收集到 {dataset[\"metadata\"][\"total_samples\"]} 个训练样本')
"

echo "训练数据已生成，位于 test/fine_tuning_data/"
echo "如需开始微调，请运行:"
echo "python test/fine_tuning_data/fine_tune_model.py"
'''
        
        with open(self.data_dir / "run_fine_tuning.sh", 'w', 
                  encoding='utf-8') as f:
            f.write(run_script)
        
        os.chmod(self.data_dir / "run_fine_tuning.sh", 0o755)

def main():
    """主函数"""
    collector = FineTuningDataCollector("/Users/robertsong/Downloads/code/testcase_AI_generator")
    
    print("开始收集微调训练数据...")
    dataset = collector.create_training_dataset()
    
    print(f"训练数据收集完成:")
    print(f"- 总样本数: {dataset['metadata']['total_samples']}")
    print(f"- 训练集: {dataset['metadata']['train_samples']}")
    print(f"- 验证集: {dataset['metadata']['val_samples']}")
    print(f"- 数据来源: {dataset['metadata']['data_sources']}")
    
    collector.generate_training_script()
    print("训练脚本已生成，位于 test/fine_tuning_data/")

if __name__ == "__main__":
    main()