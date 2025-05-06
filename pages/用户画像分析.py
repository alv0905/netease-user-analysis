import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.express as px

# 中文支持
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def render():
    st.title("🖼️ 用户画像分析")
    # 数据路径
    data_path = "E:/Netease_analysis/data/basic_info.csv"

    @st.cache_data
    def load_data(path):
        df = pd.read_csv(path)

        # ✅ 正确的省份字典（不是 set）
        province_name_map = {
            "11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古",
            "21": "辽宁", "22": "吉林", "23": "黑龙江", "31": "上海", "32": "江苏",
            "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东",
            "41": "河南", "42": "湖北", "43": "湖南", "44": "广东", "45": "广西",
            "46": "海南", "50": "重庆", "51": "四川", "52": "贵州", "53": "云南",
            "54": "西藏", "61": "陕西", "62": "甘肃", "63": "青海", "64": "宁夏",
            "65": "新疆", "71": "台湾", "81": "香港", "82": "澳门"
        }

        def clean_province(code):
            code_str = str(code)[:2]
            return province_name_map.get(code_str, "未知地区")

        df["clean_province"] = df["province"].apply(clean_province)

        # 生日时间戳转日期
        def convert_birthday(ts):
            try:
                ts = int(ts)
                if ts == -2209017600000:
                    return pd.to_datetime("1900-01-01")
                if ts == -1:
                    return pd.NaT
                return datetime.utcfromtimestamp(ts / 1000)
            except:
                return pd.NaT

        df['birthday'] = df['birthday'].apply(convert_birthday)

        # 年龄计算
        current_year = datetime.now().year
        df['age'] = df['birthday'].dt.year.apply(
            lambda x: current_year - x if pd.notnull(x) and x > 1900 else None
        )

        return df

    # 加载数据
    df = load_data(data_path)

    # --------------------------
    # 📋 原始数据展示
    # --------------------------
    st.subheader("📋 用户基础信息（前100行）")
    st.dataframe(df.head(100))

    col1, col2 = st.columns(2)
    with col1:
        # --------------------------
        # 📊 用户等级分布
        # --------------------------
        st.subheader("📊 用户等级分布")
        level_counts = df['level'].value_counts().sort_index()
        fig1, ax1 = plt.subplots()
        sns.barplot(x=level_counts.index, y=level_counts.values, palette="Blues_d", ax=ax1)
        ax1.set_xlabel("用户等级")
        ax1.set_ylabel("用户数量")
        ax1.set_title("等级分布图")
        st.pyplot(fig1)

    with col2:
        # --------------------------
        # 🧍‍♂️ 用户性别比例
        # --------------------------
        st.subheader("🧍 用户性别比例")
        gender_map = {0: "未知", 1: "男", 2: "女"}
        gender_counts = df['gender'].map(gender_map).value_counts()
        fig2, ax2 = plt.subplots()
        ax2.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%',
                colors=['gray', 'skyblue', 'pink'], startangle=140)
        ax2.axis('equal')
        st.pyplot(fig2)

    # --------------------------
    # 🗺️ 地区分布（省份）
    # --------------------------
    st.subheader("📍 用户地区分布（省级）")
    province_counts = df["clean_province"].value_counts().drop("未知地区", errors='ignore')
    province_df = province_counts.reset_index()
    province_df.columns = ["省份", "用户数量"]

    fig3 = px.bar(
        province_df,
        x="用户数量",
        y="省份",
        orientation="h",
        color="用户数量",
        color_continuous_scale="Blues",
        height=600,
        title="各省份用户分布（按人数排序）"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # --------------------------
    # 🎂 年龄分布
    # --------------------------
    st.subheader("🎂 用户年龄分布")
    df_valid_age = df[(df['age'] > 12) & (df['age'] < 80)].copy()

    fig4, ax4 = plt.subplots(figsize=(10, 6))
    sns.histplot(df_valid_age['age'], bins=15, kde=True, color='#6fa8dc',
                 edgecolor='white', line_kws={'lw': 1.5}, ax=ax4)
    ax4.set_title('用户年龄分布特征', fontsize=14, pad=20)
    ax4.set_xlabel('年龄', fontsize=12)
    ax4.set_ylabel('用户数量', fontsize=12)
    ax4.grid(axis='y', linestyle='--', alpha=0.7)

    # 添加峰值年龄注释
    peak_age = df_valid_age['age'].value_counts().idxmax()
    ax4.axvline(peak_age, color='#e74c3c', linestyle='--', lw=1)
    ax4.text(peak_age + 1, ax4.get_ylim()[1] * 0.9,
             f'峰值年龄: {peak_age}岁', color='#e74c3c')
    plt.tight_layout()
    st.pyplot(fig4)



