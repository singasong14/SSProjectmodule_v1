import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import base64
import io
import os

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Healicious Kiosk",
    layout="centered",
    page_icon="🥗",
    initial_sidebar_state="expanded"
)

# =============================
# BRAND SECTION (SVG ICON)
# =============================
BRAND_HTML = """
<div style='display:flex; align-items:center; gap:14px; margin-bottom:30px;'>
    <img src='data:image/svg+xml;utf8,
    <svg xmlns="http://www.w3.org/2000/svg" width="56" height="56">
        <rect rx="12" width="56" height="56" fill="%236ef0b0"/>
        <text x="50%" y="54%" font-size="30" text-anchor="middle" font-family="Inter" fill="white">H</text>
    </svg>'
    style='height:56px; border-radius:12px;' />
    <span style='font-size:36px; font-weight:800; font-family:Inter;'>Healicious</span>
</div>
"""
st.markdown(BRAND_HTML, unsafe_allow_html=True)

# =============================
# CUSTOM UI CSS
# =============================
st.markdown("""
<style>
body {
    background: #f5f7fa;
}
.block-container {
    padding-top: 2rem;
}
.stButton>button {
    width: 100%;
    background-color: #6ef0b0;
    color: black;
    font-weight: 700;
    border-radius: 12px;
    height: 60px;
    font-size: 20px;
    border: none;
}
.stButton>button:hover {
    background-color: #4cd893;
    color: white;
}
.input-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 10px;
}
.section-box {
    padding: 22px;
    border-radius: 18px;
    background: white;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    margin-bottom: 24px;
}
</style>
""", unsafe_allow_html=True)


# =============================
# LOAD FOOD DATABASE
# =============================
def load_food_database():
    default_data = pd.DataFrame({
        "food": ["닭가슴살", "연어샐러드", "계란찜", "두부덮밥", "현미밥", "고구마"],
        "calories": [165, 320, 140, 280, 210, 130],
        "protein": [31, 22, 12, 18, 4, 2],
        "carbs": [0, 14, 4, 32, 44, 30],
        "fat": [3.6, 18, 6, 9, 2, 0.1]
    })
    
    file_path = "/mnt/data/20250408_음식DB.xlsx"
    if os.path.exists(file_path):
        try:
            return pd.read_excel(file_path)
        except:
            return default_data
    else:
        return default_data


FOOD_DB = load_food_database()


# =============================
# USER INPUT SECTION
# =============================
st.markdown("<div class='input-title'>사용자 기본 정보 입력</div>", unsafe_allow_html=True)
with st.container():
    with st.expander("기본 정보 입력", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("키 (cm)", min_value=100, max_value=230)
            weight = st.number_input("몸무게 (kg)", min_value=30, max_value=200)
        with col2:
            age = st.number_input("나이", min_value=10, max_value=90)
            gender = st.selectbox("성별", ["남성", "여성"])

        activity = st.selectbox(
            "활동량",
            ["적음", "보통", "많음"]
        )

        goal = st.selectbox(
            "현재 건강 목표",
            ["체중 감량", "체중 증가", "유지", "체지방 감소", "근육 증가"]
        )

        preferred_food = st.text_input("좋아하는 음식 또는 오늘 떙기는 음식")
        mood = st.selectbox("오늘 기분", ["피곤함", "상쾌함", "보통", "스트레스", "기운 없음"])

        allergy = st.text_input("알레르기 (예: 땅콩, 새우 등)")
        religion = st.text_input("종교적/이념적 이유로 못 먹는 음식")

# =============================
# CALORIE CALCULATION
# =============================
def calculate_daily_calories(height, weight, age, gender, activity, goal):
    if gender == "남성":
        bmr = 66 + (13.7 * weight) + (5 * height) - (6.8 * age)
    else:
        bmr = 655 + (9.6 * weight) + (1.8 * height) - (4.7 * age)

    factor = {"적음": 1.2, "보통": 1.375, "많음": 1.55}[activity]
    tdee = bmr * factor

    if goal == "체중 감량":
        tdee -= 300
    elif goal == "체중 증가":
        tdee += 300
    elif goal == "근육 증가":
        tdee += 150

    return round(tdee)


# =============================
# MEAL RECOMMENDER
# =============================
def recommend_meals(calorie_target, preferred_food="", mood="", allergy="", religion=""):
    df = FOOD_DB.copy()

    if preferred_food:
        df = df[df["food"].str.contains(preferred_food, na=False)]

    if allergy:
        df = df[~df["food"].str.contains(allergy, na=False)]

    if religion:
        df = df[~df["food"].str.contains(religion, na=False)]

    if len(df) == 0:
        df = FOOD_DB.sample(3)

    df = df.sample(3)
    return df


# =============================
# MAIN BUTTON – RUN SYSTEM
# =============================
run = st.button("식단 설계 시작하기")

if run:
    st.markdown("### 🥗 오늘의 맞춤 영양 식단")

    calorie_target = calculate_daily_calories(height, weight, age, gender, activity, goal)
    st.success(f"하루 권장 칼로리: **{calorie_target} kcal**")

    meals = recommend_meals(
        calorie_target,
        preferred_food,
        mood,
        allergy,
        religion
    )

    st.write("### 오늘 추천 식단")
    st.dataframe(meals)

    # =============================
    # RESTAURANT RECOMMENDER (DEMO)
    # =============================
    st.markdown("### 🍽 주변 음식점 추천 (데모)")

    demo_restaurants = pd.DataFrame({
        "음식점": ["그린샐러드집", "맛있는두부집", "건강식 도시락"],
        "거리": ["150m", "320m", "500m"],
        "대표메뉴": ["연어샐러드", "두부스테이크", "현미 도시락"]
    })

    st.dataframe(demo_restaurants)

    st.info("※ 실제 위치 기반 추천은 Google Places / Kakao Local API 연동 시 활성화됩니다.")


