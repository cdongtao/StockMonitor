import requests
import pandas as pd

# 东方财富延迟行情批量接口
url = "https://push2delay.eastmoney.com/api/qt/ulist.np/get"

# 请求参数
params = {
    "ut": "c38fe8f6b4af4bd6683d94ff21883db4",
    "fltt": 2,
    "invt": 2,
    "fields": "f14,f148,f3,f12,f2,f13,f62,113.aum,113.snm,113.cum,113.alm,115.MAM,113.znm,114.bm,114.am,114.mm,113.bum,115.TAM,114.lm,114.ppm,114.fbm,113.fum,114.bbm,115.PFM,114.cm,113.pbm,113.rum,115.URM,115.CYM,114.pgm,142.lum,114.egm,113.ssm,114.vm,115.SMM,114.im,115.SFM,113.hcm,114.lhm,113.rbm,115.FGM,115.SAM,114.jmm,114.jm,225.sim,225.lcm",
    "secids": "1.603876,1.600219,1.600361,0.300057,1.603937,0.300337,1.601388,1.601600,1.600595,1.601702,1.600888,0.003038,0.002160,0.002501,0.002532,0.000612,0.000807,0.000933,0.002379,1.605208,0.002988,1.601677,0.002578,1.603271,1.603115,0.002824,0.002806,0.002540,0.300328,1.600768,0.300986,0.300828,0.002996,1.603993,1.600111,1.601600,0.000807,1.600362,0.000426,0.000630,1.601168,1.600549,0.002532,1.688795,1.688802,1.600930,1.688783,0.301656,1.560860,113.aum,113.snm,113.cum,113.alm,115.MAM,113.znm,114.bm,114.am,114.mm,113.bum,115.TAM,114.lm,114.ppm,114.fbm,113.fum,114.bbm,115.PFM,114.cm,113.pbm,113.rum,115.URM,115.CYM,114.pgm,142.lum,114.egm,113.ssm,114.vm,115.SMM,114.im,115.SFM,113.hcm,114.lhm,113.rbm,115.FGM,115.SAM,114.jmm,114.jm,225.sim,225.lcm"
}

# 发送请求
response = requests.get(url, params=params)

# 解析 JSON
data = response.json()

# 如果返回的 data 包含 'data' → 'diff' 是列表
if 'data' in data and 'diff' in data['data']:
    df = pd.DataFrame(data['data']['diff'])
    print(df.head())  # 查看前几条数据
else:
    print("未返回数据或结构变化")
