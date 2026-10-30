import requests
import pandas as pd
import time
from tabulate import tabulate


## 获取 统计涨停转化为指标

# 显示所有列
pd.set_option('display.max_columns', None)

# 显示所有行
pd.set_option('display.max_rows', None)

# 取消宽度限制，不换行
pd.set_option('display.width', 2000)
pd.set_option('display.expand_frame_repr', False)

url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
params = {
    "source": "SECURITIES",
    "client": "APP",
    "reportName": "RPT_INTSELECTION_LIMITHIS",
    "columns": "TRADE_DATE,LIMIT_NUMBERS,NATURAL_LIMIT,DAILY_LIMIT,TOUCH_LIMIT,SEALING_RATE,NATURAL_LIMIT_YES,LIMIT_PER_YES,POSITION_SUGGESTION,MONEYMAKING_EFFECT,SEALING_RATE_YES,LIMIT_DOWN_NUM,CJDT_NUM,DT_FBL",
    "filter": "(TRADE_DATE<='2025-12-26')",
    "pageNumber": 1,
    "pageSize": 2,
    "sortTypes": -1,
    "sortColumns": "TRADE_DATE",
    "em_timestamp": str(int(time.time()*1000))
}

resp = requests.get(url, params=params)
data = resp.json()["result"]["data"]

df = pd.DataFrame(data)
# print(df)
print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
