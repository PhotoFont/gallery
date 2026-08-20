import os
import base64
import streamlit as st

st.set_page_config(page_title="Saksitpra Gallery", layout="wide")

# ฟังก์ชันแปลงรูปภาพเป็น Base64 เพื่อใส่ใน HTML/CSS Button
def get_image_base64(image_path):
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Custom CSS แปลง st.button หน้าแรกให้กลายเป็นรูปภาพการ์ดแบบเต็มตัว
st.markdown("""
<style>
    /* ซ่อนปุ่ม Fullscreen Default ของ Streamlit */
    button[title="View fullscreen"] {
        display: none !important;
    }

    /* ตกแต่งโครงสร้างการ์ดอัลบั้ม */
    .album-card-wrapper {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        overflow: hidden;
        background: #ffffff;
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .album-card-wrapper:hover {
        transform: translateY(-4px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.12);
    }

    /* ปรับแต่งปุ่มรูปภาพปกให้ออกแบบเหมือน Clickable Image */
    .img-btn-container button {
        width: 100% !important;
        height: 180px !important;
        border: none !important;
        border-radius: 0px !important;
        background-position: center !important;
        background-size: cover !important;
        background-repeat: no-repeat !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
    }
    .img-btn-container button:hover {
        opacity: 0.9;
    }
    .img-btn-container button p {
        display: none !important; /* ซ่อนข้อความในปุ่มรูป */
    }

    /* ปรับแต่งปุ่มชื่ออัลบั้มด้านล่างรูป */
    .title-btn-container button {
        width: 100% !important;
        border: none !important;
        background: transparent !important;
        text-align: left !important;
        padding: 8px 12px 2px 12px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: #111111 !important;
        box-shadow: none !important;
    }
    .title-btn-container button:hover {
        color: #0066cc !important;
        background: #f8f9fa !important;
    }

    .album-sub-text {
        font-size: 0.8rem;
        color: #777777;
        padding: 0 12px 8px 12px;
    }

    /* เมนูอัลบั้มที่ Sidebar */
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

albums_list = get_albums()
st.sidebar.subheader("📁 อัลบั้มทั้งหมด")

if not albums_list:
    st.sidebar.caption("ยังไม่มีอัลบั้ม")
else:
    for alb in albums_list:
        icon = "📂" if st.session_state.active_album == alb else "📁"
        st.sidebar.markdown('<div class="sidebar-album-btn">', unsafe_allow_html=True)
        if st.sidebar.button(f"{icon} {alb}", key=f"sb_alb_{alb}"):
            st.session_state.active_album = alb
            st.rerun()
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

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

# 1. Grid View (หน้าแรก)
if st.session_state.active_album is None:
    st.title("Albums")
    st.caption("คลิกที่รูปภาพหรือชื่ออัลบั้มเพื่อเข้าชมรูปภาพภายใน")

    if not albums_list:
        st.info("ยังไม่มีอัลบั้มรูปภาพ")
    else:
        cols = st.columns(4)
        for idx, album in enumerate(albums_list):
            images = get_images(album)
            cover_img_path = os.path.join(GALLERY_DIR, album, images[0]) if images else ""
            img_b64 = get_image_base64(cover_img_path)
            
            with cols[idx % 4]:
                st.markdown('<div class="album-card-wrapper">', unsafe_allow_html=True)
                
                # กำหนดรูปภาพพื้นหลังให้ปุ่มกดผ่าน CSS Dynamic Style
                bg_style = f"background-image: url('data:image/jpeg;base64,{img_b64}');" if img_b64 else "background-color: #eee;"
                st.markdown(f'<style>.img-btn-{idx} button {{ {bg_style} }}</style>', unsafe_allow_html=True)
                
                # ปุ่มกดที่รูปปก
                st.markdown(f'<div class="img-btn-container img-btn-{idx}">', unsafe_allow_html=True)
                if st.button(" ", key=f"cover_click_{album}"):
                    st.session_state.active_album = album
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

                # ปุ่มกดที่ชื่ออัลบั้ม
                st.markdown('<div class="title-btn-container">', unsafe_allow_html=True)
                if st.button(f"📁 {album}", key=f"title_click_{album}"):
                    st.session_state.active_album = album
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown(f'<div class="album-sub-text">{len(images)} photos</div>', unsafe_allow_html=True)
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
        st.caption("💡 คลิกปุ่มรูปภาพเพื่อซูมดูขนาดใหญ่")
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