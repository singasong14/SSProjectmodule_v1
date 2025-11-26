import streamlit as st
import pandas as pd
import numpy as np
import os

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Healicious Kiosk",
    layout="centered",
    page_icon="🥗",
    initial_sidebar_state="expanded",
)

# =============================
# BRAND SECTION (SVG ICON)
# =============================
BRAND_HTML = """
<div style='display:flex; align-items:center; gap:14px; margin-bottom:24px; margin-top:4px;'>
    <img src='data:image/svg+xml;utf8,
    <svg xmlns="http://www.w3.org/2000/svg" width="56" height="56">
        <rect rx="12" width="56" height="56" fill="%236ef0b0"/>
        <text x="50%" y="54%" font-size="30" text-anchor="middle" font-family="Inter" fill="white">H</text>
    </svg>'
    style='height:56px; border-radius:12px;' />
    <div>
        <div style='font-size:30px; font-weight:800; font-family:Inter;'>Healicious</div>
        <div style='font-size:13px; color:#5f6b7a; margin-top:2px;'>Healthy + Delicious 식습관 코치</div>
    </div>
</div>
"""
st.markdown(BRAND_HTML, unsafe_allow_html=True)

# =============================
# CUSTOM UI CSS
# =============================
st.markdown(
    """
<style>
body {
    background: #f5f7fa;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 900px;
}
.section-box {
    padding: 20px 22px;
    border-radius: 18px;
    background: white;
    box-shadow: 0 4px 18px rgba(15,23,42,0.05);
    margin-bottom: 18px;
}
.section-title {
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 6px;
}
.section-caption {
    font-size: 13px;
    color: #6b7280;
    margin-bottom: 8px;
}
.badge {
    display:inline-block;
    padding: 2px 8px;
    border-radius:999px;
    font-size:11px;
    background:#ecfdf3;
    color:#15803d;
    margin-right:6px;
}
.badge-danger {
    background:#fef2f2;
    color:#b91c1c;
}
.stButton>button {
    width: 100%;
    background-color: #6ef0b0;
    color: #111827;
    font-weight: 700;
    border-radius: 999px;
    height: 56px;
    font-size: 18px;
    border: none;
}
.stButton>button:hover {
    background-color: #4cd893;
    color: white;
}
.meal-card {
    border-radius: 16px;
    padding: 14px 16px;
    background:#f9fafb;
    margin-bottom:10px;
}
.meal-title {
    font-size:16px;
    font-weight:700;
}
.meal-sub {
    font-size:12px;
    color:#6b7280;
}
.kcal-tag {
    font-size:12px;
    font-weight:600;
    padding:2px 8px;
    border-radius:999px;
    background:#e0f2fe;
    color:#0369a1;
}
.macro-line {
    font-size:12px;
    color:#4b5563;
}
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# LOAD FOOD DATABASE
# =============================
def load_food_database():
    # 기본 DB (식품군 + 대략적인 영양성분)
    default_data = pd.DataFrame(
        {
            "food": [
                "닭가슴살 구이",
                "연어 샐러드",
                "두부 스테이크",
                "현미밥",
                "고구마 구이",
                "야채 스틱 & 후무스",
                "그릭 요거트 & 베리",
                "계란찜",
                "두부김치 (저염)",
                "비빔밥 (채소 듬뿍)",
                "콩나물국",
            ],
            "category": [
                "단백질",
                "단백질",
                "단백질",
                "곡류",
                "곡류",
                "채소/지방",
                "유제품",
                "단백질",
                "단백질",
                "혼합식",
                "국/찌개",
                "혼합식",
            

            ],
            "calories": [180, 320, 260, 210, 160, 190, 180, 140, 230, 550, 60, 320],
            "protein": [35, 22, 20, 4, 2, 6, 15, 12, 18, 18, 4, 22],
            "carbs": [2, 14, 10, 44, 38, 16, 18, 4, 8, 70, 8, 30],
            "fat": [4, 18, 14, 2, 0.5, 10, 5, 6, 14, 14, 1, 8],
        }
    )

    file_path = "/mnt/data/20250408_음식DB.xlsx"
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            # 필수 컬럼 없으면 기본값으로 보정
            needed = ["food", "calories", "protein", "carbs", "fat"]
            for col in needed:
                if col not in df.columns:
                    df[col] = default_data[col]
            if "category" not in df.columns:
                df["category"] = "기타"
            return df
        except Exception:
            return default_data
    else:
        return default_data


FOOD_DB = load_food_database()

# =============================
# 과학적 원리 설명 영역
# =============================
with st.expander("⚗️ Healicious의 영양 설계 원리", expanded=False):
    st.markdown(
        """
- **1단계 – 에너지 요구량(TDEE) 계산**  
  키·몸무게·나이·성별로 기초대사량(BMR)을 구하고, 활동량에 따라 **총 소모 칼로리(TDEE)** 를 추정합니다.

- **2단계 – 목표에 따른 칼로리 조정**  
  - 체중 감량: TDEE에서 약 **300 kcal 감소**  
  - 체중 증가: TDEE에 약 **300 kcal 증가**  
  - 근육 증가: 단백질을 늘리고, TDEE에 약 **150 kcal 증가**

- **3단계 – 거시 영양소 비율 설정**  
  하루 칼로리를 단백질·탄수화물·지방으로 나눕니다.
  - 단백질: 체중(kg) × 1.2–2.0 g  
  - 나머지 칼로리 중  
    - 체중 감량: 탄수화물 40%, 지방 60%  
    - 유지/건강: 탄수화물 50%, 지방 50%  
    - 근육 증가: 탄수화물 45%, 지방 55%

- **4단계 – 식품군 균형**  
  한 끼 안에서  
  - **단백질 식품**(닭가슴살·콩류·두부 등)  
  - **곡류/전분**(현미밥·고구마 등)  
  - **채소/과일**  
  을 최소 2~3가지 이상 섞어서 **포만감·영양·맛**을 동시에 고려합니다.
"""
    )

# =============================
# HELPER – 칼로리 & 매크로 계산
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

    # 너무 낮게 떨어지는 것 방지
    return max(1200, round(tdee))


def calculate_macro_targets(weight, calorie_target, goal):
    # 단백질(g/kg) 설정
    if goal in ["체중 감량", "체지방 감소"]:
        protein_per_kg = 1.6
        carb_ratio = 0.40
    elif goal in ["근육 증가"]:
        protein_per_kg = 2.0
        carb_ratio = 0.45
    else:  # 유지 / 체중 증가
        protein_per_kg = 1.2
        carb_ratio = 0.50

    protein_g = protein_per_kg * weight
    protein_kcal = protein_g * 4

    remaining_kcal = max(0, calorie_target - protein_kcal)
    carbs_kcal = remaining_kcal * carb_ratio
    fat_kcal = remaining_kcal - carbs_kcal

    carbs_g = carbs_kcal / 4
    fat_g = fat_kcal / 9 if fat_kcal > 0 else 0

    return {
        "protein_g": round(protein_g),
        "carbs_g": round(carbs_g),
        "fat_g": round(fat_g),
    }

# =============================
# USER INPUT SECTION
# =============================
with st.container():
    with st.expander("👤 기본 정보 입력", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("키 (cm)", min_value=100, max_value=230, value=170)
            weight = st.number_input("몸무게 (kg)", min_value=30, max_value=200, value=60)
        with col2:
            age = st.number_input("나이", min_value=10, max_value=90, value=18)
            gender = st.selectbox("성별", ["남성", "여성"])

        activity = st.selectbox("활동량", ["적음", "보통", "많음"])

        goal = st.selectbox(
            "현재 건강 목표",
            ["체중 감량", "체중 증가", "유지", "체지방 감소", "근육 증가"],
        )

    col_pref1, col_pref2 = st.columns(2)
    with col_pref1:
        preferred_food = st.text_input("좋아하는 음식 / 오늘 땡기는 음식")
        mood = st.selectbox(
            "오늘 기분",
            ["피곤함", "상쾌함", "보통", "스트레스", "기운 없음"],
        )
    with col_pref2:
        allergy = st.text_input("알레르기 (예: 땅콩, 새우 등)")
        religion = st.text_input("종교적/이념적 이유로 못 먹는 음식 (예: 돼지고기 등)")

    st.markdown("---")

# =============================
# MEAL RECOMMENDER (균형 설계)
# =============================
def filter_foods(df, preferred_food, allergy, religion):
    tmp = df.copy()

    # 선호 음식이 실제로 DB에 있으면 그쪽만 필터링
    if preferred_food:
        mask_pref = tmp["food"].astype(str).str.contains(preferred_food, na=False)
        if mask_pref.any():
            tmp = tmp[mask_pref]

    # 알레르기, 종교 제한 제외
    if allergy:
        tmp = tmp[~tmp["food"].astype(str).str.contains(allergy, na=False)]
    if religion:
        tmp = tmp[~tmp["food"].astype(str).str.contains(religion, na=False)]

    if len(tmp) == 0:
        tmp = df.copy()

    return tmp.reset_index(drop=True)


def build_meal_plan(df, calorie_target, macro_target):
    # 끼니별 칼로리 비율 (아침 30%, 점심 40%, 저녁 30%)
    ratios = {"아침": 0.3, "점심": 0.4, "저녁": 0.3}
    meals = {}

    # 밀도 계산 (단백질/탄수화물 밀도)
    df = df.copy()
    df["protein_density"] = df["protein"] / df["calories"].replace(0, np.nan)
    df["carb_density"] = df["carbs"] / df["calories"].replace(0, np.nan)

    for meal_name, r in ratios.items():
        target_kcal = calorie_target * r
        selected_rows = []

        # 단백질 식품 1개, 곡류/혼합식 1개, 기타 1개 우선 조합
        protein_candidates = df[df["category"].isin(["단백질"])].sort_values(
            "protein_density", ascending=False
        )
        carb_candidates = df[df["category"].isin(["곡류", "혼합식"])].sort_values(
            "carb_density", ascending=False
        )
        etc_candidates = df[~df["category"].isin(["단백질", "곡류"])]

        def pick_one(candidate_df):
            if len(candidate_df) == 0:
                return None
            return candidate_df.iloc[np.random.randint(0, len(candidate_df))]

        for candidate_df in [protein_candidates, carb_candidates, etc_candidates]:
            row = pick_one(candidate_df)
            if row is not None:
                selected_rows.append(row)

        # 필요시 추가 샘플링으로 칼로리 근사
        loop_guard = 0
        total_kcal = sum(rw["calories"] for rw in selected_rows)
        while total_kcal < target_kcal * 0.9 and loop_guard < 10:
            row = df.sample(1).iloc[0]
            selected_rows.append(row)
            total_kcal = sum(rw["calories"] for rw in selected_rows)
            loop_guard += 1

        if len(selected_rows) == 0:
            continue

        meal_df = (
            pd.DataFrame(selected_rows)
            .groupby("food", as_index=False)
            .agg(
                {
                    "category": "first",
                    "calories": "sum",
                    "protein": "sum",
                    "carbs": "sum",
                    "fat": "sum",
                }
            )
        )
        meals[meal_name] = meal_df

    return meals


def summarize_plan(meals):
    frames = []
    for meal_name, df in meals.items():
        tmp = df.copy()
        tmp["meal"] = meal_name
        frames.append(tmp)
    full = pd.concat(frames, ignore_index=True)
    summary = {
        "calories": int(full["calories"].sum()),
        "protein": int(full["protein"].sum()),
        "carbs": int(full["carbs"].sum()),
        "fat": int(full["fat"].sum()),
    }
    return full, summary

# =============================
# MAIN BUTTON – RUN SYSTEM
# =============================
run = st.button("🥗 오늘 식단 설계 시작하기")

if run:
    if height == 0 or weight == 0:
        st.error("키와 몸무게를 먼저 입력해 주세요.")
        st.stop()

    st.markdown("### ✅ 오늘의 맞춤 영양 설계 결과")

    calorie_target = calculate_daily_calories(height, weight, age, gender, activity, goal)
    macro_target = calculate_macro_targets(weight, calorie_target, goal)

    col_kcal, col_macro = st.columns(2)
    with col_kcal:
        st.metric("하루 권장 칼로리", f"{calorie_target} kcal")
    with col_macro:
        st.markdown(
            f"""
**매크로 목표치 (대략)**  

- 단백질: **{macro_target['protein_g']} g**  
- 탄수화물: **{macro_target['carbs_g']} g**  
- 지방: **{macro_target['fat_g']} g**
"""
        )

    base_foods = filter_foods(FOOD_DB, preferred_food, allergy, religion)
    meals = build_meal_plan(base_foods, calorie_target, macro_target)

    if len(meals) == 0:
        st.error("추천할 수 있는 식단이 없습니다. 음식 DB를 확인해 주세요.")
        st.stop()

    full_plan, summary = summarize_plan(meals)

    st.markdown("### 🍱 끼니별 추천 식단")

    for meal_name in ["아침", "점심", "저녁"]:
        df_meal = meals.get(meal_name)
        if df_meal is None or len(df_meal) == 0:
            continue

        meal_kcal = int(df_meal["calories"].sum())
        meal_protein = int(df_meal["protein"].sum())
        meal_carbs = int(df_meal["carbs"].sum())
        meal_fat = int(df_meal["fat"].sum())

        st.markdown(
            f"""
<div class="meal-card">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
        <div>
            <div class="meal-title">{meal_name}</div>
            <div class="meal-sub">균형 잡힌 한 끼 추천</div>
        </div>
        <div class="kcal-tag">{meal_kcal} kcal</div>
    </div>
    <div class="macro-line">
        단백질 {meal_protein} g · 탄수화물 {meal_carbs} g · 지방 {meal_fat} g
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.table(df_meal[["food", "category", "calories", "protein", "carbs", "fat"]])

    st.markdown("### 📊 하루 전체 요약")

    col_sum1, col_sum2 = st.columns(2)
    with col_sum1:
        st.write(
            f"- 총 섭취 칼로리: **{summary['calories']} kcal** (목표 {calorie_target} kcal 근처)\n"
            f"- 총 단백질: **{summary['protein']} g** (목표 {macro_target['protein_g']} g 근처)"
        )
    with col_sum2:
        st.write(
            f"- 총 탄수화물: **{summary['carbs']} g**\n"
            f"- 총 지방: **{summary['fat']} g**"
        )

    # =============================
    # RESTAURANT RECOMMENDER (DEMO)
    # =============================
    st.markdown("### 🍽 주변 음식점 추천")

    mood_comment = {
        "피곤함": "소화가 편하고 단백질이 충분한 메뉴 위주로 구성했어요.",
        "상쾌함": "활동량을 유지할 수 있는 균형 잡힌 메뉴에 초점을 맞췄어요.",
        "보통": "과하지 않게, 하루 영양을 고르게 채우는 구성을 추천해요.",
        "스트레스": "자극적인 음식 대신, 포만감은 높고 죄책감은 적은 메뉴로 골랐어요.",
        "기운 없음": "탄수화물과 단백질을 함께 채워 에너지를 끌어올리는 구성이에요.",
    }.get(mood, "")

    if mood_comment:
        st.info(mood_comment)

    demo_restaurants = pd.DataFrame(
        {
            "음식점": ["88 SQUARE SEOUL", "1인 1잔", "청류"],
            "거리": ["158m", "88m", "218m"],
            "대표메뉴": ["닭가슴살 샐러드랩", "현미밥 + 생선구이 + 나물", "고단백 도시락"],
        }
    )

    st.dataframe(demo_restaurants)
