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

# 【デザインの洗練・調和化】
st.markdown("""
    <style>
    /* 全体のトーン調整 */
    .main .block-container { padding-top: 2.0rem; padding-bottom: 2.0rem; background-color: #f8fafc; }
    h1, h2, h3 { color: #0f172a; font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", sans-serif; font-weight: 700; }
    
    /* 東京図書館風のすっきりとしたテキストリンク・テーブル風デザイン */
    .spot-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; background-color: #ffffff; border-radius: 4px; overflow: hidden; border: 1px solid #e2e8f0; }
    .spot-table th { background-color: #1e3a8a; color: white; padding: 12px 14px; font-size: 13px; text-align: left; font-weight: 600; letter-spacing: 0.05em; }
    .spot-table td { padding: 14px 14px; border-bottom: 1px solid #e2e8f0; font-size: 13px; color: #334155; vertical-align: top; line-height: 1.5; }
    .spot-table tr:hover { background-color: #f1f5f9; }
    
    /* 路線別グループの見出し */
    .line-header { background-color: #eff6ff; padding: 10px 14px; border-left: 4px solid #1e3a8a; border-right: 1px solid #bfdbfe; border-top: 1px solid #bfdbfe; border-bottom: 1px solid #bfdbfe; font-weight: bold; font-size: 14px; color: #1e3a8a; margin-top: 10px; margin-bottom: 10px; border-radius: 0 4px 4px 0; }
    
    /* 上品で控えめな設備タグ */
    .tag-text { font-size: 11px; font-weight: 600; color: #64748b; background-color: #f1f5f9; padding: 3px 6px; border-radius: 3px; margin-right: 4px; border: 1px solid #cbd5e1; display: inline-block; }
    .tag-text-active { font-size: 11px; font-weight: 600; color: #1e3a8a; background-color: #e0f2fe; padding: 3px 6px; border-radius: 3px; margin-right: 4px; border: 1px solid #bae6fd; display: inline-block; }
    
    /* 注意書きのトーンを少しシックに */
    .rule-alert { font-size: 11px; color: #b91c1c; font-weight: 500; background-color: #fef2f2; padding: 2px 6px; border-radius: 3px; border: 1px solid #fee2e2; display: inline-block; margin-top: 4px; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 駅の座標・沿線データ（全72駅完全対応版）
# =========================================================
STATION_DATA = {
    "横浜": {"coords": (35.4657, 139.6223), "lines": ["JR東海道線", "JR根岸線", "東急東横線", "相鉄本線", "京急本線", "横浜市営地下鉄ブルーライン"]},
    "新横浜": {"coords": (35.5074, 139.6175), "lines": ["JR横浜線", "東海道新幹線", "相鉄・東急直通線", "横浜市営地下鉄ブルーライン"]},
    "戸塚": {"coords": (35.4008, 139.5341), "lines": ["JR東海道線", "JR横須賀線", "横浜市営地下鉄ブルーライン"]},
    "東戸塚": {"coords": (35.4181, 139.5474), "lines": ["JR横須賀線"]}, # 簡体字タイポを修正
    "保土ケ谷": {"coords": (35.4468, 139.5936), "lines": ["JR横須賀線"]},
    "大船": {"coords": (35.3555, 139.5307), "lines": ["JR東海道線", "JR横須賀線", "JR根岸線", "湘南モノレール"]},
    "桜木町": {"coords": (35.4503, 139.6313), "lines": ["JR根岸線", "横浜市営地下鉄ブルーライン"]},
    "日ノ出町": {"coords": (35.4433, 139.6267), "lines": ["京急本線"]},
    "山手": {"coords": (35.4269, 139.6466), "lines": ["JR根岸線"]},
    "菊名": {"coords": (35.5097, 139.6310), "lines": ["JR横浜線", "東急東横線"]},
    "センター北": {"coords": (35.5536, 139.5781), "lines": ["横浜市営地下鉄ブルーライン", "横浜市営地下鉄グリーンライン"]},
    "センター南": {"coords": (35.5444, 139.5730), "lines": ["横浜市営地下鉄ブルーライン", "横浜市営地下鉄グリーンライン"]},
    "中山": {"coords": (35.5146, 139.5394), "lines": ["JR横浜線", "横浜市営地下鉄グリーンライン"]},
    "港南中央": {"coords": (35.4004, 139.5950), "lines": ["横浜市営地下鉄ブルーライン"]},
    "みなとみらい": {"coords": (35.4578, 139.6326), "lines": ["みなとみらい線"]},
    "元町・中華街": {"coords": (35.4421, 139.6521), "lines": ["みなとみらい線"]},
    "鶴見": {"coords": (35.5074, 139.6762), "lines": ["JR京浜東北線", "JR鶴見線"]},
    "東神奈川": {"coords": (35.4778, 139.6322), "lines": ["JR京浜東北線", "JR横浜線"]},
    "星川": {"coords": (35.4568, 139.6000), "lines": ["相鉄本線"]},
    "二俣川": {"coords": (35.4624, 139.5323), "lines": ["相鉄本線", "相鉄いずみ野線"]},
    "新杉田": {"coords": (35.3868, 139.6198), "lines": ["JR根岸線", "金沢シーサイドライン"]},
    "金沢文庫": {"coords": (35.3424, 139.6217), "lines": ["京急本線"]},
    "港南台": {"coords": (35.3752, 139.5668), "lines": ["JR根岸線"]},
    "馬車道": {"coords": (35.4491, 139.6361), "lines": ["みなとみらい線"]},
    "関内": {"coords": (35.4442, 139.6364), "lines": ["JR根岸線", "横浜市営地下鉄ブルーライン"]},
    "日本大通り": {"coords": (35.4475, 139.6425), "lines": ["みなとみらい線"]},
    "あざみ野": {"coords": (35.5687, 139.5535), "lines": ["東急田園都市線", "横浜市営地下鉄ブルーライン"]},
    "西横浜": {"coords": (35.4542, 139.6105), "lines": ["相鉄本線"]},
    "天王町": {"coords": (35.4554, 139.6049), "lines": ["相鉄本線"]},
    "平沼橋": {"coords": (35.4616, 139.6159), "lines": ["相鉄本線"]},
    "三ツ境": {"coords": (35.4682, 139.5034), "lines": ["相鉄本線"]},
    "瀬谷": {"coords": (35.4705, 139.4795), "lines": ["相鉄本線"]},
    "緑園都市": {"coords": (35.4382, 139.5242), "lines": ["相鉄いずみ野線"]},
    "弥生台": {"coords": (35.4293, 139.5101), "lines": ["相鉄いずみ野線"]},
    "いずみ野": {"coords": (35.4187, 139.4952), "lines": ["相鉄いずみ野線"]},
    "いずみ中央": {"coords": (35.4057, 139.4880), "lines": ["相鉄いずみ野線"]},
    "湘南台": {"coords": (35.3963, 139.4665), "lines": ["小田急江ノ島線", "相鉄いずみ野線", "横浜市営地下鉄ブルーライン"]},
    "神奈川": {"coords": (35.4697, 139.6292), "lines": ["京急本線"]},
    "戸部": {"coords": (35.4578, 139.6206), "lines": ["京急本線"]},
    "黄金町": {"coords": (35.4418, 139.6219), "lines": ["京急本線"]},
    "南太田": {"coords": (35.4364, 139.6139), "lines": ["京急本線"]},
    "井土ヶ谷": {"coords": (35.4338, 139.5989), "lines": ["京急本線"]},
    "弘明寺(京急)": {"coords": (35.4243, 139.5982), "lines": ["京急本線"]},
    "屏風浦": {"coords": (35.3941, 139.6153), "lines": ["京急本線"]},
    "杉田": {"coords": (35.3811, 139.6201), "lines": ["京急本線"]},
    "京急富岡": {"coords": (35.3672, 139.6302), "lines": ["京急本線"]},
    "能見台": {"coords": (35.3601, 139.6288), "lines": ["京急本線"]},
    "金沢八景": {"coords": (35.3269, 139.6208), "lines": ["京急本線", "金沢シーサイドライン"]},
    "高島町": {"coords": (35.4593, 139.6223), "lines": ["横浜市営地下鉄ブルーライン"]},
    "伊勢佐木長者町": {"coords": (35.4416, 139.6343), "lines": ["横浜市営地下鉄ブルーライン"]},
    "阪東橋": {"coords": (35.4373, 139.6277), "lines": ["横浜市営地下鉄ブルーライン"]},
    "吉野町": {"coords": (35.4337, 139.6218), "lines": ["横浜市営地下鉄ブルーライン"]},
    "蒔田": {"coords": (35.4272, 139.6139), "lines": ["横浜市営地下鉄ブルーライン"]},
    "弘明寺(地下鉄)": {"coords": (35.4241, 139.6074), "lines": ["横浜市営地下鉄ブルーライン"]},
    "片倉町": {"coords": (35.4851, 139.6033), "lines": ["横浜市営地下鉄ブルーライン"]},
    "三ツ沢上町": {"coords": (35.4746, 139.6053), "lines": ["横浜市営地下鉄ブルーライン"]},
    "三ツ沢下町": {"coords": (35.4740, 139.6146), "lines": ["横浜市営地下鉄ブルーライン"]},
    "東白楽": {"coords": (35.4828, 139.6295), "lines": ["東急東横線"]},
    "白楽": {"coords": (35.4904, 139.6268), "lines": ["東急東横線"]},
    "妙蓮寺": {"coords": (35.4988, 139.6318), "lines": ["東急東横線"]},
    "大倉山": {"coords": (35.5215, 139.6300), "lines": ["東急東横線"]},
    "綱島": {"coords": (35.5365, 139.6342), "lines": ["東急東横線"]},
    "高田": {"coords": (35.5492, 139.6198), "lines": ["横浜市営地下鉄グリーンライン"]},
    "日吉本町": {"coords": (35.5516, 139.6348), "lines": ["横浜市営地下鉄グリーンライン"]},
    "石川町": {"coords": (35.4391, 139.6436), "lines": ["JR根岸線"]},
    "根岸": {"coords": (35.4158, 139.6353), "lines": ["JR根岸線"]},
    "磯子": {"coords": (35.4003, 139.6181), "lines": ["JR根岸線"]},
    "洋光台": {"coords": (35.3794, 139.5960), "lines": ["JR根岸線"]},
    "本郷台": {"coords": (35.3667, 139.5498), "lines": ["JR根岸線"]},
}

ALL_LINES = sorted(list(set([line for st_info in STATION_DATA.values() for line in st_info["lines"]])))

# =========================================================
# 勉強スポットデータベース
# =========================================================
SPOTS_DATA = [
    {"name": "神奈川県立図書館", "station": "桜木町", "line": "JR根岸線", "lat": 35.4542, "lon": 139.6275, "category": "図書館", "wifi": True, "power": True, "seats": "約300席", "rule": "PC・電卓使用全席可（サイレントエリア除く）", "access": "桜木町駅 徒歩10分", "desc": "新館は全席コンセント完備。予約システムがあり確実。非常に綺麗で静寂。"},
    {"name": "横浜市中央図書館", "station": "日ノ出町", "line": "京急本線", "lat": 35.4442, "lon": 139.6267, "category": "図書館", "wifi": True, "power": True, "seats": "約400席", "rule": "PC利用は4階・5階の指定席のみ", "access": "日ノ出町駅 徒歩3分", "desc": "地下1階から5階まで閲覧席多数。自習用の席は午前中で埋まることが多い。"},
    {"name": "横浜市中図書館", "station": "山手", "line": "JR根岸線", "lat": 35.4385, "lon": 139.6540, "category": "図書館", "wifi": False, "power": False, "seats": "約60席", "rule": "電卓不可・PC持ち込み不可", "access": "山手駅 徒歩15分", "desc": "本牧エリアの落ち着いた環境にある地域図書館。読書や静かなノート学習向け。"},
    {"name": "横浜市戸塚図書館", "station": "戸塚", "line": "JR東海道線", "lat": 35.4001, "lon": 139.5332, "category": "図書館", "wifi": False, "power": False, "seats": "約80席", "rule": "学生用自習席あり（入れ替え制）", "access": "戸塚駅西口 徒歩4分", "desc": "駅チカで便利。休日は朝から整理券が配布されることがある定番スポット。"},
    {"name": "横浜市港北図書館", "station": "菊名", "line": "東急東横線", "lat": 35.5118, "lon": 139.6293, "category": "図書館", "wifi": False, "power": False, "seats": "約70席", "rule": "PC使用不可", "access": "菊名駅東口 徒歩7分", "desc": "地域住民や高校生の利用が多い。レトロで静かな空間。"},
    {"name": "横浜市都筑図書館", "station": "センター南", "line": "横浜市営地下鉄ブルーライン", "lat": 35.5451, "lon": 139.5732, "category": "図書館", "wifi": False, "power": False, "seats": "約120席", "rule": "一部PC優先席あり（電源なし）", "access": "センター南駅 徒歩6分", "desc": "都筑区総合庁舎内。天井が高く広々としており快適。"},
    {"name": "スターバックス 横浜西口店", "station": "横浜", "line": "JR東海道線", "lat": 35.4645, "lon": 139.6210, "category": "カフェ", "wifi": True, "power": True, "seats": "約90席", "rule": "混雑時90分制", "access": "横浜駅西口 徒歩3分", "desc": "大テーブル席にコンセントあり。常に適度な雑音があり、作業が捗る。"},
    {"name": "タリーズコーヒー NEWoMan横浜店", "station": "横浜", "line": "東急東横線", "lat": 35.4661, "lon": 139.6225, "category": "カフェ", "wifi": True, "power": True, "seats": "約50席", "rule": "長時間の席占有制限あり", "access": "横浜駅直結", "desc": "駅直結の高級感ある店舗。窓側カウンターに電源あり。PCワーク向け。"},
    {"name": "スターバックス キュービックプラザ新横浜店", "station": "新横浜", "line": "JR横浜線", "lat": 35.5076, "lon": 139.6178, "category": "カフェ", "wifi": True, "power": True, "seats": "約70席", "rule": "混雑時利用制限あり", "access": "新横浜駅直結", "desc": "駅直結ビル内。PC作業利用が多い店舗。"},
    {"name": "タリーズコーヒー 綱島駅前店", "station": "綱島", "line": "東急東横線", "lat": 35.5368, "lon": 139.6342, "category": "カフェ", "wifi": True, "power": True, "seats": "約45席", "rule": "特になし", "access": "綱島駅東口 徒歩1分", "desc": "【電源あり】カウンター席にコンセント完備。ビジネス利用も多く集中しやすい環境。"},
    {"name": "上島珈琲店 金沢八景店", "station": "金沢八景", "line": "京急本線", "lat": 35.3272, "lon": 139.6212, "category": "カフェ", "wifi": True, "power": True, "seats": "約50席", "rule": "特になし", "access": "金沢八景駅 徒歩1分", "desc": "【電源あり】大学が近いエリア。レトロでモダンな空間で長時間の勉強に抜群。"},
    {"name": "プロント 湘南台店", "station": "湘南台", "line": "相鉄いずみ野線", "lat": 35.3965, "lon": 139.4668, "category": "カフェ", "wifi": True, "power": True, "seats": "約60席", "rule": "カウンター席のみ電源利用可", "access": "湘南台駅西口 徒歩1分", "desc": "【電源あり】一人用カウンター席が充実しており、PC作業や自習に最適。"},
]

df_spots = pd.DataFrame(SPOTS_DATA)

# =========================================================
# ナビゲーション・検索ヘッダー
# =========================================================
st.markdown("<h2 style='margin-bottom:0px; letter-spacing:-0.02em;'>📖 駅勉ガイド 横浜広域版</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-size:12px; color:#64748b; margin-top:4px;'>通勤・通学定期ルートから最適な自習空間を見つける、実用本位のデータベース</p>", unsafe_allow_html=True)
st.markdown("---")

# 検索枠の配置
search_mode = st.radio("【検索軸の選択】", ["鉄道路線から探す（沿線指定）", "特定の駅から探す（ピンポイント）"], horizontal=True)

col_f1, col_f2 = st.columns([2, 2])

with col_f1:
    if "鉄道路線" in search_mode:
        chosen_line = st.selectbox("路線を選択してください", ALL_LINES, index=ALL_LINES.index("JR根岸線"))
        target_stations = [st_name for st_name, info in STATION_DATA.items() if chosen_line in info["lines"]]
        display_title = f"■ {chosen_line} 沿線の学習スポット一覧"
        ref_station = target_stations[0] if target_stations else "横浜"
    else:
        chosen_station = st.selectbox("駅を選択してください", sorted(list(STATION_DATA.keys())), index=sorted(list(STATION_DATA.keys())).index("横浜"))
        target_stations = [chosen_station]
        display_title = f"■ {chosen_station} 駅周辺の学習スポット一覧"
        ref_station = chosen_station

with col_f2:
    selected_cats = st.multiselect("施設種別", ["図書館", "カフェ"], default=["図書館", "カフェ"])
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        wifi_req = st.checkbox("🛜 公衆Wi-Fi必須")
    with c_col2:
        power_req = st.checkbox("🔌 コンセント必須")

st.markdown("---")

# =========================================================
# メインコンテンツレイアウト
# =========================================================
col_main, col_map = st.columns([1.8, 1.1], gap="medium")

# フィルタリング処理
filtered_df = df_spots[df_spots["station"].isin(target_stations)].copy()

if selected_cats:
    filtered_df = filtered_df[filtered_df["category"].isin(selected_cats)]
else:
    filtered_df = pd.DataFrame(columns=df_spots.columns)

if wifi_req:
    filtered_df = filtered_df[filtered_df["wifi"]]
if power_req:
    filtered_df = filtered_df[filtered_df["power"]]

with col_main:
    st.markdown(f"<div class='line-header'>{display_title} ({len(filtered_df)}件該当)</div>", unsafe_allow_html=True)
    
    if not filtered_df.empty:
        # インデントバグを完全に回避するため、HTMLコードブロック内の行頭余白を徹底排除
        table_html = "<table class='spot-table'><thead><tr><th style='width: 18%;'>最寄り駅</th><th style='width: 32%;'>施設名 / 設備</th><th style='width: 20%;'>座席・ルール</th><th style='width: 30%;'>特徴・詳細</th></tr></thead><tbody>"
        
        for _, row in filtered_df.iterrows():
            w_tag = "<span class='tag-text-active'>🛜 Wi-Fi</span>" if row['wifi'] else "<span class='tag-text'>🛜 なし</span>"
            p_tag = "<span class='tag-text-active'>🔌 電源</span>" if row['power'] else "<span class='tag-text'>🔌 なし</span>"
            
            seats_text = row['seats'] if pd.notna(row.get('seats')) else "情報なし"
            rule_text = row['rule'] if pd.notna(row.get('rule')) else "特になし"
            
            # 複数行のインデントによる誤記動を1行ずつの文字列結合（インデントなし）で安全に実装
            table_html += f"<tr>" \
                          f"<td><b>{row['station']}駅</b><br><span style='font-size:11px; color:#64748b;'>{row['access']}</span></td>" \
                          f"<td><strong style='font-size:14px; color:#1e3a8a;'>{row['name']}</strong><br><span style='font-size:10px; color:#475569; background:#e2e8f0; padding:1px 4px; border-radius:2px; margin-right:5px; font-weight:600;'>{row['category']}</span><div style='margin-top:6px;'>{w_tag}{p_tag}</div></td>" \
                          f"<td><span style='color:#0f172a; font-weight:bold;'>{seats_text}</span><br><span class='rule-alert'>⚠ {rule_text}</span></td>" \
                          f"<td><div style='font-weight:400; color:#334155;'>{row['desc']}</div></td>" \
                          f"</tr>"
        
        table_html += "</tbody></table>"
        
        # 安全に一括レンダリング
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.warning("選択された条件に合致するスポットは現在登録されていません。条件を緩めてみてください。")

with col_map:
    st.markdown("<div style='font-size:13px; font-weight:bold; color:#1e293b; margin-bottom:8px;'>🌐 周辺マップ（位置確認用）</div>", unsafe_allow_html=True)
    
    center_lat, center_lon = STATION_DATA[ref_station]["coords"]
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="OpenStreetMap")

    if not filtered_df.empty:
        for _, spot in filtered_df.iterrows():
            pin_color = "blue" if spot['category'] == "図書館" else "cadetblue"
            seats_text = spot['seats'] if pd.notna(spot.get('seats')) else "情報なし"
            
            popup_html = f"""
            <div style='font-family:sans-serif; font-size:12px; line-height:1.4; width:200px;'>
                <strong>{spot['name']}</strong> ({seats_text})<br>
                <span style='color:#64748b;'>{spot['access']}</span>
            </div>
            """
            folium.Marker(
                [spot["lat"], spot["lon"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=spot["name"],
                icon=folium.Icon(color=pin_color, icon="info-sign")
            ).add_to(m)
            
    # 地図の一意性を保証するkeyを設定
    st_folium(m, width="100%", height=480, key=f"map_{search_mode}_{ref_station}")

# =========================================================
# フッター
# =========================================================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; font-size: 11px; color: #94a3b8; padding-top: 5px;'>
        駅勉ガイド 横浜広域版 | 当サイトは公開データを基にしたデータベースです。<br>
        最新の利用ルールや開館時間は各施設の公式サイトを直接ご確認ください。
    </div>
""", unsafe_allow_html=True)
