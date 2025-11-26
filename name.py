# 파일명: app.py
import streamlit as st
import pandas as pd
from datetime import date

# ======================
# 기본 설정 & 스타일
# ======================
st.set_page_config(
    page_title="Healicious Kiosk",
    page_icon="🥗",
    layout="wide"
)

# 커스텀 CSS로 키오스크 감성 UI 적용
st.markdown(
    """
    <style>
    /* 전체 배경 */
    .stApp {
        background: radial-gradient(circle at top left, #fdfbfb 0%, #ebedee 45%, #dfe9f3 100%);
        font-family: "Pretendard", -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }

    /* 상단 타이틀 박스 */
    .hero-box {
        padding: 1.8rem 2.2rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #4ac29a 0%, #bdfff3 100%);
        color: #0f172a;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.25);
        position: relative;
        overflow: hidden;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        margin-bottom: 0.3rem;
    }
    .hero-sub {
        font-size: 0.98rem;
        opacity: 0.9;
    }
    .hero-badge {
        position: absolute;
        right: 2.2rem;
        top: 1.8rem;
        padding: 0.4rem 0.9rem;
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.08);
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* 카드 공통 */
    .glass-card {
        border-radius: 24px;
        background: rgba(255, 255, 255, 0.70);
        box-shadow: 0 14px 34px rgba(15, 23, 42, 0.18);
        padding: 1.2rem 1.4rem;
        backdrop-filter: blur(18px);
        border: 1px solid rgba(148, 163, 184, 0.3);
    }

    /* 키오스크 큰 버튼 */
    .kiosk-btn {
        border-radius: 20px;
        border: 0;
        padding: 1.1rem 1.4rem;
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        color: white;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        width: 100%;
        box-shadow: 0 12px 24px rgba(22, 163, 74, 0.45);
        cursor: pointer;
    }
    .kiosk-btn:active {
        transform: translateY(1px) scale(0.99);
        box-shadow: 0 8px 16px rgba(22, 163, 74, 0.40);
    }

    /* 음식 카드 */
    .food-card {
        border-radius: 20px;
        padding: 0.9rem 1.1rem;
        background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
        border: 1px solid rgba(226, 232, 240, 0.9);
        margin-bottom: 0.7rem;
    }
    .food-name {
        font-size: 1.0rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.15rem;
    }
    .food-meta {
        font-size: 0.84rem;
        color: #64748b;
    }

    /* 탭 헤더 살짝 수정 */
    button[kind="secondary"] {
        border-radius: 999px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ======================
# 데이터 로드
# ======================
@st.cache_data
def load_food_db():
    # 첨부한 엑셀 파일 이름에 맞게 수정
    # 같은 폴더에 "20250408_음식DB.xlsx" 파일이 있어야 함
    df = pd.read_excel("20250408_음식DB.xlsx")
    return df

try:
    food_df = load_food_db()
except Exception as e:
    st.error("⚠️ 음식 DB(20250408_음식DB.xlsx)를 불러오는 중 오류가 발생했습니다. 파일이 같은 폴더에 있는지 확인하세요.")
    st.stop()

# 컬럼 이름 예시(엑셀 구조에 맞게 바꿔 주세요)
# 예: 음식명, 카테고리, 칼로리(kcal), 탄수화물(g), 단백질(g), 지방(g), 알레르겐, 종교제한태그, 위치태그 등
# food_df.columns 를 출력해서 실제 헤더 확인 후 아래 변수명을 맞춰 사용해 주세요.
# st.write(food_df.head())

# 내부적으로 사용할 컬럼명 매핑 (엑셀 헤더에 맞춰 수정)
NAME_COL = "음식명"
CAT_COL = "카테고리"
KCAL_COL = "칼로리"
CARB_COL = "탄수화물"
PROT_COL = "단백질"
FAT_COL = "지방"
ALLERGEN_COL = "알레르겐"
RELIGION_COL = "종교제한"
LOCATION_COL = "지역"   # 있다면 사용, 없으면 무시

# ======================
# 상단 Hero 영역
# ======================
col_hero_l, col_hero_r = st.columns([2.2, 1.2])

with col_hero_l:
    st.markdown(
        f"""
        <div class="hero-box">
            <div class="hero-badge">Healicious · Smart Nutrition Kiosk</div>
            <div class="hero-title">Healicious 키오스크</div>
            <div class="hero-sub">
                인스턴트와 가공식품에 지친 현대인을 위한 맞춤형 영양 설계·식단 추천 서비스입니다.<br/>
                키·몸무게·기분·알레르기·종교/이념 등 조건을 한 번에 입력하고,<br/>
                가장 부담 없는 오늘의 식단을 고르고, 바로 근처 음식점까지 찾아 보세요.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_hero_r:
    with st.container():
        st.write("")
        st.write("")
        st.metric("오늘 날짜", date.today().strftime("%Y-%m-%d"))
        st.caption("화면을 터치해 정보를 입력하고, 끌리는 메뉴를 골라 보세요.")

st.write("")

# ======================
# 세션 상태 초기화
# ======================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_meals" not in st.session_state:
    st.session_state.selected_meals = []

# ======================
# 헬퍼 함수
# ======================
def estimate_calories(weight, height, age, gender, activity_level, goal):
    if gender == "남성":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    factor_map = {
        "거의 없음": 1.2,
        "가벼운 활동(주 1~2회)": 1.375,
        "보통(주 3~4회)": 1.55,
        "활동적(주 5회 이상)": 1.725,
    }
    factor = factor_map.get(activity_level, 1.4)
    maintenance = bmr * factor

    if goal == "체중 감량":
        return round(maintenance - 300)
    elif goal in ["체중 증가", "근육량 증가"]:
        return round(maintenance + 300)
    else:
        return round(maintenance)

def filter_by_constraints(df, allergies, diet_type, religion_tags):
    filtered = df.copy()

    # 알레르기 필터 (쉼표 기준)
    if allergies:
        for a in [x.strip() for x in allergies.split(",") if x.strip()]:
            filtered = filtered[~filtered[ALLERGEN_COL].astype(str).str.contains(a, case=False, na=False)]

    # 종교/이념 태그 필터 (엑셀에 해당 열이 있다고 가정)
    if religion_tags:
        for tag in religion_tags:
            # 예: "돼지고기 금지" → "돼지", "halal-only" 등 엑셀 태그와 규칙 맞추기 필요
            filtered = filtered[~filtered[RELIGION_COL].astype(str).str.contains(tag, case=False, na=False)]

    # 식습관(채식, 비건 등)은 엑셀 구조에 맞게 추가 로직 구현 권장
    # 여기서는 단순 예시만 남겨둠
    return filtered

def mood_message(mood):
    if mood in ["지침", "그저 그럼"]:
        return "속이 편안하고 소화가 잘 되는 메뉴를 위주로 골라 보세요."
    elif mood in ["좋음", "매우 좋음"]:
        return "활동적인 하루를 버틸 수 있도록 단백질과 복합 탄수화물이 풍부한 메뉴를 추천합니다."
    else:
        return "균형 잡힌 한 끼를 위해 탄수화물·단백질·지방이 고르게 들어간 메뉴를 선택해 보세요."

# ======================
# 사이드바: 키오스크 네비게이션
# ======================
with st.sidebar:
    st.markdown("### 🧭 Healicious 메뉴")
    choice = st.radio(
        "화면 이동",
        ["홈", "내 정보 입력", "식단 고르기", "주변 음식점"],
        index=["홈", "내 정보 입력", "식단 고르기", "주변 음식점"].index(
            {"home": "홈", "profile": "내 정보 입력", "select": "식단 고르기", "place": "주변 음식점"}\
            .get(st.session_state.page, "홈")
        )
    )

    if choice == "홈":
        st.session_state.page = "home"
    elif choice == "내 정보 입력":
        st.session_state.page = "profile"
    elif choice == "식단 고르기":
        st.session_state.page = "select"
    elif choice == "주변 음식점":
        st.session_state.page = "place"

# ======================
# 페이지 1: 홈
# ======================
if st.session_state.page == "home":
    col_l, col_r = st.columns([1.6, 1.4])

    with col_l:
        st.markdown("### 👤 먼저, 나를 알려 주세요")
        st.write(
            "화면 왼쪽 상단의 ‘내 정보 입력’ 버튼을 눌러 키·몸무게·기분·선호 음식을 선택하면 "
            "Healicious가 오늘의 균형 잡힌 식단을 설계해 줍니다."
        )
        st.write("1. 내 정보 입력 → 2. 식단 고르기 → 3. 주변 음식점 순서로 이용하면 편합니다.")
        st.markdown("---")
        st.markdown("#### Healicious가 고려하는 것들")
        st.write("- 하루 적정 탄수화물·단백질·지방 및 칼로리 균형")
        st.write("- 감량/증량/체지방·근육 등 건강 목표")
        st.write("- 알레르기, 종교·이념, 선호 음식, 오늘의 기분")

    with col_r:
        st.markdown("### 🎨 키오스크 스타일")
        st.write("아래처럼 큰 버튼 위주 간단한 조작만으로 식단을 고를 수 있도록 설계했습니다.")
        st.button("🍽 오늘 식단 고르기 (바로 가기)", use_container_width=True, on_click=lambda: st.session_state.update({"page": "select"}))

# ======================
# 페이지 2: 사용자 정보 입력
# ======================
if st.session_state.page == "profile":
    st.markdown("## 👤 내 정보 입력")

    c1, c2, c3 = st.columns(3)

    with c1:
        name = st.text_input("이름", key="name")
        age = st.number_input("나이", min_value=10, max_value=100, value=25, step=1, key="age")
        gender = st.selectbox("성별", ["남성", "여성", "기타"], key="gender")

    with c2:
        height = st.number_input("키 (cm)", min_value=120, max_value=230, value=170, key="height")
        weight = st.number_input("몸무게 (kg)", min_value=30, max_value=200, value=65, key="weight")
        activity = st.selectbox(
            "활동량",
            ["거의 없음", "가벼운 활동(주 1~2회)", "보통(주 3~4회)", "활동적(주 5회 이상)"],
            key="activity"
        )

    with c3:
        goal = st.selectbox(
            "건강 목표",
            ["체중 감량", "체중 증가", "체지방 감소", "근육량 증가", "유지 및 건강한 식습관"],
            key="goal"
        )
        today_mood = st.select_slider(
            "오늘 기분",
            options=["지침", "그저 그럼", "보통", "좋음", "매우 좋음"],
            value="보통",
            key="mood"
        )
        meal_count = st.selectbox("오늘 먹을 끼니 수", [2, 3, 4, 5], index=1, key="meal_count")

    st.markdown("### 🍽 식습관 / 선호 / 제한")

    col_a, col_b = st.columns(2)
    with col_a:
        diet_type = st.multiselect(
            "식습관",
            ["일반식", "채식 위주", "비건", "저탄수화물", "고단백", "간헐적 단식"],
            default=["일반식"],
            key="diet_type"
        )
        preferred_foods = st.text_area(
            "선호 음식 / 떙기는 음식",
            placeholder="예: 비빔밥, 연어, 샐러드, 두부 요리 등",
            key="preferred_foods"
        )
    with col_b:
        allergies = st.text_area(
            "알레르기 / 위험 식품 (쉼표로 구분)",
            placeholder="예: 땅콩, 새우, 밀, 우유 등",
            key="allergies"
        )
        religion = st.multiselect(
            "종교·이념 제한",
            ["돼지고기 금지", "소고기 금지", "알코올 금지", "할랄만 섭취", "코셔만 섭취"],
            key="religion"
        )

    if st.button("✔ 내 정보 저장 완료", use_container_width=True):
        st.session_state.profile_filled = True
        st.success("내 정보가 저장되었습니다. 상단 메뉴에서 ‘식단 고르기’를 눌러 주세요.")

    if "profile_filled" in st.session_state and st.session_state.profile_filled:
        try:
            cal_need = estimate_calories(
                st.session_state.weight,
                st.session_state.height,
                st.session_state.age,
                st.session_state.gender,
                st.session_state.activity,
                st.session_state.goal,
            )
            st.info(f"오늘 예상 권장 열량은 약 {cal_need} kcal 입니다. (간단 추정값)")
        except Exception:
            pass

# ======================
# 페이지 3: 식단 고르기 (키오스크 화면)
# ======================
if st.session_state.page == "select":
    st.markdown("## 🍽 오늘의 식단 고르기")

    if "profile_filled" not in st.session_state:
        st.warning("먼저 ‘내 정보 입력’에서 정보를 입력해 주세요.")
    else:
        # 사용자 조건으로 음식 필터링
        filtered_df = filter_by_constraints(
            food_df,
            st.session_state.allergies,
            st.session_state.diet_type,
            st.session_state.religion
        )

        # 카테고리별 탭 (아침/점심/저녁/간식 등으로 엑셀에 맞춰 수정)
        categories = filtered_df[CAT_COL].dropna().unique().tolist()
        categories = sorted(categories)
        tab_objs = st.tabs([f"🍽 {c}" for c in categories])

        for tab, cat in zip(tab_objs, categories):
            with tab:
                st.markdown(f"#### {cat}")
                cat_df = filtered_df[filtered_df[CAT_COL] == cat]

                # 키오스크 느낌을 위해 3열 그리드로 음식 카드 배치
                cols = st.columns(3)
                for i, (_, row) in enumerate(cat_df.iterrows()):
                    col = cols[i % 3]
                    with col:
                        with st.container():
                            st.markdown('<div class="food-card">', unsafe_allow_html=True)
                            st.markdown(f'<div class="food-name">{row[NAME_COL]}</div>', unsafe_allow_html=True)
                            meta = f"""
                            <div class="food-meta">
                                {int(row.get(KCAL_COL, 0))} kcal · 
                                탄 {row.get(CARB_COL, '-')}g · 
                                단 {row.get(PROT_COL, '-')}g · 
                                지 {row.get(FAT_COL, '-')}g
                            </div>
                            """
                            st.markdown(meta, unsafe_allow_html=True)
                            if st.button("이 메뉴 선택", key=f"select-{cat}-{i}"):
                                st.session_state.selected_meals.append(row[NAME_COL])
                                st.success(f"'{row[NAME_COL]}' 이(가) 오늘의 식단에 추가되었습니다.")
                            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ✅ 오늘 선택한 메뉴")
        if st.session_state.selected_meals:
            for m in st.session_state.selected_meals:
                st.write(f"- {m}")
        else:
            st.write("아직 선택된 메뉴가 없습니다. 위에서 마음에 드는 음식을 터치해 보세요.")

        st.info(mood_message(st.session_state.mood))

# ======================
# 페이지 4: 주변 음식점 (데모)
# ======================
if st.session_state.page == "place":
    st.markdown("## 📍 내 주변 음식점 (데모)")

    loc = st.text_input("현재 위치 (구/동 또는 도시명)", placeholder="예: 서울 강남구, 부산 해운대 등", key="location")
    st.caption("※ 실제 서비스에서는 지도/배달 앱 API와 연동해 보다 정확한 위치 기반 추천을 제공할 수 있습니다.")

    if st.button("내 주변 건강한 음식점 찾기", use_container_width=True):
        if not loc:
            st.warning("위치를 입력해 주세요.")
        else:
            st.success(f"{loc} 기준으로 건강한 식사를 할 수 있는 음식점 예시입니다.")
            st.write(f"- {loc} 샐러드 전문점 (저칼로리, 고단백 메뉴)")
            st.write(f"- {loc} 현미밥·저염식 한식당")
            st.write(f"- {loc} 브런치 카페 (샐러드 + 단백질 메뉴)")
