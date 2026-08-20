import os
import base64
import streamlit as st

st.set_page_config(page_title="Saksitpra Gallery", layout="wide")

def get_image_base64(image_path):
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Custom CSS จัดระเบียบการแสดงผล
st.markdown("""
<style>
    /* ปรับแต่งภาพหน้าแรก (ไม่โดนตัด สมส่วน 100%) */
    div[data-testid="stColumn"] img {
        object-fit: contain !important;
        max-height: 240px !important;
        width: 100% !important;
        border-radius: 8px;
        background-color: #f8f9fa;
    }

    /* ปุ่มเลือกอัลบั้ม Sidebar */
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

    /* ปุ่มเปิดอัลบั้มหน้าแรก */
    .album-btn-main button {
        width: 100% !important;
        margin-top: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, 'gallery')
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ADMIN_PASSWORD = "21020166"

if not os.path.exists(GALLERY_DIR):
    os.makedirs(GALLERY_DIR, exist_ok=True)

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "active_album" not in st.session_state:
    st.session_state.active_album = None

def get_albums():
    if not os.path.exists(GALLERY_DIR):
        return []
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
                os.makedirs(new_album_path, exist_ok=True)
                st.sidebar.success(f"สร้างอัลบั้ม '{new_album_name}' แล้ว")
                st.rerun()
            else:
                st.sidebar.warning("มีชื่ออัลบั้มนี้อยู่แล้ว")

# --- MAIN PAGE RENDERING ---

# 1. Grid View (หน้าแรก - แสดงปกอัลบั้ม)
if st.session_state.active_album is None:
    st.title("Albums")
    st.caption("เลือกดูอัลบั้มรูปภาพจากปุ่มชื่ออัลบั้มด้านล่างหรือเมนูด้านซ้าย")

    if not albums_list:
        st.info("ยังไม่มีอัลบั้มรูปภาพ")
    else:
        cols = st.columns(3)
        for idx, album in enumerate(albums_list):
            images = get_images(album)
            cover_img = os.path.join(GALLERY_DIR, album, images[0]) if images else None
            
            with cols[idx % 3]:
                if cover_img:
                    st.image(cover_img, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/400x300?text=No+Cover", use_container_width=True)
                
                st.markdown('<div class="album-btn-main">', unsafe_allow_html=True)
                if st.button(f"📁 เข้าชมอัลบั้ม {album} ({len(images)} รูป)", key=f"open_btn_{album}"):
                    st.session_state.active_album = album
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                st.write("")

# 2. Album Detail View (หน้าแสดงรูป - คลิกรูปเพื่อซูมได้ทันที ไม่ต้องกดปุ่ม)
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
        st.caption("💡 คลิกที่ตัวรูปภาพเพื่อเปิดดูภาพขยายใหญ่ได้ทันที")
        cols = st.columns(3)
        for idx, img_name in enumerate(images):
            img_path = os.path.join(GALLERY_DIR, current_album, img_name)
            img_b64 = get_image_base64(img_path)
            img_src = f"data:image/jpeg;base64,{img_b64}"
            
            with cols[idx % 3]:
                # ใช้นวัตกรรม HTML Lightbox คลิกรูปแล้วซูมเปิด Modal ขยายทันที
                zoom_html = f"""
                <style>
                    .zoom-img-{idx} {{
                        width: 100%;
                        max-height: 250px;
                        object-fit: contain;
                        background: #f8f9fa;
                        border-radius: 8px;
                        cursor: pointer;
                        transition: transform 0.2s ease;
                    }}
                    .zoom-img-{idx}:hover {{
                        transform: scale(1.02);
                    }}
                    
                    /* Modal Styles */
                    .modal-{idx} {{
                        display: none;
                        position: fixed;
                        z-index: 99999;
                        padding-top: 30px;
                        left: 0;
                        top: 0;
                        width: 100%;
                        height: 100%;
                        overflow: auto;
                        background-color: rgba(0,0,0,0.85);
                    }}
                    .modal-content-{idx} {{
                        margin: auto;
                        display: block;
                        max-width: 90%;
                        max-height: 85vh;
                        border-radius: 6px;
                        object-fit: contain;
                    }}
                    .close-{idx} {{
                        position: absolute;
                        top: 15px;
                        right: 35px;
                        color: #f1f1f1;
                        font-size: 40px;
                        font-weight: bold;
                        cursor: pointer;
                    }}
                </style>

                <img class="zoom-img-{idx}" src="{img_src}" onclick="document.getElementById('myModal-{idx}').style.display='block'">

                <div id="myModal-{idx}" class="modal-{idx}" onclick="this.style.display='none'">
                    <span class="close-{idx}">&times;</span>
                    <img class="modal-content-{idx}" src="{img_src}">
                </div>
                """
                st.components.v1.html(zoom_html, height=260)
                
                if st.session_state.is_admin:
                    if st.button(f"🗑️ ลบรูป {img_name}", key=f"del_{img_name}", use_container_width=True):
                        os.remove(img_path)
                        st.rerun()
                st.write("")