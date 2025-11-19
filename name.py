import streamlit as st
import pandas as pd
import altair as alt
import io

# 1. 데이터 정의
# 원본 데이터가 붙여넣기 과정에서 형식이 깨졌습니다.
# 올바른 TSV (탭으로 구분) 형식으로 몇 개의 샘플 데이터를 재구성했습니다.
# 전체 데이터를 사용하려면 이 문자열에 모든 국가를 동일한 형식으로 추가해야 합니다.
data_string = """Country	INFJ	ISFJ	INTP	ISFP	ENTP	INFP	ENTJ	ISTP	INTJ	ESFP	ESTJ	ENFP	ESTP	ISTJ	ENFJ	ESFJ
Afghanistan	0.0463	0.061	0.0549	0.046	0.0495	0.0686	0.0511	0.0434	0.0431	0.0527	0.1188	0.0796	0.0652	0.0629	0.0562	0.1006
Albania	0.0748	0.0449	0.0754	0.0334	0.0792	0.1045	0.0686	0.0233	0.0604	0.0405	0.0667	0.1045	0.0381	0.0418	0.0775	0.0665
Algeria	0.08	0.0337	0.141	0.0377	0.0739	0.1556	0.0535	0.033	0.0896	0.0279	0.0327	0.0857	0.0241	0.032	0.0556	0.044
Andorra	0.0791	0.0465	0.0512	0.0419	0.0372	0.1674	0.0465	0.0186	0.0326	0.0372	0.0605	0.1767	0.0187	0.0279	0.1163	0.0651
Angola	0.0771	0.0717	0.0564	0.0403	0.0448	0.1112	0.0492	0.0322	0.0466	0.0547	0.0592	0.0798	0.0368	0.0404	0.0807	0.1192
Antigua and Barbuda	0.0848	0.0853	0.0632	0.0592	0.047	0.1381	0.0279	0.0308	0.0328	0.0548	0.0421	0.1092	0.0245	0.0431	0.0632	0.094
Argentina	0.0884	0.044	0.106	0.0416	0.0544	0.1875	0.0309	0.0255	0.0652	0.0366	0.0245	0.1338	0.0174	0.0342	0.0625	0.0476
"""

# 2. 데이터 로드 함수 (캐싱 사용)
@st.cache_data
def load_data():
    """
    문자열 데이터를 읽어 Pandas DataFrame으로 변환합니다.
    """
    data = io.StringIO(data_string)
    # 탭으로 구분된(sep='\t') 데이터를 읽어옵니다.
    df = pd.read_csv(data, sep='\t')
    # 'Country' 열을 인덱스로 설정하여 나중에 쉽게 조회할 수 있도록 합니다.
    df = df.set_index('Country')
    return df

# 3. Streamlit 앱 메인 함수
def main():
    st.set_page_config(layout="wide")
    st.title("🌍 국가별 MBTI 성격 유형 분포")

    try:
        df = load_data()
        
        # 16가지 MBTI 유형 (차트 순서 고정용)
        mbti_types = df.columns.tolist()

        # 4. 국가 선택 (사이드바)
        st.sidebar.header("국가 선택")
        country_list = df.index.tolist()
        selected_country = st.sidebar.selectbox(
            "분포를 확인할 국가를 선택하세요:",
            country_list
        )

        # 5. 선택된 국가의 데이터 처리
        st.header(f"'{selected_country}'의 MBTI 분포")
        country_data = df.loc[selected_country]
        
        # Altair 차트를 위한 데이터 프레임으로 변환
        chart_data = country_data.reset_index()
        chart_data.columns = ['MBTI', '분포율']

        # 6. 막대 그래프 생성 (Altair)
        chart = alt.Chart(chart_data).mark_bar().encode(
            # X축: MBTI 유형 (원본 순서대로 정렬)
            x=alt.X('MBTI', sort=mbti_types),
            
            # Y축: 분포율
            y=alt.Y('분포율', axis=alt.Axis(format='%')), # Y축 서식을 퍼센트로
            
            # 마우스를 올리면 정보 표시
            tooltip=[
                alt.Tooltip('MBTI', title='유형'),
                alt.Tooltip('분포율', title='비율', format='.2%') # 툴팁 서식도 퍼센트로
            ]
        ).properties(
            title=f"{selected_country} MBTI 분포"
        ).interactive() # 차트 확대/축소 가능

        # 7. 차트 표시
        st.altair_chart(chart, use_container_width=True)

        # 8. 원본 데이터 표시 (선택 사항)
        if st.checkbox(f"'{selected_country}'의 원본 데이터 보기"):
            st.dataframe(chart_data.set_index('MBTI').style.format({'분포율': '{:.2%}'}))

    except Exception as e:
        st.error(f"데이터를 로드하는 중 오류가 발생했습니다: {e}")
        st.info("app.py 파일의 'data_string' 변수에 올바른 형식의 데이터가 포함되어 있는지 확인하세요.")

if __name__ == "__main__":
    main()
