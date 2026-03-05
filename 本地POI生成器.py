import pandas as pd
import folium
from folium.plugins import MarkerCluster

# 1. 数据读取
def load_data(file_path):
    for enc in ['utf-8-sig', 'gbk', 'utf-16']:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except:
            continue
    return None

file_name = '北京机构坐标清单_已完成.csv'
df = load_data(file_name)

# 2. 地图初始化与自适应
amap_tiles = 'http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}'
# 重点：tiles=None 配合 TileLayer 才能隐藏乱码网址
m = folium.Map(location=[39.95, 116.40], zoom_start=10, tiles=None)

folium.TileLayer(
    tiles=amap_tiles, 
    attr='高德地图', 
    name='高德地图底图', 
    control=False  # 隐藏底图选项
).add_to(m)

# 手机自适应 Meta 标签
header_str = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />'
m.get_root().header.add_child(folium.Element(header_str))

# 3. 北京边界（蓝色虚线）
bj_admin_url = 'https://geo.datav.aliyun.com/areas_v3/bound/110000_full.json'
folium.GeoJson(bj_admin_url, name='北京市边界', 
               style_function=lambda x: {'fillColor': 'transparent', 'color': '#1a73e8', 'weight': 2, 'dashArray': '5, 5'}).add_to(m)

# 4. 动态生成各区聚合图层
all_districts = ['朝阳', '昌平', '海淀', '西城', '东城', '大兴', '通州', '顺义', '丰台', '房山', '门头沟', '石景山', '怀柔', '密云', '延庆', '平谷']
colors = ['orange', 'blue', 'green', 'red', 'purple', 'cadetblue', 'darkred', 'darkblue', 'darkgreen']
color_idx = 0

for dist in all_districts:
    dist_df = df[df['地址'].str.contains(dist, na=False)]
    if not dist_df.empty:
        group = folium.FeatureGroup(name=f'{dist}区 ({len(dist_df)}点)')
        cluster = MarkerCluster().add_to(group)
        current_color = colors[color_idx % len(colors)]
        color_idx += 1
        
        for _, row in dist_df.iterrows():
            try:
                lng_s, lat_s = str(row['经纬度']).split(',')
                popup_html = f"""
                <div style="width: 220px; font-family: 'Microsoft YaHei';">
                    <h4 style="margin: 0 0 5px 0; color: #1a73e8; font-size: 16px;">{row['名称']}</h4>
                    <p style="margin: 0; font-size: 13px; color: #666;"><b>地址:</b> {row['地址']}</p>
                </div>
                """
                folium.Marker(
                    location=[float(lat_s), float(lng_s)], 
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color=current_color, icon='info-sign')
                ).add_to(cluster)
            except: continue
        group.add_to(m)

# ==========================================
# 5. 图层控制台（核心修改：collapsed=True 实现自动收起）
# ==========================================
# collapsed=True: 默认收起，节省空间
# overlay=True: 让各区可以多选
folium.LayerControl(collapsed=True, overlay=True).add_to(m)

# 6. 全选/全不选 JS 脚本（美化了按钮样式）
select_all_js = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    var layerControl = document.querySelector('.leaflet-control-layers');
    // 监听鼠标移入展开后的操作
    layerControl.addEventListener('mouseenter', function() {
        if (!document.getElementById('custom-tools')) {
            var overlayList = document.querySelector('.leaflet-control-layers-overlays');
            var container = document.createElement('div');
            container.id = 'custom-tools';
            container.style.padding = '8px';
            container.style.borderTop = '1px solid #ccc';
            container.style.textAlign = 'center';
            container.innerHTML = `
                <button onclick="toggleLayers(true)" style="cursor:pointer; padding:3px 8px; font-size:12px; border-radius:4px; border:1px solid #ddd; background:#f9f9f9;">全选</button>
                <button onclick="toggleLayers(false)" style="cursor:pointer; padding:3px 8px; font-size:12px; border-radius:4px; border:1px solid #ddd; background:#f9f9f9; margin-left:5px;">全不选</button>
            `;
            overlayList.parentNode.appendChild(container);
        }
    });
});

function toggleLayers(show) {
    var inputs = document.querySelectorAll('.leaflet-control-layers-selector');
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].checked !== show) {
            inputs[i].click();
        }
    }
}
</script>
"""
m.get_root().html.add_child(folium.Element(select_all_js))

# 7. 保存文件
output_file = '北京战区作战指挥系统_旗舰版.html'
m.save(output_file)
print(f"🎯 旗舰版系统生成成功！默认已收起筛选栏，视野更开阔。")