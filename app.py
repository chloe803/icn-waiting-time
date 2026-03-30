import streamlit as st
import pandas as pd

# ----------------------------
# 1️⃣ 데이터
# ----------------------------
df = pd.read_csv("actual_vs_pred_final.csv")

st.set_page_config(layout="wide")
st.title("✈️ 인천공항 구역별 대기시간 예측")

# ----------------------------
# 2️⃣ 날짜 처리 (09.01)
# ----------------------------
df["date"] = df["date"].astype(str)

# 0901 형태로 맞추기
df["date"] = df["date"].apply(lambda x: x.zfill(4))

df["date_display"] = df["date"].apply(lambda x: f"{x[:2]}.{x[2:]}")

date_list = sorted(df["date"].unique())
date_display_list = [f"{d[:2]}.{d[2:]}" for d in date_list]

selected_date_display = st.selectbox("날짜 선택", date_display_list)

selected_date = selected_date_display.replace(".", "")

# ----------------------------
# 3️⃣ 시간 처리 (핵심🔥)
# ----------------------------
# time_index = 1 ~ 1440 (이미 1분 단위)

df["time_str"] = df["time_index"].apply(
    lambda x: f"{(x-1)//60:02d}:{(x-1)%60:02d}"
)

# 24시간까지만 제한
df = df[df["time_index"] <= 1440]

time_list = sorted(df["time_str"].unique())

selected_time = st.selectbox("시간 선택", time_list)

# ----------------------------
# 4️⃣ 전체 구역 확보 (고정)
# ----------------------------
all_areas = [
    "GH","A","B","C","D","E","F","G","H",
    "IM1","IM2","J","K","L","M","N","Outside"
]

filtered = df[
    (df["date"] == selected_date) &
    (df["time_str"] == selected_time)
]

# 전체 구역 기준으로 맞추기
filtered = filtered.set_index("area").reindex(all_areas).reset_index()

# ----------------------------
# 5️⃣ 결측 처리
# ----------------------------
filtered["waiting_time"] = filtered["waiting_time"].fillna(0)
filtered["pred"] = filtered["pred"].fillna(0)

# ----------------------------
# 6️⃣ 분 단위 표시
# ----------------------------
def format_min(x):
    return f"{round(x,2)}분"

filtered["실제"] = filtered["waiting_time"].apply(format_min)
filtered["예측"] = filtered["pred"].apply(format_min)

# ----------------------------
# 7️⃣ 혼잡도
# ----------------------------
def congestion(x):
    if x < 5:
        return "원활"
    elif x < 15:
        return "보통"
    else:
        return "혼잡"

filtered["혼잡도"] = filtered["pred"].apply(congestion)

# ----------------------------
# 8️⃣ 출력
# ----------------------------
st.subheader(f"📊 {selected_date_display} / {selected_time} 대기시간")

result = filtered[["area", "실제", "예측", "혼잡도"]]
result = result.rename(columns={"area": "구역"})

st.dataframe(result, use_container_width=True)

# ----------------------------
# 9️⃣ 오차 분석
# ----------------------------
filtered["오차"] = filtered["pred"] - filtered["waiting_time"]
filtered["절대오차"] = abs(filtered["오차"])

error_df = filtered[[
    "area", "waiting_time", "pred", "오차", "절대오차"
]].rename(columns={
    "area": "구역",
    "waiting_time": "실제",
    "pred": "예측"
})

st.subheader("📉 오차 분석")
st.dataframe(error_df, use_container_width=True)
