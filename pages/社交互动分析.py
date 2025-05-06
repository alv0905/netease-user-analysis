import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

import plotly.express as px  # 用于平行分类图

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def render():
    st.title("💬 社交互动分析")

    # CSV 文件路径
    basic_info_path = "E:/Netease_analysis/data/basic_info.csv"
    social_info_path = "E:/Netease_analysis/data/social_info.csv"
    listening_path = "E:/Netease_analysis/data/listening_records.csv"
    playlist_path = "E:/Netease_analysis/data/playlist_info.csv"

    # 加载&合并数据
    df = load_and_merge_data(basic_info_path, social_info_path, listening_path, playlist_path)
    if df is None or df.empty:
        st.error("❌ 无法加载或合并数据，请检查文件路径")
        return

    st.subheader("合并后的社交数据（前100行）")
    st.dataframe(df.head(100))

    # ========== 1) 高级回归图 ==========
    st.subheader("线性回归 - 预测粉丝数")
    reg_fig = fanscount_regression(df)
    st.pyplot(reg_fig)
    # 在图下方添加文字说明
    st.markdown("""
    **说明**：这里采用了线性回归模型，试图用用户的“等级(level)”与“关注数(follows_count)”两个变量来预测粉丝数(fans_count)。
    我们将样本随机分为训练集与测试集，并在图中对比“实际粉丝数”与“预测粉丝数”。  
    越靠近红色对角线，表示预测越准确。图中显示的 R²（决定系数）也能量化模型拟合度。
    """)

    # ========== 2) 平行分类图 ==========
    st.subheader("平行分类图 (Parallel Categories)")
    fig_pc = render_parallel_categories(df)
    if fig_pc:
        st.plotly_chart(fig_pc, use_container_width=True)
        st.markdown("""
        **说明**：平行分类图可同时展示用户在多个离散化维度的分布情况。例如，我们把等级、粉丝数、关注数、地区、性别
        等字段转为分类区间，然后将其在同一个图中并列显示。每条“流线”代表一个用户在各维度上的取值组合，
        线越粗表示该组合出现次数越多。这样能直观看出不同维度之间的关联结构。
        """)
    else:
        st.warning("无法生成平行分类图，可能可用数据不足。")

@st.cache_data
def load_and_merge_data(basic_path, social_path, listen_path, playlist_path):
    if (not os.path.exists(basic_path)) or (not os.path.exists(social_path)):
        return None

    try:
        basic_df = pd.read_csv(basic_path)
        social_df = pd.read_csv(social_path)
        if os.path.exists(listen_path):
            listen_df = pd.read_csv(listen_path)
            listen_agg = listen_df.groupby("user_id", as_index=False)["playCount"].sum()
            listen_agg.rename(columns={"playCount": "total_plays"}, inplace=True)
        else:
            listen_agg = pd.DataFrame(columns=["user_id", "total_plays"])

        if os.path.exists(playlist_path):
            playlist_df = pd.read_csv(playlist_path)
        else:
            playlist_df = pd.DataFrame(columns=["user_id", "total_playlists"])

        merged = pd.merge(basic_df, social_df, on="user_id", how="left")
        if not listen_agg.empty:
            merged = pd.merge(merged, listen_agg, on="user_id", how="left")

        if "user_id" in playlist_df.columns and "total_playlists" in playlist_df.columns:
            merged = pd.merge(merged, playlist_df[["user_id", "total_playlists"]], on="user_id", how="left")

        for col in ["level", "fans_count", "follows_count", "total_plays", "total_playlists"]:
            if col in merged.columns:
                merged[col] = merged[col].fillna(0)

        return merged

    except Exception as e:
        print(e)
        return None

def fanscount_regression(df):
    feats = []
    for c in ["level", "follows_count"]:
        if c in df.columns:
            feats.append(c)

    if ("fans_count" not in df.columns) or len(feats) < 1:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "数据列不足: 无法回归粉丝数", ha="center", va="center")
        return fig

    sub = df.dropna(subset=["fans_count"] + feats).copy()
    X = sub[feats].values
    y = sub["fans_count"].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, test_size=0.2)
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.scatter(y_test, y_pred, alpha=0.7, color="steelblue")
    ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
    ax.set_xlabel("实际粉丝数")
    ax.set_ylabel("预测粉丝数")
    ax.set_title(f"线性回归 - 预测粉丝数 ($R^2$={r2:.3f})")
    return fig

def render_parallel_categories(df):
    needed_cols = ["level", "fans_count", "follows_count", "province", "gender"]
    for col in needed_cols:
        if col not in df.columns:
            return None

    df_plot = df.copy()

    gender_map = {0:"未知", 1:"男", 2:"女"}
    if "gender" in df_plot.columns:
        df_plot["gender_cat"] = df_plot["gender"].map(gender_map).fillna("未知").astype(str)
    else:
        df_plot["gender_cat"] = "未知"

    if "province" in df_plot.columns:
        df_plot["province_cat"] = df_plot["province"].astype(str)
    else:
        df_plot["province_cat"] = "未知"

    df_plot["level_bin"] = pd.cut(df_plot["level"], bins=[-1,2,5,8,10, 999], labels=["Lv0-2","Lv3-5","Lv6-8","Lv9-10","Lv>10"])
    df_plot["fans_bin"] = pd.cut(df_plot["fans_count"], bins=[-1,10,50,200,500, 1e9], labels=["粉丝0-10","粉丝11-50","粉丝51-200","粉丝201-500","粉丝500+"])
    df_plot["follows_bin"] = pd.cut(df_plot["follows_count"], bins=[-1,10,50,200,500, 1e9], labels=["关注0-10","关注11-50","关注51-200","关注201-500","关注500+"])

    fig = px.parallel_categories(
        df_plot,
        dimensions=["level_bin","fans_bin","follows_bin","province_cat","gender_cat"],
        color_continuous_scale=px.colors.sequential.Inferno
    )
    fig.update_layout(title="平行分类图: 用户社交多维分布")
    return fig
