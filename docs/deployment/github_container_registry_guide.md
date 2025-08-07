# GitHub Container Registry (ghcr.io) 完整指南

## 目录
1. [准备工作](#准备工作)
2. [创建和配置 Personal Access Token](#创建和配置-personal-access-token)
3. [构建 Docker 镜像](#构建-docker-镜像)
4. [登录 ghcr.io](#登录-ghcrio)
5. [标记和推送镜像](#标记和推送镜像)
6. [设置镜像可见性](#设置镜像可见性)
7. [使用镜像](#使用镜像)
8. [自动化构建和推送](#自动化构建和推送)
9. [故障排除](#故障排除)

---

## 准备工作

### 1. 确认 Docker 已安装
```bash
docker --version
# Docker version 24.0.0, build xxx
```

### 2. 确认 GitHub 用户名
```bash
# 你的 GitHub 用户名，例如: yourusername
# 将在后续命令中使用
```

---

## 创建和配置 Personal Access Token

### 1. 创建 Token

1. 访问 GitHub Settings: https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 填写信息：
   - **Note**: `ghcr.io access for hajimi-king`
   - **Expiration**: 选择合适的过期时间
   - **Select scopes**: 
     - ✅ `write:packages` - 上传包到 GitHub Package Registry
     - ✅ `read:packages` - 从 GitHub Package Registry 下载包
     - ✅ `delete:packages` - 删除包（可选）
     - ✅ `repo` - 如果是私有仓库需要此权限

4. 点击 "Generate token"
5. **立即复制保存 Token**（只显示一次）

### 2. 保存 Token 为环境变量

```bash
# Linux/Mac
export CR_PAT=ghp_xxxxxxxxxxxxxxxxxxxx

# Windows PowerShell
$env:CR_PAT="ghp_xxxxxxxxxxxxxxxxxxxx"

# 或保存到文件（更安全）
echo "ghp_xxxxxxxxxxxxxxxxxxxx" > ~/.github-token
```

---

## 构建 Docker 镜像

### 1. 基础构建

```bash
# 在项目根目录执行
docker build -t hajimi-king:latest .

# 查看构建的镜像
docker images | grep hajimi-king
```

### 2. 多阶段构建（推荐）

```bash
# 使用 BuildKit 加速构建
DOCKER_BUILDKIT=1 docker build \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  -t hajimi-king:latest \
  .
```

### 3. 带版本标签构建

```bash
# 使用 Git 标签作为版本
VERSION=$(git describe --tags --always)

# 构建带版本的镜像
docker build \
  -t hajimi-king:latest \
  -t hajimi-king:${VERSION} \
  .
```

---

## 登录 ghcr.io

### 方法 1：使用环境变量（推荐）

```bash
echo $CR_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

### 方法 2：使用保存的 Token 文件

```bash
cat ~/.github-token | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

### 方法 3：交互式登录

```bash
docker login ghcr.io
# Username: YOUR_GITHUB_USERNAME
# Password: ghp_xxxxxxxxxxxxxxxxxxxx
```

### 验证登录成功

```bash
# 应该看到 "Login Succeeded"
```

---

## 标记和推送镜像

### 1. 标记镜像

```bash
# 基础标记
docker tag hajimi-king:latest ghcr.io/YOUR_GITHUB_USERNAME/hajimi-king:latest

# 带版本标记
docker tag hajimi-king:latest ghcr.io/YOUR_GITHUB_USERNAME/hajimi-king:v1.0.0

# 多个标记
docker tag hajimi-king:latest ghcr.io/YOUR_GITHUB_USERNAME/hajimi-king:latest
docker tag hajimi-king:latest ghcr.io/YOUR_GITHUB_USERNAME/hajimi-king:$(date +%Y%m%d)
docker tag hajimi-king:latest ghcr.io/YOUR_GITHUB_USERNAME/hajimi-king:$(git rev-parse --short HEAD)
```

### 2. 推送镜像

```bash
# 推送最新版本
docker push ghcr.io/YOUR_GITHUB_USERNAME/hajimi-king:latest

# 推送特定版本
docker push ghcr.io/YOUR_GITHUB_USERNAME/hajimi-king:v1.0.0

# 推送所有标签
docker push ghcr.io/YOUR_GITHUB_USERNAME/hajimi-king --all-tags
```

### 3. 完整示例脚本

```bash
#!/bin/bash
# build-and-push.sh

# 配置
GITHUB_USERNAME="yourusername"
IMAGE_NAME="hajimi-king"
VERSION=$(git describe --tags --always)

# 构建镜像
echo "Building image..."
docker build -t ${IMAGE_NAME}:latest .

# 标记镜像
echo "Tagging images..."
docker tag ${IMAGE_NAME}:latest ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:latest
docker tag ${IMAGE_NAME}:latest ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:${VERSION}

# 登录
echo "Logging in to ghcr.io..."
echo $CR_PAT | docker login ghcr.io -u ${GITHUB_USERNAME} --password-stdin

# 推送
echo "Pushing images..."
docker push ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:latest
docker push ghcr.io/${GITHUB_USERNAME}/${IMAGE_NAME}:${VERSION}

echo "Done! Images pushed successfully."
```

### 4. 使用自动化脚本

我们提供了便捷的自动化脚本来简化推送过程：

#### Linux/macOS 用户

```bash
# 设置环境变量
export CR_PAT="ghp_xxxxxxxxxxxxxxxxxxxx"

# 运行脚本
./scripts/push-to-ghcr.sh yourusername

# 带清理选项（推送后删除本地镜像）
./scripts/push-to-ghcr.sh yourusername --cleanup
```

#### Windows 用户

```powershell
# 设置环境变量
$env:CR_PAT = "ghp_xxxxxxxxxxxxxxxxxxxx"

# 运行脚本
.\scripts\push-to-ghcr.ps1 -GitHubUsername "yourusername"

# 带清理选项（推送后删除本地镜像）
.\scripts\push-to-ghcr.ps1 -GitHubUsername "yourusername" -CleanupLocal
```

#### 脚本功能

两个脚本都提供以下功能：
- 自动构建 Docker 镜像
- 使用 git 标签或时间戳作为版本号
- 同时推送 `latest` 和版本标签
- 可选的本地镜像清理
- 彩色输出显示进度
- 错误处理和验证

---

## 设置镜像可见性

### 1. 通过 GitHub UI 设置

1. 访问: `https://github.com/YOUR_USERNAME?tab=packages`
2. 点击你的包名（hajimi-king）
3. 点击 "Package settings"
4. 在 "Danger Zone" 部分：
   - **Change visibility**: 选择 Public 或 Private
   - **Manage Actions access**: 配置哪些仓库可以使用此镜像

### 2. 链接到仓库

在 Package settings 页面：
1. 找到 "Connect repository"
2. 选择 `YOUR_USERNAME/hajimi-king` 仓库
3. 这样可以在仓库页面看到包信息

### 3. 设置权限

```yaml
# 在仓库的 .github/workflows/docker-publish.yml 中
permissions:
  contents: read
  packages: write
```

---

## 使用镜像

### 1. 公开镜像

```bash
# 无需登录即可拉取
docker pull ghcr.io/YOUR_GITHUB_USERNAME/hajimi-king:latest
```

### 2. 私有镜像

```bash
# 需要先登录
echo $CR_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# 然后拉取
docker pull ghcr.io/YOUR_GITHUB_USERNAME/hajimi-king:latest
```

### 3. 在 docker-compose.yml 中使用

```yaml
services:
  hajimi-king:
    image: ghcr.io/YOUR_GITHUB_USERNAME/hajimi-king:latest
    # ... 其他配置
```

---

## 自动化构建和推送

### GitHub Actions 工作流

创建 `.github/workflows/docker-publish.yml`:

```yaml
name: Docker Build and Push

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to the Container registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## 故障排除

### 1. 认证失败

**错误**: `unauthorized: authentication required`

**解决方案**:
```bash
# 重新登录
docker logout ghcr.io
echo $CR_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

### 2. 权限不足

**错误**: `denied: permission_denied: write_package`

**解决方案**:
- 确认 Token 有 `write:packages` 权限
- 确认用户名正确
- 确认镜像路径格式正确：`ghcr.io/username/image:tag`

### 3. 镜像名称问题

**错误**: `invalid reference format`

**解决方案**:
```bash
# 镜像名必须小写
docker tag hajimi-king:latest ghcr.io/your-username/hajimi-king:latest
# 不是 YOUR-USERNAME（大写）
```

### 4. 推送超时

**解决方案**:
```bash
# 分层推送
docker push ghcr.io/YOUR_GITHUB_USERNAME/hajimi-king:latest --disable-content-trust
```

### 5. 查看推送的镜像

访问以下地址查看你的包：
- 个人包页面: `https://github.com/YOUR_USERNAME?tab=packages`
- 特定包页面: `https://github.com/users/YOUR_USERNAME/packages/container/package/hajimi-king`

---

## 最佳实践

### 1. 使用多标签策略

```bash
# 同时维护多个标签
docker tag hajimi-king:latest ghcr.io/username/hajimi-king:latest
docker tag hajimi-king:latest ghcr.io/username/hajimi-king:stable
docker tag hajimi-king:latest ghcr.io/username/hajimi-king:v1.0.0
docker tag hajimi-king:latest ghcr.io/username/hajimi-king:$(date +%Y%m%d)
```

### 2. 清理旧镜像

```bash
# 本地清理
docker image prune -a

# 远程清理（通过 GitHub UI 或 API）
```

### 3. 使用 .dockerignore

```bash
# .dockerignore
.git
.github
*.md
.env
data/
logs/
*.pyc
__pycache__
```

### 4. 安全建议

- 不要在 Dockerfile 中硬编码敏感信息
- 使用 GitHub Secrets 存储 Token
- 定期轮换 Personal Access Token
- 使用最小权限原则

---

## 快速命令参考

```bash
# 一键构建和推送脚本
#!/bin/bash
GITHUB_USER="yourusername"
IMAGE="hajimi-king"
VERSION="latest"

# 构建
docker build -t ${IMAGE}:${VERSION} .

# 标记
docker tag ${IMAGE}:${VERSION} ghcr.io/${GITHUB_USER}/${IMAGE}:${VERSION}

# 登录
echo $CR_PAT | docker login ghcr.io -u ${GITHUB_USER} --password-stdin

# 推送
docker push ghcr.io/${GITHUB_USER}/${IMAGE}:${VERSION}
```

这样，你的 Docker 镜像就成功推送到 GitHub Container Registry 了！