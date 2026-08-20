import os
import streamlit as st

st.set_page_config(page_title="Saksitpra Gallery", layout="wide")

# Custom CSS ตกแต่ง Card และการคลิก
st.markdown("""
<style>
    .album-card {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        background-color: #ffffff;
    }
    .album-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .album-sub {
        font-size: 0.85rem;
        color: #666666;
        margin-top: -10px;
        margin-bottom: 10px;
        padding-left: 4px;
    }
    /* ปรับแต่งปุ่มชื่ออัลบั้มให้ดูเหมือน Heading */
    div[data-testid="stButton"] > button {
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)

GALLERY_DIR = os.path.join(os.path.dirname(__file__), 'gallery')
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ADMIN_PASSWORD = "21020166"

if not os.path.exists(GALLERY_DIR):
    os.makedirs(GALLERY_DIR)

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "active_album" not in st.session_state:
    st.session_state.active_album = None

def get_albums():
    return [
        d for d in os.listdir(GALLERY_DIR)
        if os.path.isdir(os.path.join(GALLERY_DIR, d)) and not d.startswith('.')
    ]

def get_images(album_name):
    album_path = os.path.join(GALLERY_DIR, album_name)
    if not os.path.exists(album_path):
        return []
    return [
        f for f in os.listdir(album_path)
        if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS
    ]

@st.dialog("🔍 ภาพขยาย")
def show_image_modal(img_path, caption):
    st.image(img_path, caption=caption, use_container_width=True)

# --- SIDEBAR ---
st.sidebar.title("📷 Menu")

if st.sidebar.button("🏠 กลับหน้าหลัก"):
    st.session_state.active_album = None
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader("🔐 ระบบ Admin")

if not st.session_state.is_admin:
    password_input = st.sidebar.text_input("รหัสผ่าน Admin", type="password")
    if st.sidebar.button("Login"):
        if password_input == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.sidebar.success("เข้าสู่ระบบสำเร็จ!")
            st.rerun()
        else:
            st.sidebar.error("รหัสผ่านไม่ถูกต้อง")
else:
    st.sidebar.success("🟢 สถานะ: Admin")
    if st.sidebar.button("Logout"):
        st.session_state.is_admin = False
        st.rerun()

    st.sidebar.divider()
    st.sidebar.subheader("⚙️ จัดการอัลบั้ม")
    new_album_name = st.sidebar.text_input("➕ สร้างอัลบั้มใหม่")
    if st.sidebar.button("สร้างอัลบั้ม"):
        if new_album_name.strip():
            new_album_path = os.path.join(GALLERY_DIR, new_album_name.strip())
            if not os.path.exists(new_album_path):
                os.makedirs(new_album_path)
                st.sidebar.success(f"สร้างอัลบั้ม '{new_album_name}' แล้ว")
                st.rerun()
            else:
                st.sidebar.warning("มีชื่ออัลบั้มนี้อยู่แล้ว")

# --- MAIN PAGE RENDERING ---
albums = get_albums()

# 1. Grid View (หน้าแรก)
if st.session_state.active_album is None:
    st.title("Recent Projects / Albums")
    st.caption("คลิกที่รูปปกหรือชื่ออัลบั้มเพื่อเข้าชมรูปภาพภายใน")

    if not albums:
        st.info("ยังไม่มีอัลบั้มรูปภาพ")
    else:
        cols = st.columns(4)
        for idx, album in enumerate(albums):
            images = get_images(album)
            cover_img = os.path.join(GALLERY_DIR, album, images[0]) if images else None
            
            with cols[idx % 4]:
                st.markdown('<div class="album-card">', unsafe_allow_html=True)
                
                # แสดงรูปปก
                if cover_img:
                    st.image(cover_img, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/400x300?text=No+Cover", use_container_width=True)
                
                # กดที่ปุ่มรูปปก หรือ ปุ่มชื่ออัลบั้ม เพื่อเข้าอัลบั้ม
                if st.button(f"🖼️ ดูอัลบั้มนี้", key=f"img_click_{album}"):
                    st.session_state.active_album = album
                    st.rerun()

                if st.button(f"📁 {album}", key=f"title_click_{album}"):
                    st.session_state.active_album = album
                    st.rerun()

                st.markdown(f'<div class="album-sub">{len(images)} photos</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# 2. Album Detail View
else:
    current_album = st.session_state.active_album
    st.title(f"📁 อัลบั้ม: {current_album}")
    
    if st.session_state.is_admin:
        st.subheader("📤 อัปโหลดรูปภาพใหม่")
        uploaded_files = st.file_uploader("เลือกรูปภาพ", type=['jpg', 'jpeg', 'png', 'gif', 'webp'], accept_multiple_files=True)
        if st.button("บันทึกรูปภาพ"):
            if uploaded_files:
                target_dir = os.path.join(GALLERY_DIR, current_album)
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(target_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                st.success("อัปโหลดเรียบร้อย!")
                st.rerun()

    images = get_images(current_album)
    if not images:
        st.warning("ยังไม่มีรูปภาพในอัลบั้มนี้")
    else:
        st.caption("💡 คลิกปุ่มรูปภาพด้านล่างเพื่อซูมดูขนาดใหญ่")
        cols = st.columns(3)
        for idx, img_name in enumerate(images):
            img_path = os.path.join(GALLERY_DIR, current_album, img_name)
            with cols[idx % 3]:
                st.image(img_path, use_container_width=True)
                
                if st.button(f"🔍 {img_name}", key=f"zoom_{img_name}"):
                    show_image_modal(img_path, img_name)
                
                if st.session_state.is_admin:
                    if st.button("🗑️ ลบรูปนี้", key=f"del_{img_name}"):
                        os.remove(img_path)
                        st.rerun()