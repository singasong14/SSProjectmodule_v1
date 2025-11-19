import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="MBTI 국가별 분석", layout="wide")

# =========================

# 텍스트 데이터 입력

# =========================

st.sidebar.header("데이터 입력")
input_text = st.sidebar.text_area("국가별 MBTI 데이터를 붙여넣으세요 (CSV 혹은 탭/공백 구분 가능)")

# =========================

# 텍스트 -> DataFrame 변환

# =========================

def parse_text_to_df(text):
lines = text.strip().splitlines()
if not lines:
return pd.DataFrame()

```
# 첫 줄은 열 이름으로 가정
header = re.split(r"[\t,]+", lines[0].strip())
data = []
for line in lines[1:]:
    row = re.split(r"[\t,]+", line.strip())
    # 숫자는 float로 변환
    row = [float(x) if re.match(r"^\d*\.?\d+$", x) else x for x in row]
    data.append(row)
df = pd.DataFrame(data, columns=header)
return df
```

df = parse_text_to_df(input_text)

if df.empty:
st.warning("데이터가 없습니다. 좌측 사이드바에 붙여넣어 주세요.")
st.stop()

# =========================

# 사이드바 UI

# =========================

st.sidebar.header("국가 선택")
selected_country = st.sidebar.selectbox("국가를 선택하세요", df['Country'].tolist())

# =========================

# 전체 MBTI 평균 시각화

# =========================

st.header("🌎 전 세계 MBTI 평균 분포")
mean_mbti = df.iloc[:, 1:].mean().sort_values(ascending=False)
fig_mean = px.bar(
x=mean_mbti.index,
y=mean_mbti.values,
labels={"x": "MBTI", "y": "평균 비율"},
title="전체 국가 MBTI 평균 비율",
text=[f"{v:.2%}" for v in mean_mbti.values],
)
fig_mean.update_traces(marker_color='lightskyblue', textposition='outside')
fig_mean.update_layout(yaxis_tickformat=".0%", xaxis_title="MBTI 유형", yaxis_title="평균 비율")
st.plotly_chart(fig_mean, use_container_width=True)

# =========================

# 선택된 국가 MBTI 비율

# =========================

st.header(f"🇺🇳 {selected_country} MBTI 분포")
country_data = df[df['Country'] == selected_country].iloc[0, 1:]
country_data_sorted = country_data.sort_values(ascending=False)

# 색상 지정: 1등 빨강, 나머지 그라데이션

top_color = 'crimson'
gradient_colors = px.colors.sequential.Blues
other_colors = gradient_colors[:len(country_data_sorted)-1] if len(country_data_sorted) > 1 else ['lightblue']
colors = [top_color] + other_colors

fig_country = px.bar(
x=country_data_sorted.index,
y=country_data_sorted.values,
labels={"x": "MBTI", "y": "비율"},
title=f"{selected_country} MBTI 비율",
text=[f"{v:.2%}" for v in country_data_sorted.values],
)
fig_country.update_traces(marker_color=colors, textposition='outside')
fig_country.update_layout(yaxis_tickformat=".0%", xaxis_title="MBTI 유형", yaxis_title="비율")
st.plotly_chart(fig_country, use_container_width=True)

# =========================

# 팁 & 인터랙션

# =========================

st.markdown("---")
st.markdown("💡 그래프 위에 마우스를 올리면 각 MBTI 유형의 비율을 확인할 수 있습니다.")
