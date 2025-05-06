import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 正确路径
USER_CSV_PATH = r"E:\Netease_analysis\data\users.csv"

def load_users():
    if not os.path.exists(USER_CSV_PATH):
        df = pd.DataFrame(columns=["username", "password_hash", "email", "phone", "created_at"])
        df.to_csv(USER_CSV_PATH, index=False, encoding='utf-8-sig')
        return df
    try:
        df = pd.read_csv(USER_CSV_PATH, encoding='utf-8-sig')
        return df
    except:
        return pd.DataFrame(columns=["username", "password_hash", "email", "phone", "created_at"])

def save_users(df):
    df.to_csv(USER_CSV_PATH, index=False, encoding='utf-8-sig')

def login_page():
    st.title("用户登录")
    st.markdown("---")
    st.subheader("欢迎回来，请先登录！")

    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")

    if st.button("登录"):
        df = load_users()
        if username in df["username"].values:
            user_row = df[df["username"] == username].iloc[0]
            if password == str(user_row["password_hash"]):
                st.success("登录成功！")
                st.session_state["logged_in"] = True
                st.session_state["current_user"] = username
                st.rerun()  # 替换原 experimental_rerun
            else:
                st.error("密码错误，请重试。")
        else:
            st.error("用户不存在，请先注册。")

    if st.button("还没有账号？去注册"):
        st.session_state["show_register"] = True
        st.rerun()

def register_page():
    st.title("用户注册")
    st.markdown("---")
    st.subheader("创建一个新的账户")

    new_username = st.text_input("设置用户名（必填）")
    new_email = st.text_input("邮箱（选填）", placeholder="可不填，但建议填写以便找回密码")
    new_phone = st.text_input("电话（选填）", placeholder="可不填")
    new_password = st.text_input("设置密码（必填）", type="password")
    confirm_password = st.text_input("确认密码（必填）", type="password")

    if st.button("注册"):
        if not new_username or not new_password:
            st.error("用户名或密码不能为空。")
            return
        if new_password != confirm_password:
            st.error("两次输入的密码不一致。")
            return

        df = load_users()
        if new_username in df["username"].values:
            st.error("该用户名已被注册，请更换。")
        else:
            new_row = {
                "username": new_username,
                "password_hash": new_password,
                "email": new_email if new_email else "",
                "phone": new_phone if new_phone else "",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_users(df)
            st.success("注册成功，请登录！")
            st.session_state["show_register"] = False
            st.rerun()

    if st.button("返回登录"):
        st.session_state["show_register"] = False
        st.rerun()

def app():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "show_register" not in st.session_state:
        st.session_state["show_register"] = False

    if st.session_state["show_register"]:
        register_page()
    else:
        login_page()
