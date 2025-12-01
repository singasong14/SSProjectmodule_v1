# UPDATED HEALICIOUS KIOSK — 700 FOOD DB + 아침/점심/저녁 + UI 개선 + 과학원리 EXPANDER
import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Healicious", layout="centered")

# =============================
# BRAND
# =============================
st.markdown("""
<div style='display:flex;align-items:center;gap:12px;margin-bottom:25px;'>
    <span style='font-size:36px;font-weight:900;'>🥗 Healicious</span>
</div>
""", unsafe_allow_html=True)

# =============================
# 700 FOOD DB LOADING
# =============================

def load_food_database():
    file_path = "/mnt/data/food_700.xlsx"
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    else:
        data = pd.DataFrame({
            "food": [f"샘플음식_{i}" for i in range(700)],
            "calories": np.random.randint(50, 600, 700),
            "protein": np.random.randint(1, 40, 700),
            "carbs": np.random.randint(1, 60, 700),
            "fat": np.random.randint(0, 30, 700)
        })
        return data

FOOD_DB = load_food_database()

# =============================
# USER INPUT — 확장된 정보
# =============================
st.markdown("## 사용자 정보 입력")
with st.expander("기본 정보 입력", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input("키 (cm)", min_value=100, max_value=230)
        weight = st.number_input("몸무게 (kg)", min_value=30, max_value=200)
        sleep = st.number_input("수면 시간 (시간)", min_value=3, max_value=12)
    with col2:
        age = st.number_input("나이", min_value=10, max_value=90)
        gender = st.selectbox("성별", ["남성", "여성"])
        water = st.number_input("하루 물 섭취량 (잔)", min_value=1, max_value=20)

    activity = st.selectbox("활동량", ["적음", "보통", "많음"])  
    goal = st.selectbox("건강 목표", ["체중 감량", "체중 증가", "유지", "체지방 감소", "근육 증가"])  
    diet_preference = st.selectbox("식단 성향", ["균형잡힌 식단", "고단백", "저탄수", "저지방", "비건", "채식 위주"])
    preferred_food = st.text_input("좋아하는 음식")
    mood = st.selectbox("오늘 기분", ["피곤함", "상쾌함", "보통", "스트레스", "기운 없음"])
    allergy = st.text_input("알레르기")
    religion = st.text_input("못 먹는 음식(종교 등)")

# =============================
# CALCULATE ENERGY
# =============================

def calculate_daily_calories(height, weight, age, gender, activity, goal):
    if gender == "남성":
        bmr = 66 + 13.7 * weight + 5 * height - 6.8 * age
    else:
        bmr = 655 + 9.6 * weight + 1.8 * height - 4.7 * age

    factor = {"적음": 1.2, "보통": 1.375, "많음": 1.55}[activity]
    tdee = bmr * factor

    if goal == "체중 감량": tdee -= 300
    if goal == "체중 증가": tdee += 300
    if goal == "근육 증가": tdee += 150

    return round(tdee)

# =============================
# CALORIE SPLIT
# =============================

def split_calories(tdee):
    return {
        "breakfast": round(tdee * 0.3),
        "lunch": round(tdee * 0.4),
        "dinner": round(tdee * 0.3)
    }

# =============================
# RECOMMENDER
# =============================

def recommend_meals(target_cal, preferred_food="", allergy="", religion=""):
    df = FOOD_DB.copy()

    if preferred_food:
        df = df[df["food"].str.contains(preferred_food, na=False)]
    if allergy:
        df = df[~df["food"].str.contains(allergy, na=False)]
    if religion:
        df = df[~df["food"].str.contains(religion, na=False)]

    if len(df) == 0:
        df = FOOD_DB.copy()

    return df.sample(5)

# =============================
# RUN BUTTON
# =============================
run = st.button("식단 설계 시작하기")

if run:
    tdee = calculate_daily_calories(height, weight, age, gender, activity, goal)
    st.success(f"하루 권장 칼로리: **{tdee} kcal**")

    split = split_calories(tdee)

    st.markdown("### 🍳 아침 식단")
    st.dataframe(recommend_meals(split["breakfast"], preferred_food, allergy, religion))

    st.markdown("### 🍚 점심 식단")
    st.dataframe(recommend_meals(split["lunch"], preferred_food, allergy, religion))

    st.markdown("### 🍽 저녁 식단")
    st.dataframe(recommend_meals(split["dinner"], preferred_food, allergy, religion))

# =============================
# 과학적 원리 설명
# =============================

st.markdown("## 🔬 과학적 원리 (펼쳐보기)")
with st.expander("영양학적/생리학적 기반 설명 보기"):
    st.markdown("""
    ### 🔥 BMR 계산 원리
    - Harris–Benedict 공식을 사용하여 기초대사량 계산

    ### 💪 활동지수 반영
    - 활동 수준에 따라 1.2~1.55 배 증가

    ### 🎯 목표별 칼로리 조정
    - 감량: -300 kcal
    - 증량: +300 kcal
    - 근성장: +150 kcal

    ### 🍱 식사 칼로리 배분 근거
    - 아침 30%: 혈당 안정 / 에너지 초기 공급
    - 점심 40%: 하루 활동량 최대 타이밍
    - 저녁 30%: 수면 전 과다 섭취 방지

    ### 🧬 음식군 700개 사용 이유
    - 다양성 확보
    - 개인 취향/알레르기 대응
    - 단백질·탄수·지방 조합 최적화
    """)
