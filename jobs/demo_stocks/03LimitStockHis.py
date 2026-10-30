import requests
import pandas as pd
from tabulate import tabulate
import time

# ----------------------------
# 请求参数 涨停板龙头
# ----------------------------
url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
params = {
    "source": "SECURITIES",
    "client": "APP",
    "reportName": "RPT_INTSELECTION_LIMITSTOCKHIS",
    "columns": "SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,BOARD_NAME,NEWEST_PRICE,YIELD,NDAYS_NLIMITE,CLOSE_LIMITUP_TIME,LIMITUP_NUM,LIMITUP_AMOUNT,TURNOVERRATE,NET_INFLOW,TRADE_DATE,ZTJY",
    "filter": "(TRADE_DATE='2025-12-26')(IS_HOT_STOCK=1)",
    "distinct": "SECUCODE",
    "pageNumber": 1,
    "pageSize": 1000,
    "sortTypes": "-1,-1,-1",
    "sortColumns": "NDAYS_NLIMITE_RANK,ZTJY,BOARD_YILD",
    "em_timestamp": str(int(time.time()*1000))
}

# ----------------------------
# 抓取数据
# ----------------------------
resp = requests.get(url, params=params)
data = resp.json().get('result', {}).get('data', [])

# ----------------------------
# 转成 DataFrame
# ----------------------------
df = pd.DataFrame(data)

# ----------------------------
# 打印整齐表格
# ----------------------------
if not df.empty:
    # 格式化数字列（可选）
    float_cols = ['NEWEST_PRICE','YIELD','LIMITUP_AMOUNT','TURNOVERRATE','NET_INFLOW','ZTJY']
    for col in float_cols:
        if col in df.columns:
            df[col] = df[col].map(lambda x: f"{x:>10.2f}" if pd.notnull(x) else " " * 10)

    # 打印整齐表格
    print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
else:
    print("没有抓到数据")
