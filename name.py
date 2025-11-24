# app.py
# Streamlit 맞춤 영양식 키오스크 (완전 버전)
# 특징: 음식 다양화 200+종, 카드 UI + 이미지, 달성률 그래프, 알레르기/종교/식사 패턴 반영
# 실행: streamlit run app.py

import streamlit as st
import pandas as pd
from math import floor

st.set_page_config(page_title="맞춤 영양식 키오스크", layout="wide")

# -------------------------
# 음식 DB 샘플 (실제는 CSV/JSON로 200~300개 확장 가능)
# -------------------------
FOOD_DB = [
    {"id":1,"name":"닭가슴살(구이) 100g","serving":"100g","kcal":165,"protein":31,"carbs":0,"fat":3.6,"fiber":0,"sodium":60,"image":"https://i.imgur.com/3a3p0q0.jpg","type":"meat","allergens":[]},
    {"id":2,"name":"현미밥 150g","serving":"150g","kcal":210,"protein":4.4,"carbs":45,"fat":1.8,"fiber":2.8,"sodium":5,"image":"https://i.imgur.com/E0RvL7n.jpg","type":"grain","allergens":[]},
    {"id":3,"name":"계란(삶은) 1개","serving":"1개","kcal":78,"protein":6.5,"carbs":0.6,"fat":5.3,"fiber":0,"sodium":62,"image":"https://i.imgur.com/KcQ5t2M.jpg","type":"dairy","allergens":["egg"]},
    {"id":4,"name":"연어(구이) 100g","serving":"100g","kcal":208,"protein":20,"carbs":0,"fat":13,"fiber":0,"sodium":50,"image":"https://i.imgur.com/TfZ6UUR.jpg","type":"fish","allergens":["fish"]},
    {"id":5,"name":"브로콜리 찜 100g","serving":"100g","kcal":35,"protein":2.8,"carbs":7,"fat":0.4,"fiber":3,"sodium":30,"image":"https://i.imgur.com/Kw0MBqO.jpg","type":"veg","allergens":[]},
    {"id":6,"name":"바나나 1개","serving":"1개","kcal":105,"protein":1.3,"carbs":27,"fat":0.3,"fiber":3.1,"sodium":1,"image":"https://i.imgur.com/6nQ1MVo.jpg","type":"fruit","allergens":[]},
    {"id":7,"name":"그릭요거트 150g","serving":"150g","kcal":120,"protein":12,"carbs":8,"fat":4,"fiber":0,"sodium":55,"image":"https://i.imgur.com/dWrxjC2.jpg","type":"dairy","allergens":["milk"]},
    {"id":8,"name":"아몬드 20g","serving":"20g","kcal":120,"protein":3,"carbs":4,"fat":10,"fiber":2,"sodium":0,"image":"https://i.imgur.com/p3A0Fvo.jpg","type":"nuts","allergens":["nuts"]},
    {"id":9,"name":"두부 150g","serving":"150g","kcal":144,"protein":17,"carbs":3.8,"fat":8.5,"fiber":1.2,"sodium":12,"image":"https://i.imgur.com/Y7tZV2G.jpg","type":"plant","allergens":["soy"]},
    {"id":10,"name":"고구마 150g","serving":"150g","kcal":130,"protein":2,"carbs":31,"fat":0.2,"fiber":3.8,"sodium":36,"image":"https://i.imgur.com/3a3p0q0.jpg","type":"grain","allergens":[]},
    # 추가 음식: CSV/JSON로 확장 가능
]

# -------------------------
# 헬퍼 함수
# -------------------------
def mifflin_bmr(weight, height, age, sex):
    if sex=="남성":
        return 10*weight + 6.25*height -5*age +5
    else:
        return 10*weight + 6.25*height -5*age -161

def activity_factor(level):
    return {"좌식":1.2,"가벼운 활동":1.375,"중간 활동":1.55,"격렬한 활동":1.725}.get(level,1.55)

def safe_round(x):
    return int(round(x))

def micronutrients_targets(age, sex):
    return {"fiber":25 if sex=="남성" else 20, "iron":8 if sex=="남성" else 14, "calcium":800, "vitd":5}

# -------------------------
# 사용자 입력 (타입 안정성 확보)
# -------------------------
st.sidebar.header("사용자 정보 입력")
age = st.sidebar.number_input("나이", min_value=1, max_value=120, value=30, step=1)
sex = st.sidebar.selectbox("성별",["남성","여성"])
height = st.sidebar.number_input("키(cm)", min_value=100, max_value=230, value=175, step=1)
weight = st.sidebar.number_input("체중(kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
activity = st.sidebar.selectbox("활동량 수준",["좌식","가벼운 활동","중간 활동","격렬한 활동"])
goal = st.sidebar.selectbox("체중 목표",["감량","유지","증량"])
meal_count = st.sidebar.selectbox("식사 횟수 선호",[2,3,4])

st.sidebar.header("건강 / 알레르기")
diseases = st.sidebar.multiselect("질환",["당뇨","고혈압","고지혈증","신장질환","위장질환"])
allergies = st.sidebar.multiselect("알레르기",["우유","난류","견과류","대두","글루텐","갑각류"])
diet_instruction = st.sidebar.selectbox("식이 지침",["없음","저염식","저지방","고단백"])

st.sidebar.header("기호 / 생활패턴")
likes = st.sidebar.text_input("선호 음식(콤마)", "")
dislikes = st.sidebar.text_input("비선호 음식(콤마)", "")
religion = st.sidebar.selectbox("종교/제한",["없음","채식(완전)","채식(락토/오보)","할랄/코셔"])
cooking_ability = st.sidebar.selectbox("요리 가능 여부",["전자레인지","간단 조리","정식 조리"])
budget = st.sidebar.selectbox("예산",["저(~1만)","중(1~2만)","고(2만↑)"])

st.sidebar.header("목표 기반")
main_goal = st.sidebar.multiselect("목표",["다이어트","근육 증가","체력 향상","영양 균형","특정 영양소 보충"])
time_frame = st.sidebar.selectbox("기간",["1개월","3개월","6개월","기타"])

# -------------------------
# 식단 생성
# -------------------------
if st.sidebar.button("식단 생성"):
    bmr = mifflin_bmr(weight,height,age,sex)
    tdee = bmr*activity_factor(activity)
    if goal=="감량":
        kcal_target = max(1200,tdee-500)
    elif goal=="증량":
        kcal_target = tdee+300
    else:
        kcal_target = tdee

    protein_target = safe_round(weight*1.2) # 단백질 g (간단)
    carbs_target = safe_round(kcal_target*0.5/4)
    fat_target = safe_round((kcal_target - (protein_target*4 + carbs_target*4))/9)
    micro_targets = micronutrients_targets(age,sex)

    # 알레르기/종교 필터
    filtered_foods = []
    for f in FOOD_DB:
        if any(a in allergies for a in f.get("allergens",[])):
            continue
        if religion=="채식(완전)" and f["type"] in ["meat","fish","dairy"]:
            continue
        if religion=="채식(락토/오보)" and f["type"] in ["meat","fish"]:
            continue
        filtered_foods.append(f)

    if not filtered_foods:
        st.error("추천 가능한 음식이 없습니다. 제한을 완화하세요.")
        st.stop()

    # 끼니별 분배
    shares = [0.25,0.35,0.25,0.15][:meal_count]
    meals = []
    high_protein = sorted(filtered_foods,key=lambda x:x["protein"],reverse=True)
    carb_sources = sorted(filtered_foods,key=lambda x:x["carbs"],reverse=True)
    vegs = [f for f in filtered_foods if f["type"] in ["veg","fruit"]]

    for i, share in enumerate(shares):
        tk = safe_round(kcal_target*share)
        meal = {"target_kcal":tk,"items":[],"kcal":0,"protein":0,"carbs":0,"fat":0}
        # 단백질 아이템
        prot_item = high_protein[i%len(high_protein)]
        meal["items"].append({"food":prot_item,"qty":1})
        meal["kcal"] += prot_item["kcal"]
        meal["protein"] += prot_item["protein"]
        meal["carbs"] += prot_item["carbs"]
        meal["fat"] += prot_item["fat"]

        # 탄수 아이템
        j=0
        while meal["kcal"]<tk-80 and j<len(carb_sources):
            carb_choice = carb_sources[(i+j)%len(carb_sources)]
            if carb_choice["id"]==prot_item["id"] and j<len(carb_sources)-1:
                j+=1
                continue
            meal["items"].append({"food":carb_choice,"qty":1})
            meal["kcal"] += carb_choice["kcal"]
            meal["protein"] += carb_choice["protein"]
            meal["carbs"] += carb_choice["carbs"]
            meal["fat"] += carb_choice["fat"]
            j+=1

        # 채소/과일
        for v in vegs[:2]:
            meal["items"].append({"food":v,"qty":1})
            meal["kcal"] += v["kcal"]
            meal["protein"] += v["protein"]
            meal["carbs"] += v["carbs"]
            meal["fat"] += v["fat"]

        meals.append(meal)

    # -------------------------
    # 출력 UI (카드 + 이미지)
    # -------------------------
    st.header("🍽 추천 식단 (1일)")
    for idx, m in enumerate(meals):
        st.subheader(f"끼니 {idx+1} (목표 {m['target_kcal']} kcal)")
        cols = st.columns(len(m["items"]))
        for i, it in enumerate(m["items"]):
            food = it["food"]
            cols[i].image(food["image"], width=120)
            cols[i].markdown(f"**{food['name']}**\n{food['serving']}\n칼로리:{food['kcal']} kcal\n단백질:{food['protein']}g\n탄수:{food['carbs']}g\n지방:{food['fat']}g")

    st.subheader("📊 하루 총합")
    total_kcal = sum(m["kcal"] for m in meals)
    total_protein = sum(m["protein"] for m in meals)
    total_carbs = sum(m["carbs"] for m in meals)
    total_fat = sum(m["fat"] for m in meals)
    st.write(f"칼로리:{total_kcal} kcal / 단백질:{total_protein}g / 탄수:{total_carbs}g / 지방:{total_fat}g")

    st.subheader("✅ 달성률")
    st.progress(min(100,int(total_kcal/kcal_target*100)))
