# br_kiosk.py
import streamlit as st
import pandas as pd
from datetime import datetime

# =========================
# 기본 라이브러리 (helper functions & constants)
# =========================

# 파스텔톤 색상 (CSS에서 활용)
PASTEL = {
    "bg": "#FFF8F0",
    "card": "#FFF1F6",
    "accent1": "#FFDDE6",
    "accent2": "#E8F7FF",
    "accent3": "#F6F9E9",
    "text": "#333333",
    "muted": "#6B6B6B",
    "button": "#FFC9DE",
}

# 아이스크림 맛 정보 (이모지 포함)
FLAVORS = {
    "Vanilla 🍦": "Classic smooth vanilla",
    "Chocolate 🍫": "Rich dark chocolate",
    "Strawberry 🍓": "Fresh strawberry",
    "Mint Choco 🌿": "Mint with chocolate chips",
    "Cookie & Cream 🍪": "Creamy with cookie bits",
    "Pistachio 🟢": "Nutty pistachio",
    "Mango 🥭": "Tropical mango",
    "Green Tea 🍵": "Subtle matcha flavor",
    "Caramel Swirl 🍯": "Sweet caramel ribbon",
    "Lemon Sorbet 🍋": "Tangy and refreshing",
}

# 용기 옵션과 스쿱(최대 허용) 및 기본 가격 정책 (KRW)
CONTAINERS = {
    "컵 - 싱글 (Cup - Single, 1 scoop) 🥤": {"max_scoops": 1, "surcharge": 0},
    "컵 - 더블 (Cup - Double, 2 scoops) 🥤🥤": {"max_scoops": 2, "surcharge": 0},
    "콘 - 슈가 (Cone - Sugar) 🍪": {"max_scoops": 1, "surcharge": 200},
    "콘 - 와플 (Cone - Waffle) 🧇": {"max_scoops": 2, "surcharge": 500},
    "파인트 (Pint - 포장 전용) 🧊": {"max_scoops": 6, "surcharge": 0},
}

# 가격 설정
PRICE_PER_SCOOP = 3000  # 원
TOPPING_PRICE = 500     # (선택 시) 예시 토핑 가격
TAX_RATE = 0.10         # 부가세 10%
CARD_SURCHARGE_RATE = 0.005  # 카드결제 시 카드사 수수료 가상의 부과율 0.5% (표시용)

# 유틸리티 함수
def krw(amount: float) -> str:
    """숫자를 한국 원화 포맷으로 반환"""
    return f"₩{int(round(amount)):,}"

def calc_price(scoops: int, container_key: str, toppings_count: int, payment_method: str):
    container = CONTAINERS[container_key]
    subtotal = scoops * PRICE_PER_SCOOP
    subtotal += container["surcharge"]
    subtotal += toppings_count * TOPPING_PRICE
    tax = subtotal * TAX_RATE
    surcharge = 0
    if payment_method == "카드 결제 💳":
        surcharge = subtotal * CARD_SURCHARGE_RATE
    total = subtotal + tax + surcharge
    breakdown = {
        "scoops": scoops,
        "price_per_scoop": PRICE_PER_SCOOP,
        "container_surcharge": container["surcharge"],
        "toppings_count": toppings_count,
        "toppings_price": toppings_count * TOPPING_PRICE,
        "subtotal": subtotal,
        "tax": tax,
        "payment_surcharge": surcharge,
        "total": total
    }
    return breakdown

# =========================
# 스타일 (페이지 전역 CSS)
# =========================
st.set_page_config(page_title="🎉 Baskin-Robbins 키오스크 (Demo)", layout="wide")

st.markdown(
    f"""
    <style>
    :root {{
        --bg: {PASTEL['bg']};
        --card: {PASTEL['card']};
        --accent1: {PASTEL['accent1']};
        --accent2: {PASTEL['accent2']};
        --accent3: {PASTEL['accent3']};
        --text: {PASTEL['text']};
        --muted: {PASTEL['muted']};
        --button: {PASTEL['button']};
    }}
    .stApp {{
        background: linear-gradient(180deg, var(--bg) 0%, white 100%);
        color: var(--text);
        font-family: "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif;
    }}
    .card {{
        background: var(--card);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    }}
    .accent {{
        background: var(--accent2);
        padding: 12px;
        border-radius: 12px;
    }}
    .big-title {{
        font-size: 28px;
        font-weight: 800;
    }}
    .muted {{
        color: var(--muted);
    }}
    /* 버튼 컬러 커스터마이즈(구형 스트림릿에서는 적용 안될 수 있음) */
    .stButton>button {{
        background: linear-gradient(90deg, var(--button), var(--accent1));
        border: none;
        padding: 10px 16px;
        border-radius: 12px;
        font-weight: 700;
    }}
    .small {{
        font-size: 13px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# App Header
# =========================
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<div class='big-title'>🍨 배스킨 라빈스 키오스크 — 주문을 시작할게요!</div>", unsafe_allow_html=True)
        st.markdown("<div class='muted small'>친절한 안내와 함께 편하게 주문하세요. 포인트/쿠폰은 데모에선 적용되지 않아요.</div>", unsafe_allow_html=True)
    with col2:
        st.metric(label="대기 예상 시간", value="2-4 분", delta="빠름 ✅")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")  # spacing

# =========================
# 주문 입력 섹션
# =========================
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("1) 이용 방식 선택 • 용기 선택 🍽️")
    left, right = st.columns(2)
    with left:
        usage = st.radio(
            "어떻게 드시나요?",
            options=["매장 식사 🧑‍🍳", "포장 테이크아웃 🥡"],
            index=0,
            help="매장 식사는 자리에서 바로 드시는 경우, 포장은 집으로 가져가는 경우입니다."
        )
        st.caption("필요 시 직원 호출 버튼을 눌러주세요. (데모)")
    with right:
        st.markdown("**용기(컨테이너)를 골라주세요**")
        # 용기 옵션을 상황에 맞게 필터링 (예: Pint는 포장만)
        container_options = []
        for k in CONTAINERS.keys():
            if "파인트" in k and usage.startswith("매장"):
                continue  # 파인트는 포장 전용으로 가정
            container_options.append(k)
        # 기본 선택
        cont_default_idx = 0
        container_choice = st.selectbox("용기 선택", options=container_options, index=cont_default_idx)
        st.markdown(f"<div class='muted small'>선택한 용기: {container_choice}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# =========================
# 맛 선택 섹션
# =========================
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("2) 아이스크림 맛 선택 🍨")
    max_scoops = CONTAINERS[container_choice]["max_scoops"]
    st.markdown(f"<div class='muted small'>이 용기에서는 최대 **{max_scoops}** 스쿱 선택 가능합니다.</div>", unsafe_allow_html=True)

    # 사용자가 선택 가능한 스쿱 수 지정 (슬IDER or selectbox)
    scoops = st.selectbox("몇 스쿱을 원하시나요?", options=list(range(1, max_scoops + 1)), index=min(1, max_scoops)-1)
    st.markdown("**아래에서 맛을 골라주세요.** 선택 가능한 개수만큼만 선택할 수 있습니다.")
    # multiselect with limit - implement client-side limit with helper
    chosen = st.multiselect(
        f"맛 선택 (최대 {scoops}개) — 클릭해서 골라보세요",
        options=list(FLAVORS.keys()),
        default=list(FLAVORS.keys())[:scoops]
    )
    # enforce limit: if user selected more than scoops, show warning and truncate visually
    if len(chosen) > scoops:
        st.warning(f"⚠️ 선택한 맛이 {scoops}개보다 많습니다. 처음 {scoops}개만 주문에 반영됩니다.")
        chosen = chosen[:scoops]

    # 보여주기: 선택 요약
    st.markdown("**선택한 맛 요약:**")
    for i, flavor in enumerate(chosen, start=1):
        st.markdown(f"- {i}. {flavor} — {FLAVORS[flavor]}")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# =========================
# 토핑 / 추가옵션
# =========================
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("3) 추가 옵션 (선택) ✨")
    col_t1, col_t2 = st.columns([1, 3])
    with col_t1:
        add_topping = st.checkbox("토핑 추가 (+₩500)", value=False)
    with col_t2:
        if add_topping:
            topping_count = st.number_input("토핑 개수", min_value=1, max_value=5, value=1, step=1)
            st.markdown("<div class='muted small'>토핑은 스프링클/초코시럽 등으로 가정합니다.</div>", unsafe_allow_html=True)
        else:
            topping_count = 0
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# =========================
# 결제 및 요약
# =========================
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("4) 결제 방식 선택 • 최종 확인 💳💵")
    colp1, colp2 = st.columns([2, 1])
    with colp1:
        payment_method = st.radio("결제 수단을 선택해 주세요", options=["현금 결제 💵", "카드 결제 💳"], index=1)
        note = ""
        if payment_method == "카드 결제 💳":
            note = "카드 결제 시 가상의 결제 수수료(0.5%)가 반영됩니다."
        else:
            note = "현금 결제 시 추가 수수료는 없습니다."
        st.caption(note)
    with colp2:
        # 주문 버튼 (시뮬레이션)
        confirm = st.button("결제 진행하기 🔒")
    # Price calculation & display
    breakdown = calc_price(scoops=scoops, container_key=container_choice, toppings_count=topping_count, payment_method=payment_method)

    st.markdown("### 주문 내역 요약")
    # Two-column summary + price breakdown
    sleft, sright = st.columns([2, 1])
    with sleft:
        st.markdown(f"- **이용 방식:** {usage}")
        st.markdown(f"- **용기:** {container_choice}")
        st.markdown(f"- **스쿱 수:** {scoops}개")
        st.markdown(f"- **맛:** {', '.join(chosen) if chosen else '선택 없음'}")
        st.markdown(f"- **토핑:** {'있음 ('+str(topping_count)+'개)' if topping_count>0 else '없음'}")
        st.markdown(f"- **결제 수단:** {payment_method}")
    with sright:
        st.metric(label="소계 (가격)", value=krw(breakdown["subtotal"]))
        st.markdown(f"- 부가세 (10%): {krw(breakdown['tax'])}")
        if breakdown["payment_surcharge"] > 0:
            st.markdown(f"- 결제 수수료 (카드 0.5%): {krw(breakdown['payment_surcharge'])}")
        st.markdown(f"### 최종 결제금액: **{krw(breakdown['total'])}**")

    # 작은 친절 문구
    st.markdown("<div class='muted small'>영수증은 결제 후 발행됩니다. 데모에서는 결제가 실제로 이루어지지 않습니다.</div>", unsafe_allow_html=True)

    # 결제 시 시뮬레이션 결과
    if confirm:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"결제가 완료되었습니다! 🎉 ({now})")
        st.markdown("#### 영수증")
        receipt_lines = [
            "===== 배스킨 라빈스 (데모 키오스크) =====",
            f"주문시간: {now}",
            f"이용: {usage}",
            f"용기: {container_choice}",
            f"스쿱: {scoops}개 — {' / '.join(chosen) if chosen else '선택 없음'}",
            f"토핑: {'있음 ('+str(topping_count)+'개)' if topping_count>0 else '없음'}",
            f"결제: {payment_method}",
            f"소계: {krw(breakdown['subtotal'])}",
            f"부가세: {krw(breakdown['tax'])}",
        ]
        if breakdown["payment_surcharge"] > 0:
            receipt_lines.append(f"결제수수료: {krw(breakdown['payment_surcharge'])}")
        receipt_lines.append(f"총계: {krw(breakdown['total'])}")
        receipt_text = "\n".join(receipt_lines)
        st.code(receipt_text, language=None)
        st.balloons()

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# 하단 도움말 / 피드백
# =========================
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("💡 팁: 더 나은 UX를 원하시면 이미지(맛 사진), POS 연동, 포인트/쿠폰 적용, 바코드 출력 등을 추가할 수 있어요.")
    st.markdown("원하시면 다음 작업을 도와드릴게요:")
    st.markdown("- 맛별 이미지 추가 및 썸네일 UI\n- 쿠폰/포인트 시스템 통합\n- 결제 게이트웨이(테스트) 연동 코드\n- 영수증 프린트용 PDF 또는 바코드 생성")
    st.markdown("</div>", unsafe_allow_html=True)
