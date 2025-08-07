# Docker WARP 代理镜像问题解决方案

## 问题描述

在执行 `docker compose --profile proxy up -d` 时遇到错误：
```
pull access denied for cmj2002/warp, repository does not exist or may require 'docker login'
```

原因：`cmj2002/warp` 镜像已经不存在或变为私有仓库。

## 解决方案

### 方案 1：使用 caomingjun/warp 镜像（推荐）

这是一个维护良好的 Cloudflare WARP 代理镜像。

```yaml
warp-proxy:
  image: caomingjun/warp:latest
  container_name: warp-proxy
  restart: unless-stopped
  ports:
    - "127.0.0.1:1080:1080"
  environment:
    - WARP_SLEEP=2
  cap_add:
    - NET_ADMIN
  sysctls:
    - net.ipv6.conf.all.disable_ipv6=0
    - net.ipv4.conf.all.src_valid_mark=1
  networks:
    - hajimi-network
  profiles:
    - proxy
```

**使用方法：**
```bash
# 使用修复后的配置文件
docker compose --profile proxy up -d

# 或者直接使用新的配置文件
docker compose -f docker-compose-fixed.yml --profile proxy up -d
```

### 方案 2：使用 e7h4n/cloudflare-warp 镜像

另一个可用的 WARP 代理镜像选择。

```yaml
warp-proxy:
  image: e7h4n/cloudflare-warp:latest
  container_name: warp-proxy
  restart: unless-stopped
  ports:
    - "127.0.0.1:1080:1080"
  cap_add:
    - NET_ADMIN
  networks:
    - hajimi-network
  profiles:
    - proxy
```

### 方案 3：不使用代理

如果不需要代理功能，可以直接运行主服务：

```bash
# 不带 --profile proxy 参数
docker compose up -d
```

### 方案 4：使用通用 SOCKS5 代理

如果需要代理但不一定要用 WARP，可以使用通用的 SOCKS5 代理：

```yaml
socks5-proxy:
  image: serjs/go-socks5-proxy:latest
  container_name: socks5-proxy
  restart: unless-stopped
  ports:
    - "127.0.0.1:1080:1080"
  environment:
    - PROXY_USER=
    - PROXY_PASSWORD=
  networks:
    - hajimi-network
  profiles:
    - proxy
```

## 快速修复步骤

1. **备份原始配置：**
   ```bash
   cp docker-compose.yml docker-compose.yml.backup
   ```

2. **使用修复后的配置：**
   ```bash
   # 方法1：使用新的配置文件
   docker compose -f docker-compose-fixed.yml --profile proxy up -d
   
   # 方法2：更新原始文件
   cp docker-compose-fixed.yml docker-compose.yml
   docker compose --profile proxy up -d
   ```

3. **验证服务状态：**
   ```bash
   docker compose ps
   docker logs warp-proxy
   ```

## 配置代理到应用

在 `.env` 文件中配置代理：

```env
# 如果使用 WARP 代理
PROXY=socks5://warp-proxy:1080

# 如果使用主机网络
PROXY=socks5://127.0.0.1:1080
```

## 故障排除

### 1. 镜像拉取失败

如果新镜像也无法拉取，可能是网络问题：

```bash
# 使用镜像加速器
docker pull registry.cn-hangzhou.aliyuncs.com/caomingjun/warp:latest
docker tag registry.cn-hangzhou.aliyuncs.com/caomingjun/warp:latest caomingjun/warp:latest
```

### 2. 代理连接失败

检查代理服务日志：
```bash
docker logs warp-proxy
```

### 3. 权限问题

某些 WARP 镜像需要特殊权限：
```yaml
cap_add:
  - NET_ADMIN
sysctls:
  - net.ipv6.conf.all.disable_ipv6=0
  - net.ipv4.conf.all.src_valid_mark=1
```

## 推荐配置

基于稳定性和维护情况，推荐使用 `caomingjun/warp:latest` 镜像，它：
- 定期更新
- 有良好的文档
- 支持多种配置选项
- 社区活跃

## 参考链接

- [caomingjun/warp Docker Hub](https://hub.docker.com/r/caomingjun/warp)
- [Cloudflare WARP 官方文档](https://developers.cloudflare.com/warp-client/)
- [Docker Compose Profiles 文档](https://docs.docker.com/compose/profiles/)