import streamlit as st

# 🌈 전체 스타일 (파스텔톤 + 글자 선명)
st.markdown("""
<style>
    .title {
        font-size: 38px;
        font-weight: 800;
        color: #4b4b4b;
    }
    .subtitle {
        font-size: 20px;
        font-weight: 600;
        color: #6d6d6d;
    }
    .stButton>button {
        background-color: #ffe6f2;
        color: #333;
        border-radius: 12px;
        padding: 10px 20px;
        border: 1px solid #ffb6d9;
    }
    .stButton>button:hover {
        background-color: #ffb6d9;
        color: white;
    }
    .block {
        padding: 20px;
        background-color: #fff7fb;
        border-radius: 16px;
        border: 1px solid #ffd5eb;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 🍨 데이터
containers = {
    "싱글컵": {"price": 3500, "scoops": 1},
    "더블컵": {"price": 5900, "scoops": 2},
    "파인트": {"price": 8200, "scoops": 3},
    "쿼터": {"price": 15500, "scoops": 4},
}

flavors = [
    "🍓 스트로베리",
    "🍫 초코",
    "🍦 바닐라",
    "🍪 쿠키앤크림",
    "🍈 메로나",
    "🍇 포도샤베트",
    "🥭 망고",
    "🌈 레인보우샤베트"
]

payments = ["💳 카드결제", "💵 현금결제"]


# ----------------------------------------
# 🧁 UI 시작
# ----------------------------------------

st.markdown('<p class="title">🍨 배스킨라빈스 셀프 키오스크</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">천천히 선택해주시면 맛있는 아이스크림을 준비해드릴게요 😊</p>', unsafe_allow_html=True)
st.write("")


# ------------------------------
# Step 1. 매장/포장 선택
# ------------------------------
st.markdown('<div class="block">', unsafe_allow_html=True)
st.subheader("1️⃣ 어디서 드시나요?")

takeout = st.radio(
    "선택해주세요!",
    ["매장에서 먹기 🪑", "포장하기 🛍️"],
    horizontal=True
)
st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------
# Step 2. 용기 선택
# ------------------------------
st.markdown('<div class="block">', unsafe_allow_html=True)
st.subheader("2️⃣ 용기를 선택해주세요!")

container = st.selectbox("용기 타입", list(containers.keys()))
max_scoops = containers[container]["scoops"]  # 오류 없는 안전한 값
price = containers[container]["price"]

st.markdown(f"👉 선택한 용기: **{container}** (스쿱 {max_scoops}개 / {price:,}원)")
st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------
# Step 3. 아이스크림 선택 (스쿱 수 확정 후 출력)
# ------------------------------
st.markdown('<div class="block">', unsafe_allow_html=True)
st.subheader("3️⃣ 아이스크림 맛을 선택해주세요!")

# 용기 선택이 된 경우만 맛 선택 창 출력
selected_flavors = []

for i in range(1, max_scoops + 1):
    flavor = st.selectbox(f"🍨 {i}번 스쿱", flavors, key=f"flavor{i}")
    selected_flavors.append(flavor)

st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------
# Step 4. 결제 방식
# ------------------------------
st.markdown('<div class="block">', unsafe_allow_html=True)
st.subheader("4️⃣ 결제 방식을 선택해주세요!")

pay = st.radio("결제 선택", payments, horizontal=True)
st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------
# Step 5. 결과 출력
# ------------------------------
st.markdown('<div class="block">', unsafe_allow_html=True)
st.subheader("💖 주문 확인")

if st.button("주문 완료하기 🍨"):
    st.success("주문이 완료되었어요! 아래 내용을 확인해주세요 😊")

    st.write(f"• **이용 방법:** {takeout}")
    st.write(f"• **용기:** {container}")
    st.write(f"• **선택한 맛:** {', '.join(selected_flavors)}")
    st.write(f"• **결제 방식:** {pay}")
    st.write(f"### 💰 최종 결제 금액: **{price:,}원**")
    st.balloons()

st.markdown('</div>', unsafe_allow_html=True)
