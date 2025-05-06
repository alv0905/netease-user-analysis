# top_nav.py
import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image, ImageOps
import os
import importlib.util


def get_avatar():
    """
    返回当前用户的头像 (PIL.Image)；若未上传过则返回一个默认空白头像
    """
    avatar_path = "E:/Netease_analysis/assets/avatar.png"  # 全局默认头像
    if "current_user" in st.session_state and st.session_state["current_user"]:
        user_avatar_path = f"E:/Netease_analysis/assets/avatars/{st.session_state['current_user']}.png"
        if os.path.exists(user_avatar_path):
            avatar_path = user_avatar_path

    if os.path.exists(avatar_path):
        # 读取图像
        img = Image.open(avatar_path)
        # 这里把头像裁剪成圆形，可自行选择
        img = circle_avatar(img)
        return img
    else:
        return None


def circle_avatar(img: Image.Image) -> Image.Image:
    """
    将给定的头像图像裁剪为圆形并返回新的PIL图像对象。
    """
    # 转换为正方形最小边
    size = min(img.size)
    img = img.resize((size, size))
    # 创建一个相同尺寸的mask并绘制圆形
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageOps.expand(ImageOps.crop(mask, 0), border=0, fill=255)

    # 在mask上画一个“圆”
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask_draw)
    draw.ellipse((0, 0, size, size), fill=255)

    # 合成出圆形图
    img.putalpha(mask_draw)
    return img


def top_nav():
    """
    导航栏 + 菜单模块：
    - 菜单中包含 ['主页', '用户画像', '社交互动', '歌单偏好', '播放行为', '我的']
    - 右上角只显示 用户头像(圆形) + 当前用户昵称，不做任何点击跳转
    - 若用户未登录，则显示“未登录”，头像使用全局默认空白头像
    """
    if "prev_menu" not in st.session_state:
        st.session_state["prev_menu"] = None

    # 完整菜单项：把“我的”替换原“用户信息”
    menu_items = [
        "主页",
        "用户画像",
        "社交互动",
        "歌单偏好",
        "播放行为",
        "我的"  # <= 替代“用户信息”
    ]

    current_page = st.session_state.get("page", "主页")

    if current_page in menu_items:
        default_index = menu_items.index(current_page)
    else:
        default_index = 0

    with st.container():
        col1, col2, col3 = st.columns([8, 1, 1])

        with col1:
            selected = option_menu(
                menu_title=None,
                options=menu_items,
                icons=[
                    "house",
                    "person-circle",
                    "chat-dots",
                    "music-note-list",
                    "bar-chart",
                    "person-badge"  # '我的' 的icon
                ],
                orientation="horizontal",
                default_index=default_index,
                styles={
                    "container": {"padding": "0!important", "background-color": "#fafafa"},
                    "icon": {"color": "#f63366", "font-size": "20px"},
                    "nav-link": {
                        "font-size": "18px",
                        "text-align": "center",
                        "--hover-color": "#eee"
                    },
                    "nav-link-selected": {"background-color": "#f63366", "color": "white"},
                }
            )

        with col2:
            # 显示头像(只显示,不做任何按钮)
            avatar_img = get_avatar()
            if avatar_img:
                st.image(avatar_img, width=40)
            else:
                # 若没找到头像则显示一个空白占位
                st.write("暂无头像")

        with col3:
            # 显示用户名文字(不做点击按钮)
            username = st.session_state.get("current_user", "未登录")
            st.write(f"**{username}**")

    # 区分“默认高亮” vs “用户实际点击”
    prev_menu = st.session_state["prev_menu"]
    if selected != prev_menu:
        st.session_state["page"] = selected
        st.session_state["prev_menu"] = selected
        st.rerun()


def route_page(selected_page):
    """
    统一调度：将 selected_page 动态加载并渲染
    """
    page_map = {
        "主页": "main.py",
        "用户画像": "pages/用户画像分析.py",
        "社交互动": "pages/社交互动分析.py",
        "歌单偏好": "pages/歌单偏好分析.py",
        "播放行为": "pages/播放行为分析.py",
        "我的": "pages/用户信息页.py",  # <= '我的' 映射到“用户信息页.py”
    }

    if selected_page not in page_map:
        st.error(f"未识别的页面: {selected_page}")
        return

    file_path = f"E:/Netease_analysis/{page_map[selected_page]}"
    if not os.path.exists(file_path):
        st.error(f"无法找到文件: {file_path}")
        return

    spec = importlib.util.spec_from_file_location("page_module", file_path)
    page = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(page)
    page.render()


def main_page():
    """
    主入口：检查登录状态 -> 显示导航栏 -> 根据 page 进行路由
    """
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if not st.session_state["logged_in"]:
        import login
        login.app()
        st.stop()

    if "page" not in st.session_state:
        st.session_state["page"] = "主页"

    top_nav()
    route_page(st.session_state["page"])
