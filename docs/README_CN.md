# 🎪 Hajimi King - 自动化 API 密钥发现系统

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Status](https://img.shields.io/badge/status-beta-yellow.svg)](https://github.com/yourusername/hajimi-king)

**人人都是哈基米大王** 👑

[English](README.md) | [简体中文](#) | [快速参考](QUICK_REFERENCE.md) | [文档](docs/) | [API 参考](docs/api/)

</div>

---

## 📋 目录

- [项目概述](#-项目概述)
- [核心功能](#-核心功能)
- [快速开始](#-快速开始)
- [安装说明](#-安装说明)
- [使用方法](#-使用方法)
- [配置详情](#-配置详情)
- [API 文档](#-api-文档)
- [Docker 部署](#-docker-部署)
- [故障排除](#-故障排除)
- [贡献指南](#-贡献指南)
- [更新日志](#-更新日志)
- [许可证](#-许可证)

---

## 🌟 项目概述

Hajimi King 是一个自动化系统，专门用于从公开代码仓库中发现和验证 API 密钥。它利用 GitHub 的搜索 API 来查找可能暴露的凭据，并使用并行处理技术高效地验证它们。

> ⚠️ **免责声明**：此工具仅用于教育和安全研究目的。请始终遵守 API 服务条款，并负责任地处理发现的密钥。

### 主要优势

- 🔍 **智能搜索**：先进的查询策略，实现高效发现
- ⚡ **并行验证**：多线程验证，提供高性能
- 🔄 **增量扫描**：从上次中断的地方继续
- 🐳 **Docker 就绪**：支持 Docker 轻松部署
- 📊 **外部同步**：与负载均衡器和密钥管理系统集成

---

## ✨ 核心功能

### 基础功能

1. **GitHub 代码搜索** - 使用可自定义的查询搜索 API 密钥
2. **并行验证** - 同时验证多个密钥
3. **智能过滤** - 自动过滤文档和测试文件
4. **代理支持** - 通过多个代理轮换以提高稳定性
5. **外部同步** - 同步到 [Gemini-Balancer](https://github.com/snailyp/gemini-balance) 和 [GPT-Load](https://github.com/tbphp/gpt-load)

### 高级功能

- 📈 支持检查点的增量扫描
- 🔐 安全的凭据管理
- 📝 详细的日志记录和报告
- 🚀 零停机部署
- 📊 性能监控

---

## 🚀 快速开始

> 📖 **需要快速命令参考？** 查看我们的[快速参考指南](QUICK_REFERENCE.md)获取所有常用命令和操作。

### 前置要求

- Python 3.11 或更高版本
- Docker（可选，用于容器化部署）
- GitHub 个人访问令牌

### 一键安装

```bash
# 克隆并设置
git clone https://github.com/yourusername/hajimi-king.git && cd hajimi-king && make setup
```

### 基本使用

```bash
# 配置环境
cp env.example .env
# 编辑 .env 文件，填入你的 GitHub token

# 运行扫描器
python app/api_key_scanner.py
```

---

## 📦 安装说明

### 方法 1：本地安装

1. **克隆仓库**
   ```bash
   git clone https://github.com/yourusername/hajimi-king.git
   cd hajimi-king
   ```

2. **设置 Python 环境**
   ```bash
   # 使用 venv
   python -m venv .venv
   source .venv/bin/activate  # Windows 上使用: .venv\Scripts\activate
   
   # 安装依赖
   pip install -r requirements.txt
   ```

3. **配置环境**
   ```bash
   cp env.example .env
   # 编辑 .env 文件进行配置
   ```

### 方法 2：Docker 安装

```bash
# 使用 docker-compose
docker-compose up -d

# 或手动构建
docker build -t hajimi-king:latest .
docker run -d --name hajimi-king -v ./data:/app/data hajimi-king:latest
```

### 方法 3：使用 Makefile

```bash
# 查看可用命令
make help

# 快速设置并运行
make build
make run
```

---

## 💻 使用方法

### 命令行界面

```bash
# 基本用法
python app/api_key_scanner.py

# 使用自定义配置
python app/api_key_scanner.py --config custom.env

# 运行特定查询
python app/api_key_scanner.py --queries custom_queries.txt
```

### Python API

```python
from utils.github_client import GitHubClient
from utils.parallel_validator import ParallelKeyValidator

# 初始化客户端
github = GitHubClient(tokens=['your_token'])
validator = ParallelKeyValidator(max_workers=10)

# 搜索密钥
results = github.search_for_keys("AIzaSy in:file")

# 验证密钥
valid_keys = validator.validate_batch(potential_keys)
```

### Docker 命令

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f hajimi-king

# 停止服务
docker-compose down

# 使用自定义配置运行
docker run -v $(pwd)/custom.env:/app/.env hajimi-king:latest
```

---

## ⚙️ 配置详情

### 环境变量

基于 `env.example` 创建 `.env` 文件：

```bash
# 必需配置
GITHUB_TOKENS=ghp_token1,ghp_token2,ghp_token3  # GitHub API 令牌（逗号分隔）

# 搜索配置
QUERIES_FILE=queries.txt                        # 搜索查询文件
DATE_RANGE_DAYS=730                            # 仓库年龄过滤（天数）
FILE_PATH_BLACKLIST=readme,docs,test,example   # 要跳过的路径

# 性能配置
HAJIMI_MAX_WORKERS=10                          # 并行验证线程数
HAJIMI_BATCH_SIZE=10                           # 批处理大小
HAJIMI_BATCH_INTERVAL=60                       # 批处理间隔（秒）

# 代理配置（可选）
PROXY=http://proxy1:8080,http://proxy2:8080    # 代理列表（逗号分隔）

# 外部同步（可选）
GEMINI_BALANCER_SYNC_ENABLED=false             # 启用 Gemini Balancer 同步
GEMINI_BALANCER_URL=http://balancer:8080       # Balancer URL
GEMINI_BALANCER_AUTH=your_auth_token           # Balancer 认证令牌

# 数据存储
DATA_PATH=./data                               # 数据目录路径
```

### 搜索查询配置

编辑 `data/queries.txt` 来自定义搜索模式：

```bash
# 基础搜索
AIzaSy in:file

# 环境文件
AIzaSy in:file filename:.env
AIzaSy in:file filename:.env.example

# 特定语言
AIzaSy in:file extension:py "GEMINI_API_KEY"
AIzaSy in:file language:javascript filename:config.js

# 高级模式
"AIzaSy" "gemini" in:file
AIzaSy in:file size:<10000
```

查看[查询优化指南](queries_optimization_guide.md)了解高级策略。

---

## 📚 API 文档

### 核心模块

#### GitHubClient

处理 GitHub API 交互：

```python
class GitHubClient:
    def __init__(self, tokens: List[str])
    def search_for_keys(self, query: str) -> Dict[str, Any]
    def get_file_content(self, item: Dict[str, Any]) -> Optional[str]
```

#### ParallelKeyValidator

并行验证 API 密钥：

```python
class ParallelKeyValidator:
    def __init__(self, max_workers: int = 10)
    def validate_batch(self, keys: List[str]) -> Dict[str, ValidationResult]
    def get_stats(self) -> ValidationStats
```

#### FileManager

管理数据持久化：

```python
class FileManager:
    def __init__(self, data_dir: str)
    def save_valid_keys(self, repo: str, path: str, url: str, keys: List[str])
    def load_checkpoint(self) -> Checkpoint
    def save_checkpoint(self, checkpoint: Checkpoint)
```

完整的 API 参考请查看 [API 文档](docs/api/)。

---

## 🐳 Docker 部署

### 开发环境

```yaml
# docker-compose.yml
version: '3.8'
services:
  hajimi-king:
    build: .
    volumes:
      - ./data:/app/data
    env_file:
      - .env
```

### 生产部署

```bash
# 零停机部署
./deploy.sh --version v1.0.0

# 手动蓝绿部署
docker-compose -f docker-compose.prod.yml up -d
```

### Docker Hub

```bash
# 从 Docker Hub 拉取
docker pull yourusername/hajimi-king:latest

# 使用自定义配置运行
docker run -d \
  --name hajimi-king \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env \
  yourusername/hajimi-king:latest
```

查看 [Docker 部署指南](docker_deployment_guide.md) 了解详细说明，或查看[快速参考](QUICK_REFERENCE.md#-docker-镜像管理)获取常用 Docker 命令。

---

## 🔧 故障排除

### 常见问题

#### 1. 模块导入错误

```bash
ModuleNotFoundError: No module named 'common'
```

**解决方案**：确保从项目根目录运行：
```bash
cd /path/to/hajimi-king
python app/api_key_scanner.py  # 使用新的文件名
```

#### 2. GitHub API 速率限制

```
Error: API rate limit exceeded
```

**解决方案**：
- 在 `.env` 中添加更多 GitHub 令牌
- 实施代理轮换
- 降低请求频率

#### 3. 权限被拒绝

```
PermissionError: [Errno 13] Permission denied: './data'
```

**解决方案**：
```bash
# 修复权限
chmod -R 755 data/
# 或对于 Docker
docker exec hajimi-king chown -R appuser:appuser /app/data
```

#### 4. 内存问题

**解决方案**：调整工作线程数和批处理大小：
```bash
HAJIMI_MAX_WORKERS=5
HAJIMI_BATCH_SIZE=5
```

### 调试模式

启用调试日志：
```bash
# 在 .env 中
LOG_LEVEL=DEBUG

# 或通过命令行
LOG_LEVEL=DEBUG python app/api_key_scanner.py
```

### 获取帮助

1. 查看 [常见问题](docs/FAQ.md)
2. 搜索 [Issues](https://github.com/yourusername/hajimi-king/issues)
3. 加入我们的 [Discord](https://discord.gg/hajimi-king)

---

## 🤝 贡献指南

我们欢迎贡献！请查看我们的[贡献指南](CONTRIBUTING.md)了解详情。

### 开发设置

```bash
# Fork 并克隆
git clone https://github.com/yourusername/hajimi-king.git
cd hajimi-king

# 创建分支
git checkout -b feature/amazing-feature

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/

# 提交 PR
```

### 代码风格

- 遵循 PEP 8
- 使用 Black 进行格式化
- 运行 Ruff 进行代码检查
- 为新功能编写测试

---

## 📝 更新日志

### [未发布]
- 数据库支持密钥存储
- Web UI 密钥管理
- 高级分析仪表板

### [v0.0.1-beta] - 2024-01-07
- 初始 beta 版本发布
- 并行验证支持
- Docker 部署
- 外部同步集成

查看 [CHANGELOG.md](CHANGELOG.md) 了解完整历史。

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

- 感谢所有贡献者
- 受安全研究社区启发
- 使用 Python 和 Docker 用 ❤️ 构建

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请在 GitHub 上给我们一个星标！**

[报告问题](https://github.com/yourusername/hajimi-king/issues) · [功能请求](https://github.com/yourusername/hajimi-king/issues) · [文档](docs/)

</div>