import streamlit as st
import pandas as pd

st.title("인천공항 대기시간 예측")

df = pd.read_csv("actual_vs_pred_improved.csv")

st.write(df.head())
