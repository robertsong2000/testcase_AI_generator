# CAPL测试用例生成器 - 评估框架

本目录包含CAPL测试用例生成器的完整评估框架，用于系统性地评估和优化代码生成质量。

## 📁 目录结构

```
evaluation/
├── README.md                 # 本说明文档
├── evaluation_framework.py   # 评估框架核心代码
├── run_evaluation.py        # 评估执行脚本
├── evaluation_config.json   # 评估配置参数
└── reports/                 # 评估报告输出目录（运行时生成）
    ├── baseline_report.json    # 基线评估报告
    ├── improvement_report.json # 改进后评估报告
    └── comparison_report.json  # 对比分析报告
```

## 🎯 评估框架功能

### 1. 代码质量评估
- **语法正确性**：CAPL语法错误检测
- **功能完整性**：测试用例覆盖度验证
- **代码质量**：结构清晰度、命名规范、注释完整性
- **性能指标**：生成时间、代码长度、复杂度分析

### 2. 评估指标体系
| 指标类别 | 权重 | 阈值 | 说明 |
|---------|------|------|------|
| 语法评分 | 30% | ≥90分 | 语法错误数量 |
| 功能完整性 | 40% | ≥85分 | 测试用例覆盖率 |
| 代码质量 | 20% | ≥80分 | 可读性和规范性 |
| 生成效率 | 10% | ≤30秒 | 代码生成时间 |

### 3. 基准测试数据集
- **基础功能测试**：50个核心测试用例
- **中级功能测试**：30个复杂场景用例
- **高级功能测试**：20个边界条件用例

## 🚀 快速开始

### 1. 安装依赖
```bash
# 进入项目根目录
cd /path/to/testcase_AI_generator

# 安装评估框架依赖
pip install pandas numpy matplotlib seaborn
```

### 2. 运行完整评估
```bash
# 执行完整评估流程
python evaluation/run_evaluation.py

# 生成详细报告
python evaluation/run_evaluation.py --detailed

# 对比基线和改进结果
python evaluation/run_evaluation.py --compare-baseline
```

### 3. 单独运行评估模块
```bash
# 测试评估框架
python evaluation/evaluation_framework.py

# 使用自定义配置
python evaluation/run_evaluation.py --config custom_config.json
```

## 📊 评估报告解读

### 报告文件说明
- `baseline_report.json`：当前系统的基线性能指标
- `improvement_report.json`：优化后的性能指标
- `comparison_report.json`：基线与改进的对比分析

### 关键指标解释
```json
{
  "syntax_score": 92.5,        // 语法正确性评分 (0-100)
  "functionality_score": 87.3, // 功能完整性评分 (0-100)
  "quality_score": 83.8,       // 代码质量评分 (0-100)
  "generation_time": 25.6,     // 平均生成时间 (秒)
  "overall_score": 88.2        // 综合评分 (0-100)
}
```

## 🔧 配置自定义

### 修改评估参数
编辑 `evaluation_config.json` 文件：

```json
{
  "metrics": {
    "syntax_weight": 0.30,
    "functionality_weight": 0.40,
    "quality_weight": 0.20,
    "performance_weight": 0.10
  },
  "thresholds": {
    "min_syntax_score": 90,
    "min_functionality_score": 85,
    "min_quality_score": 80,
    "max_generation_time": 30
  }
}
```

### 添加自定义测试用例
1. 在 `sample/` 目录添加新的测试用例文件
2. 更新评估配置中的测试套件
3. 重新运行评估

## 📈 优化路线图

评估框架支持以下优化阶段：

### Phase 0: 评估测试机制（当前）
- ✅ 建立评估基线
- ✅ 定义评估指标
- ✅ 创建测试数据集

### Phase 1-5: 逐步优化
- **Phase 1**: 基础优化（提示词工程）
- **Phase 2**: RAG系统集成
- **Phase 3**: 模型微调
- **Phase 4**: 高级功能
- **Phase 5**: 性能扩展

## 🐛 常见问题

### Q: 评估框架缺少依赖包
```bash
pip install pandas numpy matplotlib seaborn
```

### Q: 如何添加新的评估指标
1. 修改 `evaluation_framework.py` 添加新指标计算逻辑
2. 更新 `evaluation_config.json` 中的权重配置
3. 重新运行评估

### Q: 如何对比不同版本的性能
```bash
# 运行基线评估
python evaluation/run_evaluation.py --baseline

# 运行改进版本评估
python evaluation/run_evaluation.py --improved

# 生成对比报告
python evaluation/run_evaluation.py --compare
```

## 📞 技术支持

如需技术支持或有改进建议，请：
1. 查看 `TODO.txt` 中的详细计划
2. 检查评估报告中的具体错误
3. 根据评估结果调整优化策略

---

**评估框架版本**: v1.0  
**最后更新**: 2024年12月