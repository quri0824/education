import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# --- 1. 페이지 설정 및 테마 적용 ---
st.set_page_config(page_title="서울 서남권 교육 분석", layout="wide")

# CSS를 활용한 아이보리 & 파스텔 핑크 테마 적용
st.markdown("""
    <style>
    /* 전체 배경색: 아이보리 */
    .stApp {
        background-color: #FFFDF5;
    }
    /* 제목 및 헤더 색상: 파스텔 핑크 */
    h1, h2, h3 {
        color: #FFB7B2 !important;
    }
    /* 인사이트 박스 스타일 */
    .insight-box {
        background-color: #FFE4E1; /* 파스텔 핑크 배경 */
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FFB7B2;
        margin-bottom: 20px;
        color: #5D5D5D;
    }
    .insight-title {
        font-weight: bold;
        color: #FF8B94;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 데이터베이스 연결 ---
DB_FILE = "education.db"

def run_query(query):
    if not os.path.exists(DB_FILE):
        return None
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query(query, conn)

# DB 파일 미존재 시 에러 처리
if not os.path.exists(DB_FILE):
    st.error("🚨 데이터베이스 파일을 찾을 수 없습니다. 'education.db' 파일 위치를 확인해주세요!")
    st.stop()

# --- 타이틀 영역 ---
st.title("서울시 서남권 사교육 & 공공 교육 대시보드")
st.markdown("---")

# ---------------------------------------------------------
# 차트 1: 자치구별 학원 밀집도
# ---------------------------------------------------------
st.header("📊 차트 1: 자치구별 학원 밀집도")
sql1 = """
SELECT 행정구역명, COUNT(*) AS 학원수 
FROM 교습소정보 GROUP BY 행정구역명 ORDER BY 학원수 DESC
"""
df1 = run_query(sql1)

fig1 = px.bar(df1, x='행정구역명', y='학원수', color='행정구역명', text_auto=True,
             color_discrete_sequence=px.colors.qualitative.Pastel)
st.plotly_chart(fig1, use_container_width=True)

# 인사이트 박스
st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">💡 분석 인사이트</div>
        <ul>
            <li><b>분석 전 예상:</b> 목동이 포함된 양천구가 가장 많겠지만, 다른 구들과의 차이가 아주 크지는 않을 것이다.</li>
            <li><b>실제 결과:</b> 양천구(2,109개)가 2위인 강서구(1,381개)보다도 약 1.5배 이상 많으며, 최하위인 금천구(369개)와는 약 5.7배라는 압도적인 격차를 보임.</li>
            <li><b>인사이트:</b> 사교육의 지역 편중이 매우 심화되어 있으며, 이는 해당 지역의 입시 열망과 사교육비 지출 의지를 직접적으로 반영함.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with st.expander("🔍 사용한 SQL문 보기"):
    st.code(sql1, language='sql')

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 차트 2: 학원 수와 도서관 이용자 수의 관계
# ---------------------------------------------------------
st.header("📈 차트 2: 학원 수와 도서관 이용자 수의 관계")
sql2 = """
SELECT A.행정구역명, COUNT(DISTINCT A.학원명) AS 학원수, B.도서관이용자수
FROM 교습소정보 A JOIN 이용자현황 B ON A.행정구역명 = B.행정구역명
GROUP BY A.행정구역명
"""
df2 = run_query(sql2)

fig2 = px.scatter(df2, x='학원수', y='도서관이용자수', color='행정구역명',
                 size='학원수', text='행정구역명',
                 color_discrete_sequence=px.colors.qualitative.Pastel)
fig2.update_traces(textposition='top center')
st.plotly_chart(fig2, use_container_width=True)

# 인사이트 박스
st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">💡 분석 인사이트</div>
        <ul>
            <li><b>분석 전 예상:</b> 학원이 많은 곳은 공공시설인 도서관은 오히려 덜 이용하지 않을까? (반비례 예상)</li>
            <li><b>실제 결과:</b> 학원 수가 많은 구일수록 도서관 이용자 수도 비례해서 증가하는 '양(+)의 상관관계'가 관찰됨.</li>
            <li><b>인사이트:</b> 교육 인프라의 동반 상승 효과로 인해 교육 환경이 좋은 곳과 부족한 곳 사이의 '전체적인 교육 에너지 격차'가 커지고 있음.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with st.expander("🔍 사용한 SQL문 보기"):
    st.code(sql2, language='sql')

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 차트 3: 자치구별 박물관 보유 현황 (LEFT JOIN)
# ---------------------------------------------------------
st.header("🏛️ 차트 3: 자치구별 박물관 보유 현황")
sql3 = """
SELECT 
    A.행정구역명, 
    COUNT(DISTINCT M.시설명) AS 박물관수
FROM (SELECT DISTINCT 행정구역명 FROM "교습소정보") A
LEFT JOIN "박물관미술관정보" M ON A.행정구역명 = M.행정구역명
GROUP BY A.행정구역명
ORDER BY 박물관수 DESC;
"""
df3 = run_query(sql3)

# 단일 색상(파스텔 핑크 계열) 및 범례 제거
fig3 = px.bar(df3, x='박물관수', y='행정구역명', orientation='h', text_auto=True)
fig3.update_traces(marker_color='#FFB7B2') # 파스텔 핑크 단일화
fig3.update_layout(showlegend=False) # 범례 제거

st.plotly_chart(fig3, use_container_width=True)

# 인사이트 박스
st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">💡 분석 인사이트</div>
        <ul>
            <li><b>분석 전 예상:</b> 학원이 많은 강서구나 양천구는 박물관도 골고루 많을 것이다.</li>
            <li><b>실제 결과:</b> 학원 수와 박물관 수는 일치하지 않음. 일부 자치구는 박물관이 0개로 나타나 문화적 자본의 부족이 확인됨.</li>
            <li><b>인사이트:</b> 박물관이 부족한 지역에 공공 문화 인프라를 우선 확충하여 '문화적 교육 결핍'를 해소할 필요가 있음.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with st.expander("🔍 사용한 SQL문 보기"):
    st.code(sql3, language='sql')

st.markdown("---")
st.caption("Seoul Southwest Education Analysis Dashboard | Theme: Ivory & Pastel Pink")
