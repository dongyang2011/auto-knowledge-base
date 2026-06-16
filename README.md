# Automated Personal Knowledge Base

全自动个人知识库系统 - 自动文章搜索 → 关键信息提取 → 关联分析 → 技术脉络梳理 → 趋势预测

## 架构

五层流水线架构：

1. **存储层** - 原始PDF、结构化提取结果、向量库、图数据库、元数据
2. **数据采集层** - 多源插件化文章搜索和PDF下载
3. **信息提取层** - LLM自动提取核心方案/实验/结论/创新点
4. **知识推理层** - 关联分析、脉络梳理、趋势预测
5. **知识输出层** - 自动生成脉络报告、知识图谱、趋势分析

## 目录结构

```
auto-knowledge-base/
├── originals/          # 原始PDF文件，按领域分目录
├── extracted/          # 提取后的结构化文件 (.md + .json)
├── outputs/            # 自动生成的分析报告
├── data/               # 数据库 (SQLite, Chroma, Neo4j)
├── logs/               # 处理日志
├── src/
│   ├── collectors/     # 数据采集器 (arXiv, GitHub, RSS, Semantic Scholar)
│   ├── extractors/     # 信息提取器 (LLM提取)
│   ├── storage/        # 存储层接口
│   └── utils/          # 工具函数
└── ...
```

## 快速开始

待补充...

## 文档

详细设计文档在 [Feishu Wiki](https://my.feishu.cn/wiki/DnOgwP2YWi1YVnk4EQacqakwn0b)
