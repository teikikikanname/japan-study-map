import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# =========================================================
# ページ全体の基本設定
# =========================================================
st.set_page_config(
    page_title="駅勉ガイド 神奈川版",
    page_icon="📖",
    layout="wide",
)

# ---------------------------------------------------------
# Google Search Console 確認について（重要）
# ---------------------------------------------------------
# Streamlitはブラウザ上でSPAとして描画されるため、
# st.markdownで挿入したmetaタグは実際の<head>内には入りません。
# そのため、この方式でのサイト確認は失敗しやすいです。
# 代わりに「Search Console > 所有権の確認 > ドメイン」から
# DNS TXTレコードで確認する方法を強く推奨します。
# （フレームワークに依存せず確実に通ります）
#
# どうしてもHTMLタグ方式を使う場合は、Streamlit Cloud側の
# 制約で<head>を直接編集できないため、Nginx等でリバースプロキシ
# を挟んで独自にHTMLを配信する必要があります。

# =========================================================
# 駅の座標データ（湘南新宿ライン沿線・概算値）
# スポットが未登録の駅でも、地図を駅位置にズームできるようにする
# =========================================================
STATION_COORDS = {
    "大宮":     (35.9068, 139.6380),
    "浦和":     (35.8617, 139.6455),
    "赤羽":     (35.7772, 139.7207),
    "池袋":     (35.7295, 139.7109),
    "新宿":     (35.6896, 139.7006),
    "渋谷":     (35.6580, 139.7016),
    "恵比寿":   (35.6465, 139.7100),
    "大崎":     (35.6197, 139.7284),
    "西大井":   (35.6015, 139.7268),
    "武蔵小杉": (35.5765, 139.6605),
    "新川崎":   (35.5495, 139.6668),
    "横浜":     (35.4657, 139.6223),
    "保土ケ谷": (35.4468, 139.5936),
    "東戸塚":   (35.4181, 139.5474),
    "戸塚":     (35.4008, 139.5341),
    "大船":     (35.3555, 139.5307),
    "北鎌倉":   (35.3376, 139.5486),
    "鎌倉":     (35.3193, 139.5501),
    "逗子":     (35.2966, 139.5798),
    "藤沢":     (35.3389, 139.4911),
    "辻堂":     (35.3315, 139.4472),
    "茅ヶ崎":   (35.3305, 139.4079),
    "平塚":     (35.3229, 139.3489),
    "大磯":     (35.3084, 139.3128),
    "二宮":     (35.3010, 139.2540),
    "国府津":   (35.2661, 139.2100),
    "鴨宮":     (35.2833, 139.1745),
    "小田原":   (35.2560, 139.1560),
}
STATIONS = list(STATION_COORDS.keys())

# =========================================================
# 勉強スポットのデータベース
# 実運用では将来的にCSVやスプレッドシート、DBに切り出すと管理が楽になります
# =========================================================
SPOTS_DATA = [
    {
        "name": "神奈川県立図書館",
        "station": "横浜",
        "lat": 35.4542,
        "lon": 139.6275,
        "category": "図書館",
        "wifi": True,
        "power": True,
        "access": "徒歩10分",
        "desc": "【電源最強】全席コンセント完備。非常に静かで集中できる環境です。",
    },
    {
        "name": "川崎市立中原図書館",
        "station": "武蔵小杉",
        "lat": 35.5755,
        "lon": 139.6631,
        "category": "図書館",
        "wifi": True,
        "power": True,
        "access": "駅直結",
        "desc": "【アクセス抜群】武蔵小杉駅直結。社会人専用席に電源が完備されています。",
    },
    {
        "name": "小田原市立駅前図書コーナー",
        "station": "小田原",
        "lat": 35.2562,
        "lon": 139.1553,
        "category": "図書館",
        "wifi": True,
        "power": True,
        "access": "徒歩1分",
        "desc": "【地下街直結】ハルネ小田原内。自習スペースに電源があります。",
    },
]


@st.cache_data
def load_spots() -> pd.DataFrame:
    """スポットデータをDataFrame化してキャッシュする。"""
    return pd.DataFrame(SPOTS_DATA)


df_spots = load_spots()

# カテゴリのアイコン対応（folium組み込みアイコン名）
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

keyword = st.sidebar.text_input("スポット名で検索（任意）", placeholder="例：図書館")

wifi_only = st.sidebar.checkbox("Wi-Fiありのみ表示")
power_only = st.sidebar.checkbox("電源ありのみ表示")

st.sidebar.markdown("---")
st.sidebar.caption(f"登録スポット数：全{len(df_spots)}件（{len(STATIONS)}駅中）")

# =========================================================
# メイン画面
# =========================================================
st.title("📖 駅勉ガイド 神奈川版")
st.write("湘南新宿ライン沿線の **電源・Wi-Fi完備** な勉強スポットを地図から簡単に探せます。")
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

    # 選択中の駅そのものにもマーカーを立てて、位置がひと目でわかるようにする
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
        # スポットと駅が両方見えるように地図の表示範囲を自動調整
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
        # データがある近隣駅をヒントとして提示
        available_stations = df_spots["station"].unique().tolist()
        if available_stations:
            st.caption("📢 現在データがあるのは次の駅です：" + "、".join(available_stations))
