import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# --- 1. 페이지 설정 및 제목 ---
st.set_page_config(page_title="서울 서남권 교육 데이터 분석", layout="wide")
st.title("🎓 서울시 서남권 사교육 & 공공 교육 대시보드")
st.markdown("이 대시보드는 지역별 학원 밀집도와 공공 시설(도서관, 박물관)의 관계를 분석합니다.")

# --- 2. 데이터베이스 연결 확인 ---
DB_FILE = "education.db"

if not os.path.exists(DB_FILE):
    # 데이터베이스 파일이 없을 경우 친절한 에러 메시지 표시
    st.error("🚨 데이터베이스 파일을 찾을 수 없습니다. 파일 위치를 확인해주세요!")
    st.stop()  # 프로그램 중단

# 데이터베이스 연결 함수 (캐싱을 통해 성능 향상)
@st.cache_data
def load_data(query):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --- 3. 차트 1: 지역별 학원 수 밀집도 ---
st.header("1. 지역별 학원 수 밀집도")
# SQL 설명: 교습소정보 테이블에서 행정구역별로 학원 이름을 카운트합니다.
query1 = """
SELECT 
    행정구역명, 
    COUNT(학원명) AS 학원수 
FROM 교습소정보 
GROUP BY 행정구역명 
ORDER BY 학원수 DESC
"""
df_academy = load_data(query1)

# 시각화 (세로 막대 차트)
fig1 = px.bar(df_academy, x='행정구역명', y='학원수', 
             color='학원수', title="행정구역별 학원 수 현황",
             labels={'학원수': '학원 수(개)', '행정구역명': '지역구'},
             text_auto=True)
st.plotly_chart(fig1, use_container_width=True)

with st.expander("사용한 SQL 쿼리 보기"):
    st.code(query1, language='sql')


# --- 4. 차트 2: 사교육과 공공시설의 관계 (산점도) ---
st.header("2. 사교육(학원)과 공공시설(도서관)의 상관관계")
# SQL 설명: 교습소정보와 이용자현황을 JOIN하여 지역별 학원수와 도서관 이용자수를 가져옵니다.
query2 = """
SELECT 
    A.행정구역명,
    COUNT(DISTINCT A.학원명) AS 학원수,
    B.도서관이용자수
FROM "교습소정보" A
JOIN "이용자현황" B ON A.행정구역명 = B.행정구역명
GROUP BY A.행정구역명
"""
df_relation = load_data(query2)

# 시각화 (산점도)
fig2 = px.scatter(df_relation, x='학원수', y='도서관이용자수', 
                 text='행정구역명', size='학원수', color='도서관이용자수',
                 title="학원 수와 도서관 이용자 수의 관계",
                 labels={'학원수': '학원 수(개)', '도서관이용자수': '도서관 이용자 수(명)'})
fig2.update_traces(textposition='top center')
st.plotly_chart(fig2, use_container_width=True)

with st.expander("사용한 SQL 쿼리 보기"):
    st.code(query2, language='sql')


# --- 5. 차트 3: 공공 교육 인프라 현황 (박물관/미술관) ---
st.header("3. 지역별 공공 교육 인프라(박물관) 현황")
# SQL 설명: 요청하신 구조를 참고하여 LEFT JOIN을 통해 박물관 유무와 개수를 파악합니다.
query3 = """
SELECT 
    A.행정구역명,
    COUNT(DISTINCT M.시설명) AS 박물관수,
    CASE 
        WHEN COUNT(DISTINCT M.시설명) > 0 THEN '있음'
        ELSE '없음'
    END AS 박물관유무
FROM "교습소정보" A
LEFT JOIN "박물관미술관정보" M ON A.행정구역명 = M.행정구역명
GROUP BY A.행정구역명
ORDER BY 박물관수 DESC
"""
df_museum = load_data(query3)

# 시각화 (가로 막대 차트 및 표)
col1, col2 = st.columns([2, 1])

with col1:
    fig3 = px.bar(df_museum, y='행정구역명', x='박물관수', 
                 color='박물관유무', orientation='h',
                 title="지역별 박물관/미술관 개수",
                 labels={'박물관수': '시설 수(개)', '행정구역명': '지역구'},
                 color_discrete_map={'있음': '#31333F', '없음': '#EF553B'})
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.write("데이터 요약")
    st.dataframe(df_museum, hide_index=True)

with st.expander("사용한 SQL 쿼리 보기"):
    st.code(query3, language='sql')

st.caption("데이터 출처: 서울시 공공데이터 (서남권 중심)")