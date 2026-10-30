import requests
import time
import pandas as pd
from tabulate import tabulate

####涨跌停监控

pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# 取消宽度限制，不换行
pd.set_option('display.width', 2000)
pd.set_option('display.expand_frame_repr', False)

# 1️⃣ 设置请求 URL 和参数
url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"

params = {
    "source": "SECURITIES",
    "client": "APP",
    "reportName": "RPT_INTSELECTION_MONITORHIS",
    "columns": ",".join([
        "SECUCODE", "SECURITY_CODE", "SECURITY_NAME_ABBR", "TRADE_DATE",
        "NEWEST_PRICE", "YIELD", "MISMATCH_LIMIT_AMOUNT", "MATCH_CHANGE_RATE",
        "MATCH_DEAL_AMOUNT", "MATCH_DEAL_VOLUME", "MISMATCH_VOLUME", "MISMATCH_AMOUNT",
        "MISMATCH_TURNOVERRATE", "BOARD_NAME", "IS_MARGININFO"
    ]),
    #(IS_ST="0") 过滤ST
    #(MARKET_TYPE in ("001","002","003","004"))  001 → 上交所主板;002 → 深交所主板;003 → 中小板;004 → 创业板
    #filter=(TRADE_DATE='2025-12-26')(IS_MISMATCH_LIMIT=1)(MARKET_TYPE in ("001","002","003","004"))(IS_ST="0")
    "filter": "(TRADE_DATE='2025-12-26')(IS_MISMATCH_LIMIT=1)",
    "pageNumber": 1,
    "pageSize": 8,
    "sortTypes": -1,
    "sortColumns": "MISMATCH_LIMIT_AMOUNT",
    "em_timestamp": str(int(time.time() * 1000))
}

# 2️⃣ 发送请求
response = requests.get(url, params=params)
data_json = response.json()

# 3️⃣ 提取数据
if data_json.get("result") and data_json["result"].get("data"):
    data_list = data_json["result"]["data"]
    df = pd.DataFrame(data_list)

    # 4️⃣ 打印数据功能说明
    print("📌 数据字段说明：")
    print("""
SECUCODE              : 股票唯一编码
SECURITY_CODE          : 股票代码
SECURITY_NAME_ABBR     : 股票简称
TRADE_DATE             : 交易日期
NEWEST_PRICE           : 最新收盘价
YIELD                  : 当日涨跌幅
MISMATCH_LIMIT_AMOUNT  : 异动涨停金额
MATCH_CHANGE_RATE      : 成交额变化率
MATCH_DEAL_AMOUNT      : 成交金额
MATCH_DEAL_VOLUME      : 成交量
MISMATCH_VOLUME        : 异动成交量
MISMATCH_AMOUNT        : 异动金额
MISMATCH_TURNOVERRATE  : 异动换手率
BOARD_NAME             : 板块
IS_MARGININFO          : 是否有融资融券信息
""")

    # 5️⃣ 打印总数
    print(f"🔹 总条数: {len(df)} 条\n")

    # 6️⃣ 打印表格
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))

else:
    print("没有抓到数据或返回为空")
