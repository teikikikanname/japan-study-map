import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# =========================================================
# ページ全体の基本設定（大手予約サイトと同様にワイド画面を活用）
# =========================================================
st.set_page_config(
    page_title="駅勉ガイド 横浜広域版",
    page_icon="📖",
    layout="wide",
)

# カスタムCSSの適用（フォントの微調整とデザイン全体のトーンを整える）
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { color: #1e3a8a; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 駅の座標データ（全72駅完全対応版）
# =========================================================
STATION_COORDS = {
    "横浜":      (35.4657, 139.6223),
    "新横浜":    (35.5074, 139.6175),
    "戸塚":      (35.4008, 139.5341),
    "東戸塚":    (35.4181, 139.5474),
    "保土ケ谷": (35.4468, 139.5936),
    "大船":      (35.3555, 139.5307),
    "鶴見":      (35.5074, 139.6762),
    "長津田":    (35.5315, 139.4951),
    "二俣川":    (35.4624, 139.5323),
    "上大岡":    (35.4088, 139.5964),
    "金沢文庫": (35.3424, 139.6217),
    "日吉":      (35.5533, 139.6469),
    "菊名":      (35.5097, 139.6310),
    "センター北": (35.5536, 139.5781),
    "センター南": (35.5444, 139.5730),
    "中山":      (35.5146, 139.5394),
    "港南中央": (35.4004, 139.5950),
    "みなとみらい": (35.4578, 139.6326),
    "元町・中華街": (35.4421, 139.6521),
    "桜木町":    (35.4503, 139.6313),
    "日ノ出町": (35.4433, 139.6267),
    "山手":      (35.4269, 139.6466),
    "東神奈川": (35.4778, 139.6322),
    "星川":      (35.4568, 139.6000),
    "馬車道":    (35.4491, 139.6361),
    "関内":      (35.4442, 139.6364),
    "日本大通り": (35.4475, 139.6425),
    "あざみ野": (35.5687, 139.5535),
    "新杉田":    (35.3868, 139.6198),
    "港南台":    (35.3752, 139.5668),
    "西横浜":    (35.4542, 139.6105),
    "天王町":    (35.4554, 139.6049),
    "平沼橋":    (35.4616, 139.6159),
    "三ツ境":    (35.4682, 139.5034),
    "瀬谷":      (35.4705, 139.4795),
    "緑園都市": (35.4382, 139.5242),
    "弥生台":    (35.4293, 139.5101),
    "いずみ野": (35.4187, 139.4952),
    "いずみ中央": (35.4057, 139.4880),
    "湘南台":    (35.3963, 139.4665),
    "神奈川":    (35.4697, 139.6292),
    "戸部":      (35.4578, 139.6206),
    "黄金町":    (35.4418, 139.6219),
    "南太田":    (35.4364, 139.6139),
    "井土ヶ谷": (35.4338, 139.5989),
    "弘明寺(京急)": (35.4243, 139.5982),
    "屏風浦":    (35.3941, 139.6153),
    "杉田":      (35.3811, 139.6201),
    "京急富岡": (35.3672, 139.6302),
    "能見台":    (35.3601, 139.6288),
    "金沢八景": (35.3269, 139.6208),
    "高島町":    (35.4593, 139.6223),
    "伊勢佐木長者町": (35.4416, 139.6343),
    "阪東橋":    (35.4373, 139.6277),
    "吉野町":    (35.4337, 139.6218),
    "蒔田":      (35.4272, 139.6139),
    "弘明寺(地下鉄)": (35.4241, 139.6074),
    "片倉町":    (35.4851, 139.6033),
    "三ツ沢上町": (35.4746, 139.6053),
    "三ツ沢下町": (35.4740, 139.6146),
    "東白楽":    (35.4828, 139.6295),
    "白楽":      (35.4904, 139.6268),
    "妙蓮寺":    (35.4988, 139.6318),
    "大倉山":    (35.5215, 139.6300),
    "綱島":      (35.5365, 139.6342),
    "高田":      (35.5492, 139.6198),
    "日吉本町": (35.5516, 139.6348),
    "石川町":    (35.4391, 139.6436),
    "根岸":      (35.4158, 139.6353),
    "磯子":      (35.4003, 139.6181),
    "洋光台":    (35.3794, 139.5960),
    "本郷台":    (35.3667, 139.5498),
}
STATIONS = sorted(list(STATION_COORDS.keys()))

# =========================================================
# 勉強スポットのデータベース
# =========================================================
SPOTS_DATA = [
    # --- 図書館データ ---
    {"name": "神奈川県立図書館", "station": "桜木町", "lat": 35.4542, "lon": 139.6275, "category": "図書館", "wifi": True, "power": True, "access": "桜木町駅 徒歩10分", "desc": "【電源最強】全席コンセント完備。非常に綺麗で静かな学習環境。"},
    {"name": "横浜市中央図書館", "station": "日ノ出町", "lat": 35.4442, "lon": 139.6267, "category": "図書館", "wifi": True, "power": True, "access": "日ノ出町駅 徒歩3分", "desc": "【大規模】地下1階から5階まで閲覧席多数あり。一部座席でPC・電源利用可能。"},
    {"name": "横浜市中図書館", "station": "山手", "lat": 35.4385, "lon": 139.6540, "category": "図書館", "wifi": False, "power": False, "access": "山手駅 徒歩15分", "desc": "本牧エリアの落ち着いた環境にある図書館。"},
    {"name": "横浜市戸塚図書館", "station": "戸塚", "lat": 35.4001, "lon": 139.5332, "category": "図書館", "wifi": False, "power": False, "access": "戸塚駅西口 徒歩4分", "desc": "駅チカ。落ち着いて勉強や読書ができる定番スポット。"},
    {"name": "横浜市港南図書館", "station": "港南中央", "lat": 35.3970, "lon": 139.5935, "category": "図書館", "wifi": False, "power": False, "access": "港南中央駅 徒歩5分", "desc": "行政機関が集まるエリアにある静かな図書館。"},
    {"name": "横浜市港北図書館", "station": "菊名", "lat": 35.5118, "lon": 139.6293, "category": "図書館", "wifi": False, "power": False, "access": "菊名駅東口 徒歩7分", "desc": "地域住民や学生の自習に広く使われています。"},
    {"name": "横浜市都筑図書館", "station": "センター南", "lat": 35.5451, "lon": 139.5732, "category": "図書館", "wifi": False, "power": False, "access": "センター南駅 徒歩6分", "desc": "都筑区総合庁舎内。広々とした快適な空間。"},
    {"name": "横浜市鶴見図書館", "station": "鶴見", "lat": 35.5090, "lon": 139.6732, "category": "図書館", "wifi": False, "power": False, "access": "鶴見駅西口 徒歩7分", "desc": "鶴見区民の学習を支える中央図書館。"},
    {"name": "横浜市神奈川図書館", "station": "東神奈川", "lat": 35.4776, "lon": 139.6289, "category": "図書館", "wifi": False, "power": False, "access": "東神奈川駅 徒歩10分", "desc": "神奈川公園近くの静かな環境。"},
    {"name": "横浜市保土ケ谷図書館", "station": "星川", "lat": 35.4528, "lon": 139.5982, "category": "図書館", "wifi": False, "power": False, "access": "星川駅 徒歩6分", "desc": "緑豊かな落ち着いた環境で勉強ができます。"},
    {"name": "横浜市旭図書館", "station": "二俣川", "lat": 35.4665, "lon": 139.5240, "category": "図書館", "wifi": False, "power": False, "access": "二俣川駅北口 徒歩11分", "desc": "学生の利用も多い相鉄沿線の学習スポット。"},

    # --- カフェデータ（横浜・新横浜・周辺） ---
    {"name": "スターバックス 横浜西口店", "station": "横浜", "lat": 35.4645, "lon": 139.6210, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅西口 徒歩3分", "desc": "定番のスタバ。作業や勉強に集中しやすい環境です。"},
    {"name": "タリーズコーヒー NEWoMan横浜店", "station": "横浜", "lat": 35.4661, "lon": 139.6225, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅直結 NEWoMan内", "desc": "駅直結の綺麗で洗練された店舗。デスクワークも快適。"},
    {"name": "ドトールコーヒー 横浜西口店", "station": "横浜", "lat": 35.4640, "lon": 139.6205, "category": "カフェ", "wifi": True, "power": False, "access": "横浜駅西口 徒歩2分", "desc": "サクッと短時間集中したい時におすすめの手軽なカフェ。"},
    {"name": "エクセルシオールカフェ 横浜駅西口店", "station": "横浜", "lat": 35.4643, "lon": 139.6208, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅西口 徒歩3分", "desc": "コンセント席も用意されておりPC作業に向いています。"},
    {"name": "カフェ・ド・クリエ 横浜北幸店", "station": "横浜", "lat": 35.4655, "lon": 139.6185, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅西口 徒歩6分", "desc": "北幸のオフィス街近くにあり、落ち着いた雰囲気で作業可能です。"},
    {"name": "スターバックス キュービックプラザ新横浜店", "station": "新横浜", "lat": 35.5076, "lon": 139.6178, "category": "カフェ", "wifi": True, "power": True, "access": "新横浜駅直結", "desc": "駅直結ビル内。PC作業利用が多い店舗。"},
    {"name": "タリーズコーヒー 新横浜店", "station": "新横浜", "lat": 35.5080, "lon": 139.6165, "category": "カフェ", "wifi": True, "power": True, "access": "新横浜駅 徒歩2分", "desc": "コンセント席も完備されているためデスクワークに最適。"},
    {"name": "タリーズコーヒー 綱島駅前店", "station": "綱島", "lat": 35.5368, "lon": 139.6342, "category": "カフェ", "wifi": True, "power": True, "access": "綱島駅東口 徒歩1分", "desc": "【電源あり】カウンター席にコンセント完備。ビジネス利用も多く集中しやすい環境。"},
    {"name": "ガスト 弘明寺店", "station": "弘明寺(地下鉄)", "lat": 35.4245, "lon": 139.6080, "category": "カフェ", "wifi": True, "power": True, "access": "地下鉄弘明寺駅 徒歩2分", "desc": "【電源あり】すかいらーくWi-Fiとコンセント完備。席が広く参考書を広げやすい。"},
    {"name": "マクドナルド 井土ヶ谷店", "station": "井土ヶ谷", "lat": 35.4335, "lon": 139.5992, "category": "カフェ", "wifi": True, "power": True, "access": "井土ヶ谷駅 徒歩1分", "desc": "【電源あり】カウンター席に充電設備あり。駅からすぐでクイックな学習に便利。"},
    {"name": "上島珈琲店 金沢八景店", "station": "金沢八景", "lat": 35.3272, "lon": 139.6212, "category": "カフェ", "wifi": True, "power": True, "access": "金沢八景駅 徒歩1分", "desc": "【電源あり】大学が近いエリア。レトロでモダンな空間で長時間の勉強に抜群。"},
    {"name": "プロント 湘南台店", "station": "湘南台", "lat": 35.3965, "lon": 139.4668, "category": "カフェ", "wifi": True, "power": True, "access": "湘南台駅西口 徒歩1分", "desc": "【電源あり】一人用カウンター席が充実しており、PC作業や自習が快適。"}
]

@st.cache_data
def load_spots() -> pd.DataFrame:
    return pd.DataFrame(SPOTS_DATA)

df_spots = load_spots()

CATEGORY_ICON = {
    "図書館": ("blue", "book"),
    "カフェ": ("orange", "coffee"),
}

def get_icon(category: str) -> folium.Icon:
    color, icon_name = CATEGORY_ICON.get(category, ("green", "info-sign"))
    return folium.Icon(color=color, icon=icon_name, prefix="fa" if icon_name != "info-sign" else "glyphicon")

# =========================================================
# サイドバー：検索・絞り込み条件（入力エリアを左に集約）
# =========================================================
st.sidebar.markdown("### 🔍 スポットを絞り込む")

target_st = st.sidebar.selectbox(
    "1. 調べたい駅を選択",
    STATIONS,
    index=STATIONS.index("横浜"),
)

selected_categories = st.sidebar.multiselect(
    "2. カテゴリ選択",
    options=["図書館", "カフェ"],
    default=["図書館", "カフェ"]
)

keyword = st.sidebar.text_input("3. キーワード検索（任意）", placeholder="例：スタバ、電源")

st.sidebar.markdown("**4. 必須設備チェック**")
wifi_only = st.sidebar.checkbox("🛜 Wi-Fiありのみ")
power_only = st.sidebar.checkbox("🔌 電源ありのみ")

st.sidebar.markdown("---")
st.sidebar.caption(f"登録駅数：{len(STATIONS)}駅 / スポット数：全{len(df_spots)}件")

# =========================================================
# メイン画面：ヘッダーデザインの洗練
# =========================================================
st.title("📖 駅勉ガイド 横浜広域版")
st.caption("大手スペース検索サイトのUIをベンチマークした、地図とリストが連動するスマートな学習空間検索システムです。")

# 大手サイトの手法①：よく使われる「主要駅」へのクイックアクセスボタン
st.markdown("##### 📌 主要駅からクイック検索")
quick_cols = st.columns(6)
quick_stations = ["横浜", "新横浜", "桜木町", "戸塚", "日吉", "湘南台"]
for idx, st_name in enumerate(quick_stations):
    with quick_cols[idx]:
        if st.button(f"🚉 {st_name}", key=f"btn_{st_name}", use_container_width=True):
            # ボタンを押したらselectboxの状態を擬似的に上書きするためのトリガー（再レンダリング）
            target_st = st_name

st.markdown("---")

# --- データフィルター処理 ---
filtered_spots = df_spots[df_spots["station"] == target_st].copy()

if selected_categories:
    filtered_spots = filtered_spots[filtered_spots["category"].isin(selected_categories)]
else:
    filtered_spots = pd.DataFrame(columns=df_spots.columns)

if keyword:
    filtered_spots = filtered_spots[filtered_spots["name"].str.contains(keyword, case=False, na=False) | filtered_spots["desc"].str.contains(keyword, case=False, na=False)]
if wifi_only:
    filtered_spots = filtered_spots[filtered_spots["wifi"]]
if power_only:
    filtered_spots = filtered_spots[filtered_spots["power"]]


# 大手サイトの手法②：[左側：地図（固定）] × [右側：スクロール付き詳細リスト] の黄金比
col1, col2 = st.columns([1.1, 1.0], gap="large")

with col1:
    st.subheader("🗺️ エリアマップ")
    
    center_lat, center_lon = STATION_COORDS[target_st]
    m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # 中心駅のピン
    folium.Marker(
        [center_lat, center_lon],
        popup=f"<b>{target_st}駅</b>",
        tooltip=f"🚉 {target_st}駅",
        icon=folium.Icon(color="red", icon="subway", prefix="fa"),
    ).add_to(m)

    if not filtered_spots.empty:
        cluster = MarkerCluster().add_to(m)
        bounds = [[center_lat, center_lon]]
        for _, spot in filtered_spots.iterrows():
            popup_html = (
                f"<div style='font-family: sans-serif; font-size: 13px; line-height: 1.5;'>"
                f"<strong style='color:#1e3a8a; font-size:14px;'>{spot['name']}</strong><br>"
                f"<span style='background:#f3f4f6; padding:2px 5px; border-radius:3px; font-size:11px;'>{spot['category']}</span><br>"
                f"🚶 {spot['access']}<br>"
                f"📝 {spot['desc']}"
                f"</div>"
            )
            folium.Marker(
                [spot["lat"], spot["lon"]],
                popup=folium.Popup(popup_html, max_width=280),
                tooltip=spot["name"],
                icon=get_icon(spot["category"]),
            ).add_to(cluster)
            bounds.append([spot["lat"], spot["lon"]])
        m.fit_bounds(bounds, padding=(40, 40))

    # 地図のレンダリング
    st_folium(m, width="100%", height=550, key=f"map_{target_st}")

with col2:
    st.subheader(f"📌 {target_st}駅周辺の検索結果 ({len(filtered_spots)}件)")

    # 大手サイトの手法③：固定高コンテナによる「無限スクロール化の防止」
    with st.container(height=550):
        if not filtered_spots.empty:
            for _, spot in filtered_spots.iterrows():
                
                # 大手サイトの手法④：設備状況のカラーバッジ（HTML/CSS）化
                wifi_badge = '<span style="background-color:#e0f2fe; color:#0369a1; padding:3px 8px; border-radius:4px; font-size:11px; font-weight:bold; margin-right:6px;">🛜 Wi-Fiあり</span>' if spot['wifi'] else '<span style="background-color:#f3f4f6; color:#9ca3af; padding:3px 8px; border-radius:4px; font-size:11px; margin-right:6px;">🛜 なし</span>'
                power_badge = '<span style="background-color:#fef3c7; color:#b45309; padding:3px 8px; border-radius:4px; font-size:11px; font-weight:bold; margin-right:6px;">🔌 電源あり</span>' if spot['power'] else '<span style="background-color:#f3f4f6; color:#9ca3af; padding:3px 8px; border-radius:4px; font-size:11px; margin-right:6px;">🔌 なし</span>'
                
                # カテゴリに応じた左端アクセントカラーの出し分け（地図ピンのカラーと脳内で同期させる）
                border_color = "#2563eb" if spot['category'] == "図書館" else "#f97316"
                bg_color = "#eff6ff" if spot['category'] == "図書館" else "#fff7ed"
                text_color = "#1e40af" if spot['category'] == "図書館" else "#c2410c"

                # 大手サイトの手法⑤：無駄なカラーメッセージを廃止した「クリーンな構造化カード型UI」
                card_html = f"""
                <div style="border: 1px solid #e5e7eb; border-left: 6px solid {border_color}; padding: 16px; border-radius: 8px; margin-bottom: 14px; background-color: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="background-color: {bg_color}; color: {text_color}; font-size: 11px; font-weight: bold; padding: 2px 8px; border-radius: 12px;">{spot['category']}</span>
                        <span style="font-size: 12px; color: #6b7280;">🚶 {spot['access']}</span>
                    </div>
                    <h4 style="margin: 0 0 10px 0; color: #111827; font-size: 16px; font-weight: bold;">{spot['name']}</h4>
                    <div style="margin-bottom: 12px;">
                        {wifi_badge}
                        {power_badge}
                    </div>
                    <div style="font-size: 13px; color: #374151; background-color: #f9fafb; padding: 10px; border-radius: 6px; border: 1px solid #f3f4f6; line-height: 1.4;">
                        {spot['desc']}
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.warning(f"現在、{target_st}駅の条件に合う勉強スポットは登録されていません。条件を緩めてみてください。")
            available_stations = df_spots["station"].unique().tolist()
            if available_stations:
                st.caption("💡 以下の駅には現在データが登録されています：\n" + "、".join(available_stations))
