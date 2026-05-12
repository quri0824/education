import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="서울 서남권 교육 데이터 분석", layout="wide")

# --- 데이터베이스 연결 함수 ---
DB_FILE = "education.db"

def run_query(query):
    """SQL 쿼리를 실행하여 판다스 데이터프레임으로 반환합니다."""
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query(query, conn)

# --- 1. DB 파일 존재 확인 ---
if not os.path.exists(DB_FILE):
    st.error("🚨 데이터베이스 파일을 찾을 수 없습니다. 'education.db' 파일이 같은 폴더에 있는지 확인해주세요!")
    st.stop()

st.title("🎓 서울시 서남권 사교육 및 공공 교육 분석")
st.write("본 대시보드는 서울 서남권 지역의 학원 현황과 공공 교육 인프라의 관계를 보여줍니다.")

# --- 차트 1: 지역별 학원 수 밀집도 ---
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
fig1 = px.bar(df1, x='행정구역명', y='학원수', text_auto=True,
             title="행정구역별 학원(교습소) 수 현황",
             labels={'학원수': '학원 수(개)'})
st.plotly_chart(fig1, use_container_width=True)

with st.expander("📝 사용한 SQL문 보기"):
    st.code(sql1, language='sql')


# --- 차트 2: 사교육과 공공시설의 관계 (산점도) ---
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
fig2 = px.scatter(df2, x='학원수', y='도서관이용자수', text='행정구역명',
                 size='학원수', title="학원 수와 도서관 이용자 수의 상관관계",
                 labels={'학원수': '학원 수(개)', '도서관이용자수': '도서관 이용자 수(명)'})
fig2.update_traces(textposition='top center')
st.plotly_chart(fig2, use_container_width=True)

with st.expander("📝 사용한 SQL문 보기"):
    st.code(sql2, language='sql')


# --- 차트 3: 자치구별 공공 교육 인프라 현황 (박물관) ---
st.header("3. 자치구별 공공 교육 인프라 현황")
# 요청하신 특수 SQL 구조 반영 (LEFT JOIN으로 0개 지역 포함)
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

# 가로 막대 차트 시각화 (단일 색상, 범례 제거)
fig3 = px.bar(df3, x='박물관수', y='행정구역명', orientation='h',
             text_auto=True, title="자치구별 박물관/미술관 보유 수",
             labels={'박물관수': '시설 수(개)', '행정구역명': '지역구'})

# 범례(Legend) 제거 및 막대 색상 통일
fig3.update_layout(showlegend=False) 
fig3.update_traces(marker_color='#636EFA') # 깔끔한 파란색 계열 단일화

st.plotly_chart(fig3, use_container_width=True)

with st.expander("📝 사용한 SQL문 보기"):
    st.code(sql3, language='sql')
