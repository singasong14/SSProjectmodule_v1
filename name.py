# Healicious Kiosk Streamlit App
# Single-file Streamlit app built for a beautiful, touch-friendly kiosk experience.
# Includes: polished UI, step-by-step user onboarding, nutrition calculation, meal recommendations,
# allergy/religion filters, mood-aware suggestions, export, and fallback local food DB.
# Also reads optional uploaded Excel DB at /mnt/data/20250408_음식DB.xlsx if available (for hosted envs).
#
# Requirements:
# pip install streamlit pandas numpy pillow openpyxl
# Run with: streamlit run Healicious_kiosk_app.py

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import io
import os
import base64

st.set_page_config(page_title="Healicious Kiosk", layout="wide", page_icon="🥗")

# ----------------------
# App CSS / Visual Theme
# ----------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
html, body, [class*="css"], .stApp {
  height: 100%;
  background: linear-gradient(180deg, #f6fbf6 0%, #ffffff 60%);
  font-family: 'Inter', sans-serif;
}
header[role="banner"] {display: none}

.kiosk-container {
  padding: 28px 36px;
}
.brand {
  display:flex; align-items:center; gap:18px; margin-bottom:14px;
}
.brand h1 { margin:0; font-size:36px; letter-spacing: -0.5px; }
.brand p { margin:0; color:#6b7280; }

.card {
  background: white; border-radius:18px; padding:22px; box-shadow: 0 8px 30px rgba(20,30,50,0.06);
}
.big-button {
  background: linear-gradient(90deg,#6ee7b7,#34d399); border-radius:12px; padding:18px 22px; color:#fff; font-weight:700; border:none; width:100%; font-size:20px; box-shadow: 0 10px 30px rgba(52,211,153,0.18);
}
.small-muted { color:#6b7280; font-size:13px; }
.card-title { font-size:18px; font-weight:700; margin-bottom:8px }
.food-card { border-radius:12px; padding:12px; }
.food-name { font-weight:700 }

/* touch-friendly controls */
.stButton>button, .stSelectbox>div>div>div, .stTextInput>div>div>input, .stNumberInput>div>div>input {
  touch-action: manipulation;
}

@media (max-width: 900px) {
  .brand h1 { font-size:28px }
}
</style>
""", unsafe_allow_html=True)

# ----------------------
# Helper functions
# ----------------------

def load_fallback_food_db():
    # A small but curated fallback DB
    return pd.DataFrame([
        {"name": "그릴드 닭가슴살 샐러드", "carbs": 12, "protein": 34, "fat": 8, "cal": 320, "vegan": False, "halal": True, "tags": "salad,protein"},
        {"name": "연어 아보카도 볼", "carbs": 10, "protein": 30, "fat": 22, "cal": 420, "vegan": False, "halal": True, "tags": "omega3"},
        {"name": "키노아 비건 볼", "carbs": 46, "protein": 14, "fat": 10, "cal": 360, "vegan": True, "halal": True, "tags": "fiber,vegan"},
        {"name": "두부 스테이크 & 야채", "carbs": 18, "protein": 26, "fat": 12, "cal": 300, "vegan": True, "halal": True, "tags": "soy"},
        {"name": "현미 혼합 곡물밥 + 된장국", "carbs": 62, "protein": 14, "fat": 6, "cal": 380, "vegan": False, "halal": True, "tags": "carb,comfort"},
        {"name": "계란과 채소 볶음밥 (저유지)", "carbs": 64, "protein": 22, "fat": 10, "cal": 410, "vegan": False, "halal": True, "tags": "quick"},
    ])


def try_load_user_db(path='/mnt/data/20250408_음식DB.xlsx'):
    if os.path.exists(path):
        try:
            df = pd.read_excel(path)
            # Basic normalization if columns exist
            expected = ['name','carbs','protein','fat','cal','vegan','halal']
            if all(col in df.columns for col in expected):
                return df
            else:
                # try to map common names
                cols = {c.lower():c for c in df.columns}
                mapping = {}
                for e in expected:
                    if e in cols:
                        mapping[cols[e]] = e
                if mapping:
                    return df.rename(columns=mapping)[expected]
                return df
        except Exception as e:
            return None
    return None


def calc_daily_calories(weight, height, age, gender, activity):
    # Mifflin-St Jeor BMR
    if gender == '남성':
        bmr = 10*weight + 6.25*height - 5*age + 5
    else:
        bmr = 10*weight + 6.25*height - 5*age - 161
    mult = {'낮음':1.2,'보통':1.45,'높음':1.7}
    return int(bmr * mult.get(activity,1.45))


def recommend_meals(df, mood, goal, avoid_list, religion, topk=4):
    # basic scoring: match goal and mood
    scores = []
    for _, row in df.iterrows():
        s = 0
        # protein preference for muscle/weight gain
        if goal in ['근육 증가','체중 증가']:
            s += row.get('protein',0)*1.5
        if goal == '체중 감량':
            s += -row.get('cal',0)/10
        # mood tweaks
        if mood == '피곤함':
            s += row.get('protein',0)
        if mood == '스트레스':
            s += -abs(row.get('carbs',0)-40)  # prefer balanced carbs
        scores.append(s)
    df = df.copy()
    df['score'] = scores

    # filters: allergies and religion
    if avoid_list:
        for a in avoid_list:
            df = df[~df['name'].str.contains(a, case=False, na=False)]
    if religion == '비건':
        df = df[df['vegan']==True]
    if religion == '할랄':
        df = df[df['halal']==True]

    df = df.sort_values('score', ascending=False).head(topk)
    return df


def make_downloadable_json(data):
    b = data.to_json(orient='records', force_ascii=False)
    b64 = base64.b64encode(b.encode()).decode()
    href = f"data:application/json;base64,{b64}"
    return href

# ----------------------
# Load DB (user-provided Excel optional)
# ----------------------
user_db = try_load_user_db()
if user_db is None:
    food_db = load_fallback_food_db()
else:
    food_db = user_db

# Ensure expected cols
for c in ['name','carbs','protein','fat','cal','vegan','halal']:
    if c not in food_db.columns:
        # try to infer
        if c == 'cal' and 'calories' in food_db.columns:
            food_db = food_db.rename(columns={'calories':'cal'})
        else:
            food_db[c] = np.nan

# ----------------------
# Kiosk layout and flow
# ----------------------

if 'step' not in st.session_state:
    st.session_state.step = 'welcome'

# Top header
with st.container():
    st.markdown('<div class="kiosk-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown('<div class="brand"><img src="data:image/svg+xml;utf8,<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"56\" height=\"56\"><rect rx=\"12\" width=\"56\" height=\"56\" fill=\"%236ef0b0\"/><text x=\"50%\" y=\"54%\" font-size=\"30\" text-anchor=\"middle\" font-family=\"Inter\" fill=\"white\">H</text></svg>" style="height:56px; border-radius:12px;"/>
                        <div><h1>Healicious Kiosk</h1><p class="small-muted">맞춤 식단을 빠르고 아름답게</p></div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div style="text-align:right"><p class="small-muted">터치에 최적화된 키오스크 모드</p></div>', unsafe_allow_html=True)

# Main content depending on step
if st.session_state.step == 'welcome':
    st.markdown('\n')
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write('')
    c1, c2 = st.columns([2,1])
    with c1:
        st.markdown('<div class="card-title">안녕하세요! Healicious에 오신 것을 환영합니다.</div>', unsafe_allow_html=True)
        st.write('건강 목표, 알레르기, 기분을 알려주시면 즉시 맞춤 식단을 설계해드립니다.')
        st.write('시작하려면 아래의 버튼을 눌러주세요 — 키오스크에서 빠르게 사용할 수 있도록 설계되었습니다.')
    with c2:
        if st.button('시작하기', key='start', help='맞춤 식단 설계 시작'):
            st.session_state.step = 'profile'
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == 'profile':
    # Large form layout for touch
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">사용자 정보 입력</div>', unsafe_allow_html=True)
    prof_col1, prof_col2, prof_col3 = st.columns([1,1,1])
    with prof_col1:
        name = st.text_input('이름 (닉네임)', value=st.session_state.get('name',''), placeholder='홍길동')
        age = st.number_input('나이', min_value=10, max_value=100, value=int(st.session_state.get('age',30)))
        gender = st.selectbox('성별', ['남성','여성'])
    with prof_col2:
        height = st.number_input('키 (cm)', min_value=120, max_value=230, value=int(st.session_state.get('height',170)))
        weight = st.number_input('몸무게 (kg)', min_value=30, max_value=200, value=int(st.session_state.get('weight',70)))
        activity = st.selectbox('활동 수준', ['낮음','보통','높음'])
    with prof_col3:
        goal = st.selectbox('건강 목표', ['유지','체중 감량','체중 증가','근육 증가','특정 부위 비율 개선'])
        mood = st.selectbox('오늘 기분', ['상쾌함','피곤함','스트레스','우울함','그냥 배고픔'])
        religion = st.selectbox('식이 제한(종교/이념)', ['없음','비건','할랄'])

    st.markdown('---')
    st.markdown('<div class="card-title">알레르기 및 피하고 싶은 재료</div>', unsafe_allow_html=True)
    avoid = st.text_area('콤마(,)로 구분하여 입력 (예: 새우,우유,땅콩)')

    st.markdown('<div style="margin-top:10px;">', unsafe_allow_html=True)
    c1, c2 = st.columns([1,1])
    with c1:
        if st.button('뒤로', key='back_to_welcome'):
            st.session_state.step = 'welcome'
    with c2:
        if st.button('다음 — 추천 생성', key='to_reco'):
            # save to state
            st.session_state.update({'name':name,'age':age,'gender':gender,'height':height,'weight':weight,'activity':activity,'goal':goal,'mood':mood,'religion':religion,'avoid':avoid})
            st.session_state.step = 'results'
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == 'results':
    # Compute recommendations
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">맞춤 추천 결과</div>', unsafe_allow_html=True)
    # gather
    name = st.session_state.get('name')
    age = st.session_state.get('age')
    height = st.session_state.get('height')
    weight = st.session_state.get('weight')
    gender = st.session_state.get('gender')
    activity = st.session_state.get('activity')
    goal = st.session_state.get('goal')
    mood = st.session_state.get('mood')
    religion = st.session_state.get('religion')
    avoid = st.session_state.get('avoid','')
    avoid_list = [a.strip() for a in avoid.split(',') if a.strip()]

    daily_cal = calc_daily_calories(weight, height, age, gender, activity)
    st.metric(label='권장 일일 칼로리 (kcal)', value=f"{daily_cal} kcal")

    # recommend meals
    recs = recommend_meals(food_db.fillna(0), mood, goal, avoid_list, religion, topk=6)

    # show as cards
    cols = st.columns(3)
    for i, (_, row) in enumerate(recs.iterrows()):
        c = cols[i%3]
        with c:
            st.markdown('<div class="card food-card">', unsafe_allow_html=True)
            st.markdown(f"<div class='food-name'>{row['name']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='small-muted'>칼로리: {int(row.get('cal',0))} kcal · 탄수화물: {int(row.get('carbs',0))}g · 단백질: {int(row.get('protein',0))}g</div>", unsafe_allow_html=True)
            st.write('')
            if st.button(f"상세보기_{i}"):
                st.session_state['detail'] = row.to_dict()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('---')
    # detail pane
    if 'detail' in st.session_state:
        d = st.session_state['detail']
        st.subheader('상세 영양 정보')
        st.write(d)

    # Nearby restaurants mock
    st.markdown('<div class="card-title">근처 음식점 추천</div>', unsafe_allow_html=True)
    # A simple mock list — in real deployment, integrate Maps/Places API
    nearby = []
    for _, r in food_db.iterrows():
        # pretend some restaurants offer those menus
        if pd.notna(r.get('name')) and len(nearby) < 4:
            nearby.append({'name': f"{r['name']} 전문점", 'menu': r['name'], 'distance': np.random.randint(150,900)})

    nr_cols = st.columns(len(nearby))
    for i, n in enumerate(nearby):
        with nr_cols[i]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"**{n['name']}**")
            st.markdown(f"{n['menu']} · {n['distance']}m")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('---')
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button('다시하기'):
            st.session_state.step = 'profile'
    with c2:
        if st.button('새 세션 (홈으로)'):
            st.session_state.clear()
            st.experimental_rerun()
    with c3:
        # download recommendations
        if not recs.empty:
            href = make_downloadable_json(recs)
            st.markdown(f"[추천 결과 다운로드(JSON)]({href})")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div style="height:30px"></div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#9ca3af; font-size:12px">Healicious — Designed for kiosks · Privacy-friendly demo</div>', unsafe_allow_html=True)

# End of file
