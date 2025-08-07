# Hajimi King 快速参考指南

## 🚀 快速开始

### 1. 环境设置
```bash
# 复制环境变量文件
cp env.example .env

# 编辑 .env 文件，设置你的 Gemini API 密钥
# GEMINI_API_KEY=your_actual_api_key_here

# 复制查询配置文件
cp queries.example data/queries.txt

# 编辑查询文件，自定义搜索模式
# nano data/queries.txt
```

### 2. 运行程序

#### 本地运行
```bash
# 使用 Python 直接运行（推荐使用并行版本）
python app/api_key_scanner.py

# 或使用串行版本
python app/hajimi_king.py
```

#### Docker 运行
```bash
# 开发环境（不含代理）
docker-compose up -d

# 开发环境（包含代理）
docker-compose --profile proxy up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📦 Docker 镜像管理

### 构建镜像
```bash
# 基础构建
docker build -t hajimi-king:latest .

# 带版本标签
docker build -t hajimi-king:v1.0.0 .
```

### 推送到 GitHub Container Registry

#### 准备工作
1. 创建 Personal Access Token：https://github.com/settings/tokens
2. 选择权限：`write:packages`, `read:packages`, `delete:packages`

#### Linux/macOS
```bash
# 设置 Token
export CR_PAT="ghp_xxxxxxxxxxxxxxxxxxxx"

# 使用脚本推送
./scripts/push-to-ghcr.sh yourusername

# 带清理选项
./scripts/push-to-ghcr.sh yourusername --cleanup
```

#### Windows PowerShell
```powershell
# 设置 Token
$env:CR_PAT = "ghp_xxxxxxxxxxxxxxxxxxxx"

# 使用脚本推送
.\scripts\push-to-ghcr.ps1 -GitHubUsername "yourusername"

# 带清理选项
.\scripts\push-to-ghcr.ps1 -GitHubUsername "yourusername" -CleanupLocal
```

#### 手动推送
```bash
# 登录
echo $CR_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# 标记
docker tag hajimi-king:latest ghcr.io/YOUR_USERNAME/hajimi-king:latest

# 推送
docker push ghcr.io/YOUR_USERNAME/hajimi-king:latest
```

## 🔧 常用 Docker Compose 命令

```bash
# 启动服务
docker-compose up -d                    # 仅主服务
docker-compose --profile proxy up -d    # 主服务 + 代理

# 查看状态
docker-compose ps                       # 查看运行状态
docker-compose logs -f                  # 实时查看日志
docker-compose logs -f hajimi-king      # 查看特定服务日志

# 管理服务
docker-compose restart hajimi-king      # 重启服务
docker-compose stop                     # 停止服务
docker-compose down                     # 停止并删除容器
docker-compose down -v                  # 停止并删除容器和卷

# 更新服务
docker-compose pull                     # 拉取最新镜像
docker-compose up -d --force-recreate   # 强制重建容器
```

## 🚀 生产部署

### 使用部署脚本
```bash
# 首次部署
./first_deploy.sh

# 后续部署（零停机）
./deploy.sh
```

### 手动部署
```bash
# 使用生产配置
docker-compose -f docker-compose.prod.yml up -d

# 查看生产日志
docker-compose -f docker-compose.prod.yml logs -f
```

## 📁 项目结构

```
hajimi-king/
├── app/                    # 主程序
│   ├── api_key_scanner.py  # 并行扫描器（推荐）
│   └── hajimi_king.py      # 串行扫描器
├── common/                 # 公共模块
├── utils/                  # 工具模块
├── scripts/                # 脚本文件
├── data/                   # 运行时数据（自动创建）
│   └── queries.txt         # 实际查询文件（从 queries.example 复制）
├── docs/                   # 文档
├── queries.example         # 查询示例文件
└── env.example            # 环境变量示例
```

## 🔍 故障排除

### 模块导入错误
```bash
# 确保在项目根目录运行
cd /path/to/hajimi-king
python app/api_key_scanner.py
```

### Docker 权限问题
```bash
# Linux: 添加用户到 docker 组
sudo usermod -aG docker $USER
# 重新登录生效
```

### 代理配置问题
```bash
# 检查代理状态
docker-compose --profile proxy ps

# 查看代理日志
docker-compose logs -f warp-proxy
```

### GitHub Container Registry 认证失败
```bash
# 重新登录
docker logout ghcr.io
echo $CR_PAT | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

## 📊 性能优化

### 并行处理配置
```bash
# 在 .env 中设置
MAX_WORKERS=10          # 并行工作线程数
BATCH_SIZE=50          # 批处理大小
REQUEST_TIMEOUT=30     # 请求超时时间
```

### 资源限制（生产环境）
```yaml
# docker-compose.prod.yml 中已配置
resources:
  limits:
    cpus: '2'
    memory: 4G
```

## 📝 日志和监控

### 查看日志文件
```bash
# 应用日志
tail -f data/logs/hajimi_king_*.log

# 查看最新日志
ls -la data/logs/ | tail -n 5
```

### 检查扫描进度
```bash
# 查看检查点
cat data/checkpoint.json | jq .

# 查看已扫描的提交
wc -l data/scanned_shas.txt
```

## 🔗 有用的链接

- [完整文档](README.md)
- [Docker 部署指南](docker_deployment_guide.md)
- [GitHub Container Registry 指南](github_container_registry_guide.md)
- [代理配置指南](proxy_configuration_guide.md)
- [查询优化指南](queries_optimization_guide.md)

## 💡 提示

1. **使用并行版本**：`api_key_scanner.py` 比 `hajimi_king.py` 快很多
2. **定期清理日志**：`data/logs/` 目录会持续增长
3. **使用代理**：在网络受限环境下使用 `--profile proxy`
4. **版本管理**：使用 Git 标签管理版本
5. **安全第一**：永远不要提交 `.env` 文件
6. **自定义查询**：编辑 `data/queries.txt` 而不是 `queries.example`

---

更新时间：2024-12-07