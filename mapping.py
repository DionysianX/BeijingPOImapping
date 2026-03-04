import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# 1. 网页标题
st.set_page_config(page_title="北京战区分布图", layout="wide")
st.title("🗺️ 北京教育机构分布在线管理系统")

# 2. 读取数据 (解决编码报错的万能写法)
file_name = '北京机构坐标清单_已完成.csv'

@st.cache_data
def load_data():
    # 依次尝试：带签名的UTF-8、GBK、以及UTF-16（Excel常用）
    encodings = ['utf-8-sig', 'gbk', 'utf-16']
    for enc in encodings:
        try:
            df = pd.read_csv(file_name, encoding=enc)
            return df
        except:
            continue
    return None

df = load_data()

if df is not None:
    st.sidebar.success(f"✅ 成功读取数据：{len(df)} 条")
else:
    st.error("❌ 依然读取失败。请检查 GitHub 里的文件名是否叫：北京机构坐标清单_已完成.csv")
    st.stop()

# 3. 筛选功能
st.sidebar.header("区域筛选")
district = st.sidebar.selectbox("选择行政区", ["全部", "朝阳", "昌平", "海淀", "西城", "东城"])
if district != "全部":
    df = df[df['地址'].str.contains(district, na=False)]

# 4. 创建地图对象
amap_tiles = 'http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}'
m = folium.Map(location=[39.95, 116.40], zoom_start=10, tiles=amap_tiles, attr='&copy; Amap')

# 【新增】加载北京市行政区划边界
# 这里使用高德公开的地理边界接口数据（GeoJSON）
bj_admin_url = 'https://geo.datav.aliyun.com/areas_v3/bound/110000_full.json'

folium.GeoJson(
    bj_admin_url,
    name='北京市边界',
    style_function=lambda x: {
        'fillColor': 'transparent', # 中间透明，不遮挡地图
        'color': '#1a73e8',        # 边界线颜色：科技蓝
        'weight': 2.5,             # 线条粗细
        'dashArray': '5, 5'        # 虚线效果，更有作战沙盘感
    }
).add_to(m)

# 5. 循环打点（保持之前的逻辑不变）
marker_cluster = MarkerCluster(disableClusteringAtZoom=14).add_to(m)
for i, row in df.iterrows():
    try:
        loc_str = str(row['经纬度']).strip()
        if ',' in loc_str:
            lng_s, lat_s = loc_str.split(',')
            lat, lng = float(lat_s), float(lng_s)
            
            # 定制弹窗
            name = str(row['名称'])
            addr = str(row['地址'])
            popup_html = f"<b>{name}</b><br><small>{addr}</small>"
            
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_html, max_width=200),
                tooltip=name
            ).add_to(marker_cluster)
    except:
        continue

# 6. 【核心修改】展示地图
# 加上 key 属性和明确的宽高，防止页面空白
st_folium(m, width=1000, height=600, key="bj_map")

# 7. 下方显示数据表
st.write("### 机构详细名单")
st.dataframe(df[['名称', '地址']], use_container_width=True)


