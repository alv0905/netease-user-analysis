import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from matplotlib.font_manager import FontProperties
import os

def render():
    st.title("📈 播放行为分析")

    # 设置中文字体
    font_path = "E:/Netease_analysis/assets/SourceHanSansHWSC/OTF/SimplifiedChineseHW/SourceHanSansHWSC-Regular.otf"
    font_prop = FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False

    @st.cache_data
    def load_data():
        listening = pd.read_csv("E:/Netease_analysis/data/listening_records.csv")
        basic = pd.read_csv("E:/Netease_analysis/data/basic_info.csv")
        social = pd.read_csv("E:/Netease_analysis/data/social_info.csv")
        playlist = pd.read_csv("E:/Netease_analysis/data/playlist_info.csv")
        return listening, basic, social, playlist

    listening_df, basic_df, social_df, playlist_df = load_data()

    # 展示部分原始数据
    st.subheader("📄 原始播放记录 (前100行)")
    st.dataframe(listening_df.head(100))

    # ------------------------------
    # (图1) 最受欢迎的歌曲 Top 20
    # ------------------------------
    st.subheader("🎵 最受欢迎的歌曲 (Top 20)")

    top_songs = listening_df['song_name'].value_counts().nlargest(20)

    fig1, ax1 = plt.subplots(figsize=(10, 6))
    bars = sns.barplot(y=top_songs.index, x=top_songs.values, palette="coolwarm", ax=ax1)

    ax1.set_title("Top 20 热门歌曲", fontproperties=font_prop, fontsize=16)
    ax1.set_xlabel("播放次数", fontproperties=font_prop, fontsize=12)
    ax1.set_ylabel("歌曲名称", fontproperties=font_prop, fontsize=12)

    for label in ax1.get_yticklabels():
        label.set_fontproperties(font_prop)
        label.set_fontsize(10)
    for label in ax1.get_xticklabels():
        label.set_fontproperties(font_prop)
        label.set_fontsize(10)

    for i, bar in enumerate(bars.patches):
        width = bar.get_width()
        ax1.text(
            width + max(top_songs.values) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f'{int(width)}',
            va='center',
            ha='left',
            fontproperties=font_prop,
            fontsize=9,
            color='black'
        )

    sns.despine(top=True, right=True)
    st.pyplot(fig1)
    st.caption("说明: 统计播放记录中最受欢迎的歌曲, 按播放次数从高到低列出前20首.")

    # ------------------------------
    # (图2) 用户评分分布 (KDE密度图)
    # ------------------------------
    st.subheader("📊 用户评分分布 (KDE 密度图)")

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.kdeplot(data=listening_df, x='score', fill=True, color="#FF7F0E",
                alpha=0.7, linewidth=2, ax=ax2)

    mean_score = listening_df['score'].mean()
    ax2.axvline(mean_score, color='gray', linestyle='--', linewidth=1.5)
    # 改用ASCII冒号, 避免方块: "均值: 27.51"
    ax2.text(
        mean_score + 0.05,
        ax2.get_ylim()[1] * 0.9,
        f'均值: {mean_score:.2f}',  # 使用ASCII冒号 ":" ，不是全角 "："
        color='gray',
        fontsize=10,
        fontproperties=font_prop  # 必须加入，让文字也用中文字体
    )

    ax2.set_title("用户评分分布曲线", fontproperties=font_prop, fontsize=18)
    ax2.set_xlabel("分数", fontproperties=font_prop, fontsize=14)
    ax2.set_ylabel("密度", fontproperties=font_prop, fontsize=14)

    for label in ax2.get_xticklabels() + ax2.get_yticklabels():
        label.set_fontproperties(font_prop)

    plt.tight_layout()
    st.pyplot(fig2)
    st.caption("说明: 使用核密度估计(KDE)观察用户在score字段上的分数分布, 并在图中标出平均分位置.")

    # ------------------------------
    # (图3) 用户喜欢的歌手词云图
    # ------------------------------
    st.subheader("☁️ 用户喜欢的歌手词云图")

    text = " ".join(listening_df['song_name'].astype(str).tolist())
    wc = WordCloud(
        font_path=font_path,
        width=1000,
        height=500,
        background_color='white',
        colormap='plasma',
        collocations=False,
        max_words=200,
        contour_width=1,
        contour_color='steelblue'
    ).generate(text)

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.imshow(wc, interpolation='bilinear')
    ax3.axis('off')
    st.pyplot(fig3)
    st.caption("说明: 以词云形式直观展示用户播放记录里出现频率较高的歌手(或歌曲名称).")

    # ------------------------------
    # (图4) 播放行为相关性分析 (热力图)
    # ------------------------------
    st.subheader("🔥 播放行为相关性分析")

    merged_df = pd.merge(listening_df, playlist_df, on='user_id', how='left')
    merged_df = pd.merge(merged_df, social_df, on='user_id', how='left')
    merged_df = pd.merge(merged_df, basic_df[['user_id', 'level']], on='user_id', how='left')

    # 相关性分析字段
    # 原列: playCount, score, liked_playlist_count, created_playlist_count,
    #       total_playlists, follows_count, fans_count, level
    # 显示中文:
    rename_map = {
        'playCount': '播放次数',
        'score': '评分',
        'liked_playlist_count': '点赞歌单数',
        'created_playlist_count': '创建歌单数',
        'total_playlists': '歌单总数',
        'follows_count': '关注数',
        'fans_count': '粉丝数',
        'level': '等级'
    }

    corr_df = merged_df[['playCount','score','liked_playlist_count','created_playlist_count',
                         'total_playlists','follows_count','fans_count','level']].copy()
    # 改列名
    corr_df.rename(columns=rename_map, inplace=True)

    corr = corr_df.corr()

    fig4, ax4 = plt.subplots(figsize=(10, 8))
    sns.set(style="whitegrid")

    heatmap = sns.heatmap(
        corr,
        annot=True,
        cmap='coolwarm',
        linewidths=0.5,
        fmt=".2f",
        annot_kws={"size": 10},
        square=True,
        cbar_kws={"shrink": 0.75},
        ax=ax4
    )
    ax4.set_title("播放行为相关性热力图", fontproperties=font_prop, fontsize=16)

    # x,y 轴标签改成中文
    ax4.set_xticklabels(ax4.get_xticklabels(), rotation=30, ha='right', fontproperties=font_prop, fontsize=10)
    ax4.set_yticklabels(ax4.get_yticklabels(), rotation=0, fontproperties=font_prop, fontsize=10)

    st.pyplot(fig4)
    st.caption("说明: 对播放次数、评分、点赞/创建歌单数、关注/粉丝数及等级等进行相关性计算, 颜色越红越正相关, 越蓝越负相关.")


