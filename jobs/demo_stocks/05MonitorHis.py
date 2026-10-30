import requests
import time
import pandas as pd
from tabulate import tabulate

## 涨停伏击
# 请求 URL
url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"

# 请求参数
params = {
    "source": "SECURITIES",
    "client": "APP",
    "reportName": "RPT_INTSELECTION_MONITORHIS",
    "columns": "SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,TRADE_DATE,BOARD_NAME,NEWEST_PRICE,YIELD,ZTJY,TURNOVERRATE,DEAL_AMOUNT,FREE_MARKET_VALUE,SEALING_RATE_YEAR,IS_MARGININFO",
    "filter": "(TRADE_DATE='2025-12-26')(IS_QUALITY_GENE=1)",
    "pageNumber": 1,
    "pageSize": 8,
    "sortTypes": -1,
    "sortColumns": "ZTJY",
    "em_timestamp": str(int(time.time() * 1000))
}

# 发送请求
response = requests.get(url, params=params)
data_json = response.json()

# 转换为 DataFrame
data_list = data_json.get("result", {}).get("data", [])
df = pd.DataFrame(data_list)

# 字段说明
fields_description = {
    "SECUCODE": "股票内部代码",
    "SECURITY_CODE": "股票交易代码",
    "SECURITY_NAME_ABBR": "股票简称",
    "TRADE_DATE": "交易日期",
    "BOARD_NAME": "板块名称",
    "NEWEST_PRICE": "最新价格",
    "YIELD": "涨跌幅",
    "ZTJY": "涨停交易活跃度",
    "TURNOVERRATE": "换手率",
    "DEAL_AMOUNT": "成交额",
    "FREE_MARKET_VALUE": "流通市值",
    "SEALING_RATE_YEAR": "年化封板率",
    "IS_MARGININFO": "是否有融资融券信息"
}

# 打印字段说明
print("字段说明：")
for col, desc in fields_description.items():
    print(f"{col}: {desc}")
print("\n")

# 打印总条数
print(f"总条数: {len(df)}\n")

# 打印表格
if not df.empty:
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=True))
else:
    print("没有获取到数据")
