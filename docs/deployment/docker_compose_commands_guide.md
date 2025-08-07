# Docker Compose 命令详解

## 关于 `docker-compose up -d`

### 默认行为

`docker-compose up -d` **不会**启动所有服务，它只会启动：
1. 没有定义 `profiles` 的服务
2. 明确指定的服务

在你的 `docker-compose.yml` 中：
- `hajimi-king` - ✅ 会启动（没有 profile）
- `warp-proxy` - ❌ 不会启动（有 `profiles: [proxy]`）

### 命令示例和效果

#### 1. 只启动主服务（不含代理）
```bash
docker-compose up -d
# 结果：只启动 hajimi-king
```

#### 2. 启动主服务和代理
```bash
docker-compose --profile proxy up -d
# 结果：启动 hajimi-king 和 warp-proxy
```

#### 3. 只启动特定服务
```bash
# 只启动主服务
docker-compose up -d hajimi-king

# 只启动代理
docker-compose up -d warp-proxy
```

#### 4. 启动所有服务（包括所有 profiles）
```bash
# 方法1：指定所有 profiles
docker-compose --profile proxy --profile monitoring up -d

# 方法2：分别启动
docker-compose up -d
docker-compose --profile proxy up -d
```

### Profile 的作用

Profile 是 Docker Compose 的一个功能，用于：
- 将服务分组
- 控制哪些服务默认启动
- 实现可选服务

你的配置中：
```yaml
warp-proxy:
    profiles:
      - proxy  # 这个服务属于 'proxy' profile
```

这意味着 `warp-proxy` 是可选的，只在需要时启动。

### 常用命令对比

| 命令 | 效果 | 适用场景 |
|------|------|----------|
| `docker-compose up -d` | 启动默认服务 | 日常开发，不需要代理 |
| `docker-compose --profile proxy up -d` | 启动默认服务 + 代理 | 需要代理访问 |
| `docker-compose down` | 停止所有运行的服务 | 清理环境 |
| `docker-compose ps` | 查看运行中的服务 | 检查状态 |

### 实际使用建议

#### 场景1：开发环境（不需要代理）
```bash
# 启动
docker-compose up -d

# 查看状态
docker-compose ps
# 应该只看到 hajimi-king 运行
```

#### 场景2：需要代理的环境
```bash
# 启动（包含代理）
docker-compose --profile proxy up -d

# 查看状态
docker-compose ps
# 应该看到 hajimi-king 和 warp-proxy 都在运行

# 验证代理
docker exec hajimi-king curl -x http://warp-proxy:1080 https://api.github.com
```

#### 场景3：临时添加代理
```bash
# 假设主服务已经在运行
docker-compose up -d warp-proxy

# 或使用 profile
docker-compose --profile proxy up -d
```

### 查看服务定义

```bash
# 查看所有服务（包括 profile 中的）
docker-compose config --services

# 查看特定 profile 的服务
docker-compose --profile proxy config --services

# 查看完整配置
docker-compose config
```

### 注意事项

1. **Profile 是可选的**：没有 profile 的服务总是会被 `docker-compose up -d` 启动
2. **Profile 可以叠加**：可以同时激活多个 profiles
3. **停止命令影响所有服务**：`docker-compose down` 会停止所有运行的服务，不管它们属于哪个 profile

### 最佳实践

1. **核心服务不设置 profile**：确保主要功能始终可用
2. **可选服务使用 profile**：如代理、监控、调试工具等
3. **在 README 中说明**：文档化不同 profile 的用途

### 你的项目中的使用

```bash
# 日常使用（无代理）
docker-compose up -d
# 只会启动 hajimi-king

# 需要代理时
docker-compose --profile proxy up -d
# 会启动 hajimi-king 和 warp-proxy

# 查看运行状态
docker-compose ps
```

这样设计的好处是：
- 默认情况下不启动不必要的服务
- 需要时可以轻松添加额外功能
- 资源使用更加高效