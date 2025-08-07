# 修复 Hajimi King 导入错误计划

## 问题分析

在运行 `app/hajimi_king_parallel.py` 时出现以下错误：
```
ModuleNotFoundError: No module named 'common'
```

### 根本原因

1. **导入顺序问题**：
   - 代码先尝试导入 `from common.Logger import logger`（第18行）
   - 然后才添加父目录到系统路径 `sys.path.append('../')`（第20行）
   - 这导致 Python 在导入时找不到 `common` 模块

2. **缺失 `__init__.py` 文件**：
   - `common/` 和 `utils/` 目录缺少 `__init__.py` 文件
   - 这些文件是 Python 识别目录为包所必需的

## 解决方案

### 方案一：快速修复（调整导入顺序）

修改 `app/hajimi_king_parallel.py`：

```python
# 将这些行移到文件开头，在所有导入之前
import sys
import os

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 然后再导入其他模块
from common.Logger import logger
from common.config import Config
# ... 其他导入
```

### 方案二：标准化项目结构（推荐）

1. **创建 `__init__.py` 文件**：
   - `common/__init__.py`
   - `utils/__init__.py`

2. **修改导入方式**：
   - 移除 `sys.path.append('../')`
   - 使用相对导入或绝对导入

3. **运行方式**：
   - 从项目根目录运行：`python -m app.hajimi_king_parallel`
   - 或设置 PYTHONPATH：`PYTHONPATH=. python app/hajimi_king_parallel.py`

## 实施步骤

1. 创建 `common/__init__.py` 文件
2. 创建 `utils/__init__.py` 文件
3. 修改 `app/hajimi_king_parallel.py` 的导入顺序
4. 测试运行程序

## 预期结果

修复后，程序应该能够正常导入所有模块并运行。