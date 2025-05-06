# pages/用户信息页.py
import streamlit as st
import pandas as pd
import os
from PIL import Image


USER_CSV_PATH = "E:/Netease_analysis/data/users.csv"
AVATAR_FOLDER = "E:/Netease_analysis/assets/avatars"

@st.cache_data
def load_user_info():
    if os.path.exists(USER_CSV_PATH):
        return pd.read_csv(USER_CSV_PATH, encoding='utf-8-sig')
    return pd.DataFrame()

def save_user_info(df):
    df.to_csv(USER_CSV_PATH, index=False, encoding='utf-8-sig')

def render():
    st.title("👤 我的用户信息")

    if not st.session_state.get("logged_in", False) or not st.session_state.get("current_user"):
        st.warning("⚠️ 您尚未登录，请返回登录页面。")
        return

    current_user = st.session_state["current_user"]

    # 每次都加载最新 CSV
    # 如果你想保留缓存，加 st.cache_data，但要在保存后 clear
    df = load_user_info()

    user_row = df[df['username'] == current_user]
    if user_row.empty:
        st.error(f"未找到用户 {current_user} 的信息。")
        return

    user_data = user_row.iloc[0]

    st.subheader("🖼️ 用户头像")
    avatar_path = os.path.join(AVATAR_FOLDER, f"{current_user}.png")
    if os.path.exists(avatar_path):
        st.image(avatar_path, width=100)
    else:
        st.info("暂无头像")

    # 允许用户上传多种图片类型
    uploaded_avatar = st.file_uploader(
        "上传新头像（支持 PNG / JPG / JPEG / BMP / GIF 等）",
        type=["png", "jpg", "jpeg", "bmp", "gif"]
    )
    if uploaded_avatar:
        os.makedirs(AVATAR_FOLDER, exist_ok=True)
        from PIL import Image
        img = Image.open(uploaded_avatar)
        img.save(avatar_path, format="PNG")
        st.success("头像上传成功，刷新后可见")

    st.subheader("📋 用户基本资料")

    phone_val = user_data.get("phone", "暂无")
    phone_str = format_phone_value(phone_val)

    st.write("用户名：", user_data.get("username", "-"))
    st.write("联系方式：", phone_str)
    st.write("邮箱：", user_data.get("email", "暂无"))
    st.write("注册时间：", user_data.get("created_at", "-"))

    st.subheader("📖 个性签名")
    intro = user_data.get("intro", "这个人很懒，还没有填写简介。")
    st.info(intro)

    if st.checkbox("✏️ 编辑我的信息"):
        new_phone = st.text_input("修改联系电话", value=user_data.get("phone", ""))
        new_email = st.text_input("修改邮箱", value=user_data.get("email", ""))
        new_intro = st.text_area("编辑个性签名", value=intro)

        if st.button("保存修改"):
            # 1. 写入 CSV
            idx = user_row.index[0]
            df.at[idx, "phone"] = new_phone
            df.at[idx, "email"] = new_email
            df.at[idx, "intro"] = new_intro
            save_user_info(df)

            # 2. 清理缓存 / 强制刷新
            st.cache_data.clear()  # 清空之前 load_user_info() 缓存
            st.success("✅ 信息已更新！")

            st.cache_data.clear()  # 清空缓存
            st.rerun()

    if st.button("🚪 退出登录", type="primary"):
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = None
        st.cache_data.clear()  # 如果有需要清理缓存
        st.session_state["page"] = "主页"
        st.stop()  # 或直接 return


def format_phone_value(value):
    if pd.isna(value) or value == "暂无":
        return "暂无"
    if isinstance(value, (float, int)):
        return str(int(value))
    return str(value)