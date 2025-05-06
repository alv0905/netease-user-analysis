import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

import plotly.express as px
from scipy.stats import pearsonr  # 用于相关系数

def render():
    st.title("🎶 歌单偏好分析")

    # 设置中文字体等
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 需保证有 SimHei 字体
    plt.rcParams['axes.unicode_minus'] = False

    # CSV 路径
    playlist_path = "E:/Netease_analysis/data/playlist_info.csv"
    basic_path = "E:/Netease_analysis/data/basic_info.csv"
    social_path = "E:/Netease_analysis/data/social_info.csv"

    @st.cache_data
    def load_data():
        playlist = pd.read_csv(playlist_path)
        basic = pd.read_csv(basic_path)
        social = pd.read_csv(social_path)
        return playlist, basic, social

    playlist_df, basic_df, social_df = load_data()

    # 合并
    merged_df = pd.merge(playlist_df, basic_df, on="user_id", how="left")
    merged_df = pd.merge(merged_df, social_df, on="user_id", how="left")

    st.subheader("合并后的用户数据 (展示前100行)")
    st.dataframe(merged_df.head(100))

    # ---------- 图1: 用户等级与歌单数量关系 (多项式拟合) ----------
    st.subheader(" 用户等级与歌单数量关系 (多项式拟合)")

    level_playlist = merged_df.groupby("level")["total_playlists"].mean().reset_index()
    # 多项式拟合
    deg = 2  # 二次多项式
    x = level_playlist["level"].values
    y = level_playlist["total_playlists"].values
    coeffs = np.polyfit(x, y, deg=deg)
    poly_func = np.poly1d(coeffs)

    x_fit = np.linspace(x.min(), x.max(), 100)
    y_fit = poly_func(x_fit)

    fig1, ax1 = plt.subplots()
    # 原折线
    ax1.plot(x, y, marker="o", label="平均歌单数")
    # 拟合线
    ax1.plot(x_fit, y_fit, "r--", label=f"多项式拟合(度={deg})")
    ax1.set_title("不同等级与歌单总数 (多项式曲线)")
    ax1.set_xlabel("用户等级")
    ax1.set_ylabel("平均歌单数量")
    ax1.legend()
    st.pyplot(fig1)
    st.caption("说明: 使用二次多项式对等级与歌单的关系做拟合, 以捕捉潜在的非线性趋势.")

    # ---------- 图2: 各省份人均歌单数量 Treemap ----------
    st.subheader(" 各省份人均歌单数量 Top10 (Treemap)")

    # 省份映射
    province_map = {
        110000: "北京", 120000: "天津", 130000: "河北", 140000: "山西", 150000: "内蒙古",
        210000: "辽宁", 220000: "吉林", 230000: "黑龙江", 310000: "上海", 320000: "江苏",
        330000: "浙江", 340000: "安徽", 350000: "福建", 360000: "江西", 370000: "山东",
        410000: "河南", 420000: "湖北", 430000: "湖南", 440000: "广东", 450000: "广西",
        460000: "海南", 500000: "重庆", 510000: "四川", 520000: "贵州", 530000: "云南",
        540000: "西藏", 610000: "陕西", 620000: "甘肃", 630000: "青海", 640000: "宁夏",
        650000: "新疆"
    }
    merged_df["province_name"] = merged_df["province"].map(province_map)

    province_avg = merged_df.groupby("province_name")["total_playlists"].mean().dropna()
    top10 = province_avg.sort_values(ascending=False).head(10).reset_index()
    top10.columns = ["province_name","avg_playlists"]

    fig2 = px.treemap(
        top10,
        path=["province_name"],
        values="avg_playlists",
        color="avg_playlists",
        color_continuous_scale="Tealgrn",
        title="各省份人均歌单数量 Top10"
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("说明: Treemap使用矩形面积/颜色呈现省份人均歌单数量, 面积和颜色均代表数值大小.")

    # ---------- 图3: 总歌单数 vs 粉丝数 (Hexbin + 相关系数) ----------
    st.subheader("总歌单数 与 粉丝数量 的关系 (Hexbin + 相关系数)")

    df_hex = merged_df.dropna(subset=["total_playlists","fans_count"]).copy()
    x_hex = df_hex["total_playlists"]
    y_hex = df_hex["fans_count"]

    # Pearson相关
    corr, pval = pearsonr(x_hex, y_hex)

    fig3, ax3 = plt.subplots(figsize=(6,4))
    hb = ax3.hexbin(x_hex, y_hex, gridsize=30, cmap="viridis", mincnt=1)
    ax3.set_xlabel("歌单总数")
    ax3.set_ylabel("粉丝数量")
    ax3.set_title("Hexbin: 歌单数量 vs 粉丝数量")
    cb = fig3.colorbar(hb, ax=ax3)
    cb.set_label("计数")

    st.pyplot(fig3)
    st.caption(f"说明: 使用Hexbin替代散点图来展示二维分布密度, Pearson相关系数={corr:.3f}, p={pval:.2g}.")



