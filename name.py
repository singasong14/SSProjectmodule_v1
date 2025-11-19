import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MBTI 국가별 비율", layout="wide")

st.title("국가별 MBTI 비율 시각화")

# Google Sheets CSV 링크 (공개 공유 설정 필요)

sheet_url = "[https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_zJ2WxI9EXAMPLE/pub?gid=2076402041&single=true&output=csv](https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_zJ2WxI9EXAMPLE/pub?gid=2076402041&single=true&output=csv)"
df = pd.read_csv(sheet_url)

# 국가 선택 UI

countries = df['Country'].unique()
selected_country = st.selectbox("국가 선택", countries)

# 선택 국가 데이터

df_country = df[df['Country'] == selected_country].melt(id_vars='Country', var_name='MBTI', value_name='Percentage')

# 색상 설정: 1등은 빨강, 나머지는 블루 계열 그라데이션

top_mbti = df_country.sort_values('Percentage', ascending=False).iloc[0]['MBTI']
colors = ['red' if mbti == top_mbti else 'lightblue' for mbti in df_country['MBTI']]

# Plotly 막대그래프

fig = px.bar(
df_country,
x='MBTI',
y='Percentage',
text='Percentage',
color=df_country['MBTI'],
color_discrete_sequence=colors
)

fig.update_traces(textposition='outside')
fig.update_layout(
title=f"{selected_country} MBTI 비율",
xaxis_title="MBTI 유형",
yaxis_title="비율 (%)",
showlegend=False,
uniformtext_minsize=8,
uniformtext_mode='hide'
)

st.plotly_chart(fig, use_container_width=True)
