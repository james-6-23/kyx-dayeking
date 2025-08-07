# 持续扫描指南

## 问题描述

程序在完成第一轮扫描后，后续循环不再查找新的密钥。这是因为：

1. **查询被标记为已处理**：每个查询处理完成后会被添加到 `checkpoint.processed_queries`
2. **增量扫描机制**：程序设计为避免重复处理相同的查询和文件
3. **文档过滤器**：包含特定关键词（如 `.example`、`docs`、`sample` 等）的文件会被自动过滤

## 解决方案

### 方案1：重置检查点（推荐用于定期全量扫描）

删除或重命名检查点文件，让程序重新开始：

```bash
# 备份当前检查点
mv data/checkpoint.json data/checkpoint_backup_$(date +%Y%m%d_%H%M%S).json
mv data/scanned_shas.txt data/scanned_shas_backup_$(date +%Y%m%d_%H%M%S).txt

# 或者直接删除
rm data/checkpoint.json
rm data/scanned_shas.txt
```

### 方案2：清除已处理查询（保留已扫描文件记录）

只清除已处理的查询，但保留已扫描的文件SHA：

```python
# 创建一个脚本 reset_queries.py
import json
import os

checkpoint_file = "data/checkpoint.json"

if os.path.exists(checkpoint_file):
    with open(checkpoint_file, 'r') as f:
        data = json.load(f)
    
    # 清空已处理的查询
    data['processed_queries'] = []
    
    with open(checkpoint_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print("已清除所有已处理的查询")
```

### 方案3：添加新的查询

在 `data/queries.txt` 中添加新的搜索查询：

```bash
# 添加更多特定的查询
echo 'AIzaSy in:file filename:config.json' >> data/queries.txt
echo 'AIzaSy in:file extension:py' >> data/queries.txt
echo 'AIzaSy in:file language:javascript' >> data/queries.txt
```

### 方案4：修改文档过滤器

如果你想扫描示例文件，可以修改环境变量：

```bash
# 在 .env 文件中修改或添加
FILE_PATH_BLACKLIST="readme,docs"  # 移除 sample, .example 等
```

### 方案5：实现定时重置功能

修改程序，添加定时重置功能：

```python
# 在 api_key_scanner.py 的主循环中添加
from datetime import datetime, timedelta

# 在 main() 函数中
last_reset_time = datetime.now()
RESET_INTERVAL_HOURS = 24  # 每24小时重置一次

while True:
    # 检查是否需要重置
    if datetime.now() - last_reset_time > timedelta(hours=RESET_INTERVAL_HOURS):
        logger.info("🔄 定时重置已处理的查询...")
        checkpoint.processed_queries.clear()
        last_reset_time = datetime.now()
```

## 最佳实践

1. **增量扫描**：适合日常运行，只扫描新的或更新的内容
2. **全量扫描**：定期（如每周）进行一次全量扫描
3. **动态查询**：根据发现的模式添加新的搜索查询
4. **监控日志**：定期检查跳过的文件数量，确保不会错过重要内容

## 查询优化建议

基于日志中的发现，建议添加以下查询：

```text
# 针对不同时间段的查询
AIzaSy in:file pushed:>2024-12-01

# 针对特定文件类型
AIzaSy in:file extension:js NOT filename:example
AIzaSy in:file extension:py NOT path:test

# 针对特定项目结构
AIzaSy in:file path:src filename:config
AIzaSy in:file path:backend filename:.env

# 组合查询提高精确度
"GEMINI_API_KEY" "AIzaSy" in:file
"apiKey" "AIzaSy" in:file extension:json
```

## 监控和告警

建议实现以下监控：

1. **扫描效率监控**：记录每次循环的有效发现率
2. **跳过率告警**：当跳过率超过90%时发送告警
3. **新发现通知**：当发现新的有效密钥时发送通知