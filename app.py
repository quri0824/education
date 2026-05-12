import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="서울 서남권 교육 데이터 분석", layout="wide")

# --- 2. 데이터베이스 파일 존재 확인 ---
DB_FILE = "education.db"

if not os.path.exists(DB_FILE):
    st.error("🚨 'education.db' 파일을 찾을 수 없습니다. 파일이 같은 폴더에 있는지 확인해주세요!")
    st.stop()

# --- 3. 데이터 로드 함수 ---
def run_query(query):
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query(query, conn)

st.title("🎓 서울시 서남권 교육 & 인프라 분석 대시보드")
st.markdown("지역별 사교육 밀집도와 공공 교육 인프라의 현황을 한눈에 확인하세요.")

# ---------------------------------------------------------
# 차트 1: 지역별 학원 수 밀집도 (세로 막대, 범례 있음)
# ---------------------------------------------------------
st.header("1. 지역별 학원 수 밀집도")
sql1 = """
SELECT 
    행정구역명, 
    COUNT(*) AS 학원수 
FROM 교습소정보 
GROUP BY 행정구역명 
ORDER BY 학원수 DESC
"""
df1 = run_query(sql1)

# color='행정구역명'을 넣어 범례가 나타나도록 설정했습니다.
fig1 = px.bar(df1, x='행정구역명', y='학원수', 
             color='행정구역명', 
             text_auto=True,
             title="행정구역별 학원(교습소) 수 현황",
             labels={'학원수': '학원 수(개)', '행정구역명': '지역구'})

st.plotly_chart(fig1, use_container_width=True)

with st.expander("📝 사용한 SQL문 보기"):
    st.code(sql1, language='sql')


# ---------------------------------------------------------
# 차트 2: 사교육과 공공시설의 관계 (산점도, 범례 있음)
# ---------------------------------------------------------
st.header("2. 사교육과 공공시설의 관계")
sql2 = """
SELECT 
    A.행정구역명,
    COUNT(DISTINCT A.학원명) AS 학원수,
    B.도서관이용자수
FROM 교습소정보 A
JOIN 이용자현황 B ON A.행정구역명 = B.행정구역명
GROUP BY A.행정구역명
"""
df2 = run_query(sql2)

# color='행정구역명'을 넣어 각 점이 어떤 구인지 범례에 표시되도록 했습니다.
fig2 = px.scatter(df2, x='학원수', y='도서관이용자수', 
                 color='행정구역명',
                 size='학원수', 
                 text='행정구역명',
                 title="학원 수와 도서관 이용자 수의 상관관계",
                 labels={'학원수': '학원 수(개)', '도서관이용자수': '도서관 이용자 수(명)'})

fig2.update_traces(textposition='top center')
st.plotly_chart(fig2, use_container_width=True)

with st.expander("📝 사용한 SQL문 보기"):
    st.code(sql2, language='sql')


# ---------------------------------------------------------
# 차트 3: 자치구별 공공 교육 인프라 현황 (가로 막대, 범례 없음)
# ---------------------------------------------------------
st.header("3. 자치구별 공공 교육 인프라 현황")
# LEFT JOIN을 사용하여 박물관이 0개인 구도 포함하는 쿼리입니다.
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

# 단일 색상으로 설정하고 범례를 제거합니다.
fig3 = px.bar(df3, x='박물관수', y='행정구역명', 
             orientation='h',
             text_auto=True, 
             title="자치구별 박물관/미술관 보유 수",
             labels={'박물관수': '시설 수(개)', '행정구역명': '지역구'})

# 3번째 차트만 범례를 숨기고 막대 색상을 하나로 고정합니다.
fig3.update_layout(showlegend=False) 
fig3.update_traces(marker_color='#4E79A7') # 차분한 파란색 단일화

st.plotly_chart(fig3, use_container_width=True)

with st.expander("📝 사용한 SQL문 보기"):
    st.code(sql3, language='sql')

st.caption("데이터 분석 도구: Streamlit & SQLite | 작성자: 시니어 개발자")
