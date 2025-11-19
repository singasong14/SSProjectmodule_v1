streamlit
pandas
plotly

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="국가별 MBTI 분석", layout="wide")

# =============================
# 1. Google Sheets 데이터 불러오기
# =============================
# 공개 링크를 CSV 형식으로 바꿔서 불러오기
sheet_url = "https://docs.google.com/spreadsheets/d/13vZps9T7aJ9OaORHDpenFa5ZfBKuVPy6rQY_lRcIY0k/export?format=csv&gid=2076402041"
df = pd.read_csv(sheet_url)

# =============================
# 2. 국가 선택 UI
# =============================
st.title("국가별 MBTI 비율 대시보드")
country_list = df['국가'].unique()
selected_country = st.selectbox("국가를 선택하세요", country_list)

country_data = df[df['국가'] == selected_country].melt(id_vars='국가', var_name='MBTI', value_name='비율')

# =============================
# 3. 색상 설정: 1등 빨간색, 나머지 그라데이션
# =============================
country_data = country_data.sort_values('비율', ascending=False)
colors = ['red'] + px.colors.sequential.Viridis[len(country_data)-1]
color_map = dict(zip(country_data['MBTI'], colors))

# =============================
# 4. Plotly 막대그래프
# =============================
fig = px.bar(
    country_data,
    x='MBTI',
    y='비율',
    color='MBTI',
    color_discrete_map=color_map,
    text='비율'
)
fig.update_traces(texttemplate='%{text}%', textposition='outside')
fig.update_layout(
    yaxis=dict(title='비율 (%)', range=[0, country_data['비율'].max()*1.2]),
    xaxis_title='MBTI 유형',
    title=f"{selected_country} MBTI 비율",
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    plot_bgcolor='white'
)
st.plotly_chart(fig, use_container_width=True)
