# Hajimi King 查询优化指南

## 查询优化的重要性

GitHub 搜索查询是 Hajimi King 的核心，好的查询策略可以：
- 🎯 提高密钥发现率
- ⚡ 减少无效搜索
- 📈 提升整体效率

## 当前查询策略

### 1. **基础广泛搜索**
```
AIzaSy in:file
```
- 搜索所有包含 Gemini API 密钥前缀的文件
- 覆盖面最广，但结果可能较多

### 2. **环境变量文件**
```
AIzaSy in:file filename:.env
AIzaSy in:file filename:.env.example
AIzaSy in:file filename:.env.local
```
- 开发者最常在 .env 文件中存储 API 密钥
- `.env.example` 经常被误用存储真实密钥

### 3. **配置文件**
```
AIzaSy in:file filename:config extension:json
AIzaSy in:file filename:config extension:yaml
```
- 针对各种配置文件格式
- 结构化配置文件中常见密钥

### 4. **语言特定搜索**
```
AIzaSy in:file extension:py "GEMINI_API_KEY"
AIzaSy in:file extension:js "GEMINI_API_KEY"
```
- 针对 Python 和 JavaScript 项目
- 搜索常见的环境变量名

### 5. **组合搜索**
```
"AIzaSy" "gemini" in:file
"AIzaSy" "api" "key" in:file
```
- 提高搜索精度
- 减少误报

### 6. **时间和大小过滤**
```
AIzaSy in:file pushed:>2024-12-07
AIzaSy in:file size:<10000
```
- 搜索最近更新的项目
- 小文件更可能是配置文件

## 高级查询技巧

### 可以添加的查询：

1. **特定组织搜索**
   ```
   AIzaSy in:file org:google
   AIzaSy in:file org:microsoft
   ```

2. **热门项目搜索**
   ```
   AIzaSy in:file stars:>100
   AIzaSy in:file stars:>1000
   ```

3. **特定路径搜索**
   ```
   AIzaSy in:file path:.github/workflows/
   AIzaSy in:file path:config/
   ```

4. **排除测试文件**
   ```
   AIzaSy in:file -path:test/ -path:tests/
   ```

5. **Docker/K8s 配置**
   ```
   AIzaSy in:file filename:docker-compose
   AIzaSy in:file extension:yaml path:k8s/
   ```

## 查询优化建议

1. **定期更新时间过滤器**
   - 将 `pushed:>2024-12-07` 更新为最近 30 天

2. **根据发现情况调整**
   - 如果某个查询发现率高，可以增加类似查询
   - 如果某个查询总是空结果，考虑移除

3. **避免重复**
   - 某些查询可能返回相同结果
   - 程序会自动去重，但减少重复查询可以提高效率

4. **考虑 API 限制**
   - GitHub 搜索 API 每个查询最多返回 1000 个结果
   - 使用更精确的查询获得更相关的结果

## 使用方法

1. **使用优化版查询**：
   ```bash
   cp data/queries_optimized.txt data/queries.txt
   ```

2. **自定义查询**：
   - 编辑 `data/queries.txt`
   - 每行一个查询
   - 使用 # 添加注释

3. **测试新查询**：
   - 先在 GitHub 网页版测试查询
   - 确认有结果后再添加到配置文件

## 注意事项

- ⚠️ 过于宽泛的查询会消耗大量 API 配额
- ⚠️ 过于具体的查询可能错过潜在结果
- ⚠️ 平衡是关键：既要覆盖面广，又要保持精准