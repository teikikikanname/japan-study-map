import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# =========================================================
# ページ全体の基本設定（落ち着いたトーンの学術的・実用的なサイト設計）
# =========================================================
st.set_page_config(
    page_title="駅勉ガイド 横浜広域版 | 沿線・駅別学習スポット検索",
    page_icon="📖",
    layout="wide",
)

# 【デザインの脱・AI化】
# グラデーションや派手なカードを全廃し、日本の伝統的なリンク集・データベースサイトの「紺・墨黒・薄灰」を採用。
# フォントもすっきりとしたゴシック体系で統一し、情報の密度（テキストの読みやすさ）を最優先。
st.markdown("""
    <style>
    /* 全体のトーン調整 */
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; background-color: #fafafa; }
    h1, h2, h3 { color: #0f172a; font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", sans-serif; }
    
    /* 東京図書館風のすっきりとしたテキストリンク・テーブル風デザイン */
    .spot-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; background-color: #ffffff; }
    .spot-table th { background-color: #1e3a8a; color: white; padding: 10px; font-size: 13px; text-align: left; font-weight: bold; }
    .spot-table td { padding: 12px 10px; border-bottom: 1px solid #e2e8f0; font-size: 13px; color: #334155; vertical-align: top; }
    .spot-table tr:hover { background-color: #f8fafc; }
    
    /* 路線別グループの見出し */
    .line-header { background-color: #f1f5f9; padding: 6px 12px; border-left: 4px solid #1e3a8a; font-weight: bold; font-size: 14px; color: #1e293b; margin-top: 15px; margin-bottom: 5px; }
    
    /* 小さく上品な設備テキスト（アイコンや派手な色は使わない） */
    .tag-text { font-size: 11px; font-weight: bold; color: #475569; background-color: #f1f5f9; padding: 2px 6px; border-radius: 2px; margin-right: 4px; border: 1px solid #cbd5e1; }
    .tag-text-active { font-size: 11px; font-weight: bold; color: #1e3a8a; background-color: #eff6ff; padding: 2px 6px; border-radius: 2px; margin-right: 4px; border: 1px solid #bfdbfe; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 駅の座標・沿線データ（東京図書館サイトに倣い、路線情報を追加）
# =========================================================
STATION_DATA = {
    "横浜": {"coords": (35.4657, 139.6223), "lines": ["JR東海道線", "JR根岸線", "東急東横線", "相鉄本線", "京急本線", "横浜市営地下鉄ブルーライン"]},
    "新横浜": {"coords": (35.5074, 139.6175), "lines": ["JR横浜線", "東海道新幹線", "相鉄・東急直通線", "横浜市営地下鉄ブルーライン"]},
    "戸塚": {"coords": (35.4008, 139.5341), "lines": ["JR東海道線", "JR横須賀線", "横浜市営地下鉄ブルーライン"]},
    "桜木町": {"coords": (35.4503, 139.6313), "lines": ["JR根岸線", "横浜市営地下鉄ブルーライン"]},
    "日ノ出町": {"coords": (35.4433, 139.6267), "lines": ["京急本線"]},
    "山手": {"coords": (35.4269, 139.6466), "lines": ["JR根岸線"]},
    "菊名": {"coords": (35.5097, 139.6310), "lines": ["JR横浜線", "東急東横線"]},
    "センター南": {"coords": (35.5444, 139.5730), "lines": ["横浜市営地下鉄ブルーライン", "横浜市営地下鉄グリーンライン"]},
    "鶴見": {"coords": (35.5074, 139.6762), "lines": ["JR京浜東北線", "JR鶴見線"]},
    "東神奈川": {"coords": (35.4778, 139.6322), "lines": ["JR京浜東北線", "JR横浜線"]},
    "星川": {"coords": (35.4568, 139.6000), "lines": ["相鉄本線"]},
    "二俣川": {"coords": (35.4624, 139.5323), "lines": ["相鉄本線", "相鉄いずみ野線"]},
    "新杉田": {"coords": (35.3868, 139.6198), "lines": ["JR根岸線", "金沢シーサイドライン"]},
    "金沢文庫": {"coords": (35.3424, 139.6217), "lines": ["京急本線"]},
    "港南台": {"coords": (35.3752, 139.5668), "lines": ["JR根岸線"]},
    "綱島": {"coords": (35.5365, 139.6342), "lines": ["東急東横線"]},
    "白楽": {"coords": (35.4904, 139.6268), "lines": ["東急東横線"]},
    "いずみ野": {"coords": (35.4187, 139.4952), "lines": ["相鉄いずみ野線"]},
    "弘明寺(京急)": {"coords": (35.4243, 139.5982), "lines": ["京急本線"]},
    "弘明寺(地下鉄)": {"coords": (35.4241, 139.6074), "lines": ["横浜市営地下鉄ブルーライン"]},
    "井土ヶ谷": {"coords": (35.4338, 139.5989), "lines": ["京急本線"]},
    "杉田": {"coords": (35.3811, 139.6201), "lines": ["京急本線"]},
    "金沢八景": {"coords": (35.3269, 139.6208), "lines": ["京急本線", "金沢シーサイドライン"]},
    "湘南台": {"coords": (35.3963, 139.4665), "lines": ["小田急江ノ島線", "相鉄いずみ野線", "横浜市営地下鉄ブルーライン"]},
}

# 全路線リストの抽出
ALL_LINES = sorted(list(set([line for st_info in STATION_DATA.values() for line in st_info["lines"]])))

# =========================================================
# 勉強スポットデータベース（座席数、ルール、路線の要素を強化）
# =========================================================
SPOTS_DATA = [
    {"name": "神奈川県立図書館", "station": "桜木町", "line": "JR根岸線", "lat": 35.4542, "lon": 139.6275, "category": "図書館", "wifi": True, "power": True, "seats": "約300席", "rule": "PC・電卓使用全席可（サイレントエリア除く）", "access": "桜木町駅 徒歩10分", "desc": "新館は全席コンセント完備。予約システムがあり確実。非常に綺麗で静寂。"},
    {"name": "横浜市中央図書館", "station": "日ノ出町", "line": "京急本線", "lat": 35.4442, "lon": 139.6267, "category": "図書館", "wifi": True, "power": True, "seats": "約400席", "rule": "PC利用は4階・5階の指定席のみ", "access": "日ノ出町駅 徒歩3分", "desc": "地下1階から5階まで閲覧席多数。自習用の席は午前中で埋まることが多い。"},
    {"name": "横浜市中図書館", "station": "山手", "line": "JR根岸線", "lat": 35.4385, "lon": 139.6540, "category": "図書館", "wifi": False, "power": False, "seats": "約60席", "rule": "電卓不可・PC持ち込み不可", "access": "山手駅 徒歩15分", "desc": "本牧エリアの落ち着いた環境にある地域図書館。読書や静かなノート学習向け。"},
    {"name": "横浜市戸塚図書館", "station": "戸塚", "line": "JR東海道線", "lat": 35.4001, "lon": 139.5332, "category": "図書館", "wifi": False, "power": False, "seats": "約80席", "rule": "学生用自習席あり（入れ替え制）", "access": "戸塚駅西口 徒歩4分", "desc": "駅チカで便利。休日は朝から整理券が配布されることがある定番スポット。"},
    {"name": "横浜市港北図書館", "station": "菊名", "line": "東急東横線", "lat": 35.5118, "lon": 139.6293, "category": "図書館", "wifi": False, "power": False, "seats": "約70席", "rule": "PC使用不可", "access": "菊名駅東口 徒歩7分", "desc": "地域住民や高校生の利用が多い。レトロで静かな空間。"},
    {"name": "横浜市都筑図書館", "station": "センター南", "line": "横浜市営地下鉄ブルーライン", "lat": 35.5451, "lon": 139.5732, "category": "図書館", "wifi": False, "power": False, "seats": "約120席", "rule": "一部PC優先席あり（電源なし）", "access": "センター南駅 徒歩6分", "desc": "都筑区総合庁舎内。天井が高く広々としており快適。"},
    {"name": "横浜市鶴見図書館", "station": "鶴見", "line": "JR京浜東北線", "lat": 35.5090, "lon": 139.6732, "category": "図書館", "wifi": False, "power": False, "seats": "約90席", "rule": "持込PC専用席あり", "access": "鶴見駅西口 徒歩7分", "desc": "鶴見区民の学習を支える拠点。学習室の席数は多め。"},
    {"name": "横浜市神奈川図書館", "station": "東神奈川", "line": "JR京浜東北線", "lat": 35.4776, "lon": 139.6289, "category": "図書館", "wifi": False, "power": False, "seats": "約50席", "rule": "自習専用席なし（一般閲覧席のみ）", "access": "東神奈川駅 徒歩10分", "desc": "神奈川公園近くの静かな環境。平日の昼間が穴場。"},
    {"name": "横浜市保土ケ谷図書館", "station": "星川", "line": "相鉄本線", "lat": 35.4528, "lon": 139.5982, "category": "図書館", "wifi": False, "power": False, "seats": "約65席", "rule": "読書・調査目的優先", "access": "星川駅 徒歩6分", "desc": "緑豊かな落ち着いた環境で、集中して本を読んだり調べ物学習ができる。"},
    {"name": "横浜市旭図書館", "station": "二俣川", "line": "相鉄本線", "lat": 35.4665, "lon": 139.5240, "category": "図書館", "wifi": False, "power": False, "seats": "約75席", "rule": "学生専用席あり（期間限定）", "access": "二俣川駅北口 徒歩11分", "desc": "相鉄沿線の主要な学習スポット。テスト期間は大変混雑する。"},
    {"name": "スターバックス 横浜西口店", "station": "横浜", "line": "JR東海道線", "lat": 35.4645, "lon": 139.6210, "category": "カフェ", "wifi": True, "power": True, "seats": "約90席", "rule": "混雑時90分制", "access": "横浜駅西口 徒歩3分", "desc": "大テーブル席にコンセントあり。常に適度な雑音があり、作業が捗る。"},
    {"name": "タリーズコーヒー NEWoMan横浜店", "station": "横浜", "line": "東急東横線", "lat": 35.4661, "lon": 139.6225, "category": "カフェ", "wifi": True, "power": True, "seats": "約50席", "rule": "長時間の席占有制限あり", "access": "横浜駅直結", "desc": "駅直結の高級感ある店舗。窓側カウンターに電源あり。PCワーク向け。"},
    {"name": "タリーズコーヒー 綱島駅前店", "station": "綱島", "line": "東急東横線", "lat": 35.5368, "lon": 139.6342, "category": "カフェ", "wifi": True, "power": True, "seats": "約45席", "rule": "特になし", "access": "綱島駅東口 徒歩1分", "desc": "仕切り付きカウンター席にコンセント完備。一人客が多く静か。"},
    {"name": "ガスト 弘明寺店", "station": "弘明寺(地下鉄)", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4245, "lon": 139.6080, "category": "カフェ", "wifi": True, "power": True, "seats": "約80席", "rule": "深夜利用可 / 混雑時制限あり", "access": "地下鉄弘明寺駅 徒歩2分", "desc": "すかいらーくWi-Fiとコンセント完備。席が広く、参考書を何冊も広げやすい。"},
    {"name": "プロント 湘南台店", "station": "湘南台", "line": "小田急江ノ島線", "lat": 35.3965, "lon": 139.4668, "category": "カフェ", "wifi": True, "power": True, "seats": "約60席", "rule": "カウンター席のみ電源利用可", "access": "湘南台駅西口 徒歩1分", "desc": "一人用カウンター席が充実しており、PC作業や自習、仕事帰りの資格勉強に最適。"}
]

df_spots = pd.DataFrame(SPOTS_DATA)

# =========================================================
# ナビゲーション・検索ヘッダー（無駄な余白を省いた高密度設計）
# =========================================================
st.markdown("<h2 style='margin-bottom:0px;'>📖 横浜広域 沿線・駅別学習スポットデータベース</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-size:12px; color:#64748b;'>通勤・通学定期券のルートから探せる、実用本位の図書館・学習スペース一覧リンク集です。</p>", unsafe_allow_html=True)
st.markdown("---")

# 東京図書館風：上部にスッキリ並ぶ検索条件ラジオ・チェック
col_f1, col_f2, col_f3 = st.columns([1.5, 1, 1.5])

with col_f1:
    search_mode = st.radio("【検索軸の選択】", ["鉄道路線から探す（沿線指定）", "特定の駅から探す（ピンポイント）"], horizontal=True)

with col_f2:
    selected_cats = st.multiselect("施設種別", ["図書館", "カフェ"], default=["図書館", "カフェ"], label_visibility="collapsed")

with col_f3:
    st.write("【絞り込み条件】")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        wifi_req = st.checkbox("🛜 公衆Wi-Fi必須")
    with c_col2:
        power_req = st.checkbox("🔌 コンセント必須")

# 検索軸に応じたセレクトボックスの切り替え
if "鉄道路線" in search_mode:
    chosen_line = st.selectbox("路線を選択してください", ALL_LINES, index=ALL_LINES.index("JR根岸線"))
    # 選択された路線が通る駅をリストアップ
    target_stations = [st_name for st_name, info in STATION_DATA.items() if chosen_line in info["lines"]]
    display_title = f"■ {chosen_line} 沿線の学習スポット一覧"
else:
    chosen_station = st.selectbox("駅を選択してください", sorted(list(STATION_DATA.keys())), index=sorted(list(STATION_DATA.keys())).index("横浜"))
    target_stations = [chosen_station]
    display_title = f"■ {chosen_station} 駅周辺の学習スポット一覧"

st.markdown("---")

# =========================================================
# メインコンテンツ：[左側：超高密度データテーブル] × [右側：位置確認用マップ]
# =========================================================
col_main, col_map = st.columns([1.8, 1.1], gap="medium")

# データのフィルタリング
filtered_df = df_spots[df_spots["station"].isin(target_stations)].copy()
if selected_cats:
    filtered_df = filtered_df[filtered_df["category"].isin(selected_categories=selected_cats)]
else:
    filtered_df = pd.DataFrame(columns=df_spots.columns)

if wifi_req:
    filtered_df = filtered_df[filtered_df["wifi"]]
if power_req:
    filtered_df = filtered_df[filtered_df["power"]]

with col_main:
    st.markdown(f"<div class='line-header'>{display_title} ({len(filtered_df)}件該当)</div>", unsafe_allow_html=True)
    
    if not filtered_df.empty:
        # 東京図書館の美学である「高密度な生HTMLテーブル」を出力
        table_html = """
        <table class='spot-table'>
            <thead>
                <tr>
                    <th style='width: 15%;'>最寄り駅</th>
                    <th style='width: 30%;'>施設名 / 設備状況</th>
                    <th style='width: 20%;'>座席数 / 利用ルール</th>
                    <th style='width: 35%;'>特徴・詳細解説</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for _, row in filtered_df.iterrows():
            # 設備のテキストバッジ風（派手な色ではなく、システムライクな色合い）
            w_tag = "<span class='tag-text-active'>🛜 Wi-Fi</span>" if row['wifi'] else "<span class='tag-text'>🛜 なし</span>"
            p_tag = "<span class='tag-text-active'>🔌 電源</span>" if row['power'] else "<span class='tag-text'>🔌 なし</span>"
            
            table_html += f"""
                <tr>
                    <td>
                        <b>{row['station']}駅</b><br>
                        <span style='font-size:11px; color:#64748b;'>{row['access']}</span>
                    </td>
                    <td>
                        <strong style='font-size:14px; color:#1e3a8a;'>{row['name']}</strong><br>
                        <span style='font-size:11px; color:#475569; background:#e2e8f0; padding:1px 4px; border-radius:2px; margin-right:5px;'>{row['category']}</span>
                        <div style='margin-top:6px;'>{w_tag}{p_tag}</div>
                    </td>
                    <td>
                        <span style='color:#0f172a; font-weight:bold;'>{row['seats']}</span><br>
                        <span style='font-size:11px; color:#dc2626;'>⚠ {row['rule']}</span>
                    </td>
                    <td>
                        <div style='font-weight:500; color:#1e293b; margin-bottom:4px;'>{row['desc']}</div>
                    </td>
                </tr>
            """
        
        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.warning("選択された条件に合致するスポットは現在登録されていません。条件を緩めてみてください。")

with col_map:
    st.markdown("<div style='font-size:13px; font-weight:bold; color:#1e293b; margin-bottom:5px;'>🌐 周辺マップ（位置確認用）</div>", unsafe_allow_html=True)
    
    # 選択された条件の基準となる座標を計算
    if "鉄道路線" in search_mode and target_stations:
        # 路線内の最初の駅の座標をマップの中心にする
        ref_station = target_stations[0]
    else:
        ref_station = chosen_station if 'chosen_station' in locals() else "横浜"
        
    center_lat, center_lon = STATION_DATA[ref_station]["coords"]
    
    # マップのデザインもAI風のカラフルなものを避け、標準的で硬派なスタイルに
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="OpenStreetMap")

    # 該当するすべてのスポットにピンを打つ
    if not filtered_df.empty:
        for _, spot in filtered_df.iterrows():
            # 図書館はネイビー、カフェはグレーなど、落ち着いたビジネスカラーで統一
            pin_color = "blue" if spot['category'] == "図書館" else "cadetblue"
            
            popup_html = f"""
            <div style='font-family:sans-serif; font-size:12px; line-height:1.4; width:200px;'>
                <strong>{spot['name']}</strong> ({spot['seats']})<br>
                <span style='color:#64748b;'>{spot['access']}</span>
            </div>
            """
            folium.Marker(
                [spot["lat"], spot["lon"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=spot["name"],
                icon=folium.Icon(color=pin_color, icon="info-sign")
            ).add_to(m)
            
    st_folium(m, width="100%", height=500, key=f"map_view_{ref_station}")

# =========================================================
# フッター（個人開発データベースとしての信頼感を醸成）
# =========================================================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; font-size: 11px; color: #94a3b8; padding-top: 10px;'>
        駅勉ガイド 横浜広域版 | 当サイトは個人の学習・作業スペース巡りの記録および公開データを基にしたデータベースです。<br>
        掲載されている情報は変更されている可能性があります。最新の利用ルールや開館時間は各施設の公式サイトを直接ご確認ください。
    </div>
""", unsafe_allow_html=True)
