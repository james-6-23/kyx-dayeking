# Docker 部署故障排除指南

## 常见问题和解决方案

### 1. 网络地址池冲突

**错误信息**：
```
failed to create network key_scanner_hajimi-network: Error response from daemon: invalid pool request: Pool overlaps with other one on this address space
```

**原因**：
Docker 网络的 IP 地址范围与现有网络冲突。

**解决方案**：

#### 方案 1：修改子网配置
编辑 `docker-compose.yml`，更改网络子网：
```yaml
networks:
  hajimi-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16  # 使用不同的子网
```

常用的备选子网：
- `172.28.0.0/16`
- `172.29.0.0/16`
- `172.30.0.0/16`
- `10.10.0.0/16`
- `10.20.0.0/16`

#### 方案 2：让 Docker 自动分配
删除 IPAM 配置，让 Docker 自动选择子网：
```yaml
networks:
  hajimi-network:
    driver: bridge
    # 删除 ipam 部分
```

#### 方案 3：清理现有网络
```bash
# 查看所有网络
docker network ls

# 删除未使用的网络
docker network prune

# 强制删除特定网络
docker network rm key_scanner_hajimi-network
```

### 2. 版本警告

**警告信息**：
```
WARN[0000] /root/key_scanner/docker-compose.yml: the attribute `version` is obsolete
```

**解决方案**：
这是 Docker Compose V2 的提示，`version` 字段已经过时。可以安全地从 `docker-compose.yml` 中删除第一行的 `version: '3.8'`。

### 3. 镜像拉取失败

**错误信息**：
```
pull access denied for hajimi-king, repository does not exist
```

**解决方案**：
这是正常的，因为本地还没有构建镜像。Docker Compose 会自动构建。

### 4. 权限问题

**错误信息**：
```
PermissionError: [Errno 13] Permission denied: '/app/data'
```

**解决方案**：
```bash
# 创建数据目录并设置权限
mkdir -p data logs
chmod -R 755 data logs

# 或者使用 sudo
sudo chown -R 1000:1000 data logs
```

### 5. 环境变量未加载

**问题**：程序无法读取 GitHub tokens

**解决方案**：
1. 确保 `.env` 文件存在：
   ```bash
   ls -la .env
   ```

2. 检查 `.env` 文件格式：
   ```bash
   # 正确格式（无空格）
   GITHUB_TOKENS=ghp_token1,ghp_token2
   
   # 错误格式
   GITHUB_TOKENS = ghp_token1, ghp_token2
   ```

3. 验证环境变量：
   ```bash
   docker-compose run --rm hajimi-king env | grep GITHUB
   ```

### 6. 容器立即退出

**问题**：容器启动后立即停止

**诊断步骤**：
```bash
# 查看容器日志
docker-compose logs hajimi-king

# 查看最后 50 行日志
docker-compose logs --tail=50 hajimi-king

# 实时查看日志
docker-compose logs -f hajimi-king
```

**常见原因**：
1. 缺少必需的环境变量（如 GITHUB_TOKENS）
2. 配置文件错误
3. Python 导入错误

### 7. 健康检查失败

**问题**：容器显示为 unhealthy

**解决方案**：
1. 检查进程是否运行：
   ```bash
   docker exec hajimi-king ps aux | grep python
   ```

2. 手动测试健康检查：
   ```bash
   docker exec hajimi-king pgrep -f "api_key_scanner"
   ```

3. 如果需要，可以临时禁用健康检查：
   ```yaml
   # 注释掉 healthcheck 部分
   # healthcheck:
   #   test: ["CMD", "pgrep", "-f", "api_key_scanner"]
   ```

### 8. 代理连接问题

**问题**：无法连接到 warp-proxy

**解决方案**：
1. 确保使用了正确的 profile：
   ```bash
   docker-compose --profile proxy up -d
   ```

2. 检查代理状态：
   ```bash
   docker-compose ps warp-proxy
   docker-compose logs warp-proxy
   ```

3. 测试代理连接：
   ```bash
   docker exec hajimi-king curl -x http://warp-proxy:1080 https://api.github.com
   ```

## 调试命令速查

```bash
# 重新构建镜像（不使用缓存）
docker-compose build --no-cache

# 查看详细构建日志
docker-compose build --progress=plain

# 进入容器调试
docker-compose run --rm hajimi-king bash

# 查看容器资源使用
docker stats hajimi-king

# 清理所有容器和网络
docker-compose down -v
docker system prune -a

# 验证 docker-compose 配置
docker-compose config

# 查看容器内文件
docker exec hajimi-king ls -la /app/
docker exec hajimi-king ls -la /app/data/
```

## 最佳实践

1. **始终先在本地测试**
   ```bash
   python app/api_key_scanner.py
   ```

2. **使用 .env.docker.example 作为模板**
   ```bash
   cp .env.docker.example .env
   nano .env  # 编辑配置
   ```

3. **逐步启动服务**
   ```bash
   # 先启动主服务
   docker-compose up -d hajimi-king
   
   # 确认运行正常后再启动代理
   docker-compose --profile proxy up -d
   ```

4. **定期清理**
   ```bash
   # 清理未使用的镜像和容器
   docker system prune -a
   
   # 清理日志
   docker-compose logs --tail=0 -f
   ```

---

更新时间：2024-12-07