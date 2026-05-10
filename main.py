import streamlit as st

# Google Analytics 連携
st.markdown("""
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-W9WDMKSB7S"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-W9WDMKSB7S');
    </script>
    """, unsafe_allow_html=True)

st.title("📖 駅勉ガイド 神奈川版")
st.write("アナリティクス接続テスト中")
