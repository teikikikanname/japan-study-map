import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- Google Analytics 連携（サチコ対策） ---
st.markdown("""
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-W9WDMKSB7S"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-W9WDMKSB7S');
    </script>
    """, unsafe_allow_html=True)

# (以下、以前の完全版コードが続きます...)

# ==========================================
# 1. ページ設定 & SEO・Google確認タグ
# ==========================================
st.set_page_config(
    page_title="駅勉ガイド | 湘南新宿ライン沿線の無料勉強場所検索（神奈川版）",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': """
        ### 駅勉ガイド 神奈川版
        湘南新宿ライン（小田原〜武蔵小杉）の定期券範囲内で、
        電源・Wi-Fi完備の勉強スポットを検索できる専門サイトです。
        """
    }
)

# Google Search Console 確認用タグ
st.markdown("""
    <head>
        <meta name="google-site-verification" content="ROSJqr15YgcHGn7S5kq-OQJI0EGH47vCPUk9OnKAJXY" />
    </head>
    """, unsafe_allow_html=True)

# デザインCSS
st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1 { color: #003399; border-bottom: 3px solid #003399; }
    .stButton>button { width: 100%; height: 80px; background-color: #003399; color: white; border-radius: 12px; font-weight: bold; font-size: 18px; }
    .back-button { height: 40px !important; background-color: #666 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. データベース（検証済み：電源・Wi-Fi情報付）
# ==========================================
stations = ["大宮", "浦和", "赤羽", "池袋", "新宿", "渋谷", "恵比寿", "大崎", "西大井", "武蔵小杉", "新川崎", "横浜", "保土ケ谷", "東戸塚", "戸塚", "大船", "北鎌倉", "鎌倉", "逗子", "藤沢", "辻堂", "茅ヶ崎", "平塚", "大磯", "二宮", "国府津", "鴨宮", "小田原"]

spots_data = [
    {"name": "神奈川県立図書館", "station": "横浜", "lat": 35.4542, "lon": 139.6275, "category": "library", "wifi": True, "power": True, "access": "徒歩10分", "desc": "【電源最強】全席コンセント完備。非常に静かで集中できます。"},
    {"name": "川崎市立中原図書館", "station": "武蔵小杉", "lat": 35.5755, "lon": 139.6631, "category": "library", "wifi": True, "power": True, "access": "徒歩1分", "desc": "【駅直結】社会人席に電源あり。平日21時まで開館。"},
    {"name": "小田原市立駅前図書コーナー", "station": "小田原", "lat": 35.2562, "lon": 139.1553, "category": "library", "wifi": True, "power": True, "access": "徒歩1分", "desc": "【ハルネ小田原内】カウンター席に電源あり。PC作業可能。"},
    {"name": "藤沢市立南市民図書館", "station": "藤沢", "lat": 35.3364, "lon": 139.4880, "category": "library", "wifi": True, "power": True, "access": "徒歩4分", "desc": "【ODAKYU 湘南 GATE内】一部座席で電源利用可能。"},
    {"name": "タリーズ 横浜中央図書館店", "station": "横浜", "lat": 35.4491, "lon": 139.6272, "category": "cafe", "wifi": True, "power": True, "access": "徒歩10分", "desc": "【カフェ】一部カウンター席に電源あり。軽食OK。"},
    {"name": "横浜市立戸塚図書館", "station": "戸塚", "lat": 35.4005, "lon": 139.5345, "category": "library", "wifi": True, "power": False, "access": "徒歩3分", "desc": "駅近で便利ですが、PC専用席の電源開放はありません。"},
    {"name": "茅ヶ崎市立図書館", "station": "茅ヶ崎", "lat": 35.3289, "lon": 139.4074, "category": "library", "wifi": True, "power": False, "access": "徒歩7分", "desc": "緑豊かな環境。Wi-Fiは利用可能。"},
    {"name": "鎌倉市立大船図書館", "station": "大船", "lat": 35.3486, "lon": 139.5323, "category": "library", "wifi": True, "power": False, "access": "徒歩7分", "desc": "落ち着いた環境。PC利用は可能（電源なし）。"},
]
df_spots = pd.DataFrame(spots_data)

# ==========================================
# 3. 画面遷移ロジック
# ==========================================
if "page" not in st.session_state:
    st.session_state.page = "top"

if st.session_state.page == "top":
    st.title("📖 駅勉ガイド 神奈川版")
    st.write("湘南新宿ライン沿線の**電源・Wi-Fi完備**な勉強スポットを探せます。")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚃 定期券の範囲から探す"):
            st.session_state.page = "range"; st.rerun()
    with col2:
        if st.button("🔍 特定の駅から探す"):
            st.session_state.page = "station"; st.rerun()

# ==========================================
# 4. 検索結果表示（共通ロジック）
# ==========================================
def display_results(target_spots):
    if not target_spots.empty:
        # 地図表示
        m = folium.Map(location=[target_spots['lat'].mean(), target_spots['lon'].mean()], zoom_start=12)
        for _, spot in target_spots.iterrows():
            # カテゴリでアイコンと色を決定
            icon_name = "book" if spot['category'] == "library" else "coffee"
            icon_color = "blue" if spot['category'] == "library" else "orange"
            
            # 電源・Wi-Fiの有無をテキスト化
            spec_text = ""
            if spot['wifi']: spec_text += " 📶Wi-Fi"
            if spot['power']: spec_text += " ⚡電源"

            folium.Marker(
                [spot['lat'], spot['lon']], 
                popup=f"<b>{spot['name']}</b><br>{spec_text}<br>{spot['access']}",
                tooltip=spot['name'],
                icon=folium.Icon(color=icon_color, icon=icon_name, prefix='fa')
            ).add_to(m)
        
        st_folium(m, width=None, height=450, use_container_width=True)

        # 詳細リスト表示
        st.write("### 🏢 スポット詳細")
        for _, spot in target_spots.iterrows():
            with st.expander(f"【{spot['station']}駅】{spot['name']} ({spot['access']})"):
                col_spec1, col_spec2 = st.columns(2)
                with col_spec1:
                    st.write("📶 Wi-Fi: " + ("✅あり" if spot['wifi'] else "❌なし"))
                with col_spec2:
                    st.write("⚡ 電源: " + ("✅あり" if spot['power'] else "❌なし"))
                st.write("---")
                st.write(f"**特徴:** {spot['desc']}")
                st.write(f"🔗 [Googleマップで開く](https://www.google.com/maps/search/?api=1&query={spot['lat']},{spot['lon']})")
    else:
        st.warning("この区間・駅にはまだ登録スポットがありません。")

# --- 1. トップ画面の判定 ---
if st.session_state.page == "top":
    st.title("📖 駅勉ガイド 神奈川版")
    st.write("湘南新宿ライン沿線の**電源・Wi-Fi完備**な勉強スポットを探せます。")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚃 定期券の範囲から探す"):
            st.session_state.page = "range"
            st.rerun()
    with col2:
        if st.button("🔍 特定の駅から探す"):
            st.session_state.page = "station"
            st.rerun()

# --- 2. 定期券モードの判定 ---
if st.session_state.page == "range":
    if st.sidebar.button("← 戻る"):
        st.session_state.page = "top"
        st.rerun()
    st.title("🚃 定期券の範囲で探す")
    col1, col2 = st.columns(2)
    with col1:
        start_st = st.selectbox("開始駅", stations, index=27)
    with col2:
        end_st = st.selectbox("終了駅", stations, index=9)
    
    idx1, idx2 = stations.index(start_st), stations.index(end_st)
    valid_range = stations[min(idx1, idx2) : max(idx1, idx2) + 1]
    target_spots = df_spots[df_spots['station'].isin(valid_range)]
    display_results(target_spots)

# --- 3. 駅名モードの判定 ---
if st.session_state.page == "station":
    if st.sidebar.button("← 戻る"):
        st.session_state.page = "top"
        st.rerun()
    st.title("🔍 特定の駅から探す")
    search_st = st.selectbox("駅名を選択してください", stations, index=9)
    target_spots = df_spots[df_spots['station'] == search_st]
    display_results(target_spots)
