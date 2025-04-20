import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import date
import json

# 구글 API 인증 (Streamlit secrets 사용)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# # local test
# creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
# client = gspread.authorize(creds)
# secrets.toml의 JSON 객체 불러오기
creds_dict = st.secrets["gcp_service_account"]
creds_json = json.loads(json.dumps(creds_dict))

# gspread에 인증 정보 전달
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(credentials)

# 시트 불러오기
spreadsheet = client.open("휴가근태관리")
sheet_usage = spreadsheet.worksheet("휴가사용률")
sheet_log = spreadsheet.worksheet("휴가사용내역")

# 데이터 프레임으로 변환
df_usage = pd.DataFrame(sheet_usage.get_all_records())
df_log = pd.DataFrame(sheet_log.get_all_records())

# Streamlit UI 시작
st.set_page_config(page_title="휴가 및 근태 관리", layout="wide")
st.title("🏖️ 휴가 및 근태 관리 시스템")

# ---------------------- 화면 1: 휴가 사용률 --------------------------
st.header("📊 휴가 사용률 조회")

# 필터 선택
names = df_usage["직원이름"].unique().tolist()
positions = df_usage["직급"].unique().tolist()

col1, col2 = st.columns(2)
selected_name = col1.selectbox("직원이름", ["전체"] + names)
selected_position = col2.selectbox("직급", ["전체"] + positions)

# 필터링
df_filtered = df_usage.copy()
if selected_name != "전체":
    df_filtered = df_filtered[df_filtered["직원이름"] == selected_name]
if selected_position != "전체":
    df_filtered = df_filtered[df_filtered["직급"] == selected_position]

# 직원번호 제외 후 출력
st.dataframe(df_filtered.drop(columns=["직원번호"]), use_container_width=True)

# ---------------------- 화면 2: 휴가 등록 --------------------------
st.header("📝 휴가 등록")

# 입력 폼
with st.form("vacation_form"):
    col1, col2 = st.columns(2)
    input_name = col1.selectbox("직원이름", names)
    input_position = col2.selectbox("직급", positions)
    col3, col4 = st.columns(2)
    input_date = col3.date_input("휴가일", date.today())
    input_type = col4.selectbox("휴가유형", ["연차", "반차"])
    
    submitted = st.form_submit_button("휴가 등록")

if submitted:
# 직원번호를 찾아서 가져오기 (있으면)
    emp_row = df_usage[df_usage["직원이름"] == input_name]
    if not emp_row.empty:
        emp_id = str(emp_row.iloc[0]["직원번호"])  # ← int64를 str로 변환
    else:
        emp_id = ""

    # 날짜도 string으로 변환
    new_row = [
        emp_id,
        str(input_name),
        str(input_position),
        input_date.strftime("%Y-%m-%d"),  # 날짜도 문자열로
        str(input_type)
    ]

    sheet_log.append_row(new_row)

    st.success(f"{input_name}님의 휴가가 등록되었습니다.")

# ---------------------- 화면 3: 휴가 사용 내역 보기 --------------------------
st.header("📅 휴가 사용 내역")

# 필요한 컬럼만 추출
df_log_view = df_log[["직원이름", "직급", "휴가일", "휴가유형"]].copy()
df_log_view["휴가일"] = pd.to_datetime(df_log_view["휴가일"], errors="coerce")

# 필터 UI
col1, col2, col3, col4 = st.columns(4)
filter_name = col1.selectbox("직원이름", ["전체"] + sorted(df_log_view["직원이름"].unique()))
filter_position = col2.selectbox("직급", ["전체"] + sorted(df_log_view["직급"].unique()))
filter_type = col3.selectbox("휴가유형", ["전체"] + sorted(df_log_view["휴가유형"].unique()))
date_start, date_end = col4.date_input("휴가일 범위", [df_log_view["휴가일"].min().date(), df_log_view["휴가일"].max().date()])

# 필터 적용
if filter_name != "전체":
    df_log_view = df_log_view[df_log_view["직원이름"] == filter_name]
if filter_position != "전체":
    df_log_view = df_log_view[df_log_view["직급"] == filter_position]
if filter_type != "전체":
    df_log_view = df_log_view[df_log_view["휴가유형"] == filter_type]
df_log_view = df_log_view[
    (df_log_view["휴가일"].dt.date >= date_start) &
    (df_log_view["휴가일"].dt.date <= date_end)
]

# 포맷
df_log_view["휴가일"] = df_log_view["휴가일"].dt.strftime("%Y-%m-%d")
df_log_view = df_log_view.sort_values(by="휴가일", ascending=False)

# 출력
st.dataframe(df_log_view, use_container_width=True)
