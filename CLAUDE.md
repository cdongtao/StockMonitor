# Stock Monitor

## 项目概述

Web 端 A 股涨停板监控工具。三个独立模块：

| 模块 | 技术 | 职责 |
|------|------|------|
| `jobs/` | Python + APScheduler | 每日收盘后拉取东方财富/Tushare 数据写入 DB；盘中每分钟实时监控 |
| `backend/` | Python FastAPI | HTTP 接口、JWT 认证、告警规则 CRUD；只读行情数据 |
| `frontend/` | React + TypeScript + Vite | Web 界面 |

**数据流：** `jobs/` 收盘后写入 PostgreSQL → `frontend/` 调 `backend/` API → 从 DB 读取返回

---

## 技术栈速查

**backend/**：FastAPI 0.110, Python 3.11, SQLAlchemy 2 (async), PostgreSQL 16, Alembic, JWT (python-jose)

**jobs/**：APScheduler 3, httpx, pandas-ta, aiosmtplib；数据源：东方财富（B1–B10, B18）+ Tushare（历史K线）

**frontend/**：React 18, TypeScript 5 (strict), TailwindCSS 3, Zustand 4, TanStack Query 5, React Router 6, Recharts 2, TradingView Lightweight Charts 4

---

## 环境变量（.env，backend/ 和 jobs/ 共用）

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/stockmonitor
SECRET_KEY=<random 32 bytes>
SMTP_HOST=
SMTP_PORT=465
SMTP_USER=
SMTP_PASS=
TUSHARE_TOKEN=
```

前端：`VITE_API_BASE_URL=http://localhost:8000`（禁止硬编码）

---

## 常用命令

```bash
# backend
cd backend && uvicorn app.main:app --reload

# jobs
cd jobs && python main.py

# frontend
cd frontend && npm run dev

# 数据库迁移
cd backend && alembic upgrade head
```

---

## 知识文档索引

详细设计见 `knowleage/` 目录：

| 文件 | 权威内容 |
|------|---------|
| `1.architecture.md` | 功能列表（B1–B18, F1–F15）、开发排期 |
| `2.backend-design.md` | backend/ 目录结构、认证设计 |
| `3.frontend-design.md` | frontend/ 目录结构、页面路由、组件复用 |
| `4.job-design.md` | jobs/ 目录结构、数据同步时间表、东方财富 API Mapping |
| `5.db-design.md` | 数据库表结构、字段定义 |
| `6.coding-rules.md` | 禁止事项、命名规范、测试要求 |
| `WebScreen/api/` | 东方财富原始 API 参数与字段说明 |

---

## 开发阶段现状

- **阶段一**（Jobs 核心数据入库）：未开始
- **阶段二**（Backend + Frontend 主要展示页）：未开始
- **阶段三**（深度数据 + 剩余页面）：未开始
- **阶段四**（告警系统）：未开始
- **阶段五**（回测）：未开始

---

## 关键约束（必须遵守）

- `backend/` 只读行情表，`jobs/` 只读用户表/告警表（写权限严格隔离）
- 禁止修改已提交的 Alembic 迁移文件，变更必须新建迁移
- 禁止在 React 组件中直接 fetch，必须通过 `api/` 层
- 禁止 TypeScript `any` 类型
- 每个 sync 任务必须 upsert（`ON CONFLICT DO UPDATE`），不得先删后插
- 每个 backend 接口必须注入 `Depends(get_current_user)`

---

## 文档维护规则

每次新增或修改 `knowleage/` 下任意文件后，必须检查其他文件是否有以下问题并立即修正：

1. **内容重复**：同一信息只能有一个权威来源，其他文件引用或删除
2. **内容冲突**：某文件的描述与已做决定不符（如 Redis、数据源归属、推送方式）
3. **内容过时**：架构调整后旧文件未同步（如模块职责变化、阶段重排）
4. **路径失效**：文件或目录改名/移动后，必须用 `grep -rn` 扫描整个项目所有引用，逐一更新为新路径