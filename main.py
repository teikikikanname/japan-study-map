import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- 1. Google Analytics 設置（ここがエラーの原因でした） ---
# 下記の st.markdown から """) までを、このままの形で貼るのがコツです。
st.markdown("""
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-W9WDMKSB7S"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-W9WDMKSB7S');
    </script>
    """, unsafe_allow_html=True)

# --- 2. Google Search Console 確認用タグ（念のため残します） ---
st.markdown("""
    <head>
        <meta name="google-site-verification" content="ROSJqr15YgcHGn7S5kq-OQJI0EGH47vCPUk9OnKAJXY" />
    </head>
    """, unsafe_allow_html=True)

# --- 3. データベース ---
stations = ["大宮", "浦和", "赤羽", "池袋", "新宿", "渋谷", "恵比寿", "大崎", "西大井", "武蔵小杉", "新川崎", "横浜", "保土ケ谷", "東戸塚", "戸塚", "大船", "北鎌倉", "鎌倉", "逗子", "藤沢", "辻堂", "茅ヶ崎", "平塚", "大磯", "二宮", "国府津", "鴨宮", "小田原"]

spots_data = [
    {"name": "神奈川県立図書館", "station": "横浜", "lat": 35.4542, "lon": 139.6275, "category": "library", "wifi": True, "power": True, "access": "徒歩10分", "desc": "【電源最強】全席コンセント完備。"},
    {"name": "川崎市立中原図書館", "station": "武蔵小杉", "lat": 35.5755, "lon": 139.6631, "category": "library", "wifi": True, "power": True, "access": "徒歩1分", "desc": "【駅直結】社会人席に電源あり。"},
    {"name": "小田原市立駅前図書コーナー", "station": "小田原", "lat": 35.2562, "lon": 139.1553, "category": "library", "wifi": True, "power": True, "access": "徒歩1分", "desc": "【ハルネ小田原内】電源あり。"},
]
df_spots = pd.DataFrame(spots_data)

# --- 4. 画面表示 ---
if "page" not in st.session_state:
    st.session_state.page = "top"

if st.session_state.page == "top":
    st.title("📖 駅勉ガイド 神奈川版")
    if st.button("🚃 定期券の範囲から探す"):
        st.session_state.page = "range"
        st.rerun()

if st.session_state.page == "range":
    if st.sidebar.button("← 戻る"):
        st.session_state.page = "top"
        st.rerun()
    st.title("🚃 定期券の範囲で探す")
    start_st = st.selectbox("開始駅", stations, index=27)
    end_st = st.selectbox("終了駅", stations, index=11)
    
    # 地図の表示
    m = folium.Map(location=[35.4437, 139.6380], zoom_start=11)
    st_folium(m, width=700, height=500)