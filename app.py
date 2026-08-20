import os
import streamlit as st

st.set_page_config(page_title="Saksitpra Gallery", layout="wide")

# Custom CSS ตกแต่ง Card และ Sidebar Menu
st.markdown("""
<style>
    .album-card {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        background-color: #ffffff;
        padding-bottom: 8px;
    }
    .album-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
    }
    
    .album-card img {
        height: 180px !important;
        object-fit: cover !important;
        width: 100% !important;
    }

    .album-sub {
        font-size: 0.8rem;
        color: #777777;
        padding-left: 10px;
        margin-top: -2px;
    }

    /* ปุ่มชื่ออัลบั้มในหน้าแรก */
    div[data-testid="stColumn"] button {
        width: 100% !important;
        border: none !important;
        background: transparent !important;
        text-align: left !important;
        padding: 6px 10px 2px 10px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: #222222 !important;
    }
    div[data-testid="stColumn"] button:hover {
        color: #0066cc !important;
        background-color: #f8f9fa !important;
    }

    /* ปุ่มรายการอัลบั้มใน Sidebar */
    .sidebar-album-btn button {
        width: 100% !important;
        text-align: left !important;
        border: none !important;
        background: transparent !important;
        padding: 6px 8px !important;
        font-size: 0.9rem !important;
        border-radius: 4px !important;
    }
    .sidebar-album-btn button:hover {
        background-color: #e9ecef !important;
        color: #0066cc !important;
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

# ----------------
# เมนูรายการอัลบั้มอัตโนมัติ (Dynamic Album List)
# ----------------
albums_list = get_albums()
st.sidebar.subheader("📁 อัลบั้มทั้งหมด")

if not albums_list:
    st.sidebar.caption("ยังไม่มีอัลบั้ม")
else:
    for alb in albums_list:
        # ตรวจสอบเพื่อไฮไลต์อัลบั้มที่เลือกอยู่ปัจจุบัน
        icon = "📂" if st.session_state.active_album == alb else "📁"
        st.sidebar.markdown('<div class="sidebar-album-btn">', unsafe_allow_html=True)
        if st.sidebar.button(f"{icon} {alb}", key=f"sb_alb_{alb}"):
            st.session_state.active_album = alb
            st.rerun()
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.divider()

# --- ระบบ ADMIN ---
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

# 1. Grid View (หน้าแรก)
if st.session_state.active_album is None:
    st.title("Recent Projects / Albums")
    st.caption("คลิกเลือกอัลบั้มที่ต้องการเข้าชม")

    if not albums_list:
        st.info("ยังไม่มีอัลบั้มรูปภาพ")
    else:
        cols = st.columns(4)
        for idx, album in enumerate(albums_list):
            images = get_images(album)
            cover_img = os.path.join(GALLERY_DIR, album, images[0]) if images else None
            
            with cols[idx % 4]:
                st.markdown('<div class="album-card">', unsafe_allow_html=True)
                
                if cover_img:
                    st.image(cover_img, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/400x300?text=No+Cover", use_container_width=True)
                
                if st.button(f"📁 {album}", key=f"click_{album}"):
                    st.session_state.active_album = album
                    st.rerun()

                st.markdown(f'<div class="album-sub">{len(images)} photos</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# 2. Album Detail View (หน้าแสดงรูปในอัลบั้ม)
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