# Docker Healthcheck 详解

## 你的 Healthcheck 配置

```yaml
healthcheck:
  test: ["CMD", "pgrep", "-f", "hajimi_king"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## 各参数含义

### 1. `test: ["CMD", "pgrep", "-f", "hajimi_king"]`
**健康检查命令**

- `CMD` - 在容器内执行命令
- `pgrep` - 进程查找命令（process grep）
- `-f` - 搜索完整的命令行（不只是进程名）
- `hajimi_king` - 要查找的进程名称

**工作原理**：
- 在容器内执行 `pgrep -f hajimi_king`
- 如果找到包含 "hajimi_king" 的进程，返回 0（成功）
- 如果没找到，返回非 0（失败）

### 2. `interval: 30s`
**检查间隔**
- 每 30 秒执行一次健康检查
- 在容器运行期间持续进行

### 3. `timeout: 10s`
**超时时间**
- 每次健康检查最多等待 10 秒
- 如果 10 秒内没有响应，认为检查失败

### 4. `retries: 3`
**重试次数**
- 连续失败 3 次后，容器状态变为 unhealthy
- 给服务一些恢复的机会

### 5. `start_period: 40s`
**启动宽限期**
- 容器启动后的前 40 秒内，健康检查失败不计入重试次数
- 给应用足够的启动时间

## 健康状态流程图

```
容器启动
   ↓
等待 40 秒（start_period）
   ↓
开始健康检查
   ↓
每 30 秒执行: pgrep -f hajimi_king
   ↓
成功 → healthy
失败 → 重试（最多 3 次）
   ↓
连续 3 次失败 → unhealthy
```

## 实际例子

### 正常情况
```bash
# 查看容器健康状态
docker ps
# STATUS 列显示: Up 2 minutes (healthy)

# 查看详细健康信息
docker inspect hajimi-king | jq '.[0].State.Health'
```

### 健康检查失败时
```json
{
  "Status": "unhealthy",
  "FailingStreak": 3,
  "Log": [
    {
      "Start": "2024-01-07T10:00:00Z",
      "End": "2024-01-07T10:00:10Z",
      "ExitCode": 1,
      "Output": ""
    }
  ]
}
```

## 其他常见的健康检查方式

### 1. HTTP 端点检查
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
```

### 2. 脚本检查
```yaml
healthcheck:
  test: ["CMD-SHELL", "python -c 'import sys; sys.exit(0)'"]
```

### 3. 文件存在检查
```yaml
healthcheck:
  test: ["CMD", "test", "-f", "/app/ready.flag"]
```

### 4. 数据库连接检查
```yaml
healthcheck:
  test: ["CMD", "pg_isready", "-U", "postgres"]
```

## 为什么需要 Healthcheck？

1. **自动重启**：不健康的容器可以被自动重启
2. **负载均衡**：只将流量发送到健康的容器
3. **监控告警**：及时发现服务问题
4. **滚动更新**：确保新版本正常运行后才继续更新

## 调试健康检查

### 1. 查看健康检查日志
```bash
docker inspect hajimi-king | jq '.[0].State.Health.Log'
```

### 2. 手动执行健康检查
```bash
docker exec hajimi-king pgrep -f hajimi_king
echo $?  # 0 表示成功，非 0 表示失败
```

### 3. 实时监控健康状态
```bash
watch -n 2 'docker ps --format "table {{.Names}}\t{{.Status}}"'
```

## 优化建议

### 当前配置的问题
`pgrep -f hajimi_king` 可能不够准确，因为：
- 文件已重命名为 `api_key_scanner.py`
- 进程名可能是 `python` 而不是 `hajimi_king`

### 改进方案

#### 方案 1：更新进程名
```yaml
healthcheck:
  test: ["CMD", "pgrep", "-f", "api_key_scanner"]
```

#### 方案 2：检查 Python 进程
```yaml
healthcheck:
  test: ["CMD", "pgrep", "-f", "python.*api_key_scanner"]
```

#### 方案 3：创建专门的健康检查端点
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:9090/health"]
```

#### 方案 4：使用 PID 文件
```yaml
healthcheck:
  test: ["CMD-SHELL", "test -f /var/run/app.pid && kill -0 $(cat /var/run/app.pid)"]
```

## 最佳实践

1. **选择合适的检查方式**
   - 进程检查：简单但不够精确
   - HTTP 检查：更准确但需要额外端点
   - 自定义脚本：最灵活但更复杂

2. **合理设置时间参数**
   - `interval`：不要太频繁（消耗资源）
   - `timeout`：给足够时间响应
   - `start_period`：考虑应用启动时间

3. **监控健康状态**
   - 集成到监控系统
   - 设置告警规则
   - 定期检查健康日志

## 总结

Healthcheck 是 Docker 的重要功能，它：
- 自动监控容器内应用的运行状态
- 提供自愈能力（配合 restart 策略）
- 改善服务的可靠性和可用性

你当前的配置会每 30 秒检查一次进程是否存在，这是一个基础但有效的健康检查策略。