import streamlit as st
import pandas as pd

# 제목
st.title("✈️ 인천공항 구역별 대기시간 예측")

# 데이터 로드
df = pd.read_csv("actual_vs_pred_improved.csv")

# 시간 컬럼 만들기 (time_index → HH:MM)
df["time"] = df["time_index"].apply(lambda x: f"{int(x//60):02d}:{int(x%60):02d}")

# ----------------------------
# 📌 사이드바 (선택 UI)
# ----------------------------
st.sidebar.header("조회 설정")

# 날짜 선택
dates = sorted(df["date"].unique())
selected_date = st.sidebar.selectbox("날짜 선택", dates)

# 시간 선택
times = sorted(df["time"].unique())
selected_time = st.sidebar.selectbox("시간 선택", times)

# ----------------------------
# 📌 데이터 필터링
# ----------------------------
filtered = df[
    (df["date"] == selected_date) &
    (df["time"] == selected_time)
]

# ----------------------------
# 📊 결과 출력
# ----------------------------
st.subheader(f"📊 {selected_date} / {selected_time} 대기시간")

# 필요한 컬럼만
result = filtered[[
    "area",
    "waiting_time",
    "pred",
]]

result = result.rename(columns={
    "area": "구역",
    "waiting_time": "실제 대기시간",
    "pred": "예측 대기시간"
})

st.dataframe(result.sort_values("구역"))

# ----------------------------
# 📈 오차 분석
# ----------------------------
st.subheader("📉 오차 분석")

filtered["error"] = filtered["pred"] - filtered["waiting_time"]
filtered["abs_error"] = abs(filtered["error"])

error_df = filtered[[
    "area",
    "waiting_time",
    "pred",
    "error",
    "abs_error"
]].rename(columns={
    "area": "구역",
    "waiting_time": "실제",
    "pred": "예측",
    "error": "오차",
    "abs_error": "절대오차"
})

st.dataframe(error_df.sort_values("절대오차", ascending=False))
