import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# =========================================================
# ページ全体の基本設定
# =========================================================
st.set_page_config(
    page_title="駅勉ガイド 横浜広域版",
    page_icon="📖",
    layout="wide",
)

# =========================================================
# 駅の座標データ（各図書館の最寄り駅を完全網羅）
# =========================================================
STATION_COORDS = {
    # ターミナル・主要駅
    "横浜":     (35.4657, 139.6223),
    "戸塚":     (35.4008, 139.5341),
    "東戸塚":   (35.4181, 139.5474),
    "保土ケ谷": (35.4468, 139.5936),
    "大船":     (35.3555, 139.5307),
    "鶴見":     (35.5074, 139.6762),
    "新横浜":   (35.5074, 139.6175),
    "長津田":   (35.5315, 139.4951),
    "二俣川":   (35.4624, 139.5323),
    "上大岡":   (35.4088, 139.5964),
    "金沢文庫": (35.3424, 139.6217),
    "日吉":     (35.5533, 139.6469),
    "菊名":     (35.5097, 139.6310),
    "センター北": (35.5536, 139.5781),
    "センター南": (35.5444, 139.5730),
    "中山":     (35.5146, 139.5394),
    "港南中央": (35.4004, 139.5950),
    "みなとみらい": (35.4578, 139.6326),
    "元町・中華街": (35.4421, 139.6521),
    
    # 【新規追加】各図書館のピンポイントな最寄り駅
    "桜木町":   (35.4503, 139.6313),  # 県立図書館の最寄り
    "日ノ出町": (35.4433, 139.6267),  # 中央図書館の最寄り
    "山手":     (35.4269, 139.6466),  # 中図書館の最寄り
    "東神奈川": (35.4778, 139.6322),  # 神奈川図書館の最寄り
    "星川":     (35.4568, 139.6000),  # 保土ケ谷図書館の最寄り
}
STATIONS = sorted(list(STATION_COORDS.keys()))

# =========================================================
# 勉強スポットのデータベース
# =========================================================
SPOTS_DATA = [
    # --- 西区・中区エリア ---
    {
        "name": "神奈川県立図書館",
        "station": "桜木町",
        "lat": 35.4542,
        "lon": 139.6275,
        "category": "図書館",
        "wifi": True,
        "power": True,
        "access": "桜木町駅 徒歩10分 / 横浜駅 徒歩20分",
        "desc": "【電源最強】全席コンセント完備。新館は非常に綺麗で集中できる学習環境が整っています。",
    },
    {
        "name": "横浜市中央図書館",
        "station": "日ノ出町",
        "lat": 35.4442,
        "lon": 139.6267,
        "category": "図書館",
        "wifi": True,
        "power": True,
        "access": "日ノ出町駅 徒歩3分 / 桜木町駅 徒歩10分",
        "desc": "【圧倒的な規模】地下1階から5階まで閲覧席が多数ある横浜最大の図書館。一部座席で調査用のPC・電源利用が可能です。",
    },
    {
        "name": "横浜市中図書館",
        "station": "山手",
        "lat": 35.4385,
        "lon": 139.6540,
        "category": "図書館",
        "wifi": False,
        "power": False,
        "access": "山手駅 徒歩15分 / 元町・中華街駅から市営バス「千代崎町」下車徒歩2分",
        "desc": "本牧エリアの落ち着いた環境にある図書館。読書や調べものに適しています。",
    },
    # --- 戸塚区・港南区エリア ---
    {
        "name": "横浜市戸塚図書館",
        "station": "戸塚",
        "lat": 35.4001,
        "lon": 139.5332,
        "category": "図書館",
        "wifi": False,
        "power": False,
        "access": "戸塚駅西口 徒歩4分",
        "desc": "【駅チカ】戸塚センター内にありアクセス抜群。座席数は限られますが、学校帰りや仕事帰りに寄りやすい定番スポットです。",
    },
    {
        "name": "横浜市港南図書館",
        "station": "港南中央",
        "lat": 35.3970,
        "lon": 139.5935,
        "category": "図書館",
        "wifi": False,
        "power": False,
        "access": "港南中央駅 徒歩5分 / 上大岡駅 徒歩12分",
        "desc": "鎌倉街道から少し入った、行政機関が集まるエリアにある図書館。自習や調べものに利用できます。",
    },
    # --- 北部エリア（港北・都筑） ---
    {
        "name": "横浜市港北図書館",
        "station": "菊名",
        "lat": 35.5118,
        "lon": 139.6293,
        "category": "図書館",
        "wifi": False,
        "power": False,
        "access": "菊名駅東口 徒歩7分",
        "desc": "新横浜からもアクセスしやすい菊名にある図書館。地域住民や学生の自習に広く使われています。",
    },
    {
        "name": "横浜市都筑図書館",
        "station": "センター南",
        "lat": 35.5451,
        "lon": 139.5732,
        "category": "図書館",
        "wifi": False,
        "power": False,
        "access": "センター南駅 徒歩6分",
        "desc": "都筑区総合庁舎内にある図書館。非常に広々としており、港北ニュータウン中心部の快適な空間です。",
    },
    # --- 鶴見・東神奈川エリア ---
    {
        "name": "横浜市鶴見図書館",
        "station": "鶴見",
        "lat": 35.5090,
        "lon": 139.6732,
        "category": "図書館",
        "wifi": False,
        "power": False,
        "access": "鶴見駅西口・京急鶴見駅 徒歩7分",
        "desc": "鶴見区民の学習を支える中央に位置する図書館。座席での閲覧・調査が可能です。",
    },
    {
        "name": "横浜市神奈川図書館",
        "station": "東神奈川",
        "lat": 35.4776,
        "lon": 139.6289,
        "category": "図書館",
        "wifi": False,
        "power": False,
        "access": "東神奈川駅・京急東神奈川駅 徒歩10分",
        "desc": "神奈川公園の近くにある静かな環境の図書館。集中して作業をしたい際におすすめです。",
    },
    # --- 相鉄沿線エリア ---
    {
        "name": "横浜市保土ケ谷図書館",
        "station": "星川",
        "lat": 35.4528,
        "lon": 139.5982,
        "category": "図書館",
        "wifi": False,
        "power": False,
        "access": "星川駅 徒歩6分 / 保土ケ谷駅からバスあり",
        "desc": "保土ケ谷公園の近くに位置する図書館。緑豊かな落ち着いた環境で読書や調べものができます。",
    },
    {
        "name": "横浜市旭図書館",
        "station": "二俣川",
        "lat": 35.4665,
        "lon": 139.5240,
        "category": "図書館",
        "wifi": False,
        "power": False,
        "access": "二俣川駅北口 徒歩11分",
        "desc": "相鉄線の主要駅である二俣川から徒歩圏内にある図書館。学生の利用も多い活気ある学習スポットです。",
    },
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
# サイドバー：検索・絞り込み条件
# =========================================================
st.sidebar.header("🔍 絞り込み条件")

target_st = st.sidebar.selectbox(
    "調べたい駅を選んでください",
    STATIONS,
    index=STATIONS.index("横浜"),
)

keyword = st.sidebar.text_input("スポット名で検索（任意）", placeholder="例：中央図書館")

wifi_only = st.sidebar.checkbox("Wi-Fiありのみ表示")
power_only = st.sidebar.checkbox("電源ありのみ表示")

st.sidebar.markdown("---")
st.sidebar.caption(f"登録スポット数：全{len(df_spots)}件（{len(STATIONS)}駅中）")

# =========================================================
# メイン画面
# =========================================================
st.title("📖 駅勉ガイド 横浜広域版")
st.write("各社の乗り換え駅やローカルな最寄り駅に対応！定期券の範囲に合わせてピンポイントで探せます。")
st.markdown("---")

# --- フィルター処理 ---
filtered_spots = df_spots[df_spots["station"] == target_st].copy()

if keyword:
    filtered_spots = filtered_spots[filtered_spots["name"].str.contains(keyword, case=False, na=False)]
if wifi_only:
    filtered_spots = filtered_spots[filtered_spots["wifi"]]
if power_only:
    filtered_spots = filtered_spots[filtered_spots["power"]]

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ スポット地図")

    center_lat, center_lon = STATION_COORDS[target_st]
    m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    folium.Marker(
        [center_lat, center_lon],
        popup=f"{target_st}駅",
        tooltip=f"🚉 {target_st}駅",
        icon=folium.Icon(color="gray", icon="train", prefix="fa"),
    ).add_to(m)

    if not filtered_spots.empty:
        cluster = MarkerCluster().add_to(m)
        bounds = [[center_lat, center_lon]]
        for _, spot in filtered_spots.iterrows():
            popup_html = (
                f"<b>{spot['name']}</b><br>"
                f"{spot['desc']}<br>"
                f"アクセス：{spot['access']}"
            )
            folium.Marker(
                [spot["lat"], spot["lon"]],
                popup=folium.Popup(popup_html, max_width=280),
                tooltip=spot["name"],
                icon=get_icon(spot["category"]),
            ).add_to(cluster)
            bounds.append([spot["lat"], spot["lon"]])
        m.fit_bounds(bounds, padding=(30, 30))

    st_folium(m, width=700, height=480, key=f"map_{target_st}")

with col2:
    st.subheader("📌 スポット詳細")

    if not filtered_spots.empty:
        for _, spot in filtered_spots.iterrows():
            st.success(f"### 📍 {spot['name']}")
            st.write(f"**カテゴリ：** {spot['category']}")
            st.write(f"**アクセス：** {spot['access']}")
            st.write(
                f"**設備：** "
                f"{'✅ Wi-Fiあり' if spot['wifi'] else '❌ Wi-Fiなし'} / "
                f"{'✅ 電源あり' if spot['power'] else '❌ 電源なし'}"
            )
            st.info(spot["desc"])
    else:
        st.warning(
            f"現在、{target_st}駅の条件に合う勉強スポットは登録されていません。\n\n"
            "今後のアップデートをお待ちください。"
        )
        available_stations = df_spots["station"].unique().tolist()
        if available_stations:
            st.caption("📢 現在データがあるのは次の駅です：" + "、".join(available_stations))
