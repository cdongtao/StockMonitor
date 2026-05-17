# Jobs Stage 1 Design — 涨停板数据入库

**日期：** 2026-05-17  
**阶段：** 第一阶段 — Jobs 核心数据入库  
**策略：** 先跑通 B1（市场统计），再类推其他 API

---

## 目标

搭通数据管道，将东方财富涨停板数据稳定写入 PostgreSQL。  
Stage 1 只实现 B1，跑通后 B2/B4 照搬模式逐步添加。

---

## 目录结构

```
jobs/
├── main.py                    # APScheduler 入口，注册定时任务 + 启动时回填检查
├── core/
│   ├── config.py              # pydantic Settings，统一读取 .env
│   └── database.py            # async SQLAlchemy engine + session factory
├── data_sources/
│   ├── base.py                # 抽象基类，封装通用 fetch + 自动分页
│   └── eastmoney.py           # 具体方法：fetch_market_stats / fetch_limit_stocks 等
├── tasks/
│   └── sync_market.py         # 调适配器拉数据 → upsert 到 DB
└── models/
    ├── market_daily_stats.py
    ├── limit_up_stocks.py
    ├── limit_up_monitor.py
    └── limit_up_detail.py
```

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 语言 | Python 3.11 |
| 定时调度 | APScheduler 3.x（AsyncIOScheduler）|
| HTTP | httpx（async）|
| ORM | SQLAlchemy 2.x（async）|
| 数据库 | PostgreSQL 16 |
| 配置 | pydantic Settings |

---

## 可配置参数（.env）

```env
# 数据库
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/stockmonitor

# 回填
BACKFILL_DAYS=90           # 回填天数，可随时调整

# 东方财富 API
EM_TIMEOUT=30              # 请求超时秒数
EM_MAX_RETRY=2             # 失败重试次数
EM_PAGE_SIZE=50            # 每页数量
EM_CONCURRENT=5            # 并发页数上限
SYNC_DELAY=1               # 回填每日间隔秒数
```

所有参数通过 `core/config.py` pydantic Settings 读取，代码中不出现硬编码值。

---

## DB 表结构

### market_daily_stats（B1/B3）
每日市场统计，每天 1 条。

```sql
CREATE TABLE market_daily_stats (
    trade_date          DATE PRIMARY KEY,
    limit_numbers       INT,
    natural_limit       INT,
    daily_limit         INT,
    touch_limit         INT,
    sealing_rate        NUMERIC,
    limit_down_num      INT,
    moneymaking_effect  INT,
    position_suggestion INT,
    raw_data            JSONB
);
```

### limit_up_stocks（B2 龙头）
涨停个股/龙头，每日多条。

```sql
CREATE TABLE limit_up_stocks (
    trade_date          DATE,
    secucode            VARCHAR,    -- "001331.SZ"
    security_code       VARCHAR,    -- "001331"
    security_name       VARCHAR,
    board_name          VARCHAR,
    newest_price        NUMERIC,
    yield               NUMERIC,
    ndays_nlimite       VARCHAR,    -- "11天11板"（字符串）
    close_limitup_time  VARCHAR,    -- "09:37:18"
    net_inflow          NUMERIC,
    ztjy                NUMERIC,
    raw_data            JSONB,
    PRIMARY KEY (trade_date, secucode)
);
```

### limit_up_monitor（B4 涨停伏击）
各子池：quality_gene / limit_sprint / limit_regulars。

```sql
CREATE TABLE limit_up_monitor (
    trade_date          DATE,
    pool_type           VARCHAR,    -- quality_gene / limit_sprint / limit_regulars
    secucode            VARCHAR,
    security_code       VARCHAR,
    security_name       VARCHAR,
    board_name          VARCHAR,
    newest_price        NUMERIC,
    yield               NUMERIC,
    ztjy                NUMERIC,
    turnoverrate        NUMERIC,
    raw_data            JSONB,      -- 各 pool_type 独有字段
    PRIMARY KEY (trade_date, pool_type, secucode)
);
```

### limit_up_detail（B5/B7 板块个股+涨停原因）

```sql
CREATE TABLE limit_up_detail (
    trade_date          DATE,
    secucode            VARCHAR,
    security_code       VARCHAR,
    security_name       VARCHAR,
    board_code          VARCHAR,    -- "BK0802"
    board_name          VARCHAR,
    limit_reason        VARCHAR,
    limit_content       TEXT,
    nlimitup            VARCHAR,    -- "9天6板"（字符串）
    close               NUMERIC,
    change_rate         NUMERIC,
    raw_data            JSONB,
    PRIMARY KEY (trade_date, secucode, board_code)
);
```

> **设计原则：** 确定字段建列，不确定/稀疏字段存 `raw_data JSONB`。`ndays_nlimite`/`nlimitup` 等中文字符串字段直接存储，不做转换。

---

## 数据流设计

### 适配器层（data_sources/）

```
base.py
└── fetch_all_pages(report_name, columns, filter, **kwargs)
    ├── 请求第 1 页，获取 result.pages 总页数
    ├── asyncio.gather 并发请求剩余页（≤ EM_CONCURRENT）
    └── 合并所有 data[] 返回 list[dict]

eastmoney.py
├── fetch_market_stats(trade_date)          # RPT_INTSELECTION_LIMITHIS → B1
├── fetch_limit_stocks(trade_date)          # RPT_INTSELECTION_LIMITSTOCKHIS → B2
├── fetch_monitor_pool(trade_date, pool_type)  # RPT_INTSELECTION_MONITORHIS → B4
└── fetch_limit_detail(trade_date)          # RPT_PCHOT_LIMITLIST_HSDETIAL → B5/B7
```

- `em_timestamp` 固定传常量 `1770038173236`
- timeout: `EM_TIMEOUT` 秒，失败重试 `EM_MAX_RETRY` 次
- 单页失败记录日志，不中断整体流程
- 返回 `list[dict]` 原始数据，不做字段转换

### 任务层（tasks/sync_market.py）

```
1. 调用 eastmoney.fetch_market_stats(trade_date)
2. 拿到 list[dict] 原始响应
3. 映射到 ORM model（取需要的列，其余存 raw_data）
4. async with session: execute upsert (ON CONFLICT DO UPDATE)
5. 记录日志：成功条数 / 失败原因
```

---

## 回填策略

```
main.py 启动时：
├── 调 RPT_INTSELECTION_DATELIST 拿最近交易日列表
├── 查询 market_daily_stats 最早记录
├── DB 为空 → 回填最近 BACKFILL_DAYS 个交易日
├── 已有数据 → 跳过，只注册定时任务
└── 回填：逐日顺序执行，每日间隔 SYNC_DELAY 秒（避免限流）
```

- upsert 写入，重复跑同一天不产生重复数据
- 只对交易日执行，跳过周末和节假日

---

## 调度设计

```python
# main.py
scheduler = AsyncIOScheduler()

# 每个交易日 15:35 执行（Stage 1 只有 B1）
scheduler.add_job(sync_market_stats, 'cron', hour=15, minute=35)

# 后续阶段逐步添加（注释占位）
# scheduler.add_job(sync_limit_stocks, 'cron', hour=15, minute=40)   # B2
# scheduler.add_job(sync_monitor_pool, 'cron', hour=15, minute=45)   # B4

scheduler.start()
```

运行方式：
```bash
cd jobs && python main.py
```

---

## 实现顺序

1. `core/config.py` + `core/database.py`
2. DB 表迁移（Alembic）— 只建 `market_daily_stats`
3. `models/market_daily_stats.py`
4. `data_sources/base.py` + `eastmoney.py`（只实现 `fetch_market_stats`）
5. `tasks/sync_market.py`（只做 B1 upsert）
6. `main.py`（回填 + 调度）
7. 测试：手动触发回填，验证数据写入

B2/B4 在 B1 跑通后按同样步骤添加。

---

## 约束

- 禁止硬编码任何配置值，全部走 `.env`
- 每个 sync 任务必须实现 upsert，不得先删后插
- 每个 sync 任务必须记录同步日志（成功条数/失败原因）
- 外部 API 调用必须设置 timeout
- 单任务失败不中断整体流程
