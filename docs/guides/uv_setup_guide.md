# UV 工具使用指南 - 现代化的 Python 环境管理

## 目录
1. [什么是 UV](#什么是-uv)
2. [UV 的优势](#uv-的优势)
3. [安装 UV](#安装-uv)
4. [使用 UV 管理项目](#使用-uv-管理项目)
5. [从 pip 迁移到 UV](#从-pip-迁移到-uv)
6. [常见问题解决](#常见问题解决)
7. [最佳实践](#最佳实践)

## 什么是 UV

UV 是一个用 Rust 编写的极速 Python 包管理器和项目管理工具，旨在替代 pip、pip-tools、pipx、poetry、pyenv、virtualenv 等工具。它由 Astral 团队开发，提供了统一的工具链来管理 Python 项目。

## UV 的优势

### 性能优势
- **速度极快**：比 pip 快 10-100 倍
- **并行下载**：同时下载多个包
- **智能缓存**：避免重复下载
- **内存效率**：Rust 实现，内存占用小

### 功能优势
- **统一工具链**：一个工具替代多个工具
- **跨平台锁文件**：确保依赖一致性
- **内置虚拟环境管理**：无需单独安装 virtualenv
- **Python 版本管理**：类似 pyenv 功能
- **兼容性好**：完全兼容 pip 和 requirements.txt

### 对比传统工具
| 功能 | 传统方式 | UV |
|------|---------|-----|
| 包管理 | pip | uv pip |
| 虚拟环境 | venv/virtualenv | uv venv |
| 依赖锁定 | pip-freeze | uv.lock |
| Python 版本管理 | pyenv | uv python |
| 速度 | 慢 | 极快 |

## 安装 UV

### Windows
```powershell
# 使用 PowerShell (推荐)
irm https://astral.sh/uv/install.ps1 | iex

# 或使用 pip
pip install uv

# 或使用 pipx
pipx install uv
```

### macOS/Linux
```bash
# 使用 curl (推荐)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip
pip install uv

# 或使用 pipx
pipx install uv

# macOS 还可以使用 Homebrew
brew install uv
```

### 验证安装
```bash
uv --version
# 输出: uv 0.x.x
```

## 使用 UV 管理项目

### 1. 初始化项目（新项目）
```bash
# 创建新项目
mkdir my-project && cd my-project

# 初始化 UV 项目
uv init

# 这会创建:
# - pyproject.toml (项目配置)
# - .python-version (Python 版本)
# - README.md
```

### 2. 配置 Python 版本
```bash
# 查看可用的 Python 版本
uv python list

# 安装特定版本的 Python
uv python install 3.11

# 设置项目 Python 版本
uv python pin 3.11
```

### 3. 创建虚拟环境
```bash
# 创建虚拟环境（使用项目指定的 Python 版本）
uv venv

# 指定 Python 版本创建
uv venv --python 3.11

# 创建到自定义目录
uv venv .venv
```

### 4. 激活虚拟环境

#### Windows (PowerShell)
```powershell
.\.venv\Scripts\Activate.ps1
```

#### Windows (CMD)
```cmd
.venv\Scripts\activate.bat
```

#### macOS/Linux
```bash
source .venv/bin/activate
```

### 5. 安装依赖

#### 从 pyproject.toml 安装
```bash
# 安装项目依赖
uv pip install -r pyproject.toml

# 或使用 sync（推荐）
uv pip sync pyproject.toml
```

#### 从 requirements.txt 安装
```bash
# 安装依赖
uv pip install -r requirements.txt

# 使用 sync 确保环境干净
uv pip sync requirements.txt
```

#### 安装单个包
```bash
# 安装包
uv pip install requests

# 安装特定版本
uv pip install requests==2.31.0

# 安装开发依赖
uv pip install -e ".[dev]"
```

### 6. 管理依赖

#### 添加依赖
```bash
# 添加运行时依赖
uv add requests

# 添加开发依赖
uv add --dev pytest black

# 添加可选依赖
uv add --optional-dependency test pytest
```

#### 更新依赖
```bash
# 更新所有依赖
uv pip compile --upgrade pyproject.toml

# 更新特定包
uv pip install --upgrade requests
```

#### 生成锁文件
```bash
# 生成 uv.lock
uv pip compile pyproject.toml -o uv.lock

# 从锁文件安装（确保一致性）
uv pip sync uv.lock
```

## 从 pip 迁移到 UV

### 1. 现有项目迁移步骤

#### 步骤 1：安装 UV
```bash
pip install uv
```

#### 步骤 2：创建 pyproject.toml
如果项目只有 requirements.txt，创建 pyproject.toml：

```toml
[project]
name = "hajimi-king"
version = "0.0.1"
description = "Automated API Key Discovery System"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    # 从 requirements.txt 复制依赖
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=23.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

#### 步骤 3：转换依赖
```bash
# 如果有 requirements.txt
uv pip compile requirements.txt -o uv.lock

# 创建新的虚拟环境
uv venv --python 3.11

# 激活环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows

# 从锁文件安装
uv pip sync uv.lock
```

### 2. Hajimi King 项目迁移示例

```bash
# 1. 克隆项目
git clone https://github.com/james-6-23/key_scanner.git
cd key_scanner

# 2. 安装 UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. 设置 Python 版本
uv python install 3.11
uv python pin 3.11

# 4. 创建虚拟环境
uv venv

# 5. 激活环境
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 6. 安装依赖
uv pip install -r pyproject.toml

# 7. 复制环境配置
cp env.example .env
cp queries.example data/queries.txt

# 8. 运行项目
python app/api_key_scanner.py
```

## 常见问题解决

### 1. PowerShell 执行策略问题（Windows）
```powershell
# 错误：无法加载脚本
# 解决方案：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Python 版本不可用
```bash
# 错误：Python 3.11 not found
# 解决方案：
uv python install 3.11
```

### 3. 依赖冲突
```bash
# 使用 UV 的解析器
uv pip compile --resolver=backtracking pyproject.toml

# 查看依赖树
uv pip tree
```

### 4. 缓存问题
```bash
# 清理 UV 缓存
uv cache clean

# 不使用缓存安装
uv pip install --no-cache-dir package-name
```

### 5. 代理设置
```bash
# 设置代理
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# Windows
set HTTP_PROXY=http://proxy.example.com:8080
set HTTPS_PROXY=http://proxy.example.com:8080
```

## 最佳实践

### 1. 项目结构
```
project/
├── .python-version    # Python 版本
├── pyproject.toml     # 项目配置
├── uv.lock           # 锁文件
├── .venv/            # 虚拟环境
├── src/              # 源代码
└── tests/            # 测试
```

### 2. 版本控制
```gitignore
# .gitignore
.venv/
__pycache__/
*.pyc
.env

# 提交这些文件
# pyproject.toml
# uv.lock
# .python-version
```

### 3. CI/CD 集成
```yaml
# GitHub Actions 示例
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Set up Python
        run: |
          uv python install 3.11
          uv venv
          
      - name: Install dependencies
        run: |
          source .venv/bin/activate
          uv pip sync uv.lock
          
      - name: Run tests
        run: |
          source .venv/bin/activate
          pytest
```

### 4. 开发工作流
```bash
# 日常开发流程
cd project
source .venv/bin/activate  # 激活环境
uv pip sync uv.lock        # 确保依赖最新
python app/main.py         # 运行应用

# 添加新依赖
uv add new-package
uv pip compile pyproject.toml -o uv.lock
git add pyproject.toml uv.lock
git commit -m "Add new-package dependency"
```

### 5. 性能优化
```bash
# 使用镜像源（中国用户）
uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package-name

# 并行安装
uv pip install --parallel package1 package2 package3

# 使用预编译轮子
uv pip install --only-binary :all: package-name
```

## UV 命令速查

```bash
# 基础命令
uv --version              # 查看版本
uv --help                # 查看帮助

# Python 管理
uv python list           # 列出可用版本
uv python install 3.11   # 安装 Python
uv python pin 3.11       # 设置项目版本

# 虚拟环境
uv venv                  # 创建虚拟环境
uv venv --python 3.11    # 指定版本创建

# 包管理
uv pip install package   # 安装包
uv pip uninstall package # 卸载包
uv pip list             # 列出已安装包
uv pip show package     # 显示包信息
uv pip tree             # 显示依赖树

# 依赖管理
uv add package          # 添加依赖
uv remove package       # 移除依赖
uv pip compile          # 生成锁文件
uv pip sync             # 同步依赖

# 缓存管理
uv cache clean          # 清理缓存
uv cache dir            # 显示缓存目录
```

## 总结

UV 提供了现代化的 Python 项目管理体验，通过其极速的性能和统一的工具链，大大简化了 Python 开发流程。对于 Hajimi King 这样的项目，使用 UV 可以：

1. **提升开发效率**：依赖安装速度提升 10-100 倍
2. **确保环境一致性**：通过 uv.lock 文件锁定依赖版本
3. **简化环境管理**：一个工具搞定所有环境相关任务
4. **改善团队协作**：统一的工具链减少环境差异

建议所有 Python 开发者尝试使用 UV，特别是在处理大型项目或需要频繁安装依赖的场景下。

---

更新时间：2024-12-07