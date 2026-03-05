import requests
import pandas as pd
import time

def get_location(address, key):
    # 自动补全“北京市”，提高高德 API 的识别率
    if not address.startswith("北京市"):
        address = "北京市" + str(address)
    
    url = f"https://restapi.amap.com/v3/geocode/geo?address={address}&output=JSON&key={key}"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data['status'] == '1' and data['geocodes']:
            location = data['geocodes'][0]['location']
            print(f"✅ 成功：{address} -> {location}")
            return location
        else:
            print(f"❌ 失败：{address} (高德未匹配到坐标)")
            return "未匹配"
    except Exception as e:
        print(f"⚠️ 错误：请求超时或网络问题 - {e}")
        return "请求出错"

# 1. 设置你的 Key（必须去高德后台申请 Web 服务 Key）
MY_KEY = '73176baf99f5041c23ff795aa0f5277b'

# 2. 读取文件（确保你的文件名是对的）
try:
    # 如果你的 CSV 编码有问题，尝试 encoding='gbk'
    df = pd.read_csv('地址表.csv', encoding='utf-8') 
    
    # 假设你的地址那一列的表头叫 "地址"
    print("正在开始批量转换，请稍候...")
    df['经纬度'] = df['地址'].apply(lambda x: get_location(x, MY_KEY))
    
    # 3. 导出结果
    df.to_csv('北京机构坐标清单_已完成.csv', index=False, encoding='utf-8-sig')
    print("\n🎉 全部处理完成！请查看：北京机构坐标清单_已完成.csv")
    
except FileNotFoundError:
    print("⚠️ 找不到文件！请检查‘地址表.csv’是否和代码在同一个文件夹里。")