import requests
import pandas as pd
import time

#获取交易日/查询那个时间可以交易
url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
params = {
    "source": "SECURITIES",
    "client": "APP",
    "reportName": "RPT_INTSELECTION_DATELIST",
    "columns": "TRADE_DATE,IS_NEW",
    "sortTypes": "-1",
    "sortColumns": "TRADE_DATE",
    "em_timestamp": str(int(time.time() * 1000))
}

resp = requests.get(url, params=params)
json_data = resp.json()

# 转成 DataFrame
data = json_data['result']['data']
df = pd.DataFrame(data)
print(df.head())
