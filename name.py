# healicious_full_app.py
import streamlit as st
import pandas as pd
import numpy as np
import os
from math import radians, cos, sin, asin, sqrt
import altair as alt

st.set_page_config(page_title="Healicious", layout="centered", initial_sidebar_state="expanded")

# -------------------------
# 헬퍼: 거리계산(Haversine)
# -------------------------
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km

# -------------------------
# DB 로드: 외부 우선, 내장 기본 제공
# -------------------------
def load_food_database(target_count=800):
    file_2000 = "/mnt/data/food_2000.xlsx"
    file_700 = "/mnt/data/food_700.xlsx"
    file_custom = "/mnt/data/20250408_음식DB.xlsx"
    for p in [file_2000, file_700, file_custom]:
        if os.path.exists(p):
            try:
                df = pd.read_excel(p)
                # 필수 컬럼 보장
                for col in ["food","calories","protein","carbs","fat","category","tags"]:
                    if col not in df.columns:
                        df[col] = ""
                st.sidebar.success(f"외부 DB 로드 성공: {os.path.basename(p)} ({len(df)}개)")
                return df
            except Exception as e:
                st.sidebar.warning(f"{os.path.basename(p)} 로드 실패: {e}")

    # 외부 파일 없으면 내장 DB 생성 (현실적 이름 + 태그)
    base = [
        ("닭가슴살 구이(100g)",165,31,0,3.6,"단백질","chicken,protein"),
        ("훈제연어(100g)",200,20,3,12,"단백질","salmon,omega3"),
        ("연어스테이크(150g)",320,22,0,18,"단백질","salmon,omega3"),
        ("삶은계란(2개)",154,12,1.2,10,"단백질","egg,protein"),
        ("두부 한모(200g)",160,16,4,8,"단백질","tofu,vegan"),
        ("현미밥(1공기)",210,4,44,2,"곡류","rice,grain"),
        ("백미밥(1공기)",280,4,56,1,"곡류","rice,grain"),
        ("된장찌개(1인분)",180,10,12,8,"국/찌개","soy,vitB"),
        ("김치찌개(1인분)",240,18,12,14,"국/찌개","kimchi,vitC"),
        ("비빔밥(1인분)",600,20,90,18,"한식","mixed,vegetable"),
        ("토마토파스타(1인분)",640,18,90,18,"면류","tomato,vitC"),
        ("크림파스타(1인분)",760,16,90,32,"면류","cream,highfat"),
        ("시저샐러드(1인분)",320,12,18,22,"샐러드","lettuce,calcium"),
        ("그릭 요거트(150g)",150,16,10,5,"간식","yogurt,probiotic"),
        ("통밀빵(1조각)",110,5,22,2,"빵","wholegrain,fiber"),
        ("고등어구이(1토막)",330,22,0,22,"반찬","fish,omega3"),
        ("감자조림(1인분)",150,3,28,2,"반찬","potato,carb"),
        ("계란말이(1인분)",230,14,4,16,"반찬","egg,protein"),
        ("닭갈비(1인분)",680,35,60,30,"외식","spicy,protein"),
        ("김밥(1줄)",320,10,55,6,"분식","seaweed,carb")
    ]
    rows = [r for r in base]

    # 패턴 확장: 현실적 이름을 조합하여 target_count까지 채움
    proteins = ["닭가슴살","훈제연어","연어","삼치","고등어","돼지안심","소고기 스테이크","두부","계란"]
    grains = ["현미밥","백미밥","잡곡밥","오트밀죽","파스타","우동","칼국수"]
    sides = ["된장찌개","김치찌개","미역국","감자조림","시금치나물","콩나물무침","오이무침"]
    salads = ["그린 샐러드","아보카도 샐러드","치킨 샐러드","연어 샐러드","퀴노아 샐러드"]
    snacks = ["통밀빵","크루아상","찐고구마","군고구마","단호박","바나나","호두(30g)"]

    rng = np.random.default_rng(seed=42)
    while len(rows) < target_count:
        choice = rng.choice(["prot","grain","side","salad","snack"])
        if choice == "prot":
            name = rng.choice(proteins)
            suffix = rng.choice(["구이(100g)","스테이크(150g)","샐러드(1인분)","샌드위치(1인분)"])
            food = f"{name} {suffix}"
            calories = int(rng.integers(120, 500))
            protein = int(rng.integers(8, 45))
            carbs = int(rng.integers(0, 60))
            fat = round(float(rng.integers(0, 30)),1)
            cat = "단백질"
            tags = name.lower()
        elif choice == "grain":
            name = rng.choice(grains)
            food = f"{name}(1인분)"
            calories = int(rng.integers(150, 750))
            protein = int(rng.integers(2, 18))
            carbs = int(rng.integers(20, 120))
            fat = round(float(rng.integers(0, 15)),1)
            cat = "곡류"
            tags = "grain"
        elif choice == "side":
            name = rng.choice(sides)
            food = f"{name}(1인분)"
            calories = int(rng.integers(20, 350))
            protein = int(rng.integers(1, 18))
            carbs = int(rng.integers(0, 50))
            fat = round(float(rng.integers(0, 20)),1)
            cat = "반찬"
            tags = "side"
        elif choice == "salad":
            food = rng.choice(salads) + "(1인분)"
            calories = int(rng.integers(80, 420))
            protein = int(rng.integers(2, 30))
            carbs = int(rng.integers(5, 40))
            fat = round(float(rng.integers(0, 30)),1)
            cat = "샐러드"
            tags = "salad"
        else:
            food = rng.choice(snacks)
            calories = int(rng.integers(50, 420))
            protein = int(rng.integers(1, 20))
            carbs = int(rng.integers(5, 70))
            fat = round(float(rng.integers(0, 30)),1)
            cat = "간식"
            tags = "snack"
        rows.append((food, calories, protein, carbs, fat, cat, tags))

    df = pd.DataFrame(rows, columns=["food","calories","protein","carbs","fat","category","tags"])
    st.sidebar.info(f"내장 DB 사용 (항목: {len(df)})")
    return df

# 기본 DB 로드 (원하면 target_count 인자 변경)
FOOD_DB = load_food_database(target_count=800)

# -------------------------
# 하나고등학교 인근 식당 샘플(EXTENDER)
# -------------------------
def load_nearby_restaurant_db():
    file_rest = "/mnt/data/nearby_restaurants.csv"
    if os.path.exists(file_rest):
        try:
            rdf = pd.read_csv(file_rest)
            return rdf
        except:
            pass
    sample = [
        {"name":"하나분식","lat":37.5975,"lon":127.0389,"category":"분식","est_cal":"라볶이 700kcal"},
        {"name":"가벼운샐러드","lat":37.5972,"lon":127.0395,"category":"샐러드","est_cal":"샐러드 350kcal"},
        {"name":"한솥도시락","lat":37.5969,"lon":127.0390,"category":"도시락","est_cal":"도시락 650kcal"},
        {"name":"국수집","lat":37.5978,"lon":127.0378,"category":"국수","est_cal":"칼국수 550kcal"},
        {"name":"김밥천국","lat":37.5981,"lon":127.0385,"category":"분식","est_cal":"김밥 320kcal"},
    ]
    return pd.DataFrame(sample)

HANAGOODGE_LAT = 37.5974
HANAGOODGE_LON = 127.0389
NEARBY_RESTAURANTS = load_nearby_restaurant_db()

# -------------------------
# UI: 사이드바(설정)
# -------------------------
st.sidebar.title("설정")
st.sidebar.markdown("앱 설정 및 DB 관리")
db_target = st.sidebar.selectbox("내장 DB 크기", [700,800,1000,1500,2000], index=1)
use_external = st.sidebar.checkbox("외부 DB 우선 사용 (있으면 자동 로드)", value=True)
if st.sidebar.button("내장 DB 재생성"):
    FOOD_DB = load_food_database(target_count=db_target)
    st.experimental_rerun()

# -------------------------
# 사용자 입력(메인)
# -------------------------
st.markdown("<h2>🥗 Healicious — 개인 맞춤 식단 설계</h2>", unsafe_allow_html=True)
with st.expander("사용자 정보 입력", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input("키 (cm)", value=170, min_value=100, max_value=230)
        weight = st.number_input("몸무게 (kg)", value=65, min_value=30, max_value=200)
        age = st.number_input("나이", value=17, min_value=10, max_value=90)
        gender = st.selectbox("성별", ["남성","여성"])
    with col2:
        sleep = st.number_input("수면 시간 (시간)", value=7, min_value=3, max_value=12)
        activity = st.selectbox("활동량", ["적음","보통","많음"])
        goal = st.selectbox("건강 목표", ["체중 감량","체중 증가","유지","체지방 감소","근육 증가"])
        diet_preference = st.selectbox("식단 성향", ["균형잡힌 식단","고단백","저탄수","저지방","비건","채식 위주"])

with st.expander("추가 설정", expanded=False):
    preferred_food = st.text_input("좋아하는 음식 (선택)")
    mood = st.selectbox("오늘 기분", ["보통","피곤함","상쾌함","스트레스","기운 없음"])
    allergy = st.text_input("알레르기 (쉼표로 구분)")
    religion = st.text_input("못 먹는 음식(종교 등, 쉼표)")

# -------------------------
# 칼로리/단백질 목표 계산
# -------------------------
def calculate_daily_calories(height, weight, age, gender, activity, goal):
    if gender == "남성":
        bmr = 66 + 13.7 * weight + 5 * height - 6.8 * age
    else:
        bmr = 655 + 9.6 * weight + 1.8 * height - 4.7 * age
    factor = {"적음":1.2, "보통":1.375, "많음":1.55}[activity]
    tdee = bmr * factor
    if goal == "체중 감량": tdee -= 300
    if goal == "체중 증가": tdee += 300
    if goal == "근육 증가": tdee += 150
    return round(tdee)

def calculate_protein_target(weight, goal):
    if goal == "근육 증가":
        g = 1.8
    elif goal in ["체중 감량","체지방 감소"]:
        g = 1.4
    elif goal == "체중 증가":
        g = 1.2
    else:
        g = 1.0
    return round(weight * g)

# -------------------------
# 추천 및 균형화 알고리즘
# -------------------------
def recommend_meals_simple(target_cal, preferred_food="", allergy="", religion="", diet_pref=None, top_n=6):
    df = FOOD_DB.copy()
    if preferred_food:
        df = df[df["food"].str.contains(preferred_food, na=False)]
    if allergy:
        for a in [x.strip() for x in allergy.split(",") if x.strip()]:
            df = df[~df["food"].str.contains(a, na=False)]
    if religion:
        for r in [x.strip() for x in religion.split(",") if x.strip()]:
            df = df[~df["food"].str.contains(r, na=False)]
    if len(df) == 0:
        df = FOOD_DB.copy()
    df["cal_diff"] = (df["calories"] - target_cal).abs()
    df = df.sort_values("cal_diff")
    return df.head(top_n)[["food","calories","protein","carbs","fat","category","tags"]]

# 더 정교한 조합 탐색(메인 단백질+곡류+채소)
def find_best_meal_combination(target_cal, protein_target_meal, available_db, used_foods=set(), required_tags=set(), sample_size=20, top_k=30):
    df = available_db.copy()
    df = df[~df["food"].isin(used_foods)]
    protein_candidates = df[df["category"].str.contains("단백질|protein|meat|fish|tofu", na=False, case=False)]
    grain_candidates = df[df["category"].str.contains("곡류|밥|grain|pasta|bread", na=False, case=False)]
    veg_candidates = df[df["category"].str.contains("채소|샐러드|vegetable", na=False, case=False)]
    if protein_candidates.empty: protein_candidates = df
    if grain_candidates.empty: grain_candidates = df
    if veg_candidates.empty: veg_candidates = df

    prot_sample = protein_candidates.sample(min(sample_size, len(protein_candidates)), random_state=42)
    grain_sample = grain_candidates.sample(min(sample_size, len(grain_candidates)), random_state=43)
    veg_sample = veg_candidates.sample(min(sample_size, len(veg_candidates)), random_state=44)

    combos = []
    for _, p in prot_sample.iterrows():
        for _, g in grain_sample.iterrows():
            for _, v in veg_sample.iterrows():
                total_cal = p["calories"] + g["calories"] + v["calories"]
                total_prot = p["protein"] + g["protein"] + v["protein"]
                cal_diff = abs(total_cal - target_cal)
                prot_diff = max(0, protein_target_meal - total_prot)
                tag_bonus = 0
                for t in required_tags:
                    if str(p["tags"]).find(t) >= 0 or str(g["tags"]).find(t) >= 0 or str(v["tags"]).find(t) >= 0:
                        tag_bonus += 1
                score = cal_diff + prot_diff*8 - tag_bonus*6
                combos.append({"foods":[p["food"], g["food"], v["food"]],
                               "cal": total_cal, "protein": total_prot, "score": score,
                               "tags": f"{p['tags']},{g['tags']},{v['tags']}"})
    combos_sorted = sorted(combos, key=lambda x: x["score"])
    return combos_sorted[:top_k]

def plan_full_day(meal_targets, protein_daily_target, db, diet_pref=None, allergy_list=[], religion_list=[]):
    df = db.copy()
    for a in allergy_list:
        df = df[~df["food"].str.contains(a, na=False)]
    for r in religion_list:
        df = df[~df["food"].str.contains(r, na=False)]

    protein_break = round(protein_daily_target * 0.3)
    protein_lunch = round(protein_daily_target * 0.4)
    protein_dinner = max(0, protein_daily_target - protein_break - protein_lunch)

    used = set()
    tag_cycle = ["vitC","iron","calcium","vitA","fiber"]
    day_plan = {}

    for i, meal in enumerate(["breakfast","lunch","dinner"]):
        req_tag = {tag_cycle[i % len(tag_cycle)]}
        p_target = [protein_break, protein_lunch, protein_dinner][i]
        combos = find_best_meal_combination(meal_targets[meal], p_target, df, used_foods=used, required_tags=req_tag, sample_size=30, top_k=20)
        if not combos:
            sel = recommend_meals_simple(meal_targets[meal], top_n=3)
            day_plan[meal] = {"type":"table", "data":sel}
            used.update(sel["food"].tolist())
            df = df[~df["food"].isin(used)]
            continue
        best = combos[0]
        day_plan[meal] = {"type":"combo", "data":best}
        used.update(best["foods"])
        df = df[~df["food"].isin(used)]
    return day_plan

# -------------------------
# 실행 버튼 및 출력(개선된 UX)
# -------------------------
run = st.button("🍽️ 식단 설계 시작하기")

if run:
    tdee = calculate_daily_calories(height, weight, age, gender, activity, goal)
    protein_target = calculate_protein_target(weight, goal)
    st.success(f"하루 권장 칼로리: **{tdee} kcal**, 하루 단백질 목표: **{protein_target} g**")

    split = {"breakfast": round(tdee*0.3), "lunch": round(tdee*0.4), "dinner": round(tdee*0.3)}
    st.markdown("### 오늘의 식사 목표")
    col1, col2, col3 = st.columns(3)
    col1.metric("아침 칼로리", f"{split['breakfast']} kcal")
    col2.metric("점심 칼로리", f"{split['lunch']} kcal")
    col3.metric("저녁 칼로리", f"{split['dinner']} kcal")

    allergy_list = [x.strip() for x in allergy.split(",") if x.strip()]
    religion_list = [x.strip() for x in religion.split(",") if x.strip()]

    day_plan = plan_full_day(split, protein_target, FOOD_DB, diet_pref=diet_preference, allergy_list=allergy_list, religion_list=religion_list)

    # 각 끼 렌더링: 카드 형태(간단) + 교체 버튼(대체 추천 표시)
    for meal in ["breakfast","lunch","dinner"]:
        st.markdown(f"### {'🍳 아침' if meal=='breakfast' else '🍚 점심' if meal=='lunch' else '🍽️ 저녁'} (목표: {split[meal]} kcal)")
        plan = day_plan.get(meal)
        if plan is None:
            st.write("추천 항목이 없습니다.")
            continue
        if plan["type"] == "table":
            st.dataframe(plan["data"])
        else:
            combo = plan["data"]
            foods = combo["foods"]
            cal = combo["cal"]
            prot = combo["protein"]
            tags = combo["tags"]
            st.info(f"선택된 조합: {', '.join(foods)}")
            st.write(f"합계 칼로리: {cal} kcal  |  합계 단백질: {prot} g")
            st.write(f"태그: {tags}")
            # 대체 추천: 상위 5개 표시
            alternatives = find_best_meal_combination(split[meal], round(protein_target * (0.3 if meal=='breakfast' else 0.4 if meal=='lunch' else 0.3)),
                                                      FOOD_DB, used_foods=set(), required_tags=set(), sample_size=25, top_k=5)
            if alternatives:
                with st.expander("대체 조합 보기"):
                    for i, alt in enumerate(alternatives):
                        st.write(f"{i+1}. {', '.join(alt['foods'])} — {alt['cal']} kcal / {alt['protein']} g (score {alt['score']:.1f})")

    # 하루 요약 그래프(칼로리/탄단지)
    summary_rows = []
    for meal in ["breakfast","lunch","dinner"]:
        p = day_plan[meal]
        if p["type"] == "table":
            dfm = p["data"]
            total_cal = dfm["calories"].sum()
            total_prot = dfm["protein"].sum()
            total_carbs = dfm["carbs"].sum()
            total_fat = dfm["fat"].sum()
        else:
            d = p["data"]
            total_cal = d["cal"]
            total_prot = d["protein"]
            # carbs/fat 추정(없다면 0)
            total_carbs = 0
            total_fat = 0
        summary_rows.append({"meal":meal, "cal":total_cal, "protein":total_prot, "carbs":total_carbs, "fat":total_fat})
    summary_df = pd.DataFrame(summary_rows)
    summary_melt = summary_df.melt(id_vars="meal", value_vars=["cal","protein","carbs","fat"], var_name="nutrient", value_name="value")
    chart = alt.Chart(summary_melt).mark_bar().encode(
        x=alt.X('meal:N', title='식사'),
        y=alt.Y('value:Q', title='양'),
        color='nutrient:N',
        column=alt.Column('nutrient:N', header=alt.Header(labelAngle=0))
    ).properties(height=150)
    st.altair_chart(chart, use_container_width=True)

# -------------------------
# 하나고등학교 인근 식당 추천(EXTENDER)
# -------------------------
st.markdown("## 🏫 하나고등학교 인근 식당 추천")
st.markdown("샘플 데이터를 사용합니다. 실제 CSV(/mnt/data/nearby_restaurants.csv)나 API로 교체하세요.")
if st.button("🔎 근처 식당 찾기 (반경 1.0km)"):
    rdf = NEARBY_RESTAURANTS.copy()
    rdf["distance_km"] = rdf.apply(lambda r: haversine(HANAGOODGE_LAT, HANAGOODGE_LON, r["lat"], r["lon"]), axis=1)
    nearby = rdf[rdf["distance_km"] <= 1.0].sort_values("distance_km").reset_index(drop=True)
    if nearby.empty:
        st.info("1km 반경 내 샘플 식당이 없습니다. nearby_restaurants.csv 업로드 또는 API 연동을 권장합니다.")
        st.dataframe(rdf.sort_values("distance_km").head(10))
    else:
        st.dataframe(nearby[["name","category","est_cal","distance_km"]])

# -------------------------
# 과학적 근거 설명
# -------------------------
st.markdown("## 🔬 과학적 원리 (펼쳐보기)")
with st.expander("영양학적/생리학적 기반 설명 보기"):
    st.write("""
    • BMR: Harris–Benedict 공식을 사용하여 기초대사량을 추정합니다.
    • 활동지수: 활동 수준에 따라 1.2~1.55 배수로 TDEE 산출.
    • 목표별 칼로리 조정: 감량 -300 kcal, 증량 +300 kcal, 근육 증가 +150 kcal.
    • 식사 배분: 아침 30% / 점심 40% / 저녁 30% (기본 가이드).
    • 균형화 원리: 각 식사에 메인 단백질 + 곡류(또는 대체) + 채소를 포함하여 탄단지 균형을 맞추고, 미세영양(비타민·미네랄) 태그를 끼니별로 분산시킵니다.
    """)

# -------------------------
# 관리자 안내
# -------------------------
st.markdown("## 개발자/관리자 안내")
st.write("""
- 외부 DB(file: /mnt/data/food_2000.xlsx 또는 food_700.xlsx 또는 20250408_음식DB.xlsx)를 올리면 자동 로드합니다.
- 추천 알고리즘·UI 개선은 추가로 조정 가능합니다(이미지, 드래그 앤 드롭, 사용자 이력 저장 등).
- 2000개 실제 항목을 원하시면 제가 샘플 엑셀을 생성해 제공해 드릴 수 있습니다.
""")
