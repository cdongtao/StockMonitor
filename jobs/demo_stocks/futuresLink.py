import requests
import pandas as pd
import json

# 接口 URL
url = "https://emcfgdata.eastmoney.com/api/futuresLink/getFuturesLinks"

# 请求头，模拟手机 Android 客户端
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro Build/TP1A.220905.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36",
    "Content-Type": "application/json"
}

# POST 数据
payload = {
    "args": {},
    "client": "android",
    "randomCode": "1687681190127168768219012363456et375d8f",
    "timestamp": 1770396919730,
    "clientType": "cfw",
    "clientVersion": "10.14"
}

# 发送 POST 请求
response = requests.post(url, headers=headers, json=payload)

# 转换为 JSON
data = response.json()

# 打印完整 JSON（可选）
print(json.dumps(data, ensure_ascii=False, indent=2))

# 转换为 DataFrame 查看
# df = pd.DataFrame(data)
# print(df.head())

# 可选：保存到 Excel
# df.to_excel("futures_links_android.xlsx", index=False)
