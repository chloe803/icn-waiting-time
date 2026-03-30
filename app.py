import streamlit as st
import pandas as pd

st.title("✈️ 인천공항 구역별 대기시간 예측")

df = pd.read_csv("actual_vs_pred_improved.csv")

# ----------------------------
# ✅ 날짜 강제 생성 (0901~0905)
# ----------------------------
df["day"] = (df["time_index"] // 1440) + 1
df["date"] = df["day"].apply(lambda x: f"09.{x:02d}")

# ----------------------------
# ✅ 시간 생성
# ----------------------------
df["time"] = df["time_index"] % 1440
df["time"] = df["time"].apply(lambda x: f"{x//60:02d}:{x%60:02d}")

# ----------------------------
# ✅ 음수 제거
# ----------------------------
df["pred"] = df["pred"].clip(lower=0)

# ----------------------------
# 📌 사이드바
# ----------------------------
st.sidebar.header("조회 설정")

dates = sorted(df["date"].unique())
selected_date = st.sidebar.selectbox("날짜 선택", dates)

times = sorted(df["time"].unique())
selected_time = st.sidebar.selectbox("시간 선택", times)

# ----------------------------
# 📌 필터링
# ----------------------------
filtered = df[
    (df["date"] == selected_date) &
    (df["time"] == selected_time)
]

# ----------------------------
# 📊 출력
# ----------------------------
st.subheader(f"📊 {selected_date} / {selected_time} 대기시간")

result = filtered[[
    "area",
    "waiting_time",
    "pred"
]].rename(columns={
    "area": "구역",
    "waiting_time": "실제 대기시간",
    "pred": "예측 대기시간"
})

st.dataframe(result.sort_values("구역"))

# ----------------------------
# 📉 오차 분석
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
