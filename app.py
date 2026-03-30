import streamlit as st
import pandas as pd

# ----------------------------
# 1️⃣ 데이터 불러오기
# ----------------------------
df = pd.read_csv("actual_vs_pred_final.csv")

# ----------------------------
# 2️⃣ 기본 설정
# ----------------------------
st.set_page_config(layout="wide")

st.title("✈️ 인천공항 구역별 대기시간 예측")

# ----------------------------
# 3️⃣ 날짜 선택 (09.01 형식)
# ----------------------------
df["date"] = df["date"].astype(str)

date_list = sorted(df["date"].unique())
date_map = {d: f"{d[:2]}.{d[2:]}" for d in date_list}

selected_date_display = st.selectbox(
    "날짜 선택",
    list(date_map.values())
)

# 다시 원래값으로 변환
selected_date = [k for k, v in date_map.items() if v == selected_date_display][0]

# ----------------------------
# 4️⃣ 시간 선택
# ----------------------------
df["time_str"] = df["time_index"].apply(
    lambda x: f"{(x-1)//60:02d}:{(x-1)%60:02d}"
)

time_list = sorted(df["time_str"].unique())

selected_time = st.selectbox("시간 선택", time_list)

# ----------------------------
# 5️⃣ 데이터 필터링
# ----------------------------
filtered = df[
    (df["date"] == selected_date) &
    (df["time_str"] == selected_time)
].copy()

# ----------------------------
# 6️⃣ 음수 제거
# ----------------------------
filtered["pred"] = filtered["pred"].clip(lower=0)

# ----------------------------
# 7️⃣ 혼잡도 라벨
# ----------------------------
def congestion_label(x):
    if x < 5:
        return "원활"
    elif x < 15:
        return "보통"
    else:
        return "혼잡"

filtered["혼잡도"] = filtered["pred"].apply(congestion_label)

# ----------------------------
# 8️⃣ 출력용 테이블
# ----------------------------
result = filtered[[
    "area", "waiting_time", "pred", "혼잡도"
]].rename(columns={
    "area": "구역",
    "waiting_time": "실제 대기시간",
    "pred": "예측 대기시간"
})

# ----------------------------
# 9️⃣ 출력
# ----------------------------
st.subheader(f"📊 {selected_date_display} / {selected_time} 대기시간")

st.dataframe(result, use_container_width=True)

# ----------------------------
# 🔟 오차 분석
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
