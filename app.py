import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("✈️ 인천공항 구역별 대기시간 예측")

# ----------------------------
# 데이터 로드
# ----------------------------
df = pd.read_csv("streamlit_service_data.csv")

# ----------------------------
# 날짜 (절대 건드리지 않음 🔥)
# ----------------------------
df["date"] = df["date"].astype(str)

# ----------------------------
# 시간 변환 (1~1440 → 00:00~23:59)
# ----------------------------
df["time_str"] = df["time_index"].apply(
    lambda x: f"{(int(x)-1)//60:02d}:{(int(x)-1)%60:02d}"
)

# ----------------------------
# 선택 UI
# ----------------------------
date_list = sorted(df["date"].unique())
selected_date = st.selectbox("날짜 선택", date_list)

time_list = sorted(df[df["date"] == selected_date]["time_str"].unique())
selected_time = st.selectbox("시간 선택", time_list)

# ----------------------------
# 필터링
# ----------------------------
filtered = df[
    (df["date"] == selected_date) &
    (df["time_str"] == selected_time)
].copy()

# ----------------------------
# 데이터 없으면 안내
# ----------------------------
if filtered.empty:
    st.warning("해당 시간 데이터 없음")
else:
    # 음수 제거
    filtered["pred"] = filtered["pred"].clip(lower=0)

    # 혼잡도
    def congestion(x):
        if x < 5:
            return "🟢 원활"
        elif x < 15:
            return "🟡 보통"
        else:
            return "🔴 혼잡"

    filtered["혼잡도"] = filtered["pred"].apply(congestion)

    # 분 단위 표시
    filtered["실제"] = filtered["waiting_time"].round(2).astype(str) + "분"
    filtered["예측"] = filtered["pred"].round(2).astype(str) + "분"

    # 정렬 (구역 순)
    filtered = filtered.sort_values("area")

    st.subheader(f"📊 {selected_date} / {selected_time}")

    st.dataframe(
        filtered[["area", "실제", "예측", "혼잡도"]]
        .rename(columns={"area": "구역"}),
        use_container_width=True
    )

    # ----------------------------
    # 오차 분석
    # ----------------------------
    filtered["오차"] = (filtered["pred"] - filtered["waiting_time"]).round(2)
    filtered["절대오차"] = filtered["오차"].abs()

    st.subheader("📉 오차 분석")

    st.dataframe(
        filtered[["area", "waiting_time", "pred", "오차", "절대오차"]]
        .rename(columns={
            "area": "구역",
            "waiting_time": "실제",
            "pred": "예측"
        }),
        use_container_width=True
    )
