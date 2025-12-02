# healicious_full_app.py
import streamlit as st
import pandas as pd
import numpy as np
import os
from math import radians, cos, sin, asin, sqrt
import altair as alt
import logging
import traceback
import datetime

# -------------------------
# 페이지 설정
# -------------------------
st.set_page_config(page_title="Healicious", layout="centered", initial_sidebar_state="expanded")

# -------------------------
# 로거 설정 (안전하게)
# -------------------------
def setup_logger(log_path="healicious_error.log"):
    logger = logging.getLogger("healicious_logger")
    if not logger.handlers:
        logger.setLevel(logging.ERROR)
        try:
            handler = logging.FileHandler(log_path, encoding="utf-8")
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        except Exception:
            # 파일 쓰기 실패 시 콘솔 핸들러로 대체 (앱 중단 방지)
            ch = logging.StreamHandler()
            ch.setLevel(logging.ERROR)
            logger.addHandler(ch)
    return logger

logger = setup_logger()

# -------------------------
# 헬퍼: 안전한 Altair 출력
# -------------------------
def safe_show_altair(df, enc_x, enc_y, enc_color=None, tooltip=None, width=600, height=400, container_width=True):
    if df is None:
        st.error("차트 표시용 데이터가 없습니다.")
        return
    if not hasattr(df, "columns"):
        st.error("유효하지 않은 데이터입니다.")
        return
    if df.empty:
        st.info("차트에 표시할 데이터가 없습니다.")
        return

    try:
        encodings = {
            "x": alt.X(enc_x),
            "y": alt.Y(enc_y)
        }
        if enc_color:
            encodings["color"] = alt.Color(enc_color)
        if tooltip:
            encodings["tooltip"] = tooltip

        chart = alt.Chart(df).mark_bar().encode(**encodings).properties(width=width, height=height)
        st.altair_chart(chart, use_container_width=container_width)
    except Exception:
        tb = traceback.format_exc()
        logger.error("차트 생성 중 예외 발생:\n%s", tb)
        # 로그에 추가 기록
        try:
            with open("healicious_error.log", "a", encoding="utf-8") as f:
                f.write(f"\n--- {datetime.datetime.now().isoformat()} ---\n")
                f.write(tb)
        except Exception:
            pass
        st.error("차트 표시 중 문제가 발생했습니다. 관리자 로그를 확인해 주세요.")

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
                for col in ["food","calories","protein","carbs","fat","category","tags"]:
                    if col not in df.columns:
                        df[col] = ""
                st.sidebar.success(f"외부 DB 로드 성공: {os.path.basename(p)} ({len(df)}개)")
                return df
            except Exception as e:
                st.sidebar.warning(f"{os.path.basename(p)} 로드 실패: {e}")

    # 외부 파일 없으면 내장 DB 생성
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
            fat = round(float(rng.integers(0, 20)),1)
            cat = "샐러드"
            tags = "salad"
        else:
            food = rng.choice(snacks)
            calories = int(rng.integers(50, 350))
            protein = int(rng.integers(1, 10))
            carbs = int(rng.integers(10, 50))
            fat = round(float(rng.integers(0, 20)),1)
            cat = "간식"
            tags = "snack"
        rows.append((food, calories, protein, carbs, fat, cat, tags))

    df = pd.DataFrame(rows, columns=["food","calories","protein","carbs","fat","category","tags"])
    df = df.reset_index(drop=True)
    st.sidebar.info(f"내장 DB 사용: {len(df)}개")
    return df

# FOOD_DB 전역 초기화
FOOD_DB = load_food_database(target_count=700)

# -------------------------
# 간단 추천 함수
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
    grain_candidates = df[df["category"].str.contains("곡류|밥|grain|pasta|bread|면", na=False, case=False)]
    veg_candidates = df[df["category"].str.contains("채소|샐러드|vegetable|야채", na=False, case=False)]
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
                total_cal = float(p["calories"]) + float(g["calories"]) + float(v["calories"])
                total_prot = float(p["protein"]) + float(g["protein"]) + float(v["protein"])
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

def plan_full_day(meal_targets, protein_daily_target, db, diet_pref=None, allergy_list=None, religion_list=None):
    if allergy_list is None:
        allergy_list = []
    if religion_list is None:
        religion_list = []
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
# 간단 에너지/단백질 계산 (기본값)
# -------------------------
def calculate_daily_calories(height_cm, weight_kg, age, gender, activity_factor, goal):
    # Mifflin-St Jeor 간단 구현 (성별 male/female)
    try:
        if gender.lower() in ["male","m","남","남자"]:
            s = 5
        else:
            s = -161
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + s
        tdee = bmr * activity_factor
        if goal == "체중 감량":
            tdee = tdee - 500
        elif goal == "체중 증가":
            tdee = tdee + 400
        return max(1100, round(tdee))
    except Exception:
        logger.error("calorie calc error:\n%s", traceback.format_exc())
        return 2000

def calculate_protein_target(weight_kg, goal):
    # 목표에 따라 g/kg 설정
    try:
        if goal == "근육 증가" or goal == "체중 증가":
            per_kg = 1.8
        elif goal == "체중 감량" or goal == "체지방 감소":
            per_kg = 1.6
        else:
            per_kg = 1.2
        return int(round(weight_kg * per_kg))
    except Exception:
        logger.error("protein calc error:\n%s", traceback.format_exc())
        return int(round(60))

# -------------------------
# UI: 입력 폼
# -------------------------
st.title("Healicious - 개인화 영양식 설계")
st.caption("승주님을 위해 안전하게 예외를 처리하는 버전입니다.")

with st.sidebar.form(key="user_input"):
    st.header("기본 정보")
    height = st.number_input("키(cm)", min_value=100, max_value=230, value=170)
    weight = st.number_input("몸무게(kg)", min_value=30.0, max_value=200.0, value=65.0)
    age = st.number_input("나이", min_value=10, max_value=120, value=17)
    gender = st.selectbox("성별", options=["male","female","남","여"], index=0)
    activity = st.selectbox("활동수준", options=[1.2,1.375,1.55,1.725,1.9], index=2, format_func=lambda x: f"활동지수 {x}")
    goal = st.selectbox("목표", options=["유지","체중 감량","체중 증가","근육 증가","체지방 감소"], index=0)
    preferred_food = st.text_input("선호 음식 (쉼표로 복수 가능)", value="")
    allergy = st.text_input("알레르기(쉼표로 구분)", value="")
    religion = st.text_input("종교 제한(쉼표로 구분)", value="")
    submit = st.form_submit_button("저장")

# 기본값 보장
if 'preferred_food' not in locals():
    preferred_food = ""
if 'allergy' not in locals():
    allergy = ""
if 'religion' not in locals():
    religion = ""

# -------------------------
# 실행 버튼 및 출력
# -------------------------
if st.button("🍽️ 식단 설계 시작하기"):
    try:
        tdee = calculate_daily_calories(height, weight, age, gender, activity, goal)
        protein_target = calculate_protein_target(weight, goal)
        st.success(f"하루 권장 칼로리: {tdee} kcal, 하루 단백질 목표: {protein_target} g")

        split = {"breakfast": round(tdee*0.3), "lunch": round(tdee*0.4), "dinner": round(tdee*0.3)}
        st.markdown("### 오늘의 식사 목표")
        col1, col2, col3 = st.columns(3)
        col1.metric("아침 칼로리", f"{split['breakfast']} kcal")
        col2.metric("점심 칼로리", f"{split['lunch']} kcal")
        col3.metric("저녁 칼로리", f"{split['dinner']} kcal")

        allergy_list = [x.strip() for x in (allergy or "").split(",") if x.strip()]
        religion_list = [x.strip() for x in (religion or "").split(",") if x.strip()]

        day_plan = plan_full_day(split, protein_target, FOOD_DB, diet_pref=None, allergy_list=allergy_list, religion_list=religion_list)

        st.markdown("### 추천 식단 (하루)")
        for meal_name in ["breakfast","lunch","dinner"]:
            st.subheader(meal_name.capitalize())
            item = day_plan.get(meal_name, {})
            if not item:
                st.info("추천할 식단이 없습니다.")
                continue
            if item["type"] == "table":
                st.table(item["data"])
            else:
                data = item["data"]
                st.write("구성:", ", ".join(data["foods"]))
                st.write(f"칼로리 합: {data['cal']:.0f} kcal, 단백질 합: {data['protein']:.0f} g")
                st.write(f"태그: {data.get('tags','')}")
        # 예시 차트: 하루 식사별 목표 칼로리(차트용 df 생성 및 안전 출력)
        chart_df = pd.DataFrame({
            "meal":["아침","점심","저녁"],
            "cal":[split["breakfast"], split["lunch"], split["dinner"]],
            "category":["목표","목표","목표"]
        })
        # 검증: 필요한 컬럼 존재 여부
        req_cols = ["meal","cal","category"]
        missing = [c for c in req_cols if c not in chart_df.columns]
        if missing:
            st.error(f"차트에 필요한 컬럼이 없습니다: {', '.join(missing)}")
        else:
            safe_show_altair(chart_df, enc_x='meal:N', enc_y='cal:Q', enc_color='category:N', tooltip=['meal','cal','category'])

    except Exception:
        tb = traceback.format_exc()
        logger.error("메인 실행 중 예외 발생:\n%s", tb)
        st.error("식단 생성 중 문제가 발생했습니다. 관리자 로그를 확인해 주세요.")
