import streamlit as st

st.set_page_config(page_title="🍨 배스킨라빈스 키오스크", layout="wide")

# ----------------------------------------
# CSS 스타일: 파스텔톤 + hover + card effect
# ----------------------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(to bottom, #fffaf0, #ffe6f0);
    font-family:'Noto Sans KR', sans-serif;
}
.card {
    background: #fff;
    border-radius: 20px;
    padding: 15px;
    margin: 5px;
    text-align:center;
    box-shadow:0 8px 20px rgba(0,0,0,0.1);
    transition: transform 0.25s, box-shadow 0.25s;
    position:relative;
}
.card:hover {
    transform: scale(1.08);
    box-shadow:0 12px 30px rgba(0,0,0,0.15);
}
.menu-title {
    font-size:18px;
    font-weight:700;
    margin:8px 0;
}
.menu-price {
    font-size:16px;
    color:#555;
    margin-bottom:5px;
}
.tooltip {
    visibility:hidden;
    width:220px;
    background-color:#ffe6f0;
    color:#333;
    text-align:left;
    border-radius:8px;
    padding:8px;
    position:absolute;
    z-index:1;
    bottom:105%;
    left:50%;
    margin-left:-110px;
    box-shadow:0 2px 8px rgba(0,0,0,0.2);
}
.card:hover .tooltip {
    visibility:visible;
}
.stButton>button {
    background: linear-gradient(90deg,#ffb6d9,#ffd2e8);
    color:#2C2C2C;
    border-radius:10px;
    padding:0.5rem 1rem;
    font-weight:700;
    border:none;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------
# 메뉴 데이터: emoji + 색깔 + 가격 + 설명
# ----------------------------------------
menu_items = {
    "골든 프랄린 버터": {"emoji":"🧈","color":"#FFD580","price":4500,"desc":"버터와 프랄린 슈가가 조화로운 달콤함"},
    "초코포키해♥": {"emoji":"🍫","color":"#D2A679","price":4500,"desc":"초코포키와 초콜릿 쿠키가 씹히는 맛"},
    "말차다미아": {"emoji":"🍵","color":"#A3CFA3","price":4500,"desc":"말차와 마카다미아, 마스카포네 치즈의 풍미"},
    "너는 참 달고나": {"emoji":"🍯","color":"#FFD966","price":4500,"desc":"달고나와 카라멜이 선사하는 달콤함"},
    "(Lessly Edition) 초코나무숲": {"emoji":"🌲","color":"#CFA3D2","price":5200,"desc":"진한 초코의 풍미가 가득"},
    "골든 애플 요거트": {"emoji":"🍏","color":"#A8E6CF","price":4500,"desc":"상큼한 사과와 요거트"},
    "(Lessly Edition) 아몬드 봉봉": {"emoji":"🥜","color":"#F0D6A0","price":5200,"desc":"달콤한 초코와 고소한 아몬드"},
    "(Lessly Edition) 엄마는 외계인": {"emoji":"👽","color":"#C5C5F0","price":5200,"desc":"초콜릿과 초코볼이 가득"},
    "아이스 맥심 모카골드": {"emoji":"☕","color":"#A0522D","price":4500,"desc":"맥심 모카골드 커피맛 그대로"},
    "사랑에 빠진 딸기": {"emoji":"🍓","color":"#FF9FB2","price":4500,"desc":"딸기, 치즈, 크런치 초콜릿"},
    "피치 요거트": {"emoji":"🍑","color":"#FFCFAB","price":4500,"desc":"부드러운 복숭아와 요거트"},
    "수박 Hero": {"emoji":"🍉","color":"#FF6666","price":4500,"desc":"여름 수박이 톡! 시원한 맛"},
    "소금 우유 아이스크림": {"emoji":"🧂","color":"#F0F0F0","price":4500,"desc":"단짠 조합의 소금 우유 아이스크림"},
    "민트 초콜릿 칩": {"emoji":"🌿","color":"#B5EAD7","price":4500,"desc":"상쾌한 민트와 초콜릿 칩"},
    "뉴욕 치즈케이크": {"emoji":"🧀","color":"#FFE5B4","price":4500,"desc":"부드러운 뉴욕 스타일 치즈케이크"},
    "레인보우 샤베트": {"emoji":"🌈","color":"#FFB3BA","price":4500,"desc":"파인애플, 오렌지, 라즈베리의 화려한 조합"},
    "체리쥬빌레": {"emoji":"🍒","color":"#FF4D6D","price":4500,"desc":"달콤한 체리 풍미"},
    "슈팅스타": {"emoji":"💫","color":"#FFD1DC","price":4500,"desc":"톡톡 튀는 팝핑캔디와 체리"},
    "오레오 쿠키 앤 크림": {"emoji":"🍪","color":"#D6D6D6","price":4500,"desc":"바닐라와 오레오 쿠키 조합"},
    "바닐라": {"emoji":"🍨","color":"#FFF5B7","price":4000,"desc":"부드러운 정통 바닐라"},
}

containers = {"싱글컵":{"price":3500,"scoops":1},"더블컵":{"price":5900,"scoops":2},"파인트":{"price":8200,"scoops":3},"쿼터":{"price":15500,"scoops":4}}
payments = ["💳 카드결제","💵 현금결제","🎁 기프티콘"]

# ----------------------------------------
# Header
# ----------------------------------------
st.markdown("## 🍨 배스킨라빈스 키오스크")
st.write("마우스를 메뉴 위에 올리면 상세 설명과 맛 색상을 확인할 수 있어요! 🌈")

# ----------------------------------------
# 1. 용기 선택
# ----------------------------------------
st.subheader("1️⃣ 용기 선택")
container = st.selectbox("용기 타입", list(containers.keys()))
max_scoops = containers[container]["scoops"]

# ----------------------------------------
# 2. 메뉴 선택 (5열 그리드)
# ----------------------------------------
st.subheader(f"2️⃣ 메뉴 선택 (최대 {max_scoops}개)")
cols = st.columns(5)
selected_flavors = []
i = 0
for name, info in menu_items.items():
    col = cols[i % 5]
    with col:
        st.markdown(f"""
        <div class='card' style='background:{info['color']}'>
            <div style='font-size:50px'>{info['emoji']}</div>
            <div class="menu-title">{name}</div>
            <div class="menu-price">{info['price']:,}원</div>
            <div class="tooltip">{info['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.checkbox("선택", key=f"chk_{name}"):
            selected_flavors.append((name, info["price"]))
    i += 1

if len(selected_flavors) > max_scoops:
    st.warning(f"⚠️ 최대 {max_scoops}개만 선택 가능합니다. 처음 {max_scoops}개만 적용됩니다.")
    selected_flavors = selected_flavors[:max_scoops]

# ----------------------------------------
# 3. 결제 선택
# ----------------------------------------
st.subheader("3️⃣ 결제 방법 선택")
payment_method = st.radio("결제 수단", payments, horizontal=True)

# ----------------------------------------
# 4. 최종 결제 금액
# ----------------------------------------
total_price = sum([p for _,p in selected_flavors])
st.markdown("---")
st.markdown(f"### 💰 최종 결제 금액: {total_price:,}원")
st.markdown(f"• 용기: {container}")
st.markdown(f"• 선택한 메뉴: {', '.join([f for f,_ in selected_flavors])}")
st.markdown(f"• 결제 수단: {payment_method}")

if st.button("주문 완료 🍨"):
    st.success("주문 완료! 즐거운 아이스크림 시간 되세요 🎉")
    st.balloons()
