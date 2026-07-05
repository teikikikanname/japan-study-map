import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- ページ全体の基本設定 ---
st.set_page_config(page_title="駅勉ガイド 神奈川版", layout="wide")

# --- Google 連携用の合言葉（一番上に置いておきます） ---
st.markdown('<meta name="google-site-verification" content="ROSJqr15YgcHGn7S5kq-OQJI0EGH47vCPUk9OnKAJXY" />', unsafe_allow_html=True)

# --- データベース（湘南新宿ライン沿線の駅と勉強スポット） ---
stations = [
    "大宮", "浦和", "赤羽", "池袋", "新宿", "渋谷", "恵比寿", "大崎", 
    "西大井", "武蔵小杉", "新川崎", "横浜", "保土ケ谷", "東戸塚", 
    "戸塚", "大船", "北鎌倉", "鎌倉", "逗子", "藤沢", "辻堂", 
    "茅ヶ崎", "平塚", "大磯", "二宮", "国府津", "鴨宮", "小田原"
]

spots_data = [
    {
        "name": "神奈川県立図書館", 
        "station": "横浜", 
        "lat": 35.4542, 
        "lon": 139.6275, 
        "category": "library", 
        "wifi": True, 
        "power": True, 
        "access": "徒歩10分", 
        "desc": "【電源最強】全席コンセント完備。非常に静かで集中できる環境です。"
    },
    {
        "name": "川崎市立中原図書館", 
        "station": "武蔵小杉", 
        "lat": 35.5755, 
        "lon": 139.6631, 
        "category": "library", 
        "wifi": True, 
        "power": True, 
        "access": "駅直結", 
        "desc": "【アクセス抜群】武蔵小杉駅直結。社会人専用席に電源が完備されています。"
    },
    {
        "name": "小田原市立駅前図書コーナー", 
        "station": "小田原", 
        "lat": 35.2562, 
        "lon": 139.1553, 
        "category": "library", 
        "wifi": True, 
        "power": True, 
        "access": "徒歩1 minute", 
        "desc": "【地下街直結】ハルネ小田原内。自習スペースに電源があります。"
    },
]
df_spots = pd.DataFrame(spots_data)

# --- アプリ画面の構築 ---
st.title("📖 駅勉ガイド 神奈川版")
st.write("湘南新宿ライン沿線の**電源・Wi-Fi完備**な勉強スポットを地図から簡単に探せます。")

# 1. 駅を選択するプルダウン（デフォルトは「横浜」駅に設定）
target_st = st.selectbox("調べたい駅を選んでください", stations, index=11)

st.markdown("---")

# 画面を左（地図）と右（詳細情報）の2列に分割
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ スポット地図")
    # 神奈川周辺を中心とした地図を初期表示
    m = folium.Map(location=[35.4437, 139.6380], zoom_start=11)

    # 選択された駅に一致するスポットだけをフィルター
    filtered_spots = df_spots[df_spots['station'] == target_st]

    # 地図にピンを立てる
    for _, spot in filtered_spots.iterrows():
        folium.Marker(
            [spot['lat'], spot['lon']],
            popup=f"<b>{spot['name']}</b><br>{spot['desc']}",
            tooltip=spot['name']
        ).add_to(m)

    # Streamlit上で地図を描画
    st_folium(m, width=700, height=450)

with col2:
    st.subheader("📌 スポット詳細")
    
    # 右側に選択された駅の詳しい情報をリスト表示
    if not filtered_spots.empty:
        for _, spot in filtered_spots.iterrows():
            st.success(f"### 📍 {spot['name']}")
            st.write(f"**アクセス:** {spot['access']}")
            st.write(f"**設備:** {'✅ Wi-Fiあり' if spot['wifi'] else '❌ Wi-Fiなし'} / {'✅ 電源あり' if spot['power'] else '❌ 電源なし'}")
            st.info(spot['desc'])
    else:
        st.warning(f"現在、{target_st}駅の勉強スポットデータは登録されていません。今後のアップデートをお待ちください。")
