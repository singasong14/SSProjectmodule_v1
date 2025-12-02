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
import requests
import folium
from streamlit_folium import st_folium

# -------------------------
# 페이지 설정
# -------------------------
st.set_page_config(page_title="Healicious", layout="wide", initial_sidebar_state="expanded")
st.title("Healicious - 개인화 영양식 설계")
st.caption("승주님을 위한 안전한 예외 처리·UX 개선·과학적 근거·인근 식당 추천 통합 버전")

# -------------------------
# 로거 설정 (안전)
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
    try:
        lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return km
    except Exception:
        return float("inf")

# -------------------------
# DB 로드: 외부 우선, 내장 기본 제공
# -------------------------
def load_food_database(target_count=700):
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
    return df

# FOOD_DB 전역 초기화
FOOD_DB = load_food_database(target_count=700)

# -------------------------
# 추천 및 조합 로직
# -------------------------
def recommend_meals_simple(target_cal, preferred_food="", allergy="", religion="", diet_pref=None, top_n=6):
    df = FOOD_DB.copy()
    if preferred_food:
        try:
            df = df[df["food"].str.contains(preferred_food, na=False)]
        except Exception:
            pass
    if allergy:
        for a in [x.strip() for x in allergy.split(",") if x.strip()]:
            try:
                df = df[~df["food"].str.contains(a, na=False)]
            except Exception:
                pass
    if religion:
        for r in [x.strip() for x in religion.split(",") if x.strip()]:
            try:
                df = df[~df["food"].str.contains(r, na=False)]
            except Exception:
                pass
    if len(df) == 0:
        df = FOOD_DB.copy()
    try:
        df["cal_diff"] = (pd.to_numeric(df["calories"], errors="coerce") - float(target_cal)).abs()
    except Exception:
        df["cal_diff"] = 999999
    df = df.sort_values("cal_diff")
    return df.head(top_n)[["food","calories","protein","carbs","fat","category","tags"]]

def find_best_meal_combination(target_cal, protein_target_meal, available_db, used_foods=set(), required_tags=set(), sample_size=20, top_k=30):
    try:
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
                    total_cal = float(p.get("calories",0)) + float(g.get("calories",0)) + float(v.get("calories",0))
                    total_prot = float(p.get("protein",0)) + float(g.get("protein",0)) + float(v.get("protein",0))
                    cal_diff = abs(total_cal - float(target_cal))
                    prot_diff = max(0, protein_target_meal - total_prot)
                    tag_bonus = 0
                    for t in required_tags:
                        try:
                            if str(p.get("tags","")).find(t) >= 0 or str(g.get("tags","")).find(t) >= 0 or str(v.get("tags","")).find(t) >= 0:
                                tag_bonus += 1
                        except Exception:
                            pass
                    score = cal_diff + prot_diff*8 - tag_bonus*6
                    combos.append({"foods":[p.get("food",""), g.get("food",""), v.get("food","")],
                                   "cal": total_cal, "protein": total_prot, "score": score,
                                   "tags": f"{p.get('tags','')},{g.get('tags','')},{v.get('tags','')}"})
        combos_sorted = sorted(combos, key=lambda x: x["score"])
        return combos_sorted[:top_k]
    except Exception:
        logger.error("combo error:\n%s", traceback.format_exc())
        return []

def plan_full_day(meal_targets, protein_daily_target, db, diet_pref=None, allergy_list=None, religion_list=None):
    if allergy_list is None:
        allergy_list = []
    if religion_list is None:
        religion_list = []
    df = db.copy()
    for a in allergy_list:
        try:
            df = df[~df["food"].str.contains(a, na=False)]
        except Exception:
            pass
    for r in religion_list:
        try:
            df = df[~df["food"].str.contains(r, na=False)]
        except Exception:
            pass

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
            try:
                used.update(sel["food"].tolist())
            except Exception:
                pass
            df = df[~df["food"].isin(used)] if not df.empty else df
            continue
        best = combos[0]
        day_plan[meal] = {"type":"combo", "data":best}
        used.update(best["foods"])
        df = df[~df["food"].isin(used)] if not df.empty else df
    return day_plan

# -------------------------
# 간단 에너지/단백질 계산
# -------------------------
def calculate_daily_calories(height_cm, weight_kg, age, gender, activity_factor, goal):
    try:
        if isinstance(gender, str) and gender.lower() in ["male","m","남","남자"]:
            s = 5
        else:
            s = -161
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + s
        tdee = bmr * activity_factor
        if goal == "체중 감량":
            tdee = tdee - 300
        elif goal == "체중 증가":
            tdee = tdee + 300
        elif goal == "근육 증가":
            tdee = tdee + 150
        return max(1100, round(tdee))
    except Exception:
        logger.error("calorie calc error:\n%s", traceback.format_exc())
        return 2000

def calculate_protein_target(weight_kg, goal):
    try:
        if goal in ["근육 증가","체중 증가"]:
            per_kg = 1.8
        elif goal in ["체중 감량","체지방 감소"]:
            per_kg = 1.6
        else:
            per_kg = 1.2
        return int(round(weight_kg * per_kg))
    except Exception:
        logger.error("protein calc error:\n%s", traceback.format_exc())
        return 60

# -------------------------
# NEARBY RESTAURANTS 샘플 또는 CSV 로드
# -------------------------
NEARBY_CSV = "/mnt/data/nearby_restaurants.csv"
if os.path.exists(NEARBY_CSV):
    try:
        NEARBY_RESTAURANTS = pd.read_csv(NEARBY_CSV)
    except Exception:
        NEARBY_RESTAURANTS = pd.DataFrame([
            {"name":"샘플식당A","category":"한식","est_cal":600,"lat":37.596,"lon":127.019},
            {"name":"샘플카페B","category":"카페","est_cal":300,"lat":37.597,"lon":127.018},
        ])
else:
    NEARBY_RESTAURANTS = pd.DataFrame([
        {"name":"샘플식당A","category":"한식","est_cal":600,"lat":37.5938,"lon":127.0200},
        {"name":"샘플분식B","category":"분식","est_cal":450,"lat":37.5945,"lon":127.0210},
        {"name":"샘플카페C","category":"카페","est_cal":350,"lat":37.5925,"lon":127.0195},
    ])

# 하나고등학교 좌표 기본값 (대체 가능)
HANAGOODGE_LAT = 37.5940
HANAGOODGE_LON = 127.0200

# -------------------------
# 사이드바: 입력 및 설정(UI 개선)
# -------------------------
with st.sidebar.form(key="user_input"):
    st.header("기본 정보 입력")
    height = st.number_input("키(cm)", min_value=100, max_value=230, value=170)
    weight = st.number_input("몸무게(kg)", min_value=30.0, max_value=200.0, value=65.0)
    age = st.number_input("나이", min_value=10, max_value=120, value=17)
    gender = st.selectbox("성별", options=["male","female","남","여"], index=0)
    activity = st.selectbox("활동수준", options=[1.2,1.375,1.55,1.725,1.9], index=2, format_func=lambda x: f"활동지수 {x}")
    goal = st.selectbox("목표", options=["유지","체중 감량","체중 증가","근육 증가","체지방 감소"], index=0)
    preferred_food = st.text_input("선호 음식 (쉼표로 복수 가능)", value="")
    allergy = st.text_input("알레르기(쉼표로 구분)", value="")
    religion = st.text_input("종교 제한(쉼표로 구분)", value="")
    debug_mode = st.checkbox("디버그 모드(개발자용)", value=False)
    reload_db = st.form_submit_button("저장 및 적용")

if reload_db:
    try:
        FOOD_DB = load_food_database(target_count=700)
        st.sidebar.success("DB 재로딩 완료")
    except Exception:
        st.sidebar.warning("DB 재로딩 중 문제가 발생했습니다. 로그 확인 필요.")

preferred_food = preferred_food or ""
allergy = allergy or ""
religion = religion or ""

# -------------------------
# 메인: 실행 및 결과 표시
# -------------------------
if st.button("🍽️ 식단 설계 시작하기"):
    try:
        tdee = calculate_daily_calories(height, weight, age, gender, activity, goal)
        protein_target = calculate_protein_target(weight, goal)

        st.success(f"하루 권장 칼로리: {tdee} kcal, 하루 단백질 목표: {protein_target} g")

        split = {"breakfast": round(tdee*0.3), "lunch": round(tdee*0.4), "dinner": round(tdee*0.3)}
        st.markdown("### 오늘의 식사 목표")
        c1, c2, c3 = st.columns(3)
        c1.metric("아침 칼로리", f"{split['breakfast']} kcal")
        c2.metric("점심 칼로리", f"{split['lunch']} kcal")
        c3.metric("저녁 칼로리", f"{split['dinner']} kcal")

        allergy_list = [x.strip() for x in (allergy or "").split(",") if x.strip()]
        religion_list = [x.strip() for x in (religion or "").split(",") if x.strip()]

        day_plan = plan_full_day(split, protein_target, FOOD_DB, diet_pref=None, allergy_list=allergy_list, religion_list=religion_list)

        # 레이아웃: 추천(왼) / 시각화(오)
        left_col, right_col = st.columns([2,1])

        with left_col:
            st.markdown("## 추천 식단 (하루)")
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
                    foods = data["foods"]
                    cal = data["cal"]
                    prot = data["protein"]
                    tags = data.get("tags","")
                    st.markdown(f"**구성:** {', '.join(foods)}")
                    st.write(f"- 칼로리 합: {cal:.0f} kcal")
                    st.write(f"- 단백질 합: {prot:.0f} g")
                    st.write(f"- 태그: {tags}")
                    if st.button(f"다른 조합 보기({meal_name})", key=f"reroll_{meal_name}"):
                        sel = recommend_meals_simple(split[meal_name], preferred_food=preferred_food, allergy=allergy, religion=religion, top_n=3)
                        st.table(sel)

            # CSV 다운로드
            all_items = []
            for m in ["breakfast","lunch","dinner"]:
                it = day_plan.get(m)
                if not it:
                    continue
                if it["type"] == "table":
                    df_export = it["data"].copy()
                    df_export["meal"] = m
                    all_items.append(df_export)
                else:
                    d = it["data"]
                    df_export = pd.DataFrame({
                        "meal":[m]*len(d["foods"]),
                        "food":d["foods"]
                    })
                    all_items.append(df_export)
            if all_items:
                export_df = pd.concat(all_items, ignore_index=True)
                csv = export_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("추천 식단 CSV 다운로드", data=csv, file_name="healicious_plan.csv", mime="text/csv")

        with right_col:
            st.markdown("## 시각화")
            chart_df = pd.DataFrame({
                "meal":["아침","점심","저녁"],
                "cal":[split["breakfast"], split["lunch"], split["dinner"]],
                "category":["목표","목표","목표"]
            })
            safe_show_altair(chart_df, enc_x='meal:N', enc_y='cal:Q', enc_color='category:N', tooltip=['meal','cal','category'], width=400, height=300)

            # 영양소 비율 예시
            nut_df = pd.DataFrame({
                "nutrient":["탄수화물","단백질","지방"],
                "percent":[55, 25, 20]
            })
            try:
                pie = alt.Chart(nut_df).mark_arc().encode(
                    theta=alt.Theta(field="percent", type="Q"),
                    color=alt.Color(field="nutrient", type="N"),
                    tooltip=["nutrient","percent"]
                ).properties(width=350, height=300)
                st.altair_chart(pie, use_container_width=True)
            except Exception:
                logger.error("pie chart error:\n%s", traceback.format_exc())

        # -------------------------
        # 하루 요약 그래프(칼로리/탄단지) 안전 처리 블록
        # -------------------------
        try:
            summary_rows = []
            for meal in ["breakfast","lunch","dinner"]:
                p = day_plan.get(meal, {})
                # 안전하게 값 추출
                total_cal = 0
                total_prot = 0
                total_carbs = 0
                total_fat = 0
                if p.get("type") == "table":
                    try:
                        dfm = p["data"].copy()
                        # 숫자형 보장
                        if "calories" in dfm.columns:
                            dfm["calories"] = pd.to_numeric(dfm["calories"], errors="coerce").fillna(0)
                            total_cal = dfm["calories"].sum()
                        if "protein" in dfm.columns:
                            dfm["protein"] = pd.to_numeric(dfm["protein"], errors="coerce").fillna(0)
                            total_prot = dfm["protein"].sum()
                        if "carbs" in dfm.columns:
                            dfm["carbs"] = pd.to_numeric(dfm["carbs"], errors="coerce").fillna(0)
                            total_carbs = dfm["carbs"].sum()
                        if "fat" in dfm.columns:
                            dfm["fat"] = pd.to_numeric(dfm["fat"], errors="coerce").fillna(0)
                            total_fat = dfm["fat"].sum()
                    except Exception:
                        logger.error("table sum error:\n%s", traceback.format_exc())
                else:
                    d = p.get("data", {})
                    try:
                        total_cal = float(d.get("cal", 0))
                    except Exception:
                        total_cal = 0
                    try:
                        total_prot = float(d.get("protein", 0))
                    except Exception:
                        total_prot = 0
                    # carbs/fat 추정값이 없다면 0으로 유지
                summary_rows.append({"meal":meal, "cal":total_cal, "protein":total_prot, "carbs":total_carbs, "fat":total_fat})
            summary_df = pd.DataFrame(summary_rows)

            # melt 및 컬럼명 정리
            if not summary_df.empty:
                # 컬럼명 통일 및 수치 보장
                for c in ["cal","protein","carbs","fat"]:
                    if c in summary_df.columns:
                        summary_df[c] = pd.to_numeric(summary_df[c], errors="coerce").fillna(0)
                    else:
                        summary_df[c] = 0
                summary_melt = summary_df.melt(id_vars="meal", value_vars=["cal","protein","carbs","fat"], var_name="nutrient", value_name="value")
            else:
                summary_melt = pd.DataFrame(columns=["meal","nutrient","value"])

            # 안전한 차트 출력: required 컬럼 검사 및 value numeric 강제
            required_cols = ["meal", "nutrient", "value"]
            if summary_melt is None or not hasattr(summary_melt, "columns"):
                st.error("요약 차트 데이터가 준비되지 않았습니다.")
            else:
                missing = [c for c in required_cols if c not in summary_melt.columns]
                if missing:
                    st.error(f"요약 차트에 필요한 컬럼이 없습니다: {', '.join(missing)}")
                elif summary_melt.empty:
                    st.info("요약 차트에 표시할 데이터가 없습니다.")
                else:
                    # value 숫자형 강제
                    summary_melt["value"] = pd.to_numeric(summary_melt["value"], errors="coerce").fillna(0)
                    # meal/nutrient 문자열화
                    summary_melt["meal"] = summary_melt["meal"].astype(str)
                    summary_melt["nutrient"] = summary_melt["nutrient"].astype(str)

                    unique_nuts = summary_melt["nutrient"].nunique()
                    try:
                        if unique_nuts <= 6:
                            chart = alt.Chart(summary_melt).mark_bar().encode(
                                x=alt.X('meal:N', title='식사'),
                                y=alt.Y('value:Q', title='양'),
                                color=alt.Color('nutrient:N', title='영양소'),
                                column=alt.Column('nutrient:N', header=alt.Header(labelAngle=0))
                            ).properties(height=150)
                        else:
                            chart = alt.Chart(summary_melt).mark_bar().encode(
                                x=alt.X('meal:N', title='식사'),
                                y=alt.Y('value:Q', title='양'),
                                color=alt.Color('nutrient:N', title='영양소'),
                                tooltip=['meal','nutrient','value']
                            ).properties(height=300)
                        st.altair_chart(chart, use_container_width=True)
                    except Exception:
                        tb = traceback.format_exc()
                        logger.error("summary chart error:\n%s", tb)
                        st.error("요약 차트 표시 중 문제가 발생했습니다. 관리자 로그를 확인해 주세요.")
        except Exception:
            tb = traceback.format_exc()
            logger.error("summary block error:\n%s", tb)
            st.error("요약 그래프 생성 중 문제가 발생했습니다. 관리자 로그를 확인해 주세요.")

        # -------------------------
        # 하나고등학교 인근 식당 추천(EXTENDER)
        # -------------------------
        st.markdown("## 🏫 하나고등학교 인근 식당 추천")
        st.markdown("샘플 데이터를 사용합니다. 실제 CSV(/mnt/data/nearby_restaurants.csv)나 API로 교체하세요.")
        try:
            if st.button("🔎 근처 식당 찾기 (반경 1.0km)"):
                rdf = NEARBY_RESTAURANTS.copy()
                # 컬럼명 방어
                if "lat" not in rdf.columns or "lon" not in rdf.columns:
                    st.warning("샘플 데이터에 위치(lat/lon) 정보가 없습니다. nearby_restaurants.csv 형식을 확인하세요.")
                else:
                    rdf["distance_km"] = rdf.apply(lambda r: haversine(HANAGOODGE_LAT, HANAGOODGE_LON, r["lat"], r["lon"]), axis=1)
                    nearby = rdf[rdf["distance_km"] <= 1.0].sort_values("distance_km").reset_index(drop=True)
                    if nearby.empty:
                        st.info("1km 반경 내 샘플 식당이 없습니다. nearby_restaurants.csv 업로드 또는 API 연동을 권장합니다.")
                        try:
                            st.dataframe(rdf.sort_values("distance_km").head(10))
                        except Exception:
                            st.dataframe(rdf.head(10))
                    else:
                        st.dataframe(nearby[["name","category","est_cal","distance_km"]])
        except Exception:
            logger.error("nearby block error:\n%s", traceback.format_exc())
            st.error("근처 식당 검색 중 문제가 발생했습니다. 관리자 로그를 확인해 주세요.")

        # -------------------------
        # 과학적 근거 설명
        # -------------------------
        st.markdown("## 🔬 과학적 원리 (펼쳐보기)")
        with st.expander("영양학적/생리학적 기반 설명 보기"):
            st.write("""
            • BMR: Mifflin–St Jeor (혹은 Harris–Benedict 유사) 기반 추정식을 사용합니다.
            • 활동지수: 활동 수준에 따라 TDEE를 조정(예: 1.2~1.9).
            • 목표별 칼로리 조정: 감량 -300 kcal, 증량 +300 kcal, 근육 증가 +150 kcal (기본값).
            • 식사 배분: 아침 30% / 점심 40% / 저녁 30% (기본 가이드).
            • 균형화 원리: 각 식사에 메인 단백질 + 곡류(또는 대체) + 채소 포함, 비타민·미네랄 태그를 끼니별로 분산.
            • 단백질 분배: 하루 단백질을 끼별로 분배(근합성 최적화 목적).
            """)
            st.write("원하시면 참고문헌(논문/가이드라인) 요약도 추가해 드리겠습니다.")

        # -------------------------
        # 관리자 안내
        # -------------------------
        st.markdown("## 개발자/관리자 안내")
        st.write("""
        - 외부 DB(file: /mnt/data/food_2000.xlsx 또는 food_700.xlsx 또는 20250408_음식DB.xlsx)를 올리면 자동 로드합니다.
        - nearby_restaurants.csv 파일을 /mnt/data에 올리면 인근 식당 데이터로 대체됩니다.
        - 추천 알고리즘·UI는 추가로 조정 가능합니다(이미지, 드래그 앤 드롭, 사용자 이력 저장 등).
        - 2000개 실제 항목을 원하시면 샘플 엑셀을 생성해 제공해 드릴 수 있습니다.
        """)

    except Exception:
        tb = traceback.format_exc()
        logger.error("메인 실행 중 예외 발생:\n%s", tb)
        if debug_mode:
            st.error(tb)
        else:
            st.error("식단 생성 중 문제가 발생했습니다. 관리자 로그를 확인해 주세요.")
