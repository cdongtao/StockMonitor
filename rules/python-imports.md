# Rule: Python Import 管理

每次读取或编辑 Python 文件时必须执行：

## 1. 删除无用导入
- 扫描文件所有 `import` 和 `from ... import`
- 检查每个导入的名称是否在文件中实际使用
- 删除未使用的导入行

## 2. 自动补全缺失导入
- 检查代码中引用的名称是否有对应导入
- 若缺失，自动添加正确的 import 语句
- 导入顺序遵循 PEP 8：标准库 → 第三方库 → 本地模块，组间空一行

## 3. 示例

```python
# 修改前（json 未使用，date 未导入）
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession

async def run(d: date) -> int:
    ...

# 修改后
import logging
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

async def run(d: date) -> int:
    ...
```

## 适用范围
- `jobs/` 下所有 `.py` 文件
- `backend/` 下所有 `.py` 文件
