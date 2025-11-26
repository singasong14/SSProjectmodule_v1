import streamlit as st
import pandas as pd
import random
from PIL import Image, ImageDraw, ImageFont

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Healicious Pro", layout="wide", page_icon="🥗", initial_sidebar_state="expanded")

# =============================
# BRAND HEADER
# =============================
st.markdown("""
<div style='display:flex; align-items:center; gap:14px; margin-bottom:30px;'>
    <span style='font-size:36px; font-weight:800; font-family:Inter;'>🥗 Healicious Pro</span>
</div>
""", unsafe_allow_html=True)

# =============================
# CUSTOM CSS
# =============================
st.markdown("""
<style>
body {background: #f5f7fa;}
.stButton>button {width:100%; background-color:#6ef0b0; color:black; font-weight:700; border-radius:12px; height:50px; font-size:18px; border:none;}
.stButton>button:hover {background-color:#4cd893; color:white;}
.card {padding:12px; border-radius:12px; background:white; box-shadow:0 4px 10px rgba(0,0,0,0.05); margin-bottom:12px;}
.card h4 {margin:0; color:#333;}
.card p {margin:2px 0; color:#555;}
</style>
""", unsafe_allow_html=True)

# =============================
# HELPER: PIL 임베디드 이미지 생성
# =============================
def generate_dummy_image(name, size=(200,150)):
    img = Image.new("RGB", size, (random.randint(50,255), random.randint(50,255), random.randint(50,255)))
    draw = ImageDraw.Draw(img)
    font_size = 20
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    text = name[:10]
    w,h = draw.textsize(text, font=font)
    draw.text(((size[0]-w)/2,(size[1]-h)/2), text, fill="white", font=font)
    return img

# =============================
# FOOD DATABASE (300개 샘플)
# =============================
def generate_food_db(n=300):
    categories = ["주식","단백질","채소반찬","서브메뉴","간식","음료"]
    sample_foods = [
        {"food":"닭가슴살","calories":165,"protein":31,"carbs":0,"fat":3.6,"category":"단백질"},
        {"food":"연어","calories":208,"protein":20,"carbs":0,"fat":13,"category":"단백질"},
        {"food":"계란찜","calories":140,"protein":12,"carbs":4,"fat":6,"category":"단백질"},
        {"food":"두부조림","calories":120,"protein":10,"carbs":5,"fat":6,"category":"단백질"},
        {"food":"현미밥","calories":210,"protein":4,"carbs":44,"fat":2,"category":"주식"},
        {"food":"고구마","calories":130,"protein":2,"carbs":30,"fat":0.1,"category":"주식"},
        {"food":"시금치나물","calories":35,"protein":3,"carbs":4,"fat":0.5,"category":"채소반찬"},
        {"food":"김치","calories":15,"protein":1,"carbs":2,"fat":0,"category":"채소반찬"},
        {"food":"아몬드","calories":50,"protein":2,"carbs":2,"fat":4,"category":"간식"},
        {"food":"두유","calories":80,"protein":5,"carbs":8,"fat":3,"category":"음료"}
    ]
    data=[]
    for i in range(n):
        base=random.choice(sample_foods)
        item=base.copy()
        item["image"]=generate_dummy_image(item["food"])
        data.append(item)
    return pd.DataFrame(data)

FOOD_DB = generate_food_db(300)

# =============================
# USER INPUT
# =============================
st.markdown("### 사용자 기본 정보 입력")
with st.expander("기본 정보 입력", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input("키 (cm)", min_value=100, max_value=230)
        weight = st.number_input("몸무게 (kg)", min_value=30, max_value=200)
    with col2:
        age = st.number_input("나이", min_value=10, max_value=90)
        gender = st.selectbox("성별", ["남성","여성"])
    activity = st.selectbox("활동량", ["적음","보통","많음"])
    goal = st.selectbox("건강 목표", ["체중 감량","체중 증가","유지","체지방 감소","근육 증가"])
    preferred_food = st.text_input("좋아하는 음식 또는 오늘 떙기는 음식")
    mood = st.selectbox("오늘 기분", ["피곤함","상쾌함","보통","스트레스","기운 없음"])
    allergy = st.text_input("알레르기 (예: 땅콩, 새우 등)")
    religion = st.text_input("못 먹는 음식(종교/이념)")

# =============================
# CALORIE + PROTEIN
# =============================
def calculate_tdee(height, weight, age, gender, activity, goal):
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
# MEAL RECOMMENDER
# =============================
def recommend_meals(calorie_target, weight, goal, preferred_food="", allergy="", religion=""):
    df = FOOD_DB.copy()
    # 필터 적용
    if allergy: df = df[~df['food'].str.contains(allergy, na=False)]
    if religion: df = df[~df['food'].str.contains(religion, na=False)]
    if preferred_food: df = df[df['food'].str.contains(preferred_food, na=False)]
    
    protein_target = weight*1.5 if goal=="근육 증가" else weight*1.2
    meal_ratio={"아침":0.25,"점심":0.35,"저녁":0.35}
    meals={}
    
    for meal, ratio in meal_ratio.items():
        meal_items=[]
        for cat in ["주식","단백질","채소반찬","서브메뉴"]:
            temp=df[df['category']==cat]
            if len(temp)==0: continue
            meal_items.append(temp.sample(1))
        meals[meal]=pd.concat(meal_items)
    return meals, protein_target

# =============================
# RUN SYSTEM
# =============================
if st.button("식단 설계 시작하기"):
    tdee = calculate_tdee(height, weight, age, gender, activity, goal)
    st.success(f"하루 권장 칼로리: {tdee} kcal")
    
    meals, protein_target = recommend_meals(tdee, weight, goal, preferred_food, allergy, religion)
    
    st.markdown("### 🥗 오늘의 맞춤 식단")
    total_protein = 0
    total_calories = 0
    for meal_name, df in meals.items():
        st.markdown(f"#### {meal_name}")
        for idx, row in df.iterrows():
            total_protein += row['protein']
            total_calories += row['calories']
            st.markdown(f"<div class='card'><h4>{row['food']} ({row['category']})</h4></div>", unsafe_allow_html=True)
            st.image(row['image'])
            st.write(f"칼로리: {row['calories']} | 단백질: {row['protein']} | 탄수화물: {row['carbs']} | 지방: {row['fat']}")
    
    st.markdown("### 💪 단백질 목표 달성률")
    st.progress(min(total_protein/protein_target,1.0))
    st.info(f"{total_protein:.1f} g / {protein_target:.1f} g")
    
    st.markdown("### 🔥 칼로리 목표 달성률")
    st.progress(min(total_calories/tdee,1.0))
    st.info(f"{total_calories:.1f} kcal / {tdee} kcal")
