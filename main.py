import streamlit as st
import pandas as pd

# 1. サイトのタイトル
st.title("📖 駅勉ガイド 神奈川版")

# 2. 地図や難しい機能は一旦なしにして、文字だけ出します
st.write("現在、サイトを修復中です。この文字が見えていれば成功です！")

# 3. Googleへの合言葉（これさえあれば、サチコの確認ボタンは押せます）
st.markdown('<meta name="google-site-verification" content="ROSJqr15YgcHGn7S5kq-OQJI0EGH47vCPUk9OnKAJXY" />', unsafe_allow_html=True)

stations = ["横浜", "武蔵小杉", "小田原"]
st.selectbox("駅を選んでください", stations)
