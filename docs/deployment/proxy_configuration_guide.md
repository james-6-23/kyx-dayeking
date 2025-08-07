# Hajimi King 代理配置指南

## 使用 Docker Compose 中的 warp-proxy

### 1. 启动代理服务

```bash
# 启动包含代理的服务
docker-compose --profile proxy up -d

# 或者只启动代理服务
docker-compose up -d warp-proxy
```

### 2. 配置 .env 文件

当使用 Docker Compose 中的 `warp-proxy` 服务时，你需要在 `.env` 文件中配置代理：

#### 方案 A：容器间通信（推荐）

如果 `hajimi-king` 和 `warp-proxy` 在同一个 Docker 网络中：

```bash
# .env 文件配置
PROXY=http://warp-proxy:1080
```

#### 方案 B：通过宿主机访问

如果需要通过宿主机访问代理：

```bash
# Windows/Mac 上的 .env 配置
PROXY=http://host.docker.internal:1080

# Linux 上的 .env 配置
PROXY=http://172.17.0.1:1080
```

#### 方案 C：本地开发（非 Docker 环境）

如果你在本地运行 Python 程序（不使用 Docker）：

```bash
# .env 文件配置
PROXY=http://127.0.0.1:1080
```

### 3. 多代理配置

你可以配置多个代理进行轮换：

```bash
# .env 文件配置
PROXY=http://warp-proxy:1080,http://proxy2:8080,http://proxy3:3128
```

### 4. 完整的 .env 示例

```bash
# GitHub API 配置
GITHUB_TOKENS=ghp_token1,ghp_token2,ghp_token3

# 代理配置（使用 Docker 内部网络）
PROXY=http://warp-proxy:1080

# 其他配置
DATA_PATH=./data
QUERIES_FILE=queries.txt
DATE_RANGE_DAYS=730
HAJIMI_CHECK_MODEL=gemini-2.0-flash-exp
```

### 5. 验证代理连接

#### 在容器内测试：

```bash
# 进入 hajimi-king 容器
docker exec -it hajimi-king /bin/bash

# 测试代理连接
curl -x http://warp-proxy:1080 https://api.github.com
```

#### 查看代理日志：

```bash
# 查看 warp-proxy 日志
docker-compose logs -f warp-proxy
```

### 6. 故障排除

#### 问题：连接被拒绝

```bash
# 检查代理服务是否运行
docker-compose ps warp-proxy

# 检查网络连接
docker network inspect kyx-dayeking_hajimi-network
```

#### 问题：代理不工作

1. 确保使用了正确的 profile：
   ```bash
   docker-compose --profile proxy up -d
   ```

2. 检查防火墙设置：
   - Windows：确保 Docker Desktop 允许通过防火墙
   - Linux：检查 iptables 规则

3. 验证端口映射：
   ```bash
   docker port warp-proxy
   ```

### 7. 高级配置

#### 使用认证的代理：

```bash
# .env 文件配置
PROXY=http://username:password@warp-proxy:1080
```

#### 配置代理超时：

```bash
# .env 文件配置
PROXY=http://warp-proxy:1080
REQUEST_TIMEOUT=60
MAX_RETRIES=5
```

### 8. Docker Compose 配置说明

```yaml
warp-proxy:
    image: cmj2002/warp:latest
    container_name: warp-proxy
    restart: unless-stopped
    ports:
      - "127.0.0.1:1080:1080"  # 只绑定到本地，提高安全性
    networks:
      - hajimi-network          # 与主服务在同一网络
    profiles:
      - proxy                   # 使用 profile 控制启动
    deploy:
      resources:
        limits:
          cpus: '0.5'          # 限制 CPU 使用
          memory: 256M         # 限制内存使用
```

### 9. 最佳实践

1. **使用容器名称**：在 Docker 环境中，使用容器名称（如 `warp-proxy`）而不是 IP 地址
2. **网络隔离**：确保代理和主服务在同一个 Docker 网络中
3. **资源限制**：为代理服务设置合理的资源限制
4. **日志监控**：定期检查代理日志，确保正常运行
5. **备用代理**：配置多个代理地址以提高可靠性

### 10. 示例命令

```bash
# 启动所有服务（包括代理）
docker-compose --profile proxy up -d

# 只启动主服务（不含代理）
docker-compose up -d hajimi-king

# 查看所有服务状态
docker-compose ps

# 停止所有服务
docker-compose down