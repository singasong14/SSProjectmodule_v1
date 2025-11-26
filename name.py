import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Healicious Kiosk", layout="centered", page_icon="🥗", initial_sidebar_state="expanded")

# =============================
# BRAND
# =============================
st.markdown("""
<div style='display:flex; align-items:center; gap:14px; margin-bottom:30px;'>
    <img src='data:image/svg+xml;utf8,
    <svg xmlns="http://www.w3.org/2000/svg" width="56" height="56">
        <rect rx="12" width="56" height="56" fill="%236ef0b0"/>
        <text x="50%" y="54%" font-size="30" text-anchor="middle" font-family="Inter" fill="white">H</text>
    </svg>' style='height:56px; border-radius:12px;'/>
    <span style='font-size:36px; font-weight:800; font-family:Inter;'>Healicious</span>
</div>
""", unsafe_allow_html=True)

# =============================
# CUSTOM CSS
# =============================
st.markdown("""
<style>
body {background: #f5f7fa;}
.block-container {padding-top: 2rem;}
.stButton>button {width:100%; background-color:#6ef0b0; color:black; font-weight:700; border-radius:12px; height:60px; font-size:20px; border:none;}
.stButton>button:hover {background-color:#4cd893; color:white;}
.input-title {font-size:22px; font-weight:700; margin-bottom:10px;}
.section-box {padding:22px; border-radius:18px; background:white; box-shadow:0 4px 20px rgba(0,0,0,0.05); margin-bottom:24px;}
.card {padding:15px; border-radius:12px; background:white; box-shadow:0 4px 10px rgba(0,0,0,0.05); margin-bottom:15px;}
.card h4 {margin:0; color:#333;}
.card p {margin:3px 0; color:#555;}
.card img {width:100%; max-height:150px; object-fit:cover; border-radius:8px; margin-bottom:5px;}
</style>
""", unsafe_allow_html=True)

# =============================
# FOOD DATABASE (예시)
# =============================
def load_food_database():
    data = [
        {"food":"닭가슴살","category":"단백질","calories":165,"protein":31,"carbs":0,"fat":3.6,"fiber":0,"vitaminC":0,"omega3":0,"tags":[],"image_url":"https://i.imgur.com/0Xb3Fsz.jpg"},
        {"food":"연어","category":"단백질","calories":208,"protein":20,"carbs":0,"fat":13,"fiber":0,"vitaminC":0,"omega3":1.2,"tags":["omega3"],"image_url":"https://i.imgur.com/qVOVtZP.jpg"},
        {"food":"계란찜","category":"단백질반찬","calories":140,"protein":12,"carbs":4,"fat":6,"fiber":0,"vitaminC":0,"omega3":0,"tags":[],"image_url":"https://i.imgur.com/TxAfiFt.jpg"},
        {"food":"두부조림","category":"단백질반찬","calories":120,"protein":10,"carbs":5,"fat":6,"fiber":0,"vitaminC":0,"omega3":0,"tags":[],"image_url":"https://i.imgur.com/2sT6uOY.jpg"},
        {"food":"현미밥","category":"주식","calories":210,"protein":4,"carbs":44,"fat":2,"fiber":3,"vitaminC":0,"omega3":0,"tags":[],"image_url":"https://i.imgur.com/7aXJ3HW.jpg"},
        {"food":"고구마","category":"주식","calories":130,"protein":2,"carbs":30,"fat":0.1,"fiber":2.5,"vitaminC":20,"omega3":0,"tags":[],"image_url":"https://i.imgur.com/3rQgj9b.jpg"},
        {"food":"시금치나물","category":"채소반찬","calories":35,"protein":3,"carbs":4,"fat":0.5,"fiber":2.7,"vitaminC":28,"omega3":0,"tags":[],"image_url":"https://i.imgur.com/Q06R1yO.jpg"},
        {"food":"김치","category":"채소반찬","calories":15,"protein":1,"carbs":2,"fat":0,"fiber":1.5,"vitaminC":10,"omega3":0,"tags":["fermented"],"image_url":"https://i.imgur.com/kbWt0uQ.jpg"},
        {"food":"아몬드","category":"서브메뉴","calories":50,"protein":2,"carbs":2,"fat":4,"fiber":1,"vitaminC":0,"omega3":0,"tags":["nut"],"image_url":"https://i.imgur.com/xlMIKJP.jpg"},
        {"food":"두유","category":"서브메뉴","calories":80,"protein":5,"carbs":8,"fat":3,"fiber":1,"vitaminC":0,"omega3":0,"tags":["vegan"],"image_url":"https://i.imgur.com/kE2E7kE.jpg"},
    ]
    return pd.DataFrame(data)

FOOD_DB = load_food_database()

# =============================
# USER INPUT
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
        activity = st.selectbox("활동량", ["적음","보통","많음"])
        goal = st.selectbox("건강 목표", ["체중 감량","체중 증가","유지","체지방 감소","근육 증가"])
        preferred_food = st.text_input("좋아하는 음식 또는 오늘 떙기는 음식")
        mood = st.selectbox("오늘 기분", ["피곤함","상쾌함","보통","스트레스","기운 없음"])
        allergy = st.text_input("알레르기 (예: 땅콩, 새우 등)")
        religion = st.text_input("종교적/이념적 이유로 못 먹는 음식")

# =============================
# CALORIE CALCULATION
# =============================
def calculate_daily_calories(height, weight, age, gender, activity, goal):
    if gender=="남성":
        bmr=66+(13.7*weight)+(5*height)-(6.8*age)
    else:
        bmr=655+(9.6*weight)+(1.8*height)-(4.7*age)
    factor={"적음":1.2,"보통":1.375,"많음":1.55}[activity]
    tdee=bmr*factor
    if goal=="체중 감량": tdee-=300
    elif goal=="체중 증가": tdee+=300
    elif goal=="근육 증가": tdee+=150
    return round(tdee)

# =============================
# SCIENTIFIC MEAL RECOMMENDER
# =============================
def recommend_meals_scientific(calorie_target, weight, goal, preferred_food="", mood="", allergy="", religion=""):
    df = FOOD_DB.copy()
    
    # 필터
    if allergy: df = df[~df['tags'].apply(lambda x: allergy in x)]
    if religion: df = df[~df['tags'].apply(lambda x: religion in x)]
    if preferred_food: df = df[df['food'].str.contains(preferred_food, na=False)]
    
    protein_target = weight*1.5 if goal=="근육 증가" else weight*1.2
    meal_ratio = {"아침":0.25,"점심":0.35,"저녁":0.35}
    meals = {}
    
    for meal, ratio in meal_ratio.items():
        meal_items=[]
        for cat in ["주식","단백질","채소반찬","서브메뉴"]:
            temp = df[df['category']==cat]
            if len(temp)==0: continue
            # Mood 기반 가중치
            if mood=="피곤함" and cat=="단백질":
                temp = temp.sample(frac=1)  # 랜덤 + 중요도
            meal_items.append(temp.sample(1))
        meals[meal] = pd.concat(meal_items)
    return meals, protein_target

# =============================
# RUN SYSTEM
# =============================
if st.button("식단 설계 시작하기"):
    calorie_target = calculate_daily_calories(height, weight, age, gender, activity, goal)
    st.success(f"하루 권장 칼로리: **{calorie_target} kcal** (TDEE 기반 계산)")

    meals, protein_target = recommend_meals_scientific(calorie_target, weight, goal, preferred_food, mood, allergy, religion)
    
    st.markdown("### 🥗 오늘의 맞춤 식단")
    total_protein = 0
    total_calories = 0
    
    for meal_name, df in meals.items():
        st.markdown(f"#### {meal_name}")
        for idx, row in df.iterrows():
            total_protein += row['protein']
            total_calories += row['calories']
            st.markdown(f"""
            <div class='card'>
                <img src='{row['image_url']}'/>
                <h4>{row['food']} ({row['category']})</h4>
                <p>칼로리: {row['calories']} kcal | 단백질: {row['protein']}g | 탄수화물: {row['carbs']}g | 지방: {row['fat']}g</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 하루 목표 시각화
    st.info(f"하루 총 단백질: {total_protein:.1f}g (목표: {protein_target:.1f}g)")
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = total_protein,
        domain = {'x':[0,1],'y':[0,1]},
        title = {'text': "단백질 목표 달성률"},
        delta = {'reference': protein_target},
        gauge = {'axis':{'range':[0, protein_target*1.2]},
                 'bar':{'color':'blue'}}
    ))
    st.plotly_chart(fig)
    
    st.info(f"하루 총 칼로리: {total_calories:.1f} kcal (목표: {calorie_target} kcal)")
