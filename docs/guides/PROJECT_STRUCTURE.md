# Hajimi King 项目文件结构索引

## 📁 当前项目结构

```
hajimi-king/
├── 📱 应用代码 (Application)
│   ├── app/                          # 主程序目录
│   │   ├── hajimi_king.py           # 主程序（串行版本）
│   │   └── api_key_scanner.py       # 主程序（并行版本，推荐使用）
│   ├── common/                       # 公共模块
│   │   ├── __init__.py
│   │   ├── config.py                # 配置管理
│   │   └── Logger.py                # 日志系统
│   └── utils/                        # 工具模块
│       ├── __init__.py
│       ├── file_manager.py          # 文件管理
│       ├── github_client.py         # GitHub API 客户端
│       ├── parallel_validator.py    # 并行验证器
│       ├── parallel_validator_integration.py
│       └── sync_utils.py            # 外部同步工具
│
├── 🐳 Docker 相关 (Docker)
│   ├── Dockerfile                    # Docker 镜像定义
│   ├── docker-compose.yml           # 开发环境配置
│   ├── docker-compose.prod.yml      # 生产环境配置
│   ├── .dockerignore                # Docker 忽略文件
│   ├── deploy.sh                    # 部署脚本
│   └── scripts/                     # 辅助脚本
│       ├── push-to-ghcr.sh         # 推送到 GitHub Container Registry (Linux/macOS)
│       └── push-to-ghcr.ps1        # 推送到 GitHub Container Registry (Windows)
│
├── 📚 文档 (Documentation)
│   ├── README.md                    # 项目说明
│   ├── HAJIMI_KING_项目深度解析文档.md  # 深度解析
│   ├── docker_deployment_guide.md   # Docker 部署指南
│   ├── github_container_registry_guide.md # GitHub Container Registry 指南
│   ├── docker_compose_commands_guide.md # Docker Compose 命令指南
│   ├── docker_healthcheck_explanation.md # Docker 健康检查说明
│   ├── proxy_configuration_guide.md # 代理配置指南
│   ├── data_directory_explanation.md # 数据目录说明
│   ├── queries_optimization_guide.md # 查询优化指南
│   ├── fix_import_error_plan.md    # 导入错误修复计划
│   ├── fix_summary.md               # 修复总结
│   └── docs/
│       └── parallel_validation_guide.md # 并行验证指南
│
├── ⚙️ 配置文件 (Configuration)
│   ├── .env                         # 环境变量（不应提交）
│   ├── env.example                  # 环境变量示例
│   ├── .env.docker.example          # Docker 环境变量示例
│   ├── queries.txt                  # 查询配置
│   ├── queries.example              # 查询配置示例
│   ├── pyproject.toml              # Python 项目配置
│   └── uv.lock                     # 依赖锁定文件
│
├── 🧪 测试 (Tests)
│   └── tests/
│       ├── performance_test.py      # 性能测试
│       └── performance_test_simple.py # 简单性能测试
│
├── 🔧 构建和部署 (Build & Deploy)
│   ├── Makefile                     # 构建自动化
│   ├── first_deploy.sh             # 首次部署脚本
│   ├── scripts/                    # 部署脚本
│   │   ├── push-to-ghcr.sh        # Linux/macOS 推送脚本
│   │   └── push-to-ghcr.ps1       # Windows 推送脚本
│   └── .github/                    # GitHub Actions 配置
│
├── 📊 数据目录 (Data) - 运行时生成
│   └── data/
│       ├── keys/                   # API 密钥存储
│       ├── logs/                   # 运行日志
│       ├── cache/                  # 缓存文件
│       ├── checkpoint.json         # 检查点
│       ├── queries.txt            # 查询配置
│       └── scanned_shas.txt       # 扫描记录
│
└── 🚫 忽略文件 (Ignore Files)
    ├── .gitignore                  # Git 忽略配置
    ├── .python-version             # Python 版本
    └── .kilocode/                  # IDE 配置

```

## 📋 文件分类索引

### 1. 核心功能模块
| 文件路径 | 功能描述 | 最后更新 |
|---------|---------|---------|
| `app/hajimi_king.py` | 主程序入口（串行版本） | 基础版本 |
| `app/api_key_scanner.py` | 主程序入口（并行版本） | 优化版本 |
| `utils/github_client.py` | GitHub API 搜索功能 | 核心功能 |
| `utils/parallel_validator.py` | 并行密钥验证 | 性能优化 |
| `utils/file_manager.py` | 文件和数据管理 | 核心功能 |
| `utils/sync_utils.py` | 外部系统同步 | 扩展功能 |

### 2. 配置和环境
| 文件路径 | 用途 | 状态 |
|---------|------|------|
| `common/config.py` | 全局配置管理 | 活跃 |
| `env.example` | 环境变量模板 | 模板 |
| `queries.example` | 查询配置模板 | 模板 |
| `pyproject.toml` | 项目依赖定义 | 活跃 |

### 3. Docker 和部署
| 文件路径 | 用途 | 环境 |
|---------|------|------|
| `Dockerfile` | 镜像构建定义 | 通用 |
| `docker-compose.yml` | 开发环境编排 | 开发 |
| `docker-compose.prod.yml` | 生产环境编排 | 生产 |
| `deploy.sh` | 零停机部署脚本 | 生产 |
| `scripts/push-to-ghcr.sh` | 推送镜像到 ghcr.io (Linux/macOS) | 通用 |
| `scripts/push-to-ghcr.ps1` | 推送镜像到 ghcr.io (Windows) | 通用 |
| `Makefile` | 自动化命令集合 | 通用 |

### 4. 文档
| 文件路径 | 内容 | 类型 |
|---------|------|------|
| `README.md` | 项目介绍和快速开始 | 用户文档 |
| `HAJIMI_KING_项目深度解析文档.md` | 技术架构详解 | 技术文档 |
| `docker_deployment_guide.md` | Docker 部署详细指南 | 部署文档 |
| `github_container_registry_guide.md` | GitHub Container Registry 使用指南 | 部署文档 |
| `docker_compose_commands_guide.md` | Docker Compose 命令参考 | 操作文档 |
| `proxy_configuration_guide.md` | 代理服务配置指南 | 配置文档 |
| `queries_optimization_guide.md` | 搜索查询优化策略 | 优化文档 |

## 🔧 建议的整理方案

### 1. 目录结构优化
```
hajimi-king/
├── src/                    # 源代码目录
│   ├── core/              # 核心功能
│   │   ├── __init__.py
│   │   ├── scanner.py     # 从 hajimi_king.py 重命名
│   │   └── parallel_scanner.py # 从 hajimi_king_parallel.py 重命名
│   ├── common/            # 保持不变
│   └── utils/             # 保持不变
├── config/                # 配置文件目录
│   ├── env.example
│   ├── queries.example
│   └── docker/           # Docker 配置
│       ├── Dockerfile
│       ├── docker-compose.yml
│       └── docker-compose.prod.yml
├── scripts/              # 脚本目录
│   ├── deploy.sh
│   ├── first_deploy.sh
│   ├── push-to-ghcr.sh
│   └── push-to-ghcr.ps1
├── docs/                 # 所有文档
│   ├── README.md
│   ├── guides/          # 指南类文档
│   ├── api/             # API 文档
│   └── architecture/    # 架构文档
├── tests/               # 保持不变
└── data/               # 运行时数据（.gitignore）
```

### 2. 文件命名规范
- Python 文件：使用小写下划线命名 `snake_case.py`
- 配置文件：使用小写连字符 `docker-compose.yml`
- 文档文件：使用大写字母 `README.md`, `CHANGELOG.md`
- 脚本文件：使用小写下划线 `deploy_script.sh`

### 3. 需要删除的冗余文件
- `fix_import_error_plan.md` - 临时修复文档，可移至 docs/archive/
- `fix_summary.md` - 临时修复总结，可移至 docs/archive/
- 重复的配置示例文件

### 4. 需要创建的新文件
- `CONTRIBUTING.md` - 贡献指南
- `.editorconfig` - 编辑器配置统一
- `requirements.txt` - 从 pyproject.toml 生成，便于兼容

## 🚀 快速导航

### 开发者快速开始
1. 环境配置：`env.example` → `.env`
2. 查询配置：`queries.example` → `data/queries.txt`
3. 运行程序：`python app/api_key_scanner.py`

### Docker 部署
1. 开发环境：`docker-compose up`
2. 生产部署：`./deploy.sh`
3. 查看文档：`docker_deployment_guide.md`

### 核心模块
- 搜索功能：`utils/github_client.py`
- 验证功能：`utils/parallel_validator.py`
- 数据管理：`utils/file_manager.py`
- 配置管理：`common/config.py`

## 📝 维护建议

1. **定期清理**：
   - 清理 data/ 目录下的旧日志
   - 归档过期的文档到 docs/archive/

2. **版本管理**：
   - 使用语义化版本号
   - 维护 CHANGELOG.md

3. **文档更新**：
   - 代码变更同步更新文档
   - 保持 README.md 简洁明了

4. **依赖管理**：
   - 定期更新依赖版本
   - 使用 uv.lock 锁定版本