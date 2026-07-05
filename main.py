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
# 駅の座標データ
# =========================================================
STATION_COORDS = {
    "横浜":     (35.4657, 139.6223),
    "新横浜":   (35.5074, 139.6175),
    "戸塚":     (35.4008, 139.5341),
    "東戸塚":   (35.4181, 139.5474),
    "保土ケ谷": (35.4468, 139.5936),
    "大船":     (35.3555, 139.5307),
    "鶴見":     (35.5074, 139.6762),
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
    "桜木町":   (35.4503, 139.6313),
    "日ノ出町": (35.4433, 139.6267),
    "山手":     (35.4269, 139.6466),
    "東神奈川": (35.4778, 139.6322),
    "星川":     (35.4568, 139.6000),
    "馬車道":   (35.4491, 139.6361),
    "関内":     (35.4442, 139.6364),
    "日本大通り": (35.4475, 139.6425),
    "あざみ野": (35.5687, 139.5535),
    "新杉田":   (35.3868, 139.6198),
    "港南台":   (35.3752, 139.5668),
}
STATIONS = sorted(list(STATION_COORDS.keys()))

# =========================================================
# 勉強スポットのデータベース（図書館 + カフェ全100店舗）
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

    # --- カフェデータ（横浜・新横浜） ---
    {"name": "スターバックス 横浜西口店", "station": "横浜", "lat": 35.4645, "lon": 139.6210, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅西口 徒歩3分", "desc": "定番のスタバ。作業や勉強に集中しやすい環境です。"},
    {"name": "タリーズコーヒー NEWoMan横浜店", "station": "横浜", "lat": 35.4661, "lon": 139.6225, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅直結 NEWoMan内", "desc": "駅直結の綺麗で洗練された店舗。デスクワークも快適。"},
    {"name": "ドトールコーヒー 横浜西口店", "station": "横浜", "lat": 35.4640, "lon": 139.6205, "category": "カフェ", "wifi": True, "power": False, "access": "横浜駅西口 徒歩2分", "desc": "サクッと短時間集中したい時におすすめの手軽なカフェ。"},
    {"name": "エクセルシオールカフェ 横浜駅西口店", "station": "横浜", "lat": 35.4643, "lon": 139.6208, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅西口 徒歩3分", "desc": "コンセント席も用意されておりPC作業に向いています。"},
    {"name": "カフェ・ド・クリエ 横浜北幸店", "station": "横浜", "lat": 35.4655, "lon": 139.6185, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅西口 徒歩6分", "desc": "北幸のオフィス街近くにあり、落ち着いた雰囲気で作業可能です。"},
    {"name": "プロント 横浜店", "station": "横浜", "lat": 35.4648, "lon": 139.6215, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅西口 徒歩2分", "desc": "一人用席が充実しています。"},
    {"name": "珈琲館 横浜西口店", "station": "横浜", "lat": 35.4650, "lon": 139.6190, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅西口 徒歩4分", "desc": "落ち着いた席の配置で作業がはかどります。"},
    {"name": "星乃珈琲店 横浜店", "station": "横浜", "lat": 35.4642, "lon": 139.6212, "category": "カフェ", "wifi": False, "power": False, "access": "横浜駅西口 徒歩3分", "desc": "ゆったりしたソファ席が多く、読書やノートでの勉強に最適。"},
    {"name": "ブルーボトルコーヒー NEWoMan横浜店", "station": "横浜", "lat": 35.4663, "lon": 139.6228, "category": "カフェ", "wifi": True, "power": False, "access": "横浜駅直結 NEWoMan内", "desc": "開放的でスタイリッシュな空間。リフレッシュを兼ねた勉強に。"},
    {"name": "タリーズコーヒー CeeU Yokohama店", "station": "横浜", "lat": 35.4635, "lon": 139.6198, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅西口 CeeU Yokohama内", "desc": "商業施設内のタリーズ。デスクワーク席あり。"},
    {"name": "スターバックス ルミネ横浜店", "station": "横浜", "lat": 35.4654, "lon": 139.6227, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅東口 ルミネ内", "desc": "ルミネの中にあるスタバ。駅内からのアクセスが非常に良い。"},
    {"name": "スターバックス そごう横浜店", "station": "横浜", "lat": 35.4652, "lon": 139.6245, "category": "カフェ", "wifi": True, "power": False, "access": "横浜駅東口 そごう内", "desc": "そごう横浜店内。隙間時間の作業に。"},
    {"name": "ゴンチャ 横浜西口店", "station": "横浜", "lat": 35.4638, "lon": 139.6200, "category": "カフェ", "wifi": True, "power": False, "access": "横浜駅西口 徒歩4分", "desc": "人気の台湾ティー専門店。学生の利用が多く、気軽に寄れます。"},
    {"name": "猿田彦珈琲 横浜店", "station": "横浜", "lat": 35.4660, "lon": 139.6218, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅周辺", "desc": "こだわりの珈琲を味わいながら、リラックスして作業に取り組めます。"},
    {"name": "UNI COFFEE ROASTERY 横浜駅西口店", "station": "横浜", "lat": 35.4662, "lon": 139.6180, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅西口 徒歩7分", "desc": "Wi-Fi・電源完備でクリエイティブな作業に最適。"},
    {"name": "24/7 coffee&roaster 横浜", "station": "横浜", "lat": 35.4656, "lon": 139.6235, "category": "カフェ", "wifi": True, "power": False, "access": "横浜駅周辺", "desc": "落ち着いたカフェ空間です。"},
    {"name": "THE ROYAL CAFE YOKOHAMA MONTE ROSA", "station": "横浜", "lat": 35.4646, "lon": 139.6220, "category": "カフェ", "wifi": True, "power": True, "access": "横浜駅構内エリア", "desc": "特別感のある上質なカフェ。大人の作業スペースとして最適。"},
    {"name": "GINZA WEST Bay Cafe Yokohama", "station": "横浜", "lat": 35.4641, "lon": 139.6195, "category": "カフェ", "wifi": False, "power": False, "access": "横浜駅西口周辺", "desc": "非常に落ち着いた空間でじっくり読書や勉強ができます。"},
    {"name": "スターバックス キュービックプラザ新横浜店", "station": "新横浜", "lat": 35.5076, "lon": 139.6178, "category": "カフェ", "wifi": True, "power": True, "access": "新横浜駅直結", "desc": "駅直結ビル内。PC作業利用が多い店舗。"},
    {"name": "タリーズコーヒー 新横浜店", "station": "新横浜", "lat": 35.5080, "lon": 139.6165, "category": "カフェ", "wifi": True, "power": True, "access": "新横浜駅 徒歩2分", "desc": "コンセント席も完備されているためデスクワークに最適。"},
    {"name": "ドトールコーヒー 新横浜駅店", "station": "新横浜", "lat": 35.5072, "lon": 139.6172, "category": "カフェ", "wifi": True, "power": False, "access": "新横浜駅構内", "desc": "駅近でサクッと移動前後に勉強を進めるのに重宝します。"},
    {"name": "エクセルシオールカフェ 新横浜店", "station": "新横浜", "lat": 35.5085, "lon": 139.6170, "category": "カフェ", "wifi": True, "power": True, "access": "新横浜駅 徒歩3分", "desc": "席数が比較的多く、ゆったりと落ち着いて勉強に取り組めます。"},
    {"name": "PRONTO 新横浜店", "station": "新横浜", "lat": 35.5068, "lon": 139.6185, "category": "カフェ", "wifi": True, "power": True, "access": "新横浜駅 徒歩4分", "desc": "カウンター席に電源があり、PC作業がしやすいです。"},
    {"name": "珈琲館 新横浜店", "station": "新横浜", "lat": 35.5090, "lon": 139.6160, "category": "カフェ", "wifi": True, "power": True, "access": "新横浜駅 徒歩5分", "desc": "静かに集中したい日の自習におすすめ。"},
    {"name": "スターバックス 新横浜駅店", "station": "新横浜", "lat": 35.5071, "lon": 139.6176, "category": "カフェ", "wifi": True, "power": True, "access": "新横浜駅構内", "desc": "ビジネスマンが多いため、作業に集中しやすい雰囲気です。"},

    # --- カフェデータ（新規追加分） ---
    {"name": "スターバックス CIAL桜木町店", "station": "桜木町", "lat": 35.4508, "lon": 139.6315, "category": "カフェ", "wifi": True, "power": True, "access": "桜木町駅直結 CIAL内", "desc": "駅直結で非常に便利。仕事や勉強の隙間時間に最適。"},
    {"name": "スターバックス コレットマーレ店", "station": "桜木町", "lat": 35.4518, "lon": 139.6305, "category": "カフェ", "wifi": True, "power": True, "access": "桜木町駅 徒歩1分", "desc": "窓側席からの景色が良く、リフレッシュしながら勉強できます。"},
    {"name": "ドトールコーヒー 桜木町店", "station": "桜木町", "lat": 35.4501, "lon": 139.6310, "category": "カフェ", "wifi": True, "power": False, "access": "桜木町駅 徒歩1分", "desc": "駅前の便利な立地。サクッと集中したいときに重宝。"},
    {"name": "タリーズコーヒー 桜木町クロスゲート店", "station": "桜木町", "lat": 35.4495, "lon": 139.6325, "category": "カフェ", "wifi": True, "power": True, "access": "桜木町駅 徒歩3分", "desc": "比較的席数が多く、落ち着いてデスクワークができる環境。"},
    {"name": "PRONTO CIAL桜木町店", "station": "桜木町", "lat": 35.4506, "lon": 139.6318, "category": "カフェ", "wifi": True, "power": True, "access": "桜木町駅直結", "desc": "一人用カウンター席が使いやすく、充電もバッチリ。"},
    {"name": "珈琲館 桜木町店", "station": "桜木町", "lat": 35.4488, "lon": 139.6300, "category": "カフェ", "wifi": True, "power": True, "access": "桜木町駅 徒歩4分", "desc": "クラシックな空間で静かに考え事をしたり自習したりできます。"},
    {"name": "UNI COFFEE ROASTERY 横浜赤レンガ倉庫店", "station": "桜木町", "lat": 35.4525, "lon": 139.6428, "category": "カフェ", "wifi": True, "power": False, "access": "桜木町駅 徒歩15分", "desc": "赤レンガ倉庫内。ロケーション抜群で読書などに向いています。"},
    {"name": "ブルーボトルコーヒー みなとみらいカフェ", "station": "桜木町", "lat": 35.4550, "lon": 139.6318, "category": "カフェ", "wifi": True, "power": False, "access": "みなとみらい駅近く", "desc": "天井が高く開放的な空間。気分転換の作業スペースに。"},
    {"name": "アニヴェルセルカフェ みなとみらい横浜", "station": "桜木町", "lat": 35.4530, "lon": 139.6360, "category": "カフェ", "wifi": True, "power": False, "access": "桜木町駅 徒歩10分", "desc": "お洒落な雰囲気でモチベーションを上げたい時に。"},
    {"name": "スターバックス ランドマークプラザ店", "station": "桜木町", "lat": 35.4552, "lon": 139.6310, "category": "カフェ", "wifi": True, "power": True, "access": "桜木町駅 徒歩5分", "desc": "ランドマーク内のスタバ。自習客も多いです。"},
    {"name": "スターバックス 横浜市役所ラクシスフロント店", "station": "馬車道", "lat": 35.4492, "lon": 139.6365, "category": "カフェ", "wifi": True, "power": True, "access": "馬車道駅直結", "desc": "市役所ビル内。新しく非常に綺麗で作業しやすい環境。"},
    {"name": "タリーズコーヒー 横浜市役所ラクシスフロント店", "station": "馬車道", "lat": 35.4490, "lon": 139.6362, "category": "カフェ", "wifi": True, "power": True, "access": "馬車道駅直結", "desc": "川沿いのテラス付近にあり、明るく開放的なスペース。"},
    {"name": "ドトールコーヒー 関内大通り店", "station": "関内", "lat": 35.4448, "lon": 139.6358, "category": "カフェ", "wifi": True, "power": False, "access": "関内駅 徒歩3分", "desc": "大通り沿いでアクセスしやすい。短時間のインプットに。"},
    {"name": "スターバックス 関内馬車道店", "station": "関内", "lat": 35.4455, "lon": 139.6352, "category": "カフェ", "wifi": True, "power": True, "access": "関内駅 徒歩4分", "desc": "PC作業向け席あり。歴史ある馬車道のスタバ。"},
    {"name": "タリーズコーヒー 関内店", "station": "関内", "lat": 35.4435, "lon": 139.6370, "category": "カフェ", "wifi": True, "power": True, "access": "関内駅 徒歩2分", "desc": "ビジネスマンの利用が多く、落ち着いて自習に励める空間。"},
    {"name": "エクセルシオールカフェ 関内セルテ店", "station": "関内", "lat": 35.4438, "lon": 139.6366, "category": "カフェ", "wifi": True, "power": True, "access": "関内駅前 セルテ内", "desc": "駅の目の前。Wi-Fi・電源完備で長時間の作業もしやすい。"},
    {"name": "PRONTO 関内店", "station": "関内", "lat": 35.4445, "lon": 139.6360, "category": "カフェ", "wifi": True, "power": True, "access": "関内駅 徒歩3分", "desc": "仕切りのある席があり、集中して勉強できます。"},
    {"name": "珈琲館 関内店", "station": "関内", "lat": 35.4450, "lon": 139.6375, "category": "カフェ", "wifi": True, "power": True, "access": "関内駅 徒歩5分", "desc": "静かな珈琲専門店。落ち着いた大人の空間。"},
    {"name": "カフェ・ド・クリエ 関内店", "station": "関内", "lat": 35.4430, "lon": 139.6355, "category": "カフェ", "wifi": True, "power": True, "access": "関内駅 徒歩4分", "desc": "電源席が充実しており、ゆったりと自分のペースで進められます。"},
    {"name": "上島珈琲店 横浜関内店", "station": "関内", "lat": 35.4460, "lon": 139.6368, "category": "カフェ", "wifi": True, "power": True, "access": "関内駅 徒歩6分", "desc": "レトロでモダンな内装。集中したい勉強に抜群。"},
    {"name": "スターバックス 日本大通り店", "station": "日本大通り", "lat": 35.4478, "lon": 139.6420, "category": "カフェ", "wifi": True, "power": True, "access": "日本大通り駅 徒歩1分", "desc": "官庁街の近く。落ち着いた客層で非常に集中しやすい。"},
    {"name": "カフェ・ド・クリエ 日本大通り店", "station": "日本大通り", "lat": 35.4472, "lon": 139.6430, "category": "カフェ", "wifi": True, "power": True, "access": "日本大通り駅 徒歩2分", "desc": "広めのテーブル席があり、参考書などを広げやすい。"},
    {"name": "タリーズコーヒー 日本大通り店", "station": "日本大通り", "lat": 35.4476, "lon": 139.6415, "category": "カフェ", "wifi": True, "power": True, "access": "日本大通り駅 徒歩1分", "desc": "駅直結ビル内。天候を気にせず作業に向かえます。"},
    {"name": "UNI COFFEE ROASTERY 横浜日本大通り南店", "station": "日本大通り", "lat": 35.4465, "lon": 139.6435, "category": "カフェ", "wifi": True, "power": True, "access": "日本大通り駅 徒歩3分", "desc": "お洒落なインテリア。電源も使えて作業がスムーズです。"},
    {"name": "喫茶エレーナ 元町店", "station": "元町・中華街", "lat": 35.4375, "lon": 139.6495, "category": "カフェ", "wifi": False, "power": False, "access": "元町・中華街駅 徒歩8分", "desc": "歴史ある純喫茶。静かに本を読んだりするのに最高。"},
    {"name": "スターバックス MARK IS みなとみらい店", "station": "みなとみらい", "lat": 35.4580, "lon": 139.6320, "category": "カフェ", "wifi": True, "power": True, "access": "みなとみらい駅直結", "desc": "商業施設内の賑やかなスタバ。活気の中で勉強したい人に。"},
    {"name": "タリーズコーヒー MARK IS みなとみらい店", "station": "みなとみらい", "lat": 35.4575, "lon": 139.6322, "category": "カフェ", "wifi": True, "power": True, "access": "みなとみらい駅直結", "desc": "カウンター席にコンセントあり。PC作業の定番スポット。"},
    {"name": "ドトールコーヒー みなとみらい店", "station": "みなとみらい", "lat": 35.4565, "lon": 139.6315, "category": "カフェ", "wifi": True, "power": False, "access": "みなとみらい駅 徒歩3分", "desc": "オフィスビルエリア。平日の隙間時間の勉強に重宝。"},
    {"name": "アフタヌーンティー・ティールーム MARK IS みなとみらい", "station": "みなとみらい", "lat": 35.4582, "lon": 139.6325, "category": "カフェ", "wifi": False, "power": False, "access": "みなとみらい駅直結", "desc": "紅茶専門店。気分転換の読書スペースに。"},
    {"name": "カフェ・ド・クリエ みなとみらい店", "station": "みなとみらい", "lat": 35.4568, "lon": 139.6308, "category": "カフェ", "wifi": True, "power": True, "access": "みなとみらい駅 徒歩4分", "desc": "ビジネス街側にあるため、比較的落ち着いて作業ができます。"},
    {"name": "スターバックス 横浜ワールドポーターズ店", "station": "みなとみらい", "lat": 35.4545, "lon": 139.6385, "category": "カフェ", "wifi": True, "power": False, "access": "みなとみらい駅 徒歩8分", "desc": "ワールドポーターズ内。平日は快適。"},
    {"name": "レオニダスカフェ 横浜ワールドポーターズ店", "station": "みなとみらい", "lat": 35.4543, "lon": 139.6380, "category": "カフェ", "wifi": False, "power": False, "access": "みなとみらい駅 徒歩8分", "desc": "チョコレート専門店併設。甘いもので脳を活性化。"},
    {"name": "UNI COFFEE ROASTERY ハンマーヘッド店", "station": "みなとみらい", "lat": 35.4560, "lon": 139.6425, "category": "カフェ", "wifi": True, "power": True, "access": "みなとみらい駅 徒歩12分", "desc": "海が見える絶好のロケーション。Wi-Fiと電源完備。"},
    {"name": "Starbucks Coffee 横浜ハンマーヘッド店", "station": "みなとみらい", "lat": 35.4558, "lon": 139.6430, "category": "カフェ", "wifi": True, "power": True, "access": "みなとみらい駅 徒歩12分", "desc": "リラックスして勉強。"},
    {"name": "PIE HOLIC", "station": "みなとみらい", "lat": 35.4540, "lon": 139.6415, "category": "カフェ", "wifi": False, "power": False, "access": "みなとみらい駅 徒歩10分", "desc": "お洒落なカリフォルニアスタイル。オフの日の勉強に。"},
    {"name": "スターバックス 元町店", "station": "元町・中華街", "lat": 35.4398, "lon": 139.6510, "category": "カフェ", "wifi": True, "power": True, "access": "元町・中華街駅 徒歩3分", "desc": "元町商店街の中。落ち着いた客層でPC作業が進みます。"},
    {"name": "上島珈琲店 山下公園店", "station": "元町・中華街", "lat": 35.4435, "lon": 139.6505, "category": "カフェ", "wifi": True, "power": True, "access": "元町・中華街駅 徒歩2分", "desc": "革張りソファ席があり長時間の勉強にも。山下公園すぐ近く。"},
    {"name": "Café Elliott Avenue", "station": "元町・中華街", "lat": 35.4440, "lon": 139.6495, "category": "カフェ", "wifi": False, "power": False, "access": "元町・中華街駅 徒歩3分", "desc": "最高峰のエスプレッソ。静かに思考を巡らせたい時に。"},
    {"name": "モトヤ パンケーキリストランテ", "station": "元町・中華街", "lat": 35.4405, "lon": 139.6520, "category": "カフェ", "wifi": False, "power": False, "access": "元町・中華街駅 徒歩4分", "desc": "読書などに適した大人の空間。"},
    {"name": "peace flower market & cafe", "station": "元町・中華街", "lat": 35.4395, "lon": 139.6500, "category": "カフェ", "wifi": False, "power": False, "access": "元町・中華街駅 徒歩5分", "desc": "お花屋さんに併設。リフレッシュしながらの学習に。"},
    {"name": "スターバックス 日吉店", "station": "日吉", "lat": 35.5535, "lon": 139.6465, "category": "カフェ", "wifi": True, "power": True, "access": "日吉駅西口 徒歩1分", "desc": "駅前の非常に便利なスタバ。学生が多く活気ある環境。"},
    {"name": "ドトールコーヒー 日吉店", "station": "日吉", "lat": 35.5538, "lon": 139.6460, "category": "カフェ", "wifi": True, "power": False, "access": "日吉駅西口 徒歩2分", "desc": "サクッと暗記ものや復習をしたいときに最適。"},
    {"name": "タリーズコーヒー 慶應義塾大学日吉キャンパス店", "station": "日吉", "lat": 35.5545, "lon": 139.6480, "category": "カフェ", "wifi": True, "power": True, "access": "日吉駅 徒歩2分", "desc": "広々としており自習に最も適した環境の一つ。"},
    {"name": "珈琲館 日吉店", "station": "日吉", "lat": 35.5530, "lon": 139.6455, "category": "カフェ", "wifi": True, "power": True, "access": "日吉駅西口 徒歩3分", "desc": "静かに集中したい時におすすめ。"},
    {"name": "サンマルクカフェ 日吉店", "station": "日吉", "lat": 35.5532, "lon": 139.6462, "category": "カフェ", "wifi": True, "power": False, "access": "日吉駅西口 徒歩2分", "desc": "自分のペースでノート作業が進められます。"},
    {"name": "スターバックス 菊名駅店", "station": "菊名", "lat": 35.5098, "lon": 139.6315, "category": "カフェ", "wifi": True, "power": True, "access": "菊名駅改札すぐ", "desc": "乗り換えの合間に作業ができる絶好の立地。電源あり。"},
    {"name": "ドトールコーヒー 菊名店", "station": "菊名", "lat": 35.5095, "lon": 139.6308, "category": "カフェ", "wifi": True, "power": False, "access": "菊名駅西口 徒歩1分", "desc": "隙間時間のインプット学習に重宝します。"},
    {"name": "タリーズコーヒー あざみ野駅店", "station": "あざみ野", "lat": 35.5685, "lon": 139.5538, "category": "カフェ", "wifi": True, "power": True, "access": "あざみ野駅直結", "desc": "乗り換え時にサクッと寄れる、電源完備の頼れるカフェ。"},
    {"name": "スターバックス あざみ野みすずが丘店", "station": "あざみ野", "lat": 35.5650, "lon": 139.5450, "category": "カフェ", "wifi": True, "power": True, "access": "あざみ野駅からバス", "desc": "落ち着いて勉強したい週末に。"},
    {"name": "スターバックス センター北店", "station": "センター北", "lat": 35.5538, "lon": 139.5785, "category": "カフェ", "wifi": True, "power": True, "access": "センター北駅 徒歩2分", "desc": "広めのデスクで集中してPC作業ができます。"},
    {"name": "タリーズコーヒー センター南店", "station": "センター南", "lat": 35.5440, "lon": 139.5728, "category": "カフェ", "wifi": True, "power": True, "access": "センター南駅直結", "desc": "カウンター席にコンセントが並んでいます。"},
    {"name": "スターバックス センター南店", "station": "センター南", "lat": 35.5446, "lon": 139.5735, "category": "カフェ", "wifi": True, "power": True, "access": "センター南駅 徒歩3分", "desc": "開放感のあるガラス張り。勉強のモチベーションが上がます。"},
    {"name": "ドトールコーヒー センター南店", "station": "センター南", "lat": 35.5442, "lon": 139.5725, "category": "カフェ", "wifi": True, "power": False, "access": "センター南駅 徒歩1分", "desc": "サクッと資料を読んだり、短時間の集中自習に便利。"},
    {"name": "スターバックス 戸塚店", "station": "戸塚", "lat": 35.4012, "lon": 139.5345, "category": "カフェ", "wifi": True, "power": True, "access": "戸塚駅東口 徒歩2分", "desc": "自習客が多く、刺激を受けます。仕事帰りや学校帰りに。"},
    {"name": "タリーズコーヒー 戸塚モディ店", "station": "戸塚", "lat": 35.4005, "lon": 139.5338, "category": "カフェ", "wifi": True, "power": True, "access": "戸塚駅直結 モディ内", "desc": "ビジネスマンの作業利用も非常に多いです。"},
    {"name": "ドトールコーヒー 戸塚店", "station": "戸塚", "lat": 35.4010, "lon": 139.5342, "category": "カフェ", "wifi": True, "power": False, "access": "戸塚駅東口 徒歩1分", "desc": "時間を無駄にしたくない時のクイック学習に。"},
    {"name": "珈琲館 戸塚店", "station": "戸塚", "lat": 35.3995, "lon": 139.5330, "category": "カフェ", "wifi": True, "power": True, "access": "戸塚駅西口 徒歩4分", "desc": "静かな空間でじっくり自習できます。"},
    {"name": "スターバックス 京急百貨店上大岡店", "station": "上大岡", "lat": 35.4090, "lon": 139.5968, "category": "カフェ", "wifi": True, "power": True, "access": "上大岡駅直結", "desc": "カウンター席で集中して作業可能。利便性抜群。"},
    {"name": "タリーズコーヒー 上大岡店", "station": "上大岡", "lat": 35.4085, "lon": 139.5960, "category": "カフェ", "wifi": True, "power": True, "access": "上大岡駅 徒歩2分", "desc": "席数が豊富でデスクワークに定評あり。"},
    {"name": "ドトールコーヒー 上大岡店", "station": "上大岡", "lat": 35.4082, "lon": 139.5958, "category": "カフェ", "wifi": True, "power": False, "access": "上大岡駅西口 徒歩2分", "desc": "隙間時間にテキストを広げるのに便利。"},
    {"name": "サンマルクカフェ 上大岡店", "station": "上大岡", "lat": 35.4080, "lon": 139.5962, "category": "カフェ", "wifi": True, "power": False, "access": "上大岡駅 徒歩3分", "desc": "一人で座れる席が多く、長時間の学習に。"},
    {"name": "スターバックス シァル鶴見店", "station": "鶴見", "lat": 35.5076, "lon": 139.6765, "category": "カフェ", "wifi": True, "power": True, "access": "鶴見駅直結 CIAL内", "desc": "駅ビル内で雨でも安心。電源席でPC作業も快適。"},
    {"name": "ドトールコーヒー 鶴見東口店", "station": "鶴見", "lat": 35.5070, "lon": 139.6760, "category": "カフェ", "wifi": True, "power": False, "access": "鶴見駅東口 徒歩1分", "desc": "クイックなインプット学習に最適。"},
    {"name": "タリーズコーヒー 鶴見店", "station": "鶴見", "lat": 35.5065, "lon": 139.6755, "category": "カフェ", "wifi": True, "power": True, "access": "鶴見駅西口 徒歩3分", "desc": "集中して作業ができる店舗。"},
    {"name": "スターバックス 東神奈川店", "station": "東神奈川", "lat": 35.4780, "lon": 139.6325, "category": "カフェ", "wifi": True, "power": True, "access": "東神奈川駅直結", "desc": "乗り換えの隙間にサクッと勉強をこなせます。"},
    {"name": "ドトールコーヒー 東神奈川店", "station": "東神奈川", "lat": 35.4775, "lon": 139.6320, "category": "カフェ", "wifi": True, "power": False, "access": "東神奈川駅 徒歩1分", "desc": "手軽にコーヒーを飲みながら復習を。"},
    {"name": "タリーズコーヒー 東神奈川店", "station": "東神奈川", "lat": 35.4782, "lon": 139.6315, "category": "カフェ", "wifi": True, "power": True, "access": "東神奈川駅 徒歩2分", "desc": "PCを使った自習に向いています。"},
    {"name": "ドトールコーヒー 保土ケ谷店", "station": "保土ケ谷", "lat": 35.4465, "lon": 139.5938, "category": "カフェ", "wifi": True, "power": False, "access": "保土ケ谷駅西口直結", "desc": "定期ルート上でサクッと勉強を進めるのに最適。"},
    {"name": "スターバックス ジョイナステラス二俣川店", "station": "二俣川", "lat": 35.4625, "lon": 139.5325, "category": "カフェ", "wifi": True, "power": True, "access": "二俣川駅直結", "desc": "綺麗で新しいデスクスペースで快適に勉強。"},
    {"name": "ドトールコーヒー 二俣川店", "station": "二俣川", "lat": 35.4620, "lon": 139.5320, "category": "カフェ", "wifi": True, "power": False, "access": "二俣川駅北口 徒歩1分", "desc": "朝のインプット学習などに重宝。"},
    {"name": "タリーズコーヒー 新杉田店", "station": "新杉田", "lat": 35.3870, "lon": 139.6200, "category": "カフェ", "wifi": True, "power": True, "access": "新杉田駅直結", "desc": "乗り換え時にピッタリなコンセント完備店舗。"},
    {"name": "ドトールコーヒー 新杉田店", "station": "新杉田", "lat": 35.3865, "lon": 139.6195, "category": "カフェ", "wifi": True, "power": False, "access": "新杉田駅 徒歩1分", "desc": "移動の合間にサクッと今日のノルマを。"},
    {"name": "スターバックス 金沢文庫店", "station": "金沢文庫", "lat": 35.3425, "lon": 139.6220, "category": "カフェ", "wifi": True, "power": True, "access": "金沢文庫駅 徒歩2分", "desc": "地元学生やビジネスマンの自習利用が多い。"},
    {"name": "ドトールコーヒー 金沢文庫店", "station": "金沢文庫", "lat": 35.3422, "lon": 139.6215, "category": "カフェ", "wifi": True, "power": False, "access": "金沢文庫駅東口 徒歩1分", "desc": "落ち着いた客席配置で集中しやすい。"},
    {"name": "タリーズコーヒー 港南台バーズ店", "station": "港南台", "lat": 35.3755, "lon": 139.5670, "category": "カフェ", "wifi": True, "power": True, "access": "港南台駅前 バーズ内", "desc": "一人用の席でじっくりPC作業や自習に取り組めます。"},
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

keyword = st.sidebar.text_input("スポット名で検索（任意）", placeholder="例：スタバ")

wifi_only = st.sidebar.checkbox("Wi-Fiありのみ表示")
power_only = st.sidebar.checkbox("電源ありのみ表示")

st.sidebar.markdown("---")
st.sidebar.caption(f"登録スポット数：全{len(df_spots)}件（{len(STATIONS)}駅中）")

# =========================================================
# メイン画面
# =========================================================
st.title("📖 駅勉ガイド 横浜広域版")
st.write("各社の乗り換え駅に対応！定期券の範囲に合わせて図書館やカフェをピンポイントで探せます。")
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
