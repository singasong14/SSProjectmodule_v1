# app.py
# Streamlit Nutrition Kiosk - Comprehensive single-file app
# Save as app.py and run with: streamlit run app.py
# requirements: streamlit, pandas

import streamlit as st
import pandas as pd
import json
from math import floor

st.set_page_config(page_title="영양식 키오스크", layout="wide")

# -------------------------
# Helper: Food DB (demo)
# -------------------------
# Each food has: name, serving_text, kcal, protein_g, carbs_g, fat_g, fiber_g, sodium_mg,
# iron_mg, calcium_mg, vitd_ug
# In production, replace with comprehensive DB (CSV / DB)
FOOD_DB = [
    {"id": 1, "name": "닭가슴살(구이) 100g", "serving": "100g", "kcal": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6, "fiber_g": 0, "sodium_mg": 60, "iron_mg": 1.0, "calcium_mg": 12, "vitd_ug": 0.2, "type":"meat", "allergens":[]},
    {"id": 2, "name": "현미밥 150g (1공기)", "serving": "150g", "kcal": 210, "protein_g": 4.4, "carbs_g": 45, "fat_g": 1.8, "fiber_g": 2.8, "sodium_mg": 5, "iron_mg": 0.6, "calcium_mg": 10, "vitd_ug": 0, "type":"grain", "allergens":[]},
    {"id": 3, "name": "계란(삶은) 1개", "serving": "1개", "kcal": 78, "protein_g": 6.5, "carbs_g": 0.6, "fat_g": 5.3, "fiber_g": 0, "sodium_mg": 62, "iron_mg": 0.6, "calcium_mg": 25, "vitd_ug": 1.1, "type":"dairy", "allergens":["egg"]},
    {"id": 4, "name": "오트밀(건조) 60g", "serving": "60g", "kcal": 230, "protein_g": 8, "carbs_g": 39, "fat_g": 4, "fiber_g": 6, "sodium_mg": 2, "iron_mg": 2.7, "calcium_mg": 20, "vitd_ug": 0, "type":"grain", "allergens":["gluten"]},
    {"id": 5, "name": "두부 150g", "serving": "150g", "kcal": 144, "protein_g": 17, "carbs_g": 3.8, "fat_g": 8.5, "fiber_g": 1.2, "sodium_mg": 12, "iron_mg": 2.1, "calcium_mg": 180, "vitd_ug": 0, "type":"plant", "allergens":["soy"]},
    {"id": 6, "name": "연어(구이) 100g", "serving": "100g", "kcal": 208, "protein_g": 20, "carbs_g": 0, "fat_g": 13, "fiber_g": 0, "sodium_mg": 50, "iron_mg": 0.5, "calcium_mg": 9, "vitd_ug": 10.9, "type":"fish", "allergens":["fish"]},
    {"id": 7, "name": "브로콜리 찜 100g", "serving": "100g", "kcal": 35, "protein_g": 2.8, "carbs_g": 7, "fat_g": 0.4, "fiber_g": 3, "sodium_mg": 30, "iron_mg": 0.7, "calcium_mg": 47, "vitd_ug": 0, "type":"veg", "allergens":[]},
    {"id": 8, "name": "바나나(중) 1개", "serving": "1개", "kcal": 105, "protein_g": 1.3, "carbs_g": 27, "fat_g": 0.3, "fiber_g": 3.1, "sodium_mg": 1, "iron_mg": 0.3, "calcium_mg": 6, "vitd_ug": 0, "type":"fruit", "allergens":[]},
    {"id": 9, "name": "혼합견과류 20g", "serving": "20g", "kcal": 120, "protein_g": 3, "carbs_g": 4, "fat_g": 10, "fiber_g": 2, "sodium_mg": 0, "iron_mg": 0.6, "calcium_mg": 20, "vitd_ug": 0, "type":"nuts", "allergens":["nuts"]},
    {"id": 10, "name": "그릭요거트 150g", "serving": "150g", "kcal": 120, "protein_g": 12, "carbs_g": 8, "fat_g": 4, "fiber_g": 0, "sodium_mg": 55, "iron_mg": 0.1, "calcium_mg": 150, "vitd_ug": 0.5, "type":"dairy", "allergens":["milk"]},
    {"id": 11, "name": "고구마(중) 150g", "serving":"150g", "kcal":130, "protein_g":2, "carbs_g":31, "fat_g":0.2, "fiber_g":3.8, "sodium_mg":36, "iron_mg":0.8, "calcium_mg":30, "vitd_ug":0, "type":"grain", "allergens":[]}
]

# -------------------------
# Utility functions
# -------------------------
def mifflin_bmr(weight, height, age, sex):
    # Mifflin-St Jeor
    if sex == "남성":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def activity_factor(level):
    mapping = {
        "좌식": 1.2,
        "가벼운 활동": 1.375,
        "중간 활동": 1.55,
        "격렬한 활동": 1.725
    }
    return mapping.get(level, 1.55)

def safe_round(x):
    return int(round(x))

# Simple micronutrient targets (demonstrative)
# For production use, replace with full KDRI table by age & sex.
def micronutrient_targets(age, sex):
    # returns dict with simple targets
    # values are approximate placeholders:
    return {
        "fiber_g": 25 if sex=="남성" else 20,
        "iron_mg": 8 if sex=="남성" else 14,   # women of reproductive age need more
        "calcium_mg": 800,
        "vitd_ug": 5
    }

# -------------------------
# Sidebar form: All inputs
# -------------------------
st.sidebar.header("사용자 정보 입력 (필수)")
age = st.sidebar.number_input("나이", min_value=1, max_value=120, value=30)
sex = st.sidebar.selectbox("성별", ["남성", "여성"])
height = st.sidebar.number_input("키 (cm)", min_value=100, max_value=230, value=175)
weight = st.sidebar.number_input("체중 (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
activity = st.sidebar.selectbox("활동량 수준", ["좌식", "가벼운 활동", "중간 활동", "격렬한 활동"])
goal = st.sidebar.selectbox("체중 목표", ["감량", "유지", "증량"])
meal_count = st.sidebar.selectbox("식사 횟수 선호", [2,3,4])
st.sidebar.markdown("---")
st.sidebar.header("건강 / 질환 / 알레르기")
diseases = st.sidebar.multiselect("현재 질병(해당시 체크)", ["당뇨", "고혈압", "고지혈증", "신장 질환", "위장 질환"])
allergies = st.sidebar.multiselect("알레르기 · 불내증", ["우유","난류","견과류","대두","글루텐","갑각류"])
diet_instruction = st.sidebar.selectbox("의사가 권장한 식이", ["해당 없음","저염식","저지방","고단백"])
meds = st.sidebar.text_input("복용중인 약(선택 입력)")
st.sidebar.markdown("---")
st.sidebar.header("기호 / 생활 패턴")
likes = st.sidebar.text_input("선호 음식 (콤마로 구분 예: 치킨,두부)", "")
dislikes = st.sidebar.text_input("비선호 음식 (콤마로 구분 예: 버섯,피망)", "")
religion = st.sidebar.selectbox("종교/문화 제한", ["해당 없음","채식주의(완전)","채식주의(락토/오보)","할랄/코셔 등"])
eat_times = st.sidebar.text_input("식사 가능한 시간대(예: 아침 7-8, 점심 12-13, 저녁 19-20)", "")
snack_habit = st.sidebar.selectbox("간식 섭취 여부", ["없음","가끔","자주"])
spice_pref = st.sidebar.selectbox("맵고 짠 것 선호도", ["약함","보통","강함"])
st.sidebar.markdown("---")
st.sidebar.header("생활 / 예산 / 조리")
cooking_ability = st.sidebar.selectbox("요리 가능 여부", ["전자레인지 전용","간단 조리 가능","정식 조리 가능"])
budget = st.sidebar.selectbox("하루 예산", ["저(~1만)","중(1~2만)","고(2만↑)"])
prep_time = st.sidebar.selectbox("식사 준비 시간(평균)", ["5분","10분","20분 이상"])
st.sidebar.markdown("---")
st.sidebar.header("목표 기반 정보")
main_goal = st.sidebar.multiselect("주요 목표(복수 선택 가능)", ["다이어트","근육 증가","체력 향상","영양 균형","특정 영양소 보충(단백질/철분/비타민D)"])
time_frame = st.sidebar.selectbox("시간 목표", ["한 달","3개월","6개월","기타"])

if st.sidebar.button("맞춤 식단 생성"):
    # -------------------------
    # 1) Energy & macro targets
    # -------------------------
    bmr = mifflin_bmr(weight, height, age, sex)
    tdee = bmr * activity_factor(activity)

    # goal adjustments
    if goal == "감량":
        kcal_target = max(1200, tdee - 500)
    elif goal == "증량":
        kcal_target = tdee + 300
    else:
        kcal_target = tdee

    # macros: set protein per kg based on goal
    if "근육 증가" in main_goal or goal == "증량":
        prot_per_kg = 1.4
    elif goal == "감량":
        prot_per_kg = 1.2
    else:
        prot_per_kg = 1.0

    protein_target_g = safe_round(prot_per_kg * weight)
    # carbs default 50% energy, fat rest
    carbs_kcal = 0.5 * kcal_target
    carbs_target_g = safe_round(carbs_kcal / 4)
    protein_kcal = protein_target_g * 4
    fat_kcal = kcal_target - (protein_kcal + carbs_kcal)
    fat_target_g = safe_round(max(0, fat_kcal / 9))

    micro_targets = micronutrient_targets(age, sex)

    # adjust for disease constraints (simple rule-based)
    sodium_limit_mg = 2300
    if "고혈압" in diseases or "심혈관" in diseases:
        sodium_limit_mg = 1500

    if diet_instruction == "저염식":
        sodium_limit_mg = min(sodium_limit_mg, 1500)
    if "신장 질환" in diseases:
        # example: restrict protein if severe (this is illustrative)
        protein_target_g = min(protein_target_g, safe_round(0.8 * weight))

    # -------------------------
    # 2) Filter food DB
    # -------------------------
    user_allergies = set(allergies)
    filtered_foods = []
    for f in FOOD_DB:
        if any(a in user_allergies for a in f.get("allergens", [])):
            continue
        # religious/diet filters
        if religion == "채식주의(완전)":
            if f["type"] in ("meat","fish","dairy"):
                continue
        if religion == "채식주의(락토/오보)":
            if f["type"] in ("meat","fish"):
                continue
        filtered_foods.append(f)
    if len(filtered_foods)==0:
        st.error("제한 조건(알레르기/종교 등)으로 추천 가능한 음식이 없습니다. 제한을 완화하거나 DB를 확장하세요.")
        st.stop()

    # -------------------------
    # 3) Meal assembly heuristic
    # -------------------------
    # distribute kcal per meal
    if meal_count == 2:
        shares = [0.55, 0.45]
    elif meal_count == 3:
        shares = [0.25,0.40,0.35]
    else:
        shares = [0.22,0.33,0.30,0.15][:meal_count]

    meals = []
    remaining_protein = protein_target_g
    remaining_kcal = kcal_target

    # Prefer high-protein items each meal
    high_protein = sorted(filtered_foods, key=lambda x: x["protein_g"], reverse=True)
    carb_sources = sorted(filtered_foods, key=lambda x: x["carbs_g"], reverse=True)
    vegs = [f for f in filtered_foods if f["type"] in ("veg","fruit")]
    fats = sorted(filtered_foods, key=lambda x: x["fat_g"], reverse=True)

    for i, share in enumerate(shares):
        tk = safe_round(kcal_target * share)
        meal = {"target_kcal": tk, "items": [], "kcal":0, "protein_g":0, "carbs_g":0, "fat_g":0, "fiber_g":0, "sodium_mg":0, "iron_mg":0, "calcium_mg":0, "vitd_ug":0}
        # 1) protein item
        prot_item = high_protein[i % len(high_protein)]
        add_qty = 1
        meal["items"].append({"food":prot_item, "qty":add_qty})
        meal["kcal"] += prot_item["kcal"] * add_qty
        meal["protein_g"] += prot_item["protein_g"] * add_qty
        meal["carbs_g"] += prot_item["carbs_g"] * add_qty
        meal["fat_g"] += prot_item["fat_g"] * add_qty
        meal["fiber_g"] += prot_item["fiber_g"] * add_qty
        meal["sodium_mg"] += prot_item["sodium_mg"] * add_qty
        meal["iron_mg"] += prot_item["iron_mg"] * add_qty
        meal["calcium_mg"] += prot_item["calcium_mg"] * add_qty
        meal["vitd_ug"] += prot_item["vitd_ug"] * add_qty

        # 2) carb item until reach near meal kcal
        j = 0
        while meal["kcal"] < tk - 80 and j < len(carb_sources):
            carb_choice = carb_sources[(i + j) % len(carb_sources)]
            # avoid duplicate same as protein if it's the same
            if carb_choice["id"] == prot_item["id"] and j < len(carb_sources)-1:
                j+=1
                continue
            meal["items"].append({"food":carb_choice, "qty":1})
            meal["kcal"] += carb_choice["kcal"]
            meal["protein_g"] += carb_choice["protein_g"]
            meal["carbs_g"] += carb_choice["carbs_g"]
            meal["fat_g"] += carb_choice["fat_g"]
            meal["fiber_g"] += carb_choice["fiber_g"]
            meal["sodium_mg"] += carb_choice["sodium_mg"]
            meal["iron_mg"] += carb_choice["iron_mg"]
            meal["calcium_mg"] += carb_choice["calcium_mg"]
            meal["vitd_ug"] += carb_choice["vitd_ug"]
            j += 1

        # 3) veg/fruit items (1-2)
        for v in vegs[:2]:
            meal["items"].append({"food":v, "qty":1})
            meal["kcal"] += v["kcal"]
            meal["protein_g"] += v["protein_g"]
            meal["carbs_g"] += v["carbs_g"]
            meal["fat_g"] += v["fat_g"]
            meal["fiber_g"] += v["fiber_g"]
            meal["sodium_mg"] += v["sodium_mg"]
            meal["iron_mg"] += v["iron_mg"]
            meal["calcium_mg"] += v["calcium_mg"]
            meal["vitd_ug"] += v["vitd_ug"]

        # 4) small high-fat/nuts if kcal still under
        if meal["kcal"] < tk - 80 and len(fats)>0:
            f = fats[0]
            meal["items"].append({"food":f, "qty":0.5})
            meal["kcal"] += f["kcal"]*0.5
            meal["protein_g"] += f["protein_g"]*0.5
            meal["carbs_g"] += f["carbs_g"]*0.5
            meal["fat_g"] += f["fat_g"]*0.5
            meal["fiber_g"] += f["fiber_g"]*0.5
            meal["sodium_mg"] += f["sodium_mg"]*0.5
            meal["iron_mg"] += f["iron_mg"]*0.5
            meal["calcium_mg"] += f["calcium_mg"]*0.5
            meal["vitd_ug"] += f["vitd_ug"]*0.5

        meals.append(meal)

    # -------------------------
    # 4) Summarize totals & warnings
    # -------------------------
    total = {"kcal":0,"protein_g":0,"carbs_g":0,"fat_g":0,"fiber_g":0,"sodium_mg":0,"iron_mg":0,"calcium_mg":0,"vitd_ug":0}
    for m in meals:
        for k in total.keys():
            total[k] += m.get(k,0)
    # rounding
    for k in total:
        if isinstance(total[k], float):
            total[k] = safe_round(total[k])

    warnings = []
    if total["protein_g"] < protein_target_g:
        warnings.append(f"단백질 부족: 목표 {protein_target_g} g / 섭취 {total['protein_g']} g")
    if total["fiber_g"] < micro_targets["fiber_g"]:
        warnings.append(f"식이섬유 부족: 권장 {micro_targets['fiber_g']} g / 섭취 {total['fiber_g']} g")
    if total["sodium_mg"] > sodium_limit_mg:
        warnings.append(f"나트륨 초과: 권장 ≤{sodium_limit_mg} mg / 섭취 {total['sodium_mg']} mg")
    if total["iron_mg"] < micro_targets["iron_mg"]:
        warnings.append(f"철분 부족: 권장 {micro_targets['iron_mg']} mg / 섭취 {total['iron_mg']} mg")
    if total["calcium_mg"] < micro_targets["calcium_mg"]:
        warnings.append(f"칼슘 부족: 권장 {micro_targets['calcium_mg']} mg / 섭취 {total['calcium_mg']} mg")
    if total["vitd_ug"] < micro_targets["vitd_ug"]:
        warnings.append(f"비타민D 부족: 권장 {micro_targets['vitd_ug']} µg / 섭취 {total['vitd_ug']} µg")

    # adjust messages for disease specific
    if "당뇨" in diseases:
        warnings.append("당뇨 경고: 탄수화물 구성 및 당질 분배를 추가로 조정하세요.")

    # -------------------------
    # 5) Output UI
    # -------------------------
    st.header("🔎 계산 요약")
    col1, col2, col3 = st.columns(3)
    col1.metric("BMR (기초대사량)", f"{safe_round(bmr)} kcal")
    col2.metric("TDEE (일일 필요)", f"{safe_round(tdee)} kcal")
    col3.metric("목표 칼로리", f"{safe_round(kcal_target)} kcal")

    st.subheader("🎯 매크로 목표")
    st.write(f"- 단백질: {protein_target_g} g / 일\n- 탄수화물: {carbs_target_g} g / 일\n- 지방: {fat_target_g} g / 일")
    st.write(f"- 식이섬유 목표(간단): {micro_targets['fiber_g']} g / 일, 나트륨 제한: ≤{sodium_limit_mg} mg")

    st.subheader("🍽 제안된 1일 식단 (끼니별)")
    for idx, m in enumerate(meals):
        st.markdown(f"**끼니 {idx+1} (목표 {m['target_kcal']} kcal)**")
        df_rows = []
        for it in m["items"]:
            food = it["food"]
            qty = it["qty"]
            df_rows.append({
                "음식": food["name"],
                "서빙": food["serving"],
                "수량(배수)": qty,
                "칼로리(kcal)": safe_round(food["kcal"] * qty),
                "단백질(g)": round(food["protein_g"] * qty,1),
                "탄수(g)": round(food["carbs_g"] * qty,1),
                "지방(g)": round(food["fat_g"] * qty,1),
                "섬유(g)": round(food["fiber_g"] * qty,1),
                "나트륨(mg)": safe_round(food["sodium_mg"] * qty)
            })
        st.table(pd.DataFrame(df_rows))
        st.write(f"합계: 칼로리 {safe_round(m['kcal'])} kcal · 단백질 {safe_round(m['protein_g'])} g · 탄수 {safe_round(m['carbs_g'])} g · 지방 {safe_round(m['fat_g'])} g · 섬유 {safe_round(m['fiber_g'])} g")

    st.subheader("📊 1일 총합")
    st.write(pd.DataFrame([total], index=["오늘합계"]).T.rename(columns={"오늘합계":"값"}))

    if warnings:
        st.subheader("⚠️ 주의 포인트")
        for w in warnings:
            st.warning(w)
    else:
        st.success("좋아요! 주요 영양소가 목표에 근접합니다.")

    # provide replacements for disliked foods
    if dislikes:
        dislikes_list = [x.strip() for x in dislikes.split(",") if x.strip()]
        replacements = []
        for d in dislikes_list:
            for f in filtered_foods:
                if d in f["name"]:
                    # naive: suggest same-type alternative
                    alt = next((x for x in filtered_foods if x["type"]==f["type"] and x["id"]!=f["id"]), None)
                    if alt:
                        replacements.append((f["name"], alt["name"]))
        if replacements:
            st.subheader("🔁 대체 제안")
            for orig, alt in replacements:
                st.info(f"{orig} → 대체: {alt}")

    # download JSON
    output = {
        "user": {"age":age,"sex":sex,"height":height,"weight":weight,"activity":activity,"goal":goal,"meal_count":meal_count},
        "targets":{"kcal_target":kcal_target,"protein_g":protein_target_g,"carbs_g":carbs_target_g,"fat_g":fat_target_g,"micro_targets":micro_targets},
        "meals": meals,
        "totals": total,
        "warnings": warnings
    }
    st.download_button("📥 식단 JSON 다운로드", data=json.dumps(output, ensure_ascii=False, indent=2), file_name="meal_plan.json", mime="application/json")

    # simple "save profile" (local)
    if st.button("프로필 / 식단 저장 (로컬)"):
        st.write("로컬 저장(데모): JSON 파일을 다운로드해 보관하세요.")
