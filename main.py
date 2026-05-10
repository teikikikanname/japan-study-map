import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ページ設定
st.set_page_config(page_title="駅勉ガイド | 神奈川版", page_icon="📖", layout="wide")

# デザインCSS
st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1 { color: #003399; border-bottom: 3px solid #003399; margin-bottom: 20px; }
    h2 { color: #003399; }
    .stButton>button { width: 100%; height: 80px; background-color: #003399; color: white; border-radius: 12px; font-weight: bold; font-size: 18px; }
    .back-button>button { height: 40px !important; background-color: #666 !important; }
    </style>
    """, unsafe_allow_html=True)

# 1. データベース（共通）
stations = ["大宮", "浦和", "赤羽", "池袋", "新宿", "渋谷", "恵比寿", "大崎", "西大井", "武蔵小杉", "新川崎", "横浜", "保土ケ谷", "東戸塚", "戸塚", "大船", "北鎌倉", "鎌倉", "逗子", "藤沢", "辻堂", "茅ヶ崎", "平塚", "大磯", "二宮", "国府津", "鴨宮", "小田原"]

spots_data = [
    {"name": "小田原市立駅前図書コーナー", "station": "小田原", "lat": 35.2562, "lon": 139.1553, "access": "徒歩1分", "desc": "駅直結ハルネ小田原内。"},
    {"name": "小田原市立かもめ図書館", "station": "鴨宮", "lat": 35.2741, "lon": 139.1739, "access": "徒歩10分", "desc": "小田原市の拠点図書館。"},
    {"name": "国府津学習館（図書室）", "station": "国府津", "lat": 35.2809, "lon": 139.2132, "access": "徒歩15分", "desc": "地域の学習拠点。"},
    {"name": "二宮町図書館", "station": "二宮", "lat": 35.2995, "lon": 139.2588, "access": "徒歩7分", "desc": "町立の温かみのある図書館。"},
    {"name": "大磯町立図書館", "station": "大磯", "lat": 35.3113, "lon": 139.3142, "access": "徒歩3分", "desc": "駅から近く便利です。"},
    {"name": "平塚市中央図書館", "station": "平塚", "lat": 35.3352, "lon": 139.3515, "access": "徒歩20分", "desc": "規模が大きく自習に最適。"},
    {"name": "茅ヶ崎市立図書館", "station": "茅ヶ崎", "lat": 35.3289, "lon": 139.4074, "access": "徒歩7分", "desc": "緑豊かな環境にある図書館。"},
    {"name": "藤沢市立辻堂市民図書館", "station": "辻堂", "lat": 35.3353, "lon": 139.4452, "access": "徒歩4分", "desc": "駅近でアクセス抜群。"},
    {"name": "藤沢市立南市民図書館", "station": "藤沢", "lat": 35.3364, "lon": 139.4880, "access": "徒歩4分", "desc": "ODAKYU 湘南 GATE 6F内。"},
    {"name": "鎌倉市立大船図書館", "station": "大船", "lat": 35.3486, "lon": 139.5323, "access": "徒歩7分", "desc": "駅から徒歩圏内。"},
    {"name": "鎌倉市立鎌倉図書館", "station": "鎌倉", "lat": 35.3197, "lon": 139.5467, "access": "徒歩8分", "desc": "古都の雰囲気を感じる図書館。"},
    {"name": "逗子市立図書館", "station": "逗子", "lat": 35.2974, "lon": 139.5781, "access": "徒歩7分", "desc": "明るくモダンな館内。"},
    {"name": "横浜市立戸塚図書館", "station": "戸塚", "lat": 35.4005, "lon": 139.5345, "access": "徒歩3分", "desc": "戸塚駅西口からすぐ。"},
    {"name": "横浜市立中央図書館", "station": "横浜", "lat": 35.4491, "lon": 139.6272, "access": "徒歩20分", "desc": "県内最大。自習席多数。"},
    {"name": "川崎市立幸図書館 日吉分館", "station": "新川崎", "lat": 35.5468, "lon": 139.6732, "access": "徒歩15分", "desc": "新川崎駅から徒歩圏内。"},
    {"name": "川崎市立中原図書館", "station": "武蔵小杉", "lat": 35.5755, "lon": 139.6631, "access": "徒歩1分", "desc": "駅直結・北口すぐ。"},
]
df_spots = pd.DataFrame(spots_data)

# --- 状態管理の初期化 ---
if "page" not in st.session_state:
    st.session_state.page = "top"  # ページ状態：top, range, station

# --- TOPページ ---
if st.session_state.page == "top":
    st.title("📖 駅勉ガイド 神奈川版")
    st.write("どのように勉強スポットを探しますか？")
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚃 定期券の範囲から探す"):
            st.session_state.page = "range"
            st.rerun()
            
    with col2:
        if st.button("🔍 特定の駅から探す"):
            st.session_state.page = "station"
            st.rerun()

# --- 定期券検索ページ ---
elif st.session_state.page == "range":
    st.sidebar.markdown('<div class="back-button">', unsafe_allow_html=True)
    if st.sidebar.button("← 戻る"):
        st.session_state.page = "top"
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    st.title("🚃 定期券の範囲で探す")
    col1, col2 = st.columns(2)
    with col1:
        start_st = st.selectbox("開始駅", stations, index=27) # 小田原
    with col2:
        end_st = st.selectbox("終了駅", stations, index=9)   # 武蔵小杉
    
    idx1, idx2 = stations.index(start_st), stations.index(end_st)
    valid_range = stations[min(idx1, idx2) : max(idx1, idx2) + 1]
    target_spots = df_spots[df_spots['station'].isin(valid_range)]
    
    # 地図とリスト表示（共通処理を関数化しても良いですが、ここではシンプルに記述）
    if not target_spots.empty:
        m = folium.Map(location=[target_spots['lat'].mean(), target_spots['lon'].mean()], zoom_start=11)
        for _, spot in target_spots.iterrows():
            folium.Marker([spot['lat'], spot['lon']], popup=f"{spot['name']}({spot['access']})", icon=folium.Icon(color='blue')).add_to(m)
        st_folium(m, width=None, height=400, use_container_width=True)
        for _, spot in target_spots.iterrows():
            with st.expander(f"【{spot['station']}駅】{spot['name']} ({spot['access']})"):
                st.write(spot['desc'])
    else:
        st.info("この区間に登録スポットはありません。")

# --- 駅名検索ページ ---
elif st.session_state.page == "station":
    st.sidebar.markdown('<div class="back-button">', unsafe_allow_html=True)
    if st.sidebar.button("← 戻る"):
        st.session_state.page = "top"
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    st.title("🔍 特定の駅から探す")
    search_st = st.selectbox("駅名を選択してください", stations, index=9) # 武蔵小杉
    
    # その駅のスポットを抽出
    target_spots = df_spots[df_spots['station'] == search_st]
    
    if not target_spots.empty:
        st.write(f"### {search_st}駅周辺のスポット")
        m = folium.Map(location=[target_spots['lat'].iloc[0], target_spots['lon'].iloc[0]], zoom_start=14)
        for _, spot in target_spots.iterrows():
            folium.Marker([spot['lat'], spot['lon']], popup=f"{spot['name']}({spot['access']})", icon=folium.Icon(color='green')).add_to(m)
        st_folium(m, width=None, height=400, use_container_width=True)
        
        for _, spot in target_spots.iterrows():
            with st.expander(f"📌 {spot['name']} ({spot['access']})"):
                st.write(spot['desc'])
                st.write(f"🔗 [Googleマップで開く](https://www.google.com/maps/search/?api=1&query={spot['lat']},{spot['lon']})")
    else:
        st.warning(f"現在、{search_st}駅の徒歩圏内に登録されている無料スポットはありません。")
        st.info("💡 湘南新宿ラインの隣の駅もチェックしてみてください。")
