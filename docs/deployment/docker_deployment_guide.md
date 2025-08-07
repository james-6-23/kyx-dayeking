# Hajimi King Docker 部署指南

## 目录
1. [快速开始](#快速开始)
2. [Docker 镜像构建](#docker-镜像构建)
3. [环境变量配置](#环境变量配置)
4. [数据卷映射](#数据卷映射)
5. [性能优化](#性能优化)
6. [零停机部署](#零停机部署)
7. [监控和日志](#监控和日志)
8. [故障排除](#故障排除)

## 快速开始

### 1. 开发环境部署
```bash
# 构建并启动
docker-compose up -d --build

# 查看日志
docker-compose logs -f hajimi-king

# 停止服务
docker-compose down
```

### 2. 生产环境部署
```bash
# 使用部署脚本
chmod +x deploy.sh
./deploy.sh --version v1.0.0 --push

# 或手动部署
docker-compose -f docker-compose.prod.yml up -d
```

## Docker 镜像构建

### 多阶段构建优化
我们的 Dockerfile 使用多阶段构建来优化镜像大小：

1. **构建阶段**：安装构建依赖和 Python 包
2. **运行阶段**：只包含运行时必需的文件

### 构建命令
```bash
# 基础构建
docker build -t hajimi-king:latest .

# 带缓存的构建（更快）
docker build --cache-from hajimi-king:latest -t hajimi-king:latest .

# 指定版本标签
docker build -t hajimi-king:v1.0.0 -t hajimi-king:latest .
```

### 镜像大小优化技巧
- 使用 `python:3.11-slim` 基础镜像
- 多阶段构建分离构建和运行环境
- 清理 apt 缓存：`rm -rf /var/lib/apt/lists/*`
- 使用 `.dockerignore` 排除不必要的文件

## 环境变量配置

### 必需的环境变量
```bash
# GitHub API 配置
GITHUB_TOKENS=token1,token2,token3

# 数据路径
DATA_PATH=/app/data

# 搜索配置
QUERIES_FILE=queries.txt
DATE_RANGE_DAYS=730
```

### 性能相关配置
```bash
# 并行验证器配置
HAJIMI_MAX_WORKERS=10      # 并行工作线程数
HAJIMI_BATCH_SIZE=10       # 批处理大小
HAJIMI_BATCH_INTERVAL=60   # 批处理间隔（秒）

# 代理配置
PROXY=http://proxy1:8080,http://proxy2:8080
```

### 外部同步配置
```bash
# Gemini Balancer
GEMINI_BALANCER_SYNC_ENABLED=true
GEMINI_BALANCER_URL=http://balancer:8080
GEMINI_BALANCER_AUTH=your_auth_token

# GPT Load
GPT_LOAD_SYNC_ENABLED=true
GPT_LOAD_URL=http://gpt-load:8080
GPT_LOAD_AUTH=your_auth_token
GPT_LOAD_GROUP_NAME=group1,group2
```

## 数据卷映射

### 目录结构
```
/app/data/
├── keys/           # API 密钥存储
├── logs/           # 应用日志
├── cache/          # 缓存数据
├── checkpoint.json # 检查点文件
├── queries.txt     # 搜索查询配置
└── scanned_shas.txt # 已扫描记录
```

### Docker Compose 卷配置
```yaml
volumes:
  # 持久化数据
  - ./data:/app/data:rw
  
  # 只读配置
  - ./queries.txt:/app/data/queries.txt:ro
  
  # 日志分离
  - ./logs:/app/logs:rw
  
  # 缓存使用命名卷（更好的性能）
  - queries-cache:/app/data/cache
```

### 权限设置
```bash
# 创建目录并设置权限
mkdir -p data/{keys,logs,cache}
chown -R 1000:1000 data/

# Docker 内使用非 root 用户（UID 1000）
```

## 性能优化

### 1. 资源限制
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### 2. 并行处理优化
```bash
# 根据 CPU 核心数调整
HAJIMI_MAX_WORKERS=20  # 生产环境可以更高

# 批处理优化
HAJIMI_BATCH_SIZE=20   # 增加批处理大小
HAJIMI_BATCH_INTERVAL=30  # 减少等待时间
```

### 3. 网络优化
```yaml
# 使用自定义网络
networks:
  hajimi-network:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: br-hajimi
```

### 4. 存储优化
```bash
# 使用本地 SSD 存储
volumes:
  hajimi-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /ssd/hajimi/data
```

## 零停机部署

### 蓝绿部署策略
1. **Blue 容器**：当前运行的版本
2. **Green 容器**：新部署的版本
3. **切换流程**：
   - 启动 Green 容器
   - 健康检查通过
   - 切换流量
   - 停止 Blue 容器

### 使用部署脚本
```bash
# 基本部署
./deploy.sh

# 指定版本
./deploy.sh --version v1.0.1

# 跳过备份
./deploy.sh --no-backup

# 推送到镜像仓库
./deploy.sh --push

# 禁用自动回滚
./deploy.sh --no-rollback
```

### 手动蓝绿部署
```bash
# 1. 启动新版本（Green）
VERSION=v1.0.1 INSTANCE=green docker-compose -f docker-compose.prod.yml up -d

# 2. 检查健康状态
docker exec hajimi-king-green curl http://localhost:9090/health

# 3. 切换流量（如果使用负载均衡）
# 更新负载均衡器配置指向 Green

# 4. 停止旧版本（Blue）
docker stop hajimi-king-blue
docker rm hajimi-king-blue
```

## 监控和日志

### 日志配置
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
    labels: "service=hajimi-king"
```

### 查看日志
```bash
# 实时日志
docker logs -f hajimi-king

# 最近 100 行
docker logs --tail 100 hajimi-king

# 带时间戳
docker logs -t hajimi-king
```

### 健康检查
```bash
# 内置健康检查
curl http://localhost:9090/health

# Docker 健康状态
docker inspect hajimi-king | jq '.[0].State.Health'
```

### 性能监控
```bash
# CPU 和内存使用
docker stats hajimi-king

# 详细资源使用
docker exec hajimi-king ps aux
docker exec hajimi-king free -h
```

## 故障排除

### 常见问题

#### 1. 容器无法启动
```bash
# 检查日志
docker logs hajimi-king

# 检查配置
docker-compose config

# 验证环境变量
docker exec hajimi-king env
```

#### 2. 权限问题
```bash
# 修复数据目录权限
docker exec hajimi-king chown -R appuser:appuser /app/data

# 或在宿主机上
sudo chown -R 1000:1000 ./data
```

#### 3. 网络连接问题
```bash
# 测试网络连接
docker exec hajimi-king ping -c 3 google.com
docker exec hajimi-king curl -I https://api.github.com

# 检查代理配置
docker exec hajimi-king env | grep PROXY
```

#### 4. 内存不足
```bash
# 增加内存限制
docker update --memory 4g hajimi-king

# 或修改 docker-compose.yml
```

### 调试模式
```bash
# 进入容器调试
docker exec -it hajimi-king /bin/bash

# 以 root 用户进入
docker exec -it -u root hajimi-king /bin/bash

# 运行调试命令
docker run --rm -it --entrypoint /bin/bash hajimi-king:latest
```

### 备份和恢复
```bash
# 备份数据
docker run --rm \
  -v hajimi-data:/data:ro \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/hajimi-backup-$(date +%Y%m%d).tar.gz -C /data .

# 恢复数据
docker run --rm \
  -v hajimi-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/hajimi-backup-20250807.tar.gz -C /data
```

## 最佳实践

1. **定期更新基础镜像**
   ```bash
   docker pull python:3.11-slim
   docker build --no-cache -t hajimi-king:latest .
   ```

2. **使用健康检查**
   - 确保健康检查端点正常工作
   - 设置合理的检查间隔和超时

3. **日志轮转**
   - 配置适当的日志大小限制
   - 定期归档旧日志

4. **安全加固**
   - 使用非 root 用户运行
   - 限制容器权限
   - 定期更新依赖

5. **监控告警**
   - 设置资源使用告警
   - 监控 API 配额使用
   - 跟踪密钥发现率

## 总结

通过以上配置，你可以实现：
- ✅ 高效的 Docker 镜像（多阶段构建）
- ✅ 灵活的环境配置
- ✅ 持久化数据存储
- ✅ 零停机部署（蓝绿部署）
- ✅ 完善的监控和日志
- ✅ 生产级别的安全和性能