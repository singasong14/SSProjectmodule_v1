import streamlit as st

st.set_page_config(page_title="🍨 배스킨라빈스 키오스크", layout="wide")

# ----------------------------------------
# CSS 스타일
# ----------------------------------------
st.markdown("""
<style>
body {background-color:#FAF7F5; font-family:'Noto Sans KR', sans-serif;}
.card {
    background-color:#fff7fb;
    border-radius:15px;
    padding:10px;
    margin:5px;
    text-align:center;
    box-shadow:0 4px 12px rgba(0,0,0,0.08);
    transition: transform 0.2s;
    position:relative;
}
.card:hover {
    transform: scale(1.05);
}
.card img {
    width:100%;
    border-radius:12px;
}
.tooltip {
    visibility:hidden;
    width:220px;
    background-color:#ffe6f2;
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
.menu-title {font-size:16px; font-weight:700; margin:5px 0;}
.menu-price {font-size:14px; color:#555;}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------
# 메뉴 데이터 (모든 맛)
# 이미지 URL은 placeholder 예시
# ----------------------------------------
menu_items = {
    "골든 프랄린 버터": {"emoji":"🧈","price":4500,"desc":"버터와 프랄린 슈가가 조화로운 달콤함","img":"https://via.placeholder.com/150"},
    "초코포키해♥": {"emoji":"🍫","price":4500,"desc":"초코포키와 초콜릿 쿠키가 씹히는 맛","img":"https://via.placeholder.com/150"},
    "말차다미아": {"emoji":"🍵","price":4500,"desc":"말차와 마카다미아, 마스카포네 치즈의 풍미","img":"https://via.placeholder.com/150"},
    "너는 참 달고나": {"emoji":"🍯","price":4500,"desc":"달고나와 카라멜이 선사하는 달콤함","img":"https://via.placeholder.com/150"},
    "(Lessly Edition) 초코나무숲": {"emoji":"🌲","price":5200,"desc":"진한 초코의 풍미가 가득","img":"https://via.placeholder.com/150"},
    "골든 애플 요거트": {"emoji":"🍏","price":4500,"desc":"상큼한 사과와 요거트","img":"https://via.placeholder.com/150"},
    "(Lessly Edition) 아몬드 봉봉": {"emoji":"🥜","price":5200,"desc":"달콤한 초코와 고소한 아몬드","img":"https://via.placeholder.com/150"},
    "(Lessly Edition) 엄마는 외계인": {"emoji":"👽","price":5200,"desc":"초콜릿과 초코볼이 가득","img":"https://via.placeholder.com/150"},
    "아이스 맥심 모카골드": {"emoji":"☕","price":4500,"desc":"맥심 모카골드 커피맛 그대로","img":"https://via.placeholder.com/150"},
    "사랑에 빠진 딸기": {"emoji":"🍓","price":4500,"desc":"딸기, 치즈, 크런치 초콜릿","img":"https://via.placeholder.com/150"},
    "피치 요거트": {"emoji":"🍑","price":4500,"desc":"부드러운 복숭아와 요거트","img":"https://via.placeholder.com/150"},
    "수박 Hero": {"emoji":"🍉","price":4500,"desc":"여름 수박이 톡! 시원한 맛","img":"https://via.placeholder.com/150"},
    "소금 우유 아이스크림": {"emoji":"🧂","price":4500,"desc":"단짠 조합의 소금 우유 아이스크림","img":"https://via.placeholder.com/150"},
    "민트 초콜릿 칩": {"emoji":"🌿","price":4500,"desc":"상쾌한 민트와 초콜릿 칩","img":"https://via.placeholder.com/150"},
    "뉴욕 치즈케이크": {"emoji":"🧀","price":4500,"desc":"부드러운 뉴욕 스타일 치즈케이크","img":"https://via.placeholder.com/150"},
    "레인보우 샤베트": {"emoji":"🌈","price":4500,"desc":"파인애플, 오렌지, 라즈베리의 화려한 조합","img":"https://via.placeholder.com/150"},
    "체리쥬빌레": {"emoji":"🍒","price":4500,"desc":"달콤한 체리 풍미","img":"https://via.placeholder.com/150"},
    "슈팅스타": {"emoji":"💫","price":4500,"desc":"톡톡 튀는 팝핑캔디와 체리","img":"https://via.placeholder.com/150"},
    "오레오 쿠키 앤 크림": {"emoji":"🍪","price":4500,"desc":"바닐라와 오레오 쿠키 조합","img":"https://via.placeholder.com/150"},
    "바닐라": {"emoji":"🍨","price":4000,"desc":"부드러운 정통 바닐라","img":"https://via.placeholder.com/150"},
    # 필요시 나머지 맛들도 동일하게 추가 가능
}

containers = {"싱글컵":{"price":3500,"scoops":1},"더블컵":{"price":5900,"scoops":2},"파인트":{"price":8200,"scoops":3},"쿼터":{"price":15500,"scoops":4}}
payments = ["💳 카드결제","💵 현금결제","🎁 기프티콘"]

# ----------------------------------------
# Header
# ----------------------------------------
st.markdown("## 🍨 배스킨라빈스 키오스크")
st.write("마우스를 메뉴 위에 올리면 상세 설명이 보여요! 😉")
st.write("")

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
        <div class='card'>
            <img src="{info['img']}" alt="{name}">
            <div class="menu-title">{info['emoji']} {name}</div>
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
