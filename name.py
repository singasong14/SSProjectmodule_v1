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
# LOAD FOOD DATABASE (500+ items)
# =============================
def load_food_database():
    # 재현 가능한 난수
    np.random.seed(42)

    explicit_items = [
        ("닭가슴살", 165, 31, 0, 3.6),
        ("훈제 닭가슴살", 130, 25, 2, 2.0),
        ("삶은 계란", 77, 6, 1, 5.0),
        ("계란후라이", 180, 13, 1, 14.0),
        ("계란찜", 140, 12, 4, 6.0),
        ("두부", 84, 9, 2, 4.0),
        ("연두부", 55, 5, 2, 3.0),
        ("두부스테이크", 210, 15, 10, 12.0),
        ("연어샐러드", 330, 22, 14, 18.0),
        ("치킨샐러드", 240, 26, 12, 10.0),
        ("그린샐러드", 140, 4, 12, 7.0),
        ("아보카도샐러드", 280, 8, 15, 20.0),
        ("현미밥", 210, 4, 44, 2.0),
        ("백미밥", 280, 4, 56, 1.0),
        ("잡곡밥", 240, 6, 48, 2.0),
        ("오트밀죽", 180, 6, 30, 3.0),
        ("훈제 연어", 200, 20, 3, 12.0),
        ("연어 스테이크", 320, 22, 14, 18.0),
        ("삼치구이", 280, 22, 0, 18.0),
        ("고등어구이", 360, 24, 0, 28.0),
        ("소고기 불고기", 310, 25, 8, 18.0),
        ("쇠고기 스테이크", 350, 30, 0, 25.0),
        ("돼지안심구이", 230, 28, 3, 12.0),
        ("김치찌개", 240, 18, 12, 14.0),
        ("된장찌개", 120, 8, 10, 4.0),
        ("순두부찌개", 280, 18, 14, 18.0),
        ("갈비탕", 350, 26, 8, 24.0),
        ("삼계탕", 650, 45, 12, 40.0),
        ("미소된장국", 70, 5, 8, 2.0),
        ("감자조림", 150, 3, 28, 2.0),
        ("진미채볶음", 220, 12, 20, 6.0),
        ("어묵볶음", 180, 10, 16, 8.0),
        ("브로콜리", 55, 4, 6, 1.0),
        ("시금치나물", 40, 3, 2, 1.0),
        ("콩나물무침", 55, 4, 5, 1.0),
        ("오이무침", 45, 1, 8, 1.0),
        ("계란말이", 230, 14, 4, 16.0),
        ("메밀소바", 350, 18, 50, 4.0),
        ("우동", 420, 12, 70, 4.0),
        ("쌀국수", 390, 20, 60, 6.0),
        ("토마토파스타", 640, 18, 92, 18.0),
        ("크림파스타", 760, 16, 90, 32.0),
        ("로제파스타", 700, 20, 88, 26.0),
        ("통밀빵", 110, 5, 22, 2.0),
        ("바게트", 250, 8, 52, 1.0),
        ("크루아상", 260, 4, 28, 14.0),
        ("찐고구마", 140, 2, 30, 0.1),
        ("군고구마", 180, 2, 38, 0.2),
        ("단호박", 70, 1, 16, 0.1),
        ("그릭 요거트", 150, 16, 10, 5.0),
        ("고단백 요거트", 130, 18, 8, 1.0),
        ("콩비지", 120, 8, 6, 6.0),
        ("두부김치", 210, 14, 10, 10.0),
        ("오징어볶음", 220, 28, 6, 6.0),
        ("낙지연포탕", 180, 20, 4, 4.0),
        ("바지락술찜", 160, 18, 6, 2.0),
        ("해물파전", 450, 18, 50, 20.0),
        ("파래김", 35, 5, 2, 0.5),
        ("김밥", 330, 10, 60, 6.0),
        ("참치김밥", 380, 16, 62, 10.0),
        ("샐러드랩", 420, 20, 50, 18.0),
        ("현미 도시락", 540, 28, 72, 12.0),
        ("닭갈비", 520, 30, 44, 20.0),
        ("제육볶음", 610, 34, 28, 36.0),
        ("고구마샐러드", 210, 3, 34, 6.0),
        ("옥수수샐러드", 190, 4, 30, 5.0),
        ("미역국", 40, 3, 3, 1.0),
        ("콩자반", 160, 8, 12, 8.0),
        ("두부조림", 120, 9, 6, 6.0),
        ("닭곰탕", 480, 36, 10, 24.0),
        ("어묵국", 100, 8, 6, 4.0),
        ("감자국", 80, 2, 14, 1.0),
    ]

    # explicit_items 수를 기준으로 자동 생성해 500개 채우기
    total_target = 500
    items = list(explicit_items)
    current_count = len(items)

    # 이미 충분하면 그대로 DataFrame으로 변환
    if current_count < total_target:
        for i in range(current_count, total_target):
            name = f"샘플음식{i+1}"
            calories = int(np.random.uniform(60, 800))
            protein = int(np.random.uniform(1, 60))
            carbs = int(np.random.uniform(0, 120))
            fat = round(float(np.random.uniform(0.1, 40.0)), 1)
            items.append((name, calories, protein, carbs, fat))

    default_data = pd.DataFrame(items, columns=["food", "calories", "protein", "carbs", "fat"])

    # 외부 파일 우선 로드 (엑셀 또는 csv)
    file_xlsx = "/mnt/data/20250408_음식DB.xlsx"
    file_csv = "/mnt/data/20250408_음식DB.csv"

    if os.path.exists(file_xlsx):
        try:
            return pd.read_excel(file_xlsx)
        except Exception:
            return default_data
    if os.path.exists(file_csv):
        try:
            return pd.read_csv(file_csv)
        except Exception:
            return default_data

    # 파일이 없으면 기본 500종 반환
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
            height = st.number_input("키 (cm)", min_value=100, max_value=230, value=170)
            weight = st.number_input("몸무게 (kg)", min_value=30, max_value=200, value=70)
        with col2:
            age = st.number_input("나이", min_value=10, max_value=90, value=30)
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

    return int(round(tdee))


# =============================
# MEAL RECOMMENDER
# =============================
def recommend_meals(calorie_target, preferred_food="", mood="", allergy="", religion=""):
    df = FOOD_DB.copy()

    # 안전한 문자열 필터 (대소문자 무시)
    if preferred_food:
        df = df[df["food"].str.contains(preferred_food, na=False, case=False)]

    if allergy:
        df = df[~df["food"].str.contains(allergy, na=False, case=False)]

    if religion:
        df = df[~df["food"].str.contains(religion, na=False, case=False)]

    # 만약 필터로 항목이 모두 제거되면 기본 DB에서 무작위 3개 제공
    if len(df) == 0:
        df = FOOD_DB.sample(3, random_state=42)

    # 기본적으로 3개 추천. 칼로리 타깃과 약간 매칭시키기 위해 근사치를 사용할 수 있음
    # 현재는 간단 샘플링
    df = df.sample(min(6, len(df)), random_state=42)
    return df.reset_index(drop=True)


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

# =============================
# OPTIONAL: Save default DB to /mnt/data for editing
# (한번만 저장하려면 아래 주석 해제)
# =============================
# try:
#     FOOD_DB.to_csv('/mnt/data/Healicious_food_db_500.csv', index=False)
# except Exception:
#     pass
