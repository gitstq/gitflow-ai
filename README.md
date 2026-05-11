# 🚀 GitFlow AI

<div align="center">

**AI驱动的终端Git工作流智能助手 | AI-Powered Terminal Git Workflow Assistant**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

[简体中文](#简体中文) | [繁體中文](#繁體中文) | [English](#english)

</div>

---

## 简体中文

### 🎉 项目介绍

GitFlow AI 是一款**轻量级、零依赖**的终端Git工作流智能助手，专为提升开发者Git使用体验而设计。它能够智能分析代码变更、生成符合规范的提交信息、提供分支策略建议，并预警潜在的合并冲突。

**灵感来源**：在日常开发中，我们经常遇到提交信息不规范、分支管理混乱、合并冲突频发等问题。GitFlow AI 通过AI技术赋能传统Git工作流，让版本控制更加智能高效。

**自研差异化亮点**：
- 🧠 **智能语义分析** - 不仅生成提交信息，还能分析代码变更意图
- 🌿 **分支策略顾问** - 根据项目特征推荐最适合的工作流
- ⚠️ **冲突风险预警** - 提前识别潜在合并冲突，防患于未然
- 🔒 **本地优先设计** - 支持Ollama本地模型，代码隐私零泄露
- 🇨🇳 **中文语义理解** - 针对中文开发者优化的自然语言处理

### ✨ 核心特性

| 特性 | 描述 | 状态 |
|------|------|------|
| 🤖 **智能提交分析** | 自动分析代码变更，生成Conventional Commits格式建议 | ✅ 可用 |
| 📝 **AI提交生成** | 支持OpenAI/Anthropic/DeepSeek/Ollama多后端 | ✅ 可用 |
| 🌿 **分支策略顾问** | 检测并推荐Git Flow/GitHub Flow等最佳实践 | ✅ 可用 |
| ⚠️ **冲突风险预警** | 分析分支状态，提前预警合并风险 | ✅ 可用 |
| 📊 **仓库深度分析** | 提交统计、作者分布、分支健康度检查 | ✅ 可用 |
| 🎨 **精美终端UI** | 彩色输出、进度条、表格展示 | ✅ 可用 |
| 🔧 **零依赖核心** | 纯Python标准库实现，安装即用 | ✅ 可用 |
| 🌍 **多语言支持** | 简体中文、繁体中文、English | ✅ 可用 |

### 🚀 快速开始

#### 环境要求

- **Python**: 3.8 或更高版本
- **Git**: 2.20 或更高版本
- **操作系统**: Windows / macOS / Linux

#### 安装步骤

```bash
# 方式1: 从PyPI安装（推荐）
pip install gitflow-ai

# 方式2: 从源码安装
git clone https://github.com/gitstq/gitflow-ai.git
cd gitflow-ai
pip install -e .

# 方式3: 仅安装核心功能（零依赖）
pip install gitflow-ai

# 安装AI后端支持（可选）
pip install gitflow-ai[all]  # 安装所有AI后端
pip install gitflow-ai[ai]   # 仅OpenAI/Anthropic
pip install gitflow-ai[ollama]  # 仅Ollama本地模型
```

#### 快速启动

```bash
# 查看帮助
gitflow --help

# 查看仓库状态
gitflow status

# 获取提交建议
gitflow suggest

# 智能提交（分析+生成+提交）
gitflow commit

# 使用AI生成提交信息
gitflow ai-commit

# 查看分支策略建议
gitflow workflow
```

### 📖 详细使用指南

#### 智能提交分析

```bash
# 添加文件到暂存区
git add .

# 获取提交建议
gitflow suggest

# 输出示例:
# 📊 变更统计
#   变更文件: 3
#   新增行数: +45
#   删除行数: -12
#
# 📝 提交信息建议
#   1. feat(core): add new functionality to files [90%]
#   2. feat: add new functionality [85%]
```

#### AI生成提交信息

```bash
# 配置AI后端（选择其一）
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export DEEPSEEK_API_KEY="your-key"

# 或使用本地Ollama（无需API Key）
ollama run llama2

# 使用AI生成提交
gitflow ai-commit
```

#### 分支策略顾问

```bash
# 检测当前工作流
gitflow workflow --detect

# 对比不同工作流
gitflow workflow --compare

# 获取分支名建议
gitflow branch --suggest-name "添加用户认证功能"
# 输出: feature/add-user-auth

# 分析冲突风险
gitflow branch --risk
```

### 💡 设计思路与迭代规划

#### 技术选型原因

- **Python 3.8+**: 成熟稳定、跨平台、标准库丰富
- **零依赖核心**: 降低安装门槛，避免依赖地狱
- **插件化AI后端**: 灵活支持多种AI提供商，用户自主选择
- **TUI界面**: 终端原生体验，无需GUI依赖

#### 后续功能迭代计划

- [ ] **v1.1.0** - PR自动生成、Code Review建议
- [ ] **v1.2.0** - 提交历史可视化、变更趋势分析
- [ ] **v1.3.0** - 团队协作功能、共享配置
- [ ] **v2.0.0** - Web Dashboard、多仓库管理

#### 社区贡献方向

- 支持更多Git托管平台（GitLab、Gitee等）
- 扩展AI后端支持（Gemini、Azure等）
- 多语言本地化（日语、韩语、西班牙语）
- IDE插件开发（VS Code、JetBrains）

### 📦 打包与部署指南

#### 本地开发

```bash
# 克隆仓库
git clone https://github.com/gitstq/gitflow-ai.git
cd gitflow-ai

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或: venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/
flake8 src/
```

#### 构建发布

```bash
# 构建分发包
python -m build

# 上传到PyPI
python -m twine upload dist/*
```

### 🤝 贡献指南

我们欢迎所有形式的贡献！

**提交PR规范**：
1. Fork本仓库并创建特性分支 (`git checkout -b feature/amazing-feature`)
2. 提交更改 (`git commit -m 'feat: add amazing feature'`)
3. 推送到分支 (`git push origin feature/amazing-feature`)
4. 创建Pull Request

**Issue反馈规则**：
- 使用清晰的标题描述问题
- 提供复现步骤和环境信息
- 附上错误日志和截图（如有）

### 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 繁體中文

### 🎉 專案介紹

GitFlow AI 是一款**輕量級、零依賴**的終端Git工作流智能助手，專為提升開發者Git使用體驗而設計。

**核心功能**：
- 🤖 **智能提交分析** - 自動分析代碼變更，生成Conventional Commits格式建議
- 🌿 **分支策略顧問** - 根據專案特徵推薦最適合的工作流
- ⚠️ **衝突風險預警** - 提前識別潛在合併衝突
- 🔒 **本地優先設計** - 支援Ollama本地模型，代碼隱私零洩露

### ✨ 核心特性

- **零依賴核心** - 純Python標準庫實現，安裝即用
- **多AI後端支援** - OpenAI/Anthropic/DeepSeek/Ollama
- **精美終端UI** - 彩色輸出、進度條、表格展示
- **多語言支援** - 簡體中文、繁體中文、English

### 🚀 快速開始

```bash
# 安裝
pip install gitflow-ai

# 查看倉庫狀態
gitflow status

# 獲取提交建議
gitflow suggest

# 智能提交
gitflow commit
```

### 📄 開源協議

[MIT License](LICENSE)

---

## English

### 🎉 Project Introduction

GitFlow AI is a **lightweight, zero-dependency** terminal Git workflow assistant designed to enhance developers' Git experience.

**Key Features**:
- 🤖 **Smart Commit Analysis** - Auto-analyze code changes and generate Conventional Commits suggestions
- 🌿 **Branch Strategy Advisor** - Recommend optimal workflow based on project characteristics
- ⚠️ **Conflict Risk Warning** - Identify potential merge conflicts in advance
- 🔒 **Local-First Design** - Support Ollama local models for zero code privacy leakage

### ✨ Core Features

- **Zero-Dependency Core** - Pure Python standard library, install and use immediately
- **Multi-AI Backend Support** - OpenAI/Anthropic/DeepSeek/Ollama
- **Beautiful Terminal UI** - Colorful output, progress bars, table display
- **Multi-Language Support** - Simplified Chinese, Traditional Chinese, English

### 🚀 Quick Start

```bash
# Install
pip install gitflow-ai

# Check repository status
gitflow status

# Get commit suggestions
gitflow suggest

# Smart commit
gitflow commit
```

### 📄 License

[MIT License](LICENSE)

---

<div align="center">

**Made with ❤️ by GitFlow AI Team**

[⭐ Star us on GitHub](https://github.com/gitstq/gitflow-ai) | [🐛 Report Issue](https://github.com/gitstq/gitflow-ai/issues) | [💡 Request Feature](https://github.com/gitstq/gitflow-ai/issues)

</div>
