import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from math import radians, sin, cos, sqrt, atan2

# =========================================================
# 距離計算ユーティリティ（ハーバサイン公式：2点間の直線距離をkmで算出）
# =========================================================
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0  # 地球の半径 (km)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# =========================================================
# ページ全体の基本設定
# =========================================================
st.set_page_config(
    page_title="駅勉ガイド 横浜広域版 | 沿線・駅別学習スポット検索",
    page_icon="📖",
    layout="wide",
)

# 【デザイン設定】
st.markdown("""
    <style>
    .main .block-container { padding-top: 2.0rem; padding-bottom: 2.0rem; background-color: #f8fafc; }
    h1, h2, h3 { color: #0f172a; font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", sans-serif; font-weight: 700; }
    .spot-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; background-color: #ffffff; border-radius: 4px; overflow: hidden; border: 1px solid #e2e8f0; }
    .spot-table th { background-color: #1e3a8a; color: white; padding: 12px 14px; font-size: 13px; text-align: left; font-weight: 600; letter-spacing: 0.05em; }
    .spot-table td { padding: 14px 14px; border-bottom: 1px solid #e2e8f0; font-size: 13px; color: #334155; vertical-align: top; line-height: 1.5; }
    .spot-table tr:hover { background-color: #f1f5f9; }
    .line-header { background-color: #eff6ff; padding: 10px 14px; border-left: 4px solid #1e3a8a; border-right: 1px solid #bfdbfe; border-top: 1px solid #bfdbfe; border-bottom: 1px solid #bfdbfe; font-weight: bold; font-size: 14px; color: #1e3a8a; margin-top: 10px; margin-bottom: 10px; border-radius: 0 4px 4px 0; }
    .tag-text { font-size: 11px; font-weight: 600; color: #64748b; background-color: #f1f5f9; padding: 3px 6px; border-radius: 3px; margin-right: 4px; border: 1px solid #cbd5e1; display: inline-block; margin-top: 2px; }
    .tag-text-active { font-size: 11px; font-weight: 600; color: #1e3a8a; background-color: #e0f2fe; padding: 3px 6px; border-radius: 3px; margin-right: 4px; border: 1px solid #bae6fd; display: inline-block; margin-top: 2px; }
    .rule-alert { font-size: 11px; color: #b91c1c; font-weight: 500; background-color: #fef2f2; padding: 2px 6px; border-radius: 3px; border: 1px solid #fee2e2; display: inline-block; margin-top: 4px; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 駅の座標・沿線データ（星川駅経度も139.6000に完全修復）
# =========================================================
STATION_DATA = {
    "横浜": {"coords": (35.4657, 139.6223), "lines": ["JR東海道線", "JR根岸線", "東急東横線", "相鉄本線", "京急本線", "横浜市営地下鉄ブルーライン"]},
    "新横浜": {"coords": (35.5074, 139.6175), "lines": ["JR横浜線", "東海道新幹線", "相鉄・東急直通線", "横浜市営地下鉄ブルーライン"]},
    "戸塚": {"coords": (35.4008, 139.5341), "lines": ["JR東海道線", "JR横須賀線", "横浜市営地下鉄ブルーライン"]},
    "東戸塚": {"coords": (35.4181, 139.5474), "lines": ["JR横須賀線"]},
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
# 勉強スポットデータベース（全172店舗・完全復旧版キャッシュ）
# =========================================================
@st.cache_data
def load_spots_dataframe():
    spots_data = [
        # --- 図書館データ ---
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

        # --- 横浜駅周辺のカフェ（完全復旧） ---
        {"name": "スターバックス 横浜西口店", "station": "横浜", "line": "JR東海道線", "lat": 35.4645, "lon": 139.6210, "category": "カフェ", "wifi": True, "power": True, "seats": "約90席", "rule": "混雑時90分制", "access": "横浜駅西口 徒歩3分", "desc": "大テーブル席にコンセントあり。常に適度な雑音があり、作業が捗る。"},
        {"name": "タリーズコーヒー NEWoMan横浜店", "station": "横浜", "line": "東急東横線", "lat": 35.4661, "lon": 139.6225, "category": "カフェ", "wifi": True, "power": True, "seats": "約50席", "rule": "長時間の席占有制限あり", "access": "横浜駅直結", "desc": "駅直結の高級感ある店舗。窓側カウンターに電源あり。PCワーク向け。"},
        {"name": "ドトールコーヒーショップ 横浜西口店", "station": "横浜", "line": "JR東海道線", "lat": 35.4640, "lon": 139.6205, "category": "カフェ", "wifi": True, "power": False, "seats": "約120席", "rule": "特になし", "access": "横浜駅西口 徒歩2分", "desc": "サクッと短時間集中したい時におすすめの手軽なカフェ。"},
        {"name": "エクセルシオールカフェ 横浜駅西口店", "station": "横浜", "line": "JR東海道線", "lat": 35.4643, "lon": 139.6208, "category": "カフェ", "wifi": True, "power": True, "seats": "約80席", "rule": "特になし", "access": "横浜駅西口 徒歩3分", "desc": "コンセント席も用意されておりPC作業に向いています。"},
        {"name": "カフェ・ド・クリエ 横浜北幸店", "station": "横浜", "line": "JR東海道線", "lat": 35.4655, "lon": 139.6185, "category": "カフェ", "wifi": True, "power": True, "seats": "約70席", "rule": "特になし", "access": "横浜駅西口 徒歩6分", "desc": "北幸のオフィス街近くにあり、落ち着いた雰囲気で作業可能です。"},
        {"name": "プロント 横浜店", "station": "横浜", "line": "JR東海道線", "lat": 35.4648, "lon": 139.6215, "category": "カフェ", "wifi": True, "power": True, "seats": "約60席", "rule": "特になし", "access": "横浜駅西口 徒歩2分", "desc": "一人用席が充実しています。"},
        {"name": "珈琲館 横浜西口店", "station": "横浜", "line": "JR東海道線", "lat": 35.4650, "lon": 139.6190, "category": "カフェ", "wifi": True, "power": True, "seats": "約55席", "rule": "特になし", "access": "横浜駅西口 徒歩4分", "desc": "落ち着いた席の配置で作業がはかどります。"},
        {"name": "星乃珈琲店 横浜店", "station": "横浜", "line": "JR東海道線", "lat": 35.4642, "lon": 139.6212, "category": "カフェ", "wifi": False, "power": False, "seats": "約80席", "rule": "自習向きではない（読書向け）", "access": "横浜駅西口 徒歩3分", "desc": "ゆったりしたソファ席が多く、読書やノートでの勉強に最適。"},
        {"name": "ブルーボトルコーヒー NEWoMan横浜店", "station": "横浜", "line": "東急東横線", "lat": 35.4663, "lon": 139.6228, "category": "カフェ", "wifi": True, "power": False, "seats": "約35席", "rule": "特になし", "access": "横浜駅直結", "desc": "開放的な空間。リフレッシュを兼ねた勉強に。"},
        {"name": "タリーズコーヒー CeeU Yokohama店", "station": "横浜", "line": "JR東海道線", "lat": 35.4635, "lon": 139.6198, "category": "カフェ", "wifi": True, "power": True, "seats": "約65席", "rule": "特になし", "access": "横浜駅西口 徒歩4分", "desc": "商業施設内のタリーズ。デスクワーク席あり。"},
        {"name": "スターバックス ルミネ横浜店", "station": "横浜", "line": "東急東横線", "lat": 35.4654, "lon": 139.6227, "category": "カフェ", "wifi": True, "power": True, "seats": "約60席", "rule": "混雑時利用制限あり", "access": "横浜駅東口 ルミネ内", "desc": "ルミネの中にあるスタバ。駅内からのアクセスが非常に良い。"},
        {"name": "スターバックス そごう横浜店", "station": "横浜", "line": "京急本線", "lat": 35.4652, "lon": 139.6245, "category": "カフェ", "wifi": True, "power": False, "seats": "約40席", "rule": "特になし", "access": "横浜駅東口 そごう内", "desc": "そごう横浜店内。隙間時間の作業に。"},
        {"name": "ゴンチャ 横浜西口店", "station": "横浜", "line": "JR東海道線", "lat": 35.4638, "lon": 139.6200, "category": "カフェ", "wifi": True, "power": False, "seats": "約30席", "rule": "特になし", "access": "横浜駅西口 徒歩4分", "desc": "人気の台湾ティー専門店。学生の利用が多く、気軽に寄れます。"},
        {"name": "猿田彦珈琲 横浜店", "station": "横浜", "line": "JR東海道線", "lat": 35.4660, "lon": 139.6218, "category": "カフェ", "wifi": True, "power": True, "seats": "約40席", "rule": "特になし", "access": "横浜駅周辺", "desc": "こだわりの珈琲を味わいながら、リラックスして作業に取り組めます。"},
        {"name": "UNI COFFEE ROASTERY 横浜駅西口店", "station": "横浜", "line": "相鉄本線", "lat": 35.4662, "lon": 139.6180, "category": "カフェ", "wifi": True, "power": True, "seats": "約50席", "rule": "特になし", "access": "横浜駅西口 徒歩7分", "desc": "Wi-Fi・電源完備でクリエイティブな作業に最適。"},
        {"name": "24/7 coffee&roaster 横浜", "station": "横浜", "line": "JR東海道線", "lat": 35.4656, "lon": 139.6235, "category": "カフェ", "wifi": True, "power": False, "seats": "約45席", "rule": "特になし", "access": "横浜駅周辺", "desc": "落ち着いたカフェ空間です。"},
        {"name": "THE ROYAL CAFE YOKOHAMA MONTE ROSA", "station": "横浜", "line": "JR東海道線", "lat": 35.4646, "lon": 139.6220, "category": "カフェ", "wifi": True, "power": True, "seats": "約40席", "rule": "特になし", "access": "横浜駅構内エリア", "desc": "特別感のある上質なカフェ。大人の作業スペースとして最適。"},
        {"name": "GINZA WEST Bay Cafe Yokohama", "station": "横浜", "line": "JR東海道線", "lat": 35.4641, "lon": 139.6195, "category": "カフェ", "wifi": False, "power": False, "seats": "約40席", "rule": "自習より読書・思考向け", "access": "横浜駅西口周辺", "desc": "非常に落ち着いた空間でじっくり読書や勉強ができます。"},

        # --- 新横浜駅周辺のカフェ（完全復旧） ---
        {"name": "スターバックス キュービックプラザ新横浜店", "station": "新横浜", "line": "JR横浜線", "lat": 35.5076, "lon": 139.6178, "category": "カフェ", "wifi": True, "power": True, "seats": "約70席", "rule": "混雑時利用制限あり", "access": "新横浜駅直結", "desc": "駅直結ビル内。PC作業利用が多い店舗。"},
        {"name": "タリーズコーヒー 新横浜店", "station": "新横浜", "line": "JR横浜線", "lat": 35.5080, "lon": 139.6165, "category": "カフェ", "wifi": True, "power": True, "seats": "約60席", "rule": "カウンターのみ電源可", "access": "新横浜駅 徒歩2分", "desc": "コンセント席も完備されているためデスクワークに最適。"},
        {"name": "ドトールコーヒー 新横浜駅店", "station": "新横浜", "line": "JR横浜線", "lat": 35.5072, "lon": 139.6172, "category": "カフェ", "wifi": True, "power": False, "seats": "約50席", "rule": "特になし", "access": "新横浜駅構内", "desc": "駅近でサクッと移動前後に勉強を進めるのに重宝します。"},
        {"name": "エクセルシオールカフェ 新横浜店", "station": "新横浜", "line": "JR横浜線", "lat": 35.5085, "lon": 139.6170, "category": "カフェ", "wifi": True, "power": True, "seats": "約75席", "rule": "特になし", "access": "新横浜駅 徒歩3分", "desc": "席数が比較的多く、ゆったりと落ち着いて勉強に取り組めます。"},
        {"name": "PRONTO 新横浜店", "station": "新横浜", "line": "JR横浜線", "lat": 35.5068, "lon": 139.6185, "category": "カフェ", "wifi": True, "power": True, "seats": "約50席", "rule": "カウンター席のみ電源可", "access": "新横浜駅 徒歩4分", "desc": "カウンター席に電源があり、PC作業がしやすいです。"},
        {"name": "珈琲館 新横浜店", "station": "新横浜", "line": "JR横浜線", "lat": 35.5090, "lon": 139.6160, "category": "カフェ", "wifi": True, "power": True, "seats": "約45席", "rule": "特になし", "access": "新横浜駅 徒歩5分", "desc": "静かに集中したい日の自習におすすめ。"},
        {"name": "スターバックス 新横浜駅店", "station": "新横浜", "line": "JR横浜線", "lat": 35.5071, "lon": 139.6176, "category": "カフェ", "wifi": True, "power": True, "seats": "約55席", "rule": "混雑時90分制", "access": "新横浜駅構内", "desc": "ビジネスマンが多いため、作業に集中しやすい雰囲気です。"},

        # --- 戸塚・上大岡・二俣川・鶴見・東神奈川・文庫のカフェ（完全復旧） ---
        {"name": "スターバックス 戸塚店", "station": "戸塚", "line": "JR東海道線", "lat": 35.4012, "lon": 139.5345, "category": "カフェ", "wifi": True, "power": True, "seats": "約70席", "rule": "混雑時席譲り合い", "access": "戸塚駅東口 徒歩2分", "desc": "自習客が多く非常に刺激を受ける環境。仕事帰りや学校帰りに。"},
        {"name": "タリーズコーヒー 戸塚モディ店", "station": "戸塚", "line": "JR東海道線", "lat": 35.4005, "lon": 139.5338, "category": "カフェ", "wifi": True, "power": True, "seats": "約60席", "rule": "特になし", "access": "戸塚駅直結 モディ内", "desc": "ビジネスマンや資格勉強の作業利用も非常に多い定番スペース。"},
        {"name": "ドトールコーヒー 戸塚店", "station": "戸塚", "line": "JR東海道線", "lat": 35.4010, "lon": 139.5342, "category": "カフェ", "wifi": True, "power": False, "seats": "約55席", "rule": "特になし", "access": "戸塚駅東口 徒歩1分", "desc": "時間を無駄にしたくない時のクイックな暗記や直前チェックに。"},
        {"name": "珈琲館 戸塚店", "station": "戸塚", "line": "JR東海道線", "lat": 35.3995, "lon": 139.5330, "category": "カフェ", "wifi": True, "power": True, "seats": "約50席", "rule": "特になし", "access": "戸塚駅西口 徒歩4分", "desc": "静かな空間でじっくり落ち着いて自習に励むことができます。"},
        {"name": "スターバックス 京急百貨店上大岡店", "station": "上大岡", "line": "京急本線", "lat": 35.4090, "lon": 139.5968, "category": "カフェ", "wifi": True, "power": True, "seats": "約65席", "rule": "混雑時利用制限あり", "access": "上大岡駅直結", "desc": "百貨店内。一人用カウンター席で集中して作業可能。利便性抜群。"},
        {"name": "タリーズコーヒー 上大岡店", "station": "上大岡", "line": "京急本線", "lat": 35.4085, "lon": 139.5960, "category": "カフェ", "wifi": True, "power": True, "seats": "約55席", "rule": "特になし", "access": "上大岡駅 徒歩2分", "desc": "席数が豊富で、落ち着いたデスクワークに定評があります。"},
        {"name": "ドトールコーヒー 上大岡店", "station": "上大岡", "line": "京急本線", "lat": 35.4082, "lon": 139.5958, "category": "カフェ", "wifi": True, "power": False, "seats": "約50席", "rule": "特になし", "access": "上大岡駅西口 徒歩2分", "desc": "隙間時間にテキストを開いて学習を進めるのに非常に便利。"},
        {"name": "サンマルクカフェ 上大岡店", "station": "上大岡", "line": "京急本線", "lat": 35.4080, "lon": 139.5962, "category": "カフェ", "wifi": True, "power": False, "seats": "約70席", "rule": "特になし", "access": "上大岡駅 徒歩3分", "desc": "一人で座れる席が多く、長時間の読書やノートまとめに。"},
        {"name": "スターバックス シァル鶴見店", "station": "鶴見", "line": "JR京浜東北線", "lat": 35.5076, "lon": 139.6765, "category": "カフェ", "wifi": True, "power": True, "seats": "約60席", "rule": "特になし", "access": "鶴見駅直結 CIAL内", "desc": "駅ビル内で雨でも安心。充実した電源席でPC作業も快適。"},
        {"name": "タリーズコーヒー 鶴見店", "station": "鶴見", "line": "JR京浜東北線", "lat": 35.5065, "lon": 139.6755, "category": "カフェ", "wifi": True, "power": True, "seats": "約50席", "rule": "特になし", "access": "鶴見駅西口 徒歩3分", "desc": "落ち着いた客層が多く、集中して作業ができる優良店舗。"},
        {"name": "スターバックス 東神奈川店", "station": "東神奈川", "line": "JR京浜東北線", "lat": 35.4780, "lon": 139.6325, "category": "カフェ", "wifi": True, "power": True, "seats": "約45席", "rule": "混雑時90分制", "access": "東神奈川駅直結", "desc": "乗り換えの隙間時間にサクッと勉強をこなせる好立地。"},
        {"name": "タリーズコーヒー 東神奈川店", "station": "東神奈川", "line": "JR京浜東北線", "lat": 35.4782, "lon": 139.6315, "category": "カフェ", "wifi": True, "power": True, "seats": "約40席", "rule": "特になし", "access": "東神奈川駅 徒歩2分", "desc": "静かな環境でPCを用いた自習にとても向いています。"},
        {"name": "スターバックス ジョイナステラス二俣川店", "station": "二俣川", "line": "相鉄本線", "lat": 35.4625, "lon": 139.5325, "category": "カフェ", "wifi": True, "power": True, "seats": "約65席", "rule": "混雑時制限あり", "access": "二俣川駅直結", "desc": "綺麗で新しいデスクスペースで非常に快適に勉強可能。"},
        {"name": "タリーズコーヒー 新杉田店", "station": "新杉田", "line": "JR根岸線", "lat": 35.3870, "lon": 139.6200, "category": "カフェ", "wifi": True, "power": True, "seats": "約45席", "rule": "特になし", "access": "新杉田駅直結", "desc": "シーサイドライン乗り換え時にピッタリなコンセント完備店舗。"},
        {"name": "スターバックス 金沢文庫店", "station": "金沢文庫", "line": "京急本線", "lat": 35.3425, "lon": 139.6220, "category": "カフェ", "wifi": True, "power": True, "seats": "約55席", "rule": "特になし", "access": "金沢文庫駅 徒歩2分", "desc": "地元学生やビジネスマンの自習・作業利用が非常に多い。"},

        # --- 東戸塚駅 ---
        {"name": "スターバックスコーヒー 西武東戸塚S.C.店", "station": "東戸塚", "line": "JR横須賀線", "lat": 35.4185, "lon": 139.5460, "category": "カフェ", "wifi": True, "power": True, "seats": "席数多め", "rule": "混雑時利用制限あり", "access": "東戸塚駅東口 徒歩2分", "desc": "西武館内。カウンター席を中心にPC・勉強利用が盛んです。"},
        {"name": "ドトールコーヒーショップ 東戸塚店", "station": "東戸塚", "line": "JR横須賀線", "lat": 35.4178, "lon": 139.5478, "category": "カフェ", "wifi": True, "power": False, "seats": "中規模店", "rule": "特になし", "access": "東戸塚駅東口 徒歩1分", "desc": "駅前の好立地。サクッと短時間の参考書チェックや読書に適しています。"},
        {"name": "タリーズコーヒー 東戸塚西口店", "station": "東戸塚", "line": "JR横須賀線", "lat": 35.4180, "lon": 139.5450, "category": "カフェ", "wifi": True, "power": True, "seats": "落ち着いた配置", "rule": "特になし", "access": "東戸塚駅西口 徒歩1分", "desc": "西口側の静かな店舗。電源席があり、落ち着いてPC作業や自習に取り組めます。"},
        {"name": "サンマルクカフェ 東戸塚店", "station": "東戸塚", "line": "JR横須賀線", "lat": 35.4190, "lon": 139.5480, "category": "カフェ", "wifi": True, "power": False, "seats": "ゆったり席", "rule": "特になし", "access": "東戸塚駅周辺", "desc": "広めの席設計でリラックスしながらノートまとめ等が可能です。"},
        {"name": "PRONTO 東戸塚店", "station": "東戸塚", "line": "JR横須賀線", "lat": 35.4175, "lon": 139.5465, "category": "カフェ", "wifi": True, "power": True, "seats": "一人席あり", "rule": "特になし", "access": "東戸塚駅直結周辺", "desc": "昼間はビジネスパーソンや学生のワークスペースとして機能。"},
        {"name": "珈琲館 東戸塚店", "station": "東戸塚", "line": "JR横須賀線", "lat": 35.4195, "lon": 139.5470, "category": "カフェ", "wifi": True, "power": True, "seats": "落ち着いた空間", "rule": "特になし", "access": "東戸塚駅 徒歩3分", "desc": "珈琲を味わいながら静かに集中して勉強したい時におすすめ。"},
        {"name": "星乃珈琲店 東戸塚店", "station": "東戸塚", "line": "JR横須賀線", "lat": 35.4200, "lon": 139.5460, "category": "カフェ", "wifi": False, "power": False, "seats": "ボックス席中心", "rule": "自習混雑時配慮", "access": "東戸塚駅 徒歩4分", "desc": "落ち着いたシックな内装。思考の整理や読書によるインプットに。"},
        {"name": "倉式珈琲店 西武東戸塚店", "station": "東戸塚", "line": "JR横須賀線", "lat": 35.4184, "lon": 139.5462, "category": "カフェ", "wifi": True, "power": False, "seats": "館内店舗", "rule": "特になし", "access": "東戸塚駅東口 徒歩2分", "desc": "サイフォン珈琲が魅力。落ち着いた和モダンな空間で長文読解などに集中。"},

        # --- 保土ケ谷駅 ---
        {"name": "ドトールコーヒーショップ 保土ケ谷店", "station": "保土ケ谷", "line": "JR横須賀線", "lat": 35.4465, "lon": 139.5935, "category": "カフェ", "wifi": True, "power": False, "seats": "駅ビル周辺", "rule": "特になし", "access": "保土ケ谷駅直結・至近", "desc": "移動前後の隙間時間での暗記作業やクイックなタスク処理に重宝。"},
        {"name": "タリーズコーヒー 保土ケ谷店", "station": "保土ケ谷", "line": "JR横須賀線", "lat": 35.4470, "lon": 139.5940, "category": "カフェ", "wifi": True, "power": True, "seats": "カウンター電源", "rule": "特になし", "access": "保土ケ谷駅 徒歩1分", "desc": "一人用カウンター席に電源完備。PCを用いたオンライン学習も快適。"},
        {"name": "スターバックスコーヒー 保土ケ谷駅店", "station": "保土ケ谷", "line": "JR横須賀線", "lat": 35.4468, "lon": 139.5938, "category": "カフェ", "wifi": True, "power": True, "seats": "コンパクト", "rule": "混雑時90分制", "access": "保土ケ谷駅構内エリア", "desc": "駅アクセス抜群。洗練された空間で集中力が高まります。"},
        {"name": "珈琲館 保土ケ谷店", "station": "保土ケ谷", "line": "JR横須賀線", "lat": 35.4460, "lon": 139.5930, "category": "カフェ", "wifi": True, "power": True, "seats": "レトロモダン", "rule": "特になし", "access": "保土ケ谷駅 徒歩2分", "desc": "静かなクラシック空間。じっくりとテキストを読み込む勉強に最適。"},
        {"name": "カフェ・ベローチェ 保土ケ谷店", "station": "保土ケ谷", "line": "JR横須賀線", "lat": 35.4475, "lon": 139.5945, "category": "カフェ", "wifi": True, "power": False, "seats": "席数多め", "rule": "特になし", "access": "保土ケ谷駅 徒歩2分", "desc": "広めの店内で開放感があり、気兼ねなく参考書を広げられます。"},
        {"name": "モリバコーヒー 保土ケ谷店", "station": "保土ケ谷", "line": "JR横須賀線", "lat": 35.4463, "lon": 139.5932, "category": "カフェ", "wifi": True, "power": True, "seats": "リーズナブル", "rule": "特になし", "access": "保土ケ谷駅東口すぐ", "desc": "日常使いしやすい価格帯。手軽に作業環境を確保したい時に重宝。"},

        # --- 大船駅 ---
        {"name": "スターバックスコーヒー 大船ルミネウィング店", "station": "大船", "line": "JR東海道線", "lat": 35.3556, "lon": 139.5308, "category": "カフェ", "wifi": True, "power": True, "seats": "ルミネ内", "rule": "混雑時利用制限あり", "access": "大船駅直結", "desc": "ルミネ内のため利便性抜群。常に多くの学習者や作業者で賑わっています。"},
        {"name": "ドトールコーヒーショップ 大船店", "station": "大船", "line": "JR東海道線", "lat": 35.3550, "lon": 139.5315, "category": "カフェ", "wifi": True, "power": False, "seats": "駅チカ", "rule": "特になし", "access": "大船駅東口 徒歩2分", "desc": "回転が早く、隙間時間の集中暗記や軽作業にとても便利。"},
        {"name": "タリーズコーヒー 大船店", "station": "大船", "line": "JR東海道線", "lat": 35.3560, "lon": 139.5300, "category": "カフェ", "wifi": True, "power": True, "seats": "コンセントあり", "rule": "特になし", "access": "大船駅西口 徒歩1分", "desc": "西口側の落ち着いた環境。PC学習を伴う資格勉強などにおすすめ。"},
        {"name": "サンマルクカフェ 大船店", "station": "大船", "line": "JR東海道線", "lat": 35.3545, "lon": 139.5320, "category": "カフェ", "wifi": True, "power": False, "seats": "広め", "rule": "特になし", "access": "大船駅周辺", "desc": "ゆったりしたソファ席が多く、長時間の読書やリサーチの整理に。"},
        {"name": "星乃珈琲店 大船店", "station": "大船", "line": "JR東海道線", "lat": 35.3540, "lon": 139.5325, "category": "カフェ", "wifi": False, "power": False, "seats": "重厚な内装", "rule": "自習マナー遵守", "access": "大船駅東口 徒歩3分", "desc": "プライベート感のある座席構造。周囲を気にせず集中したい時に。"},
        {"name": "珈琲館 大船店", "station": "大船", "line": "JR東海道線", "lat": 35.3565, "lon": 139.5310, "category": "カフェ", "wifi": True, "power": True, "seats": "落ち着き重視", "rule": "特になし", "access": "大船駅 徒歩3分", "desc": "年齢層が高めで静かな空間が保たれており、大人の勉強場所に最適。"},
        {"name": "コメダ珈琲店 大船東口店", "station": "大船", "line": "JR東海道線", "lat": 35.3538, "lon": 139.5330, "category": "カフェ", "wifi": True, "power": True, "seats": "大型ブース席", "rule": "混雑時時間制限あり", "access": "大船駅東口 徒歩4分", "desc": "各席が独立した広い木製ブース調。資料を何冊も広げての勉強に向いています。"},
        {"name": "PRONTO 大船店", "station": "大船", "line": "JR東海道線", "lat": 35.3552, "lon": 139.5322, "category": "カフェ", "wifi": True, "power": True, "seats": "使い勝手良好", "rule": "特になし", "access": "大船駅東口 徒歩2分", "desc": "駅近で使いやすい。昼下がりの時間帯などは比較的静かに自習可能。"},

        # --- みなとみらい駅 ---
        {"name": "BERTH COFFEE みなとみらい", "station": "みなとみらい", "line": "みなとみらい線", "lat": 35.4590, "lon": 139.6310, "category": "カフェ", "wifi": True, "power": True, "seats": "洗練空間", "rule": "特になし", "access": "みなとみらい駅 徒歩3分", "desc": "ホテルの1階に位置するクリエイティブなカフェ。作業や勉強が非常に捗る。"},
        {"name": "カフェ・ド・クリエ グラン クイーンズスクエア横浜", "station": "みなとみらい", "line": "みなとみらい線", "lat": 35.4570, "lon": 139.6330, "category": "カフェ", "wifi": True, "power": True, "seats": "大型店舗", "rule": "特になし", "access": "みなとみらい駅直結", "desc": "クイーンズスクエア内。電源完備のビジネスパーソン向けカウンターあり。"},
        {"name": "VANILLA BEANS みなとみらい本店", "station": "みなとみらい", "line": "みなとみらい線", "lat": 35.4540, "lon": 139.6340, "category": "カフェ", "wifi": False, "power": False, "seats": "お洒落空間", "rule": "混雑時配慮", "access": "みなとみらい駅 徒歩7分", "desc": "チョコレート専門店の上質な空間。気分転換を兼ねたリラックス読書に。"},
        {"name": "Merengue Hawaiian Cafe", "station": "みなとみらい", "line": "みなとみらい線", "lat": 35.4610, "lon": 139.6290, "category": "カフェ", "wifi": True, "power": False, "seats": "広々設計", "rule": "特になし", "access": "みなとみらい駅周辺", "desc": "ハワイアンな明るい空間。平日の午前中など空いている時間はノート作業に◎。"},
        {"name": "アンティコカフェ アルアビス 横浜店", "station": "みなとみらい", "line": "みなとみらい線", "lat": 35.4565, "lon": 139.6320, "category": "カフェ", "wifi": True, "power": False, "seats": "イタリアン調", "rule": "特になし", "access": "みなとみらいエリア", "desc": "大人のシックな雰囲気。静かに手帳をまとめたり、語学のテキストを進めるのに向く。"},
        {"name": "カフェレクセル CIAL桜木町店", "station": "みなとみらい", "line": "みなとみらい線", "lat": 35.4508, "lon": 139.6315, "category": "カフェ", "wifi": True, "power": True, "seats": "上質空間", "rule": "特になし", "access": "桜木町・みなとみらい境界", "desc": "ドトール高級業態。電源・Wi-Fiが安定しており、長時間の勉強環境として優秀。"},

        # --- 馬車道駅 ---
        {"name": "THE HONEY CREPE YOKOHAMA", "station": "馬車道", "line": "みなとみらい線", "lat": 35.4495, "lon": 139.6365, "category": "カフェ", "wifi": False, "power": False, "seats": "小規模", "rule": "特になし", "access": "馬車道駅 徒歩2分", "desc": "アットホームなカフェ。混雑を避けた時間帯のちょっとした読書向け。"},
        {"name": "Pavlov（パブロフ）", "station": "馬車道", "line": "みなとみらい線", "lat": 35.4485, "lon": 139.6375, "category": "カフェ", "wifi": False, "power": False, "seats": "高級感あり", "rule": "自習は非推奨気味", "access": "馬車道駅 徒歩3分", "desc": "お洒落なパウンドケーキ専門店。勉強というよりは、ご褒便読書の時間に。"},
        {"name": "スターバックスコーヒー 横浜馬車道店", "station": "馬車道", "line": "みなとみらい線", "lat": 35.4491, "lon": 139.6361, "category": "カフェ", "wifi": True, "power": True, "seats": "街並み調和", "rule": "混雑時時間制限", "access": "馬車道駅すぐ", "desc": "歴史ある馬車道の雰囲気に溶け込んだ店舗。窓側カウンター等で集中できます。"},
        {"name": "タリーズコーヒー 馬車道店", "station": "馬車道", "line": "みなとみらい線", "lat": 35.4488, "lon": 139.6358, "category": "カフェ", "wifi": True, "power": True, "seats": "ビジネス対応", "rule": "特になし", "access": "馬車道駅 徒歩1分", "desc": "オフィス街が近いため平日はデスクワーク環境として非常に最適化されています。"},
        {"name": "ドトールコーヒーショップ 馬車道店", "station": "馬車道", "line": "みなとみらい線", "lat": 35.4493, "lon": 139.6368, "category": "カフェ", "wifi": True, "power": False, "seats": "定番", "rule": "特になし", "access": "馬車道駅 徒歩1分", "desc": "安定した価格と環境。朝活としての勉強ルーティンにぴったり。"},
        {"name": "UNI COFFEE ROASTERY 馬車道店", "station": "馬車道", "line": "みなとみらい線", "lat": 35.4482, "lon": 139.6350, "category": "カフェ", "wifi": True, "power": True, "seats": "モダン", "rule": "特になし", "access": "馬車道駅 徒歩3分", "desc": "横浜発のお洒落カフェ。Wi-Fi・電源の完備はもちろん、空間の居心地が抜群。"},
        {"name": "カフェ・ド・クリエ 馬車道店", "station": "馬車道", "line": "みなとみらい線", "lat": 35.4500, "lon": 139.6370, "category": "カフェ", "wifi": True, "power": True, "seats": "仕切り席あり", "rule": "特になし", "access": "馬車道駅 徒歩2分", "desc": "一人用の仕切り付きカウンター席が用意されており、集中自習に最適。"},
        {"name": "喫茶エレーナ", "station": "馬車道", "line": "みなとみらい線", "lat": 35.4410, "lon": 139.6480, "category": "カフェ", "wifi": False, "power": False, "seats": "レトロ", "rule": "読書向き", "access": "馬車道・山手広域エリア", "desc": "丘の上の老舗喫茶店。デジタルを離れてじっくり本と向き合いたい時に。"},

        # --- 京急富岡駅 ---
        {"name": "Mugibiyori", "station": "京急富岡", "line": "京急本線", "lat": 35.3675, "lon": 139.6300, "category": "カフェ", "wifi": False, "power": False, "seats": "地域密着", "rule": "特になし", "access": "京急富岡駅 徒歩3分", "desc": "穏やかな時間が流れるカフェ。軽めのノート作業やスケジュール管理に。"},
        {"name": "カフェ・ノアール", "station": "京急富岡", "line": "京急本線", "lat": 35.3668, "lon": 139.6310, "category": "カフェ", "wifi": False, "power": False, "seats": "レトロ", "rule": "特になし", "access": "京急富岡駅 徒歩2分", "desc": "静かな地元喫茶。喧騒を離れてリラックスして文章を読みたいときに。"},
        {"name": "SEA DROP Roast Coffee", "station": "京急富岡", "line": "京急本線", "lat": 35.3680, "lon": 139.6295, "category": "カフェ", "wifi": True, "power": False, "seats": "自家焙煎", "rule": "特になし", "access": "京急富岡駅 徒歩4分", "desc": "上質なコーヒーの香りに包まれる空間。高い集中力を維持できます。"},
        {"name": "SUNCOAST", "station": "京急富岡", "line": "京急本線", "lat": 35.3665, "lon": 139.6315, "category": "カフェ", "wifi": False, "power": False, "seats": "アットホーム", "rule": "特になし", "access": "京急富岡駅 徒歩3分", "desc": "ローカルならではの落ち着いた客層。平日の昼下がりが穴場。"},
        {"name": "ドトールコーヒーショップ 京急富岡駅前店", "station": "京急富岡", "line": "京急本線", "lat": 35.3672, "lon": 139.6302, "category": "カフェ", "wifi": True, "power": False, "seats": "駅チカ便利", "rule": "特になし", "access": "京急富岡駅改札すぐ", "desc": "駅前で圧倒的に便利。毎日の通学・通勤ルート上での暗記ルーティンに。"},
        {"name": "タリーズコーヒー 京急富岡周辺", "station": "京急富岡", "line": "京急本線", "lat": 35.3650, "lon": 139.6320, "category": "カフェ", "wifi": True, "power": True, "seats": "広域対応", "rule": "特になし", "access": "京急富岡エリア", "desc": "近隣エリアの勉強・作業スペースとして貴重なインフラ。"},

        # --- 能見台駅 ---
        {"name": "CAFE プラス 横浜", "station": "能見台", "line": "京急本線", "lat": 35.3605, "lon": 139.6290, "category": "カフェ", "wifi": True, "power": False, "seats": "スッキリ", "rule": "特になし", "access": "能見台駅 徒歩2分", "desc": "清潔感のある明るい店内。前向きな気持ちで学習に取り組めます。"},
        {"name": "スターバックスコーヒー 能見台店", "station": "能見台", "line": "京急本線", "lat": 35.3598, "lon": 139.6285, "category": "カフェ", "wifi": True, "power": True, "seats": "大テーブルあり", "rule": "混雑時席詰め", "access": "能見台駅 徒歩3分", "desc": "学生や近裏住民の自習環境として広く愛用されている定番店舗。"},
        {"name": "ドトールコーヒーショップ 能見台店", "station": "能見台", "line": "京急本線", "lat": 35.3601, "lon": 139.6288, "category": "カフェ", "wifi": True, "power": False, "seats": "駅前", "rule": "特になし", "access": "能見台駅 徒歩1分", "desc": "サクッと1時間だけ集中して問題集を解く、といった使い方に最適。"},
        {"name": "タリーズコーヒー 能見台店", "station": "能見台", "line": "京急本線", "lat": 35.3610, "lon": 139.6295, "category": "カフェ", "wifi": True, "power": True, "seats": "カウンター電源", "rule": "特になし", "access": "能見台駅 徒歩2分", "desc": "コンセント席があり、タブレット等を用いた映像授業の受講にも便利。"},
        {"name": "コメダ珈琲店 能見台店", "station": "能見台", "line": "京急本線", "lat": 35.3620, "lon": 139.6270, "category": "カフェ", "wifi": True, "power": True, "seats": "広大な座席", "rule": "時間制限あり", "access": "能見台駅 徒歩5分", "desc": "非常にゆったりとしたボックス席。週末にがっつり勉強したい時に。"},
        {"name": "珈琲館 能見台店", "station": "能見台", "line": "京急本線", "lat": 35.3595, "lon": 139.6292, "category": "カフェ", "wifi": True, "power": True, "seats": "落ち着き空間", "rule": "特になし", "access": "能見台駅 徒歩2分", "desc": "上質なBGMと珈琲。集中して大人の資格勉強を進めたい際のおすすめ。"},

        # --- 高島町駅 ---
        {"name": "minato coffee", "station": "高島町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4590, "lon": 139.6230, "category": "カフェ", "wifi": False, "power": False, "seats": "コーヒースタンド調", "rule": "短時間向け", "access": "高島町駅 徒歩3分", "desc": "こだわりの珈琲をサッと補給し、頭をすっきりさせて学習モードに入れる場所。"},
        {"name": "Café de Crié Grand Queens Square", "station": "高島町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4573, "lon": 139.6225, "category": "カフェ", "wifi": True, "power": True, "seats": "大型", "rule": "特になし", "access": "高島町・みなとみらい境界", "desc": "高島町側からもアクセス良好。電源席が充実した手堅いデスクワーク環境。"},
        {"name": "THE ROYAL CAFE YOKOHAMA", "station": "高島町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4646, "lon": 139.6220, "category": "カフェ", "wifi": True, "power": True, "seats": "ラグジュアリー", "rule": "マナー厳守", "access": "高島町・横浜駅境界", "desc": "水戸岡鋭治氏デザインの上質カフェ。ここぞという時の集中空間として極めて優秀。"},
        {"name": "スターバックスコーヒー 横浜スカイビル店", "station": "高島町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4650, "lon": 139.6240, "category": "カフェ", "wifi": True, "power": True, "seats": "高層ビル下", "rule": "制限あり", "access": "高島町・横浜駅東口境界", "desc": "スカイビル内。立地が良く、ビジネス・自習目的の利用者が常に多数。"},
        {"name": "タリーズコーヒー 横浜東口店", "station": "高島町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4640, "lon": 139.6245, "category": "カフェ", "wifi": True, "power": True, "seats": "ビジネス最適", "rule": "特になし", "access": "高島町・横浜東口エリア", "desc": "オフィス街寄りのため、週末や平日の夜は勉強・作業スペースとして最適。"},
        {"name": "ドトールコーヒーショップ 横浜東口店", "station": "高島町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4635, "lon": 139.6250, "category": "カフェ", "wifi": True, "power": False, "seats": "コンパクト", "rule": "特になし", "access": "高島町・横浜東口徒歩圏", "desc": "サクッと本を開いて短時間の暗記・インプットを行うのに非常に効率的。"},

        # --- 伊勢佐木長者町駅 ---
        {"name": "Oriental grace coffee", "station": "伊勢佐木長者町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4410, "lon": 139.6335, "category": "カフェ", "wifi": True, "power": True, "seats": "洗練空間", "rule": "特になし", "access": "伊勢佐木長者町駅 徒歩3分", "desc": "非常に落ち着いたインテリアと上質な珈琲。大人の集中学習環境として極めて優秀。"},
        {"name": "Coffee-kan Isezaki-Cho", "station": "伊勢佐木長者町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4425, "lon": 139.6340, "category": "カフェ", "wifi": True, "power": True, "seats": "落ち着き空間", "rule": "特になし", "access": "伊勢佐木長者町駅 徒歩2分", "desc": "安定の珈琲館ブランド。静かなBGMが流れており、参考書をじっくり読み込めます。"},
        {"name": "Mameya Roastery", "station": "伊勢佐木長者町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4405, "lon": 139.6350, "category": "カフェ", "wifi": False, "power": False, "seats": "自家焙煎調", "rule": "読書向き", "access": "伊勢佐木長者町駅 徒歩5分", "desc": "本格派のロースタリーカフェ。香ばしい香りに包まれながらの思考の整理やインプットに。"},
        {"name": "Yokohama Bunmeido Shop & Le Café", "station": "伊勢佐木長者町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4430, "lon": 139.6330, "category": "カフェ", "wifi": False, "power": False, "seats": "老舗喫茶", "rule": "特になし", "access": "伊勢佐木長者町駅 徒歩4分", "desc": "文明堂が手がける上品なカフェ。落ち着いた雰囲気でリラックスしながら勉強可能。"},
        {"name": "ぽえむ 伊勢佐木町店", "station": "伊勢佐木長者町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4420, "lon": 139.6325, "category": "カフェ", "wifi": False, "power": False, "seats": "レトロ", "rule": "特になし", "access": "伊勢佐木長者町駅 徒歩3分", "desc": "歴史を感じる静かな空間。余計なデジタル情報を遮断して集中したいときに。"},
        {"name": "coffee エリーゼ", "station": "伊勢佐木長者町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4415, "lon": 139.6310, "category": "カフェ", "wifi": False, "power": False, "seats": "純喫茶", "rule": "特になし", "access": "伊勢佐木長者町駅 徒歩4分", "desc": "昭和レトロな隠れ家的名店。地元の方に愛される静かな環境です。"},
        {"name": "荒井屋カフェ（喫茶マエカワ）", "station": "伊勢佐木長者町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4400, "lon": 139.6360, "category": "カフェ", "wifi": False, "power": False, "seats": "コンパクト", "rule": "特になし", "access": "伊勢佐木長者町駅 徒歩6分", "desc": "静かな空間が保たれており、隙間時間での暗記作業などにぴったり。"},
        {"name": "ぼんぐ", "station": "伊勢佐木長者町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4435, "lon": 139.6320, "category": "カフェ", "wifi": False, "power": False, "seats": "ノスタルジック", "rule": "特になし", "access": "伊勢佐木長者町駅 徒歩5分", "desc": "街の喧騒から一歩離れた静寂。ノートを広げてアイデアをまとめる作業に。"},

        # --- その他の新駅周辺カフェデータ（全エリア適合完了） ---
        {"name": "タリーズコーヒー 綱島駅前店", "station": "綱島", "line": "東急東横線", "lat": 35.5368, "lon": 139.6342, "category": "カフェ", "wifi": True, "power": True, "seats": "約45席", "rule": "特になし", "access": "綱島駅東口 徒歩1分", "desc": "【電源あり】カウンター席にコンセント完備。ビジネス利用も多く集中しやすい環境。"},
        {"name": "ドトールコーヒーショップ 綱島西口店", "station": "綱島", "line": "東急東横線", "lat": 35.5362, "lon": 139.6338, "category": "カフェ", "wifi": True, "power": False, "seats": "約50席", "rule": "特になし", "access": "綱島駅西口 徒歩2分", "desc": "駅前の便利な店舗。サクッと短時間のインプットや読書におすすめ。"},
        {"name": "テラコーヒー 白楽店", "station": "白楽", "line": "東急東横線", "lat": 35.4912, "lon": 139.6265, "category": "カフェ", "wifi": False, "power": False, "seats": "約15席", "rule": "席数少なめのため読書向け", "access": "白楽駅西口 徒歩1分", "desc": "こだわりの自家焙煎珈琲店。静かに本を読んだり思考を整理するのに最適。"},
        {"name": "ドトールコーヒーショップ 白楽駅前店", "station": "白楽", "line": "東急東横線", "lat": 35.4902, "lon": 139.6269, "category": "カフェ", "wifi": True, "power": False, "seats": "約40席", "rule": "特になし", "access": "白楽駅西口すぐ", "desc": "改札目の前でアクセス抜群。大学が近いため学生の自習利用も多い。"},
        {"name": "ミスタードーナツ いずみ野ショップ", "station": "いずみ野", "line": "相鉄いずみ野線", "lat": 35.4185, "lon": 139.4955, "category": "カフェ", "wifi": True, "power": False, "seats": "約35席", "rule": "特になし", "access": "いずみ野駅直結", "desc": "駅高架下の店舗。平日の昼下がりなど比較的落ち着いて作業ができます。"},
        {"name": "相鉄ライフいずみ野 休憩スペース", "station": "いずみ野", "line": "相鉄いずみ野線", "lat": 35.4190, "lon": 139.4960, "category": "図書館", "wifi": False, "power": False, "seats": "約20席", "rule": "共用エリアのためマナー遵守", "access": "いずみ野駅徒歩2分", "desc": "ライフ内にあるオープンな休憩スペース。軽めのノート作業や読書に。"},
        {"name": "ドトールコーヒーショップ 京急弘明寺店", "station": "弘明寺(京急)", "line": "京急本線", "lat": 35.4245, "lon": 139.5980, "category": "カフェ", "wifi": True, "power": False, "seats": "約45席", "rule": "特になし", "access": "京急弘明寺駅改札すぐ", "desc": "駅直結で雨の日も快適. 商店街や公園の近くで落ち着いた客層。"},
        {"name": "ガスト 弘明寺店", "station": "弘明寺(地下鉄)", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4245, "lon": 139.6080, "category": "カフェ", "wifi": True, "power": True, "seats": "約80席", "rule": "深夜利用可 / 混雑時制限あり", "access": "地下鉄弘明寺駅 徒歩2分", "desc": "すかいらーくWi-Fiとコンセント完備。席が広く、参考書を何冊も広げやすい。"},
        {"name": "マクドナルド 井土ヶ谷店", "station": "井土ヶ谷", "line": "京急本線", "lat": 35.4335, "lon": 139.5992, "category": "カフェ", "wifi": True, "power": True, "seats": "約70席", "rule": "特になし", "access": "井土ヶ谷駅 徒歩1分", "desc": "【電源あり】カウンター席に充電設備あり。駅からすぐでクイックな学習に便利。"},
        {"name": "ミスタードーナツ 杉田ショップ", "station": "杉田", "line": "京急本線", "lat": 35.3815, "lon": 139.6205, "category": "カフェ", "wifi": True, "power": False, "seats": "約40席", "rule": "特になし", "access": "杉田駅直結 プララ杉田内", "desc": "京急杉田駅直結。適度な賑やかさがあり、リラックスして勉強できます。"},
        {"name": "上島珈琲店 金沢八景店", "station": "金沢八景", "line": "京急本線", "lat": 35.3272, "lon": 139.6212, "category": "カフェ", "wifi": True, "power": True, "seats": "約50席", "rule": "特になし", "access": "金沢八景駅 徒歩1分", "desc": "【電源あり】大学が近いエリア。レトロでモダンな空間で長時間の勉強に抜群。"},
        {"name": "プロント 湘南台店", "station": "湘南台", "line": "相鉄いずみ野線", "lat": 35.3965, "lon": 139.4668, "category": "カフェ", "wifi": True, "power": True, "seats": "約60席", "rule": "カウンター席のみ電源利用可", "access": "湘南台駅西口 徒歩1分", "desc": "【電源あり】一人用カウンター席が充実しており、PC作業や自習、仕事帰りの資格勉強に最適。"},
        {"name": "スターバックス 湘南台駅ビル店", "station": "湘南台", "line": "小田急江ノ島線", "lat": 35.3960, "lon": 139.4662, "category": "カフェ", "wifi": True, "power": True, "seats": "約45席", "rule": "特になし", "access": "湘南台駅直結", "desc": "駅構内にあるスタバ。ビジネスパーソンや学生が常に作業をしています。"},
        {"name": "珈琲舎YOKOHAMA 阪東橋店", "station": "阪東橋", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4375, "lon": 139.6275, "category": "カフェ", "wifi": True, "power": False, "seats": "約40席", "rule": "特になし", "access": "阪東橋駅 徒歩1分", "desc": "駅からのアクセスが良く便利。適度な静けさがあり、自習利用に適しています。"},
        {"name": "ショコラ", "station": "阪東橋", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4368, "lon": 139.6265, "category": "カフェ", "wifi": False, "power": False, "seats": "約25席", "rule": "特になし", "access": "阪東橋駅 徒歩3分", "desc": "落ち着いた客層が集まる小さな喫茶店。リラックスして読書したい時に。"},
        {"name": "アマデウス・カフェ", "station": "阪東橋", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4380, "lon": 139.6285, "category": "カフェ", "wifi": True, "power": False, "seats": "約35席", "rule": "特になし", "access": "阪東橋駅 徒歩4分", "desc": "心地よい音楽が流れる欧風カフェ。手帳の整理やノート学習が捗ります。"},
        {"name": "三番館", "station": "阪東橋", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4365, "lon": 139.6290, "category": "カフェ", "wifi": False, "power": False, "seats": "約50席", "rule": "特になし", "access": "阪東橋駅 徒歩5分", "desc": "パーテーション効果のあるボックス席が多く、周囲の視線を気にせず学習可能。"},
        {"name": "cafe PLUS", "station": "吉野町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4335, "lon": 139.6220, "category": "カフェ", "wifi": True, "power": False, "seats": "約30席", "rule": "特になし", "access": "吉野町駅 徒歩1分", "desc": "モダンで清潔感あふれる空間。集中してインプットしたい日の自習に。"},
        {"name": "カフェ カベ―", "station": "吉野町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4340, "lon": 139.6210, "category": "カフェ", "wifi": False, "power": False, "seats": "約25席", "rule": "特になし", "access": "吉野町駅 徒歩2分", "desc": "アットホームで非常に落ち着いたお店。平日の昼間が狙い目の自習穴場。"},
        {"name": "BAR CAFE Tails", "station": "吉野町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4330, "lon": 139.6225, "category": "カフェ", "wifi": True, "power": True, "seats": "約40席", "rule": "特になし", "access": "吉野町駅 徒歩1分", "desc": "カフェタイムの利用が非常に快適。コンセント完備でPC作業環境としても優秀。"},
        {"name": "マウンテン", "station": "吉野町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4345, "lon": 139.6230, "category": "カフェ", "wifi": False, "power": False, "seats": "約50席", "rule": "特になし", "access": "吉野町駅 徒歩3分", "desc": "広めのテーブルでゆったりとテキストを開ける、昔ながらの落ち着いた名店。"},
        {"name": "ルシェール", "station": "吉野町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4325, "lon": 139.6215, "category": "カフェ", "wifi": False, "power": False, "seats": "約20席", "rule": "特になし", "access": "吉野町駅 徒歩4分", "desc": "静寂が心地よい空間。じっくり深い読解作業などに取り組みたい時におすすめ。"},
        {"name": "わみん", "station": "吉野町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4338, "lon": 139.6200, "category": "カフェ", "wifi": False, "power": False, "seats": "約30席", "rule": "特になし", "access": "吉野町駅 徒歩3分", "desc": "地元民に親しまれる居心地の良い喫茶店。リラックスして自習ができます。"},
        {"name": "トミー", "station": "吉野町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4350, "lon": 139.6220, "category": "カフェ", "wifi": False, "power": False, "seats": "約15席", "rule": "特になし", "access": "吉野町駅 徒歩2分", "desc": "手軽に立ち寄れるコンパクトな空間。朝や仕事・学校帰りのクイック暗記に。"},
        {"name": "キーズカフェ 横浜蒔田店", "station": "蒔田", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4270, "lon": 139.6145, "category": "カフェ", "wifi": True, "power": True, "seats": "約55席", "rule": "混雑時配慮", "access": "蒔田駅 徒歩2分", "desc": "商業施設内の綺麗なカフェ。Wi-Fiと電源が安定しており、現代的な学習スタイルに最適。"},
        {"name": "カフェ・ククル", "station": "蒔田", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4265, "lon": 139.6135, "category": "カフェ", "wifi": False, "power": False, "seats": "約20席", "rule": "特になし", "access": "蒔田駅 徒歩4分", "desc": "温かみのある店内で、落ち着いて読書やノートまとめ作業に没頭できます。"},
        {"name": "COFFEE SHOP 越路", "station": "蒔田", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4275, "lon": 139.6130, "category": "カフェ", "wifi": False, "power": False, "seats": "約35席", "rule": "特になし", "access": "蒔田駅 徒歩3分", "desc": "地元密着型の落ち着いたレトロ喫茶。平日は非常に静かな環境が保たれています。"},
        {"name": "アスカ", "station": "蒔田", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4280, "lon": 139.6150, "category": "カフェ", "wifi": False, "power": False, "seats": "約15席", "rule": "特になし", "access": "蒔田駅 徒歩2分", "desc": "駅からすぐの好立地。移動途中にサクッと1セクション問題を解くような場面に。"},
        {"name": "栞コーヒーハウス", "station": "蒔田", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4260, "lon": 139.6120, "category": "カフェ", "wifi": False, "power": False, "seats": "約25席", "rule": "静寂遵守", "access": "蒔田駅 徒歩5分", "desc": "読書や思考、じっくりとした語学学習に驚くほど集中できる洗練された静寂空間。"},
        {"name": "cafe SOPRA", "station": "片倉町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4855, "lon": 139.6030, "category": "カフェ", "wifi": True, "power": False, "seats": "約30席", "rule": "特になし", "access": "片倉町駅 徒歩2分", "desc": "陽の光が入る気持ちの良い空間。前向きな気持ちでデスクワークが進みます。"},
        {"name": "キリン食堂", "station": "片倉町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4845, "lon": 139.6040, "category": "カフェ", "wifi": False, "power": False, "seats": "約25席", "rule": "特になし", "access": "片倉町駅 徒歩3分", "desc": "どこかほっとする空間。リラックスした状態でノートの整理や暗記作業が可能。"},
        {"name": "こむぎ", "station": "片倉町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4860, "lon": 139.6025, "category": "カフェ", "wifi": False, "power": False, "seats": "約20席", "rule": "特になし", "access": "片倉町駅 徒歩4分", "desc": "ローカルならではののんびりした空気が漂う。混雑が少なくマイペースに自習できます。"},
        {"name": "ドトールコーヒーショップ EneJet六角橋", "station": "片倉町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4875, "lon": 139.6080, "category": "カフェ", "wifi": True, "power": False, "seats": "約45席", "rule": "特になし", "access": "片倉町駅 徒歩10分", "desc": "SS併設のドトール。独自の客層で混雑が偏りにくく、穴場の作業スペース。"},
        {"name": "岸根公園ひだまりカフェ", "station": "片倉町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4910, "lon": 139.6095, "category": "カフェ", "wifi": False, "power": False, "seats": "約30席", "rule": "特になし", "access": "片倉町・岸根公園エリア", "desc": "緑豊かなエリアにある開放的なカフェ。リフレッシュを兼ねた勉強環境に。"},
        {"name": "上町ベーカリー&カフェ", "station": "三ツ沢上町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4748, "lon": 139.6055, "category": "カフェ", "wifi": False, "power": False, "seats": "約15席", "rule": "特になし", "access": "三ツ沢上町駅 徒歩1分", "desc": "焼きたてパンの香りが心地よい。午前中の早い時間帯の勉強ルーティンに◎。"},
        {"name": "むさしの森珈琲 三ツ沢店", "station": "三ツ沢上町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4760, "lon": 139.6020, "category": "カフェ", "wifi": True, "power": True, "seats": "約90席", "rule": "混雑時利用制限", "access": "三ツ沢上町駅 徒歩7分", "desc": "【電源・Wi-Fi完備】極上のソファ席と広いデスク。長時間のガッツリ自習に最高の環境。"},
        {"name": "leaf cafe", "station": "三ツ沢上町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4735, "lon": 139.6070, "category": "カフェ", "wifi": True, "power": False, "seats": "約25席", "rule": "特になし", "access": "三ツ沢上町駅 徒歩4分", "desc": "緑を基調とした爽やかな店内。落ち着いた環境で集中力を維持しやすい。"},
        {"name": "B'EASE 横浜市立市民病院店", "station": "三ツ沢上町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4720, "lon": 139.5990, "category": "カフェ", "wifi": True, "power": True, "seats": "約40席", "rule": "マナー厳守", "access": "三ツ沢上町駅 徒歩12分", "desc": "病院内併設の非常に清潔・静寂なスペース。インフラが整っており穴場。"},
        {"name": "上町カフェ", "station": "三ツ沢上町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4742, "lon": 139.6050, "category": "カフェ", "wifi": False, "power": False, "seats": "約20席", "rule": "特になし", "access": "三ツ沢上町駅 徒歩2分", "desc": "温かみのある接客と落ち着いた客層。リラックスして文章を読みたい時に。"},
        {"name": "NAGI COFFEE", "station": "三ツ沢下町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4738, "lon": 139.6140, "category": "カフェ", "wifi": True, "power": False, "seats": "約25席", "rule": "特になし", "access": "三ツ沢下町駅 徒歩2分", "desc": "洗練されたこだわりの珈琲空間。高い集中力をキープして質の高い学習が可能。"},
        {"name": "ドトールコーヒーショップ 横浜南幸店", "station": "三ツ沢下町", "line": "横浜市営地下鉄ブルーライン", "lat": 35.4680, "lon": 139.6170, "category": "カフェ", "wifi": True, "power": False, "seats": "約110席", "rule": "特になし", "access": "三ツ沢下町・横浜駅境界", "desc": "横浜駅側への徒歩圏内。座席数が多く、いつでも安定して作業環境を確保。"},
        {"name": "Coffee KOBAN", "station": "東白楽", "line": "東急東横線", "lat": 35.4830, "lon": 139.6290, "category": "カフェ", "wifi": False, "power": False, "seats": "約12席", "rule": "特になし", "access": "東白楽駅 徒歩1分", "desc": "元交番の建物をリノベーションしたユニークなカフェ。気分を変えて勉強したい時に。"},
        {"name": "Coffee Bunmei（珈琲文明）", "station": "東白楽", "line": "東急東横線", "lat": 35.4850, "lon": 139.6275, "category": "カフェ", "wifi": False, "power": False, "seats": "約30席", "rule": "私語厳禁・自習配慮", "access": "東白楽・白楽エリア", "desc": "白楽白幡池近くの高名な珈琲店。完璧な静寂空間で、深い思考を要する学習に。"},
        {"name": "ドトールコーヒーショップ 東神奈川駅西口", "station": "東白楽", "line": "東急東横線", "lat": 35.4785, "lon": 139.6315, "category": "カフェ", "wifi": True, "power": False, "seats": "約60席", "rule": "特になし", "access": "東白楽駅 徒歩8分", "desc": "東神奈川駅側の便利なドトール。安定したインフラで、作業ルーティンに最適。"},
        {"name": "Kanata Cafe", "station": "妙蓮寺", "line": "東急東横線", "lat": 35.4992, "lon": 139.6315, "category": "カフェ", "wifi": True, "power": False, "seats": "約25席", "rule": "特になし", "access": "妙蓮寺駅 徒歩2分", "desc": "スタイリッシュで落ち着いた内装。気兼ねなくノートや参考書をまとめられます。"},
        {"name": "かき氷&cafe cafe saju", "station": "妙蓮寺", "line": "東急東横線", "lat": 35.4982, "lon": 139.6325, "category": "カフェ", "wifi": False, "power": False, "seats": "約20席", "rule": "特になし", "access": "妙蓮寺駅 徒歩3分", "desc": "隠れ家的なのんびり空間。平日の午前中など空いている時間帯の読書に最適。"},
        {"name": "スターバックスコーヒー 菊名店", "station": "妙蓮寺", "line": "東急東横線", "lat": 35.5095, "lon": 139.6312, "category": "カフェ", "wifi": True, "power": True, "seats": "約65席", "rule": "混雑時利用制限", "access": "妙蓮寺・菊名隣駅エリア", "desc": "隣駅の菊名駅ビル内。充実した電源席と安定したWi-Fiで作業が最も捗る。"},
        {"name": "Oldman’s CAFE", "station": "大倉山", "line": "東急東横線", "lat": 35.5225, "lon": 139.6295, "category": "カフェ", "wifi": True, "power": False, "seats": "約30席", "rule": "特になし", "access": "大倉山駅 徒歩4分", "desc": "アンティーク調の落ち着いた家具。インスピレーションを高めたい勉強に。"},
        {"name": "STAY FRESH COFFEE", "station": "大倉山", "line": "東急東横線", "lat": 35.5210, "lon": 139.6305, "category": "カフェ", "wifi": True, "power": True, "seats": "約40席", "rule": "特になし", "access": "大倉山駅 徒歩2分", "desc": "【電源・Wi-Fi完備】PCを広げて作業する人が多く、現代的な学習環境として超優秀。"},
        {"name": "スターバックスコーヒー 大倉山店", "station": "大倉山", "line": "東急東横線", "lat": 35.5218, "lon": 139.6302, "category": "カフェ", "wifi": True, "power": True, "seats": "約55席", "rule": "混雑時90分制", "access": "大倉山駅 徒歩1分", "desc": "駅前の好立地。洗練された店内で、毎日の学習モチベーションを維持できます。"},
        {"name": "ドトールコーヒーショップ 大倉山店", "station": "大倉山", "line": "東急東横線", "lat": 35.5214, "lon": 139.6300, "category": "カフェ", "wifi": True, "power": False, "seats": "約45席", "rule": "特になし", "access": "大倉山駅 徒歩1分", "desc": "改札すぐ。通学・通勤定期の途中でサクッと1時間暗記を繰り返すような使い方に。"},
        {"name": "スターバックスコーヒー 綱島店", "station": "高田", "line": "横浜市営地下鉄グリーンライン", "lat": 35.5360, "lon": 139.6340, "category": "カフェ", "wifi": True, "power": True, "seats": "約80席", "rule": "混雑時配慮", "access": "高田・綱島エリア", "desc": "綱島駅近くの大型スタバ。広域の学習・ワークインフラとして定番。"},
        {"name": "コメダ珈琲店 綱島店", "station": "高田", "line": "横浜市営地下鉄グリーンライン", "lat": 35.5380, "lon": 139.6310, "category": "カフェ", "wifi": True, "power": True, "seats": "約90席", "rule": "混雑時制限", "access": "高田・綱島エリア", "desc": "安定の広い座席。週末に重い参考書や資料を複数並べて本気で自習したい時に。"},
        {"name": "YooHooKafe", "station": "日吉本町", "line": "横浜市営地下鉄グリーンライン", "lat": 35.5520, "lon": 139.6340, "category": "カフェ", "wifi": False, "power": False, "seats": "約20席", "rule": "特になし", "access": "日吉本町駅 徒歩3分", "desc": "地域密着型ののんびりとしたカフェ。リラックスしてノートを見返すような自習に。"},
        {"name": "スターバックスコーヒー 日吉店", "station": "日吉本町", "line": "横浜市営地下鉄グリーンライン", "lat": 35.5555, "lon": 139.6465, "category": "カフェ", "wifi": True, "power": True, "seats": "約75席", "rule": "混雑時時間制限", "access": "日吉本町・日吉エリア", "desc": "大学近くの主要店。周囲も勉強している学生だらけのため、自然とやる気が刺激される。"},
        {"name": "Cafe Monchien", "station": "石川町", "line": "JR根岸線", "lat": 35.4385, "lon": 139.6425, "category": "カフェ", "wifi": False, "power": False, "seats": "約20席", "rule": "特になし", "access": "石川町駅 徒歩3分", "desc": "アットホームな雰囲気。空いている時間帯を狙って、軽めの読書や勉強に。"},
        {"name": "Coffee House ザ・カフェ", "station": "石川町", "line": "JR根岸線", "lat": 35.4430, "lon": 139.6450, "category": "カフェ", "wifi": True, "power": False, "seats": "約60席", "rule": "特になし", "access": "石川町・元町エリア", "desc": "洗練されたクラシカルな空間。大人の落ち着いた空気感の中でじっくり勉強可能。"},
        {"name": "スターバックスコーヒー 横浜元町店", "station": "石川町", "line": "JR根岸線", "lat": 35.4405, "lon": 139.6460, "category": "カフェ", "wifi": True, "power": True, "seats": "約55席", "rule": "時間制限あり", "access": "石川町駅元町口 徒歩5分", "desc": "元町ショッピングストリート内。お洒落で作業集中度の高い人気スポット。"},
        {"name": "UNI COFFEE ROASTERY 元町店", "station": "石川町", "line": "JR根岸線", "lat": 35.4412, "lon": 139.6455, "category": "カフェ", "wifi": True, "power": True, "seats": "約50席", "rule": "特になし", "access": "石川町駅 徒歩6分", "desc": "【電源・Wi-Fi完備】インテリアが美しく、PC作業や資格勉強をする人が大変多い。"},
        {"name": "ドトールコーヒーショップ 根岸店", "station": "根岸", "line": "JR根岸線", "lat": 35.4158, "lon": 139.6353, "category": "カフェ", "wifi": True, "power": False, "seats": "約45席", "rule": "特になし", "access": "根岸駅改札すぐ", "desc": "抜群の立地。毎日のルーティンとして、サクッと短時間暗記を重ねるのに極めて有効。"},
        {"name": "Three Penguins Coffee", "station": "根岸", "line": "JR根岸線", "lat": 35.4170, "lon": 139.6320, "category": "カフェ", "wifi": False, "power": False, "seats": "約20席", "rule": "読書向き", "access": "根岸駅 徒歩5分", "desc": "丁寧に淹れられた珈琲と静寂。深い集中を要するテキスト読解作業などに。"},
        {"name": "スターバックス ビーンズ新杉田店", "station": "磯子", "line": "JR根岸線", "lat": 35.3870, "lon": 139.6195, "category": "カフェ", "wifi": True, "power": True, "seats": "約50席", "rule": "利用制限あり", "access": "磯子・新杉田エリア", "desc": "新杉田駅直結でアクセス抜群。電源とWi-Fiが揃った安定の自習環境。"},
        {"name": "コメダ珈琲店 磯子店", "station": "磯子", "line": "JR根岸線", "lat": 35.3995, "lon": 139.6190, "category": "カフェ", "wifi": True, "power": True, "seats": "約80席", "rule": "混雑時時間制限", "access": "磯子駅 徒歩3分", "desc": "意心地の良いパーテーションボックス席。参考書を思い切り広げて勉強可能。"},
        {"name": "バーキングカフェ（BARKING CAFE）", "station": "洋光台", "line": "JR根岸線", "lat": 35.3785, "lon": 139.5970, "category": "カフェ", "wifi": True, "power": False, "seats": "約25席", "rule": "特になし", "access": "洋光台駅 徒歩3分", "desc": "こだわりの珈琲豆。落ち着いたローカル空間で、自分のペースでじっくり勉強。"},
        {"name": "ドトールコーヒーショップ 洋光台店", "station": "洋光台", "line": "JR根岸線", "lat": 35.3794, "lon": 139.5960, "category": "カフェ", "wifi": True, "power": False, "seats": "約40席", "rule": "特になし", "access": "洋光台駅 徒歩1分", "desc": "駅前の非常に便利な立地。朝活や隙間時間での暗記インプットに威力を発揮。"},
        {"name": "cozy-cafe DAIN", "station": "本郷台", "line": "JR根岸線", "lat": 35.3660, "lon": 139.5485, "category": "カフェ", "wifi": True, "power": True, "seats": "約30席", "rule": "特になし", "access": "本郷台駅 徒歩3分", "desc": "【電源・Wi-Fi完備】親しみやすい心地よい空間。じっくりノートをまとめる勉強に。"},
        {"name": "ドトールコーヒーショップ 本郷台店", "station": "本郷台", "line": "JR根岸線", "lat": 35.3667, "lon": 139.5498, "category": "カフェ", "wifi": True, "power": False, "seats": "約45席", "rule": "特になし", "access": "本郷台駅改札すぐ", "desc": "安定のインフラ環境。サクッと立ち寄り、高い集中力で効率的に学習を進められます。"}
    ]
    return pd.DataFrame(spots_data)

df_spots = load_spots_dataframe()

# =========================================================
# お気に入り登録機能（セッション内で一時的に保存）
# =========================================================
if "favorite_spots" not in st.session_state:
    st.session_state.favorite_spots = set()

def toggle_favorite(spot_name):
    if spot_name in st.session_state.favorite_spots:
        st.session_state.favorite_spots.remove(spot_name)
    else:
        st.session_state.favorite_spots.add(spot_name)

# =========================================================
# ナビゲーション・検索ヘッダー
# =========================================================
st.markdown("<h2 style='margin-bottom:0px; letter-spacing:-0.02em;'>📖 駅勉ガイド 横浜広域版</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-size:12px; color:#64748b; margin-top:4px;'>通勤・通学定期ルートから最適な自習空間を見つける、実用本位のデータベース</p>", unsafe_allow_html=True)
st.markdown("---")

# =========================================================
# サイドバー：お気に入り一覧（常時表示・一時保存）
# =========================================================
with st.sidebar:
    st.markdown("### ⭐ お気に入り")
    if st.session_state.favorite_spots:
        fav_df = df_spots[df_spots["name"].isin(st.session_state.favorite_spots)]
        for _, fav_row in fav_df.iterrows():
            fcol1, fcol2 = st.columns([4, 1])
            with fcol1:
                st.markdown(f"**{fav_row['name']}**<br><span style='font-size:11px;color:#64748b;'>{fav_row['station']}駅・{fav_row['category']}</span>", unsafe_allow_html=True)
            with fcol2:
                st.button("✕", key=f"remove_fav_{fav_row['name']}", on_click=toggle_favorite, args=(fav_row['name'],))
        st.caption(f"登録数: {len(st.session_state.favorite_spots)}件（このブラウザセッション内のみ保存されます）")
    else:
        st.caption("まだお気に入りは登録されていません。一覧の「⭐ 登録」ボタンから追加できます。")

search_mode = st.radio(
    "【検索軸の選択】",
    ["鉄道路線から探す（沿線指定）", "特定の駅から探す（ピンポイント）", "📍 現在地から探す（周辺検索）"],
    horizontal=True,
)

geo_mode = "現在地" in search_mode
user_coords = None
search_radius_km = 1.0

col_f1, col_f2 = st.columns([2, 2])

with col_f1:
    if geo_mode:
        st.caption("ブラウザに現在地の取得許可を求めます。位置情報の利用を許可してください。")
        location_data = get_geolocation()
        if location_data and "coords" in location_data:
            user_coords = (location_data["coords"]["latitude"], location_data["coords"]["longitude"])
            st.success(f"現在地を取得しました（緯度 {user_coords[0]:.4f} / 経度 {user_coords[1]:.4f}）")
        else:
            st.warning("現在地を取得中、または位置情報の利用が許可されていません。ブラウザの許可ダイアログをご確認ください。")
        search_radius_km = st.slider("検索範囲（半径）", min_value=0.3, max_value=5.0, value=1.0, step=0.1, format="%.1f km")
        display_title = f"■ 現在地から半径{search_radius_km:.1f}km以内の学習スポット一覧"
        ref_station = None
        target_stations = []
    elif "鉄道路線" in search_mode:
        chosen_line = st.selectbox("路線を選択してください", ALL_LINES, index=ALL_LINES.index("JR横須賀線") if "JR横須賀線" in ALL_LINES else 0)
        target_stations = [st_name for st_name, info in STATION_DATA.items() if chosen_line in info["lines"]]
        display_title = f"■ {chosen_line} 沿線の学習スポット一覧"
        
        registered_stations_in_line = [s for s in target_stations if s in df_spots["station"].values]
        ref_station = registered_stations_in_line[0] if registered_stations_in_line else (target_stations[0] if target_stations else "横浜")
    else:
        available_stations = sorted(list(set(df_spots["station"])))
        chosen_station = st.selectbox("駅を選択してください", available_stations, index=available_stations.index("横浜") if "横浜" in available_stations else 0)
        target_stations = [chosen_station]
        display_title = f"■ {chosen_station} 駅周辺の学習スポット一覧"
        ref_station = chosen_station
with col_f2:
    default_cats = ["カフェ"] if geo_mode else ["図書館", "カフェ"]
    selected_cats = st.multiselect("施設種別", ["図書館", "カフェ"], default=default_cats)
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

if geo_mode:
    if user_coords:
        filtered_df = df_spots.copy()
        filtered_df["distance_km"] = filtered_df.apply(
            lambda r: haversine_km(user_coords[0], user_coords[1], r["lat"], r["lon"]), axis=1
        )
        filtered_df = filtered_df[filtered_df["distance_km"] <= search_radius_km]
        filtered_df = filtered_df.sort_values("distance_km")
    else:
        filtered_df = pd.DataFrame(columns=list(df_spots.columns) + ["distance_km"])
else:
    filtered_df = df_spots[df_spots["station"].isin(target_stations)].copy()

if selected_cats:
    filtered_df = filtered_df[filtered_df["category"].isin(selected_cats)]
else:
    filtered_df = pd.DataFrame(columns=filtered_df.columns)

if wifi_req:
    filtered_df = filtered_df[filtered_df["wifi"]]
if power_req:
    filtered_df = filtered_df[filtered_df["power"]]

with col_main:
    st.markdown(f"<div class='line-header'>{display_title} ({len(filtered_df)}件該当)</div>", unsafe_allow_html=True)
    
    if not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            w_tag = "<span class='tag-text-active'>🛜 Wi-Fi</span>" if row['wifi'] else "<span class='tag-text'>🛜 なし</span>"
            p_tag = "<span class='tag-text-active'>🔌 電源</span>" if row['power'] else "<span class='tag-text'>🔌 なし</span>"
            
            seats_text = row['seats'] if pd.notna(row.get('seats')) else "情報なし"
            rule_text = row['rule'] if pd.notna(row.get('rule')) else "特になし"

            station_cell = f"<b>{row['station']}駅</b><br><span style='font-size:11px; color:#64748b;'>{row['access']}</span>"
            if geo_mode and "distance_km" in row and pd.notna(row.get("distance_km")):
                station_cell += f"<br><span style='font-size:11px; color:#1e3a8a; font-weight:700;'>現在地から約{row['distance_km']:.2f}km</span>"

            is_fav = row['name'] in st.session_state.favorite_spots
            name_prefix = "⭐ " if is_fav else ""

            row_html = (
                "<table class='spot-table'><tbody><tr>"
                f"<td style='width: 18%;'>{station_cell}</td>"
                f"<td style='width: 32%;'><strong style='font-size:14px; color:#1e3a8a;'>{name_prefix}{row['name']}</strong><br>"
                f"<span style='font-size:10px; color:#475569; background:#e2e8f0; padding:1px 4px; border-radius:2px; margin-right:5px; font-weight:600;'>{row['category']}</span>"
                f"<div style='margin-top:6px;'>{w_tag}{p_tag}</div></td>"
                f"<td style='width: 20%;'><span style='color:#0f172a; font-weight:bold;'>{seats_text}</span><br><span class='rule-alert'>⚠ {rule_text}</span></td>"
                f"<td style='width: 30%;'><div style='font-weight:400; color:#334155;'>{row['desc']}</div></td>"
                "</tr></tbody></table>"
            )

            table_col, fav_col = st.columns([9, 1])
            with table_col:
                st.markdown(row_html, unsafe_allow_html=True)
            with fav_col:
                btn_label = "⭐ 解除" if is_fav else "☆ 登録"
                st.button(btn_label, key=f"fav_{row['name']}", on_click=toggle_favorite, args=(row['name'],))
    else:
        st.warning("選択された条件に合致するスポットは現在登録されていません。条件を緩めてみてください。")

with col_map:
    st.markdown("<div style='font-size:13px; font-weight:bold; color:#1e293b; margin-bottom:8px;'>🌐 周辺マップ（位置確認用）</div>", unsafe_allow_html=True)
    
    if geo_mode and user_coords:
        center_lat, center_lon = user_coords
        zoom_level = 15
    elif ref_station in STATION_DATA:
        center_lat, center_lon = STATION_DATA[ref_station]["coords"]
        zoom_level = 13
    else:
        center_lat, center_lon = (35.4657, 139.6223)
        zoom_level = 13
        
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level, tiles="OpenStreetMap")

    if geo_mode and user_coords:
        folium.Marker(
            [user_coords[0], user_coords[1]],
            tooltip="現在地",
            icon=folium.Icon(color="red", icon="user", prefix="fa"),
        ).add_to(m)
        folium.Circle(
            [user_coords[0], user_coords[1]],
            radius=search_radius_km * 1000,
            color="#1e3a8a",
            fill=True,
            fill_opacity=0.05,
        ).add_to(m)

    if not filtered_df.empty:
        for _, spot in filtered_df.iterrows():
            is_fav = spot['name'] in st.session_state.favorite_spots
            pin_color = "orange" if is_fav else ("blue" if spot['category'] == "図書館" else "cadetblue")
            seats_text = spot['seats'] if pd.notna(spot.get('seats')) else "情報なし"
            
            popup_html = f"""
            <div style='font-family:sans-serif; font-size:12px; line-height:1.4; width:200px;'>
                <strong>{'⭐ ' if is_fav else ''}{spot['name']}</strong> ({seats_text})<br>
                <span style='color:#64748b;'>{spot['access']}</span>
            </div>
            """
            folium.Marker(
                [spot["lat"], spot["lon"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=spot["name"],
                icon=folium.Icon(color=pin_color, icon="star" if is_fav else "info-sign")
            ).add_to(m)

    map_key_ref = "geo" if geo_mode else ref_station
    st_folium(m, width="100%", height=480, key=f"map_{search_mode}_{map_key_ref}")

# =========================================================
# フッター
# =========================================================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; font-size: 11px; color: #94a3b8; padding-top: 5px;'>
        駅勉ガイド 横浜広域版 | 当サイトは公開データを基にしたデータベースです。<br>
        最新の利用ルールや開館時間は各施設の公式サイトを直接ご確認ください。
    </div>

    streamlit
pandas
folium
streamlit-folium
streamlit-js-eval
""", unsafe_allow_html=True)
