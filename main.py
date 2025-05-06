import streamlit as st
import pandas as pd
import numpy as np
# 需要 scikit-learn
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import io
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 设置 matplotlib 中文字体
font_path = "E:/Netease_analysis/assets/SourceHanSansHWSC/OTF/SimplifiedChineseHW/SourceHanSansHWSC-Regular.otf"
font_prop = font_manager.FontProperties(fname=font_path)


def render():
    # ---------------------
    # 你的现有主页布局
    # ---------------------
    st.title("🎵 网易云音乐用户行为分析平台")
    st.markdown("### 📊 平台功能概览")
    colA, colB = st.columns(2)

    with colA:
        st.subheader("👤 用户画像分析")
        st.markdown("用户基础信息、地区、性别、等级等")
        st.subheader("🎶 歌单偏好分析")
        st.markdown("歌单创建、收藏、推荐算法等")

    with colB:
        st.subheader("🎼 播放行为分析")
        st.markdown("播放记录、热门歌曲、评分趋势等")
        st.subheader("💬 社交互动分析")
        st.markdown("粉丝数、关注行为、社区互动等")

    st.markdown("### 🌟 平台亮点")
    st.success("✅ 数据来自真实网易云用户，保证分析的真实性")
    st.success("✅ 多维度分析，涵盖播放、社交、歌单行为等")
    st.success("✅ 交互式网页平台，所有图表均可实时展示")

    st.markdown("### 🧭 如何使用本平台")
    st.markdown(
        "1. 👉 点击顶部菜单切换分析模块  \n"
        "2. 📈 查看交互图表与分析数据  \n"
        "3. 📝 图表可导出保存，用于报告或研究  \n"
    )
    st.info("📌 提示：点击顶部菜单栏选择你想查看的分析模块。")

    # ---------------------
    # 新增：综合四张表的聚类可视化
    # ---------------------
    st.markdown("---")
    st.markdown("## 🎨 用户聚类分布")

    merged_df = load_and_merge_data()
    if merged_df.empty:
        st.warning("❓ 未获取到合并后的用户数据，可能 CSV 路径不正确或文件为空。")
        return

    # 选择 K 值
    n_clusters = st.slider("选择聚类个数 (K)", min_value=2, max_value=6, value=3, step=1)

    fig, labels = cluster_and_visualize(merged_df, n_clusters=n_clusters)
    st.pyplot(fig)

    st.caption("此图使用K-means算法 + PCA降维。颜色=聚类分组，仅供参考。")

    # ✅ 新增：展示各聚类在原始特征上的均值表
    cluster_summary_df = interpret_clusters(merged_df, labels)
    st.markdown("### 各聚类平均特征值")
    st.dataframe(cluster_summary_df)

    st.info("""
        通过上表可以看出每个聚类在 [level, total_plays, total_playlists, fans_count, follows_count]
        等指标上的均值。结合散点图颜色，你可以轻松得出：
        - 哪个聚类等级最高？
        - 哪个聚类粉丝数最多？
        - 哪个聚类播放量最多？
        等结论。
        """)


def load_and_merge_data():
    # 路径参考
    try:
        basic = pd.read_csv("E:/Netease_analysis/data/basic_info.csv")
        listen = pd.read_csv("E:/Netease_analysis/data/listening_records.csv")
        playlist = pd.read_csv("E:/Netease_analysis/data/playlist_info.csv")
        social = pd.read_csv("E:/Netease_analysis/data/social_info.csv")
    except Exception as e:
        st.error(f"读取CSV出错: {e}")
        return pd.DataFrame()

    listen_agg = listen.groupby("user_id", as_index=False)["playCount"].sum()
    listen_agg.rename(columns={"playCount": "total_plays"}, inplace=True)

    merged = pd.merge(basic[["user_id", "level"]], listen_agg, on="user_id", how="left")
    merged = pd.merge(merged, playlist[["user_id", "total_playlists"]], on="user_id", how="left")
    merged = pd.merge(merged, social[["user_id", "fans_count", "follows_count"]], on="user_id", how="left")

    for col in ["total_plays", "total_playlists", "fans_count", "follows_count", "level"]:
        merged[col] = merged[col].fillna(0)

    return merged


def cluster_and_visualize(merged_df, n_clusters=3):
    X = merged_df[["level", "total_plays", "total_playlists", "fans_count", "follows_count"]].values

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X)

    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X)

    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap="rainbow", alpha=0.7)
    ax.set_xlabel("PCA-1")
    ax.set_ylabel("PCA-2")
    ax.set_title(f"用户聚类结果 (K={n_clusters})", fontproperties=font_prop)


    return fig, labels


def interpret_clusters(merged_df, labels):
    """
    根据聚类结果 labels，对 merged_df 的 [level, total_plays, ...] 做 groupby 平均值。
    返回一个 DataFrame：
        cluster | level | total_plays | total_playlists | fans_count | follows_count | user_count
    """
    # 把 labels 写回 merged_df
    temp_df = merged_df.copy()
    temp_df["cluster"] = labels

    # groupby 计算均值
    # 注意：user_count 统计各簇人数
    group_mean = temp_df.groupby("cluster", as_index=False).agg({
        "user_id": "count",
        "level": "mean",
        "total_plays": "mean",
        "total_playlists": "mean",
        "fans_count": "mean",
        "follows_count": "mean"
    }).rename(columns={"user_id": "user_count"})

    # 美化数值
    # group_mean = group_mean.round(2)  # 若你想保留两位小数

    # 让 cluster 列放在最左边
    columns_order = ["cluster", "user_count", "level", "total_plays", "total_playlists", "fans_count", "follows_count"]
    group_mean = group_mean[columns_order]

    return group_mean
