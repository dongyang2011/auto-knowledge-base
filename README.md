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

### 1. 安装依赖

```bash
cd auto-knowledge-base
pip install -r requirements.txt
# 或者使用 pyproject.toml
pip install .
```

依赖：
- `requests` - HTTP 请求
- `feedparser` - RSS 解析
- `PyMuPDF` - PDF 文本提取
- `chromadb` - 向量存储
- `openai` - LLM API
- `pydantic` - 数据验证

### 2. 配置环境变量

复制 `.env.example` 到 `.env`:

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 API Key:

```
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o
# OPENAI_BASE_URL=https://api.openai.com/v1  # 如果需要代理，修改这里
```

### 3. 运行端到端流水线

搜索 arXiv 上的论文，下载 PDF，提取信息：

```bash
python run_pipeline.py --query "large language model" --limit 10
```

参数说明:
- `--query`: 搜索关键词，会作为分类目录名
- `--limit`: 最多处理多少篇论文

### 4. 输出结果

处理完成后，你会得到:

- **原始 PDF**: `originals/{query}/`
- **提取结果**: `extracted/{query}/{id}.md` (人工阅读) + `.json` (程序处理)
- **元数据库**: `data/articles.db` - 记录每篇文章的处理状态

### 5. 查看结果

你可以查看提取的 Markdown 文件，格式大概是这样:

```markdown
# Attention Is All You Need

## 基本信息
- **作者**: Ashish Vaswani, ...
- **年份**: 2017
- **来源**: arxiv

## 核心方案
本文提出了Transformer架构...

## 实验设置
### 数据集
- WMT 2014 English-German
...
```


## 文档

详细设计文档在 [Feishu Wiki](https://my.feishu.cn/wiki/DnOgwP2YWi1YVnk4EQacqakwn0b)
