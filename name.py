# br_kiosk.py
import streamlit as st
from datetime import datetime

# =========================================
# 🎨 파스텔톤 색상 + 높은 가독성
# =========================================
st.set_page_config(page_title="🍨 BR 키오스크", layout="wide")

PALETTE = {
    "bg": "#FAF7F5",
    "card": "#FFFFFF",
    "accent": "#FFE4EE",
    "accent2": "#E7F6FF",
    "accent3": "#FFF9D6",
    "text": "#2C2C2C",
    "subtext": "#6D6D6D",
    "point": "#FF8FB1",
}

# CSS 적용
st.markdown(
    f"""
    <style>
    body {{
        background-color: {PALETTE['bg']};
        color: {PALETTE['text']};
        font-family: 'Noto Sans KR', sans-serif;
    }}

    .card {{
        background: {PALETTE['card']};
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        margin-bottom: 18px;
    }}

    .title {{
        font-size: 30px;
        font-weight: 800;
        color: {PALETTE['text']};
    }}

    .subtitle {{
        font-size: 18px;
        margin-bottom: 8px;
        font-weight: 700;
        color: {PALETTE['text']};
    }}

    .note {{
        color: {PALETTE['subtext']};
        font-size: 14px;
    }}

    .stButton>button {{
        background: linear-gradient(90deg, #ffb6d9, #ffd2e8);
        color: black;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 10px;
        font-weight: 700;
        font-size: 16px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================
# 데이터 / 설정
# =========================================
CONTAINERS = {
    "컵 - 싱글 (1스쿱) 🥤": {"max": 1, "price": 0},
    "컵 - 더블 (2스쿱) 🥤🥤": {"max": 2, "price": 0},
    "콘 - 슈가 (1스쿱) 🍪": {"max": 1, "price": 300},
    "콘 - 와플 (2스쿱) 🧇": {"max": 2, "price": 600},
    "파인트 (6스쿱) 🧊": {"max": 6, "price": 0},
}

FLAVORS = [
    "바닐라 🍦", "초코 🍫", "스트로베리 🍓", "녹차 🍵",
    "민트초코 🌿", "망고 🥭", "쿠키앤크림 🍪", "카라멜 🍯",
]

BASE_PRICE = 3200  # per scoop
TOPPING_PRICE = 700
TAX = 0.1
CARD_FEE = 0.004


def krw(x): return f"₩{int(x):,}"


# =========================================
# Header
# =========================================
st.markdown(
    """
    <div class='card'>
        <div class='title'>🍨 Baskin Robbins 키오스크</div>
        <div class='note'>원하는 조합으로 나만의 아이스크림을 만들어보세요!</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================
# 1. 먹고 갈지 / 포장할지
# =========================================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>1) 이용 방식 선택 🏷️</div>", unsafe_allow_html=True)

usage = st.radio("어떻게 이용하시겠어요?", ["매장에서 먹기 🍽️", "포장하기 🥡"])
st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# 2. 용기 선택
# =========================================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>2) 용기 선택 🍧</div>", unsafe_allow_html=True)

container_list = list(CONTAINERS.keys())
container = st.selectbox("용기를 골라주세요", container_list)
max_scoops = CONTAINERS[container]["max"]
extra_price = CONTAINERS[container]["price"]

st.markdown(
    f"<div class='note'>이 용기는 최대 <b>{max_scoops} 스쿱</b>까지 담을 수 있어요.</div>",
    unsafe_allow_html=True
)
st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# 3. 맛 선택
# =========================================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>3) 아이스크림 맛 선택 🍨</div>", unsafe_allow_html=True)

scoops = st.slider("스쿱 수 선택", 1, max_scoops, max_scoops)

flavors = st.multiselect("스쿱 수에 맞게 맛을 골라주세요", FLAVORS, default=FLAVORS[:scoops])
if len(flavors) > scoops:
    st.warning(f"⚠️ {scoops}개까지만 선택할 수 있어요! 처음 {scoops}개만 사용됩니다.")
    flavors = flavors[:scoops]

st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# 4. 토핑 선택
# =========================================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>4) 토핑 추가 ✨</div>", unsafe_allow_html=True)

add_topping = st.checkbox("토핑 추가하기 (+700원)")
topping_count = st.number_input("토핑 개수", 1, 5, 1) if add_topping else 0

st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# 5. 결제
# =========================================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>5) 결제 방식 선택 💳</div>", unsafe_allow_html=True)

pay = st.radio("결제 수단을 선택해주세요", ["현금 💵", "카드 💳"])

# 가격 계산
subtotal = scoops * BASE_PRICE + extra_price + topping_count * TOPPING_PRICE
tax = subtotal * TAX
fee = subtotal * CARD_FEE if pay == "카드 💳" else 0
total = subtotal + tax + fee

st.markdown("---")
st.markdown(f"**소계**: {krw(subtotal)}")
st.markdown(f"**부가세(10%)**: {krw(tax)}")
if fee > 0:
    st.markdown(f"**카드 수수료**: {krw(fee)}")
st.markdown(f"### 👉 최종 결제 금액: <b>{krw(total)}</b>", unsafe_allow_html=True)

confirm = st.button("결제하기 🚀")

if confirm:
    st.success("결제가 완료되었습니다! 즐거운 시간 되세요 😊")
    st.balloons()

st.markdown("</div>", unsafe_allow_html=True)
