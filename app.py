import os
import base64
import mimetypes
from urllib.parse import quote, unquote
import streamlit as st

st.set_page_config(page_title="Saksitpra Gallery", layout="wide")

def get_image_base64(image_path):
    if not os.path.exists(image_path):
        return "", "image/jpeg"
    
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/jpeg"
        
    with open(image_path, "rb") as img_file:
        b64_str = base64.b64encode(img_file.read()).decode("utf-8")
        return b64_str, mime_type

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* ปรับแต่งปุ่มและระยะห่างใน Sidebar ให้เรียงชิดกันสวยงาม */
    div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        gap: 0.4rem !important;
    }

    .sidebar-album-btn {
        margin-bottom: -6px !important;
    }

    .sidebar-album-btn button {
        width: 100% !important;
        text-align: left !important;
        border: 1px solid #e9ecef !important;
        background: #ffffff !important;
        padding: 6px 12px !important;
        font-size: 0.9rem !important;
        border-radius: 6px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
    }

    .sidebar-album-btn button:hover {
        background-color: #e9ecef !important;
        color: #0066cc !important;
        border-color: #0066cc !important;
    }

    /* แกลเลอรีจัดเรียงรูปภาพแบบ Grid แน่นสวยงาม */
    .photo-gallery {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
        gap: 14px;
        padding: 10px 0 20px 0;
    }
    
    .photo-card {
        display: block;
        position: relative;
        width: 100%;
        height: 230px;
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        transition: all 0.25s ease-in-out;
        text-decoration: none !important;
    }
    
    .photo-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 18px rgba(0,0,0,0.15);
        border-color: #0066cc;
    }
    
    .photo-card img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        padding: 6px;
        background-color: #f8f9fa;
    }

    /* Grid สำหรับหน้าแสดงอัลบั้มหน้าแรก */
    .album-gallery {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 18px;
        padding: 10px 0;
    }
    
    .album-card {
        display: block;
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #e9ecef;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        text-decoration: none !important;
        transition: all 0.2s ease;
    }
    
    .album-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
    }
    
    .album-card img {
        width: 100%;
        height: 180px;
        object-fit: contain;
        background: #f8f9fa;
        padding: 6px;
    }
    
    .album-info {
        padding: 12px;
        text-align: center;
        background: #ffffff;
        border-top: 1px solid #f1f3f5;
    }
    
    .album-title {
        font-weight: 600;
        font-size: 1.05rem;
        color: #212529;
        margin-bottom: 2px;
    }
    
    .album-count {
        font-size: 0.85rem;
        color: #6c757d;
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

# ใช้สำหรับล้างค่า file_uploader
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

def get_albums():
    if not os.path.exists(GALLERY_DIR):
        return []
    albums = [
        d for d in os.listdir(GALLERY_DIR)
        if os.path.isdir(os.path.join(GALLERY_DIR, d)) and not d.startswith('.')
    ]
    return sorted(albums)

def get_images(album_name):
    album_path = os.path.join(GALLERY_DIR, album_name)
    if not os.path.exists(album_path):
        return []
    return sorted([
        f for f in os.listdir(album_path)
        if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS
    ])

# Dialog ขยายรูปภาพแบบเต็มจอ
@st.dialog("🖼️ ภาพขยาย", width="large")
def show_image_modal(img_path, img_name, album_name):
    st.image(img_path, use_container_width=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"📁 อัลบั้ม: **{album_name}** | 📄 ไฟล์: `{img_name}`")
    with col2:
        if st.session_state.get("is_admin", False):
            if st.button("🗑️ ลบรูปภาพนี้", type="primary", use_container_width=True):
                if os.path.exists(img_path):
                    os.remove(img_path)
                    st.toast("ลบรูปภาพเรียบร้อยแล้ว!")
                    if "zoom" in st.query_params:
                        del st.query_params["zoom"]
                    st.rerun()

# --- SYSTEM QUERY PARAMS HANDLER ---
query_params = st.query_params

if "album" in query_params:
    alb_param = unquote(query_params["album"])
    if alb_param in get_albums():
        st.session_state.active_album = alb_param

# --- SIDEBAR ---
st.sidebar.title("📷 Gallery Menu")

if st.sidebar.button("🏠 กลับหน้าหลัก"):
    st.session_state.active_album = None
    st.query_params.clear()
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
            st.query_params["album"] = alb
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

# 1. หน้าหลัก - แสดงรายการอัลบั้มแบบ Grid
if st.session_state.active_album is None:
    st.title("📁 อัลบั้มรูปภาพ")
    st.caption("คลิกที่รูปปกหรือชื่ออัลบั้มเพื่อเปิดเข้าชมรูปภาพภายใน")

    if not albums_list:
        st.info("ยังไม่มีอัลบั้มรูปภาพ")
    else:
        album_html = '<div class="album-gallery">'
        for album in albums_list:
            images = get_images(album)
            cover_img_path = os.path.join(GALLERY_DIR, album, images[0]) if images else None
            
            if cover_img_path and os.path.exists(cover_img_path):
                img_b64, mime_type = get_image_base64(cover_img_path)
                img_src = f"data:{mime_type};base64,{img_b64}"
            else:
                img_src = "https://via.placeholder.com/400x300?text=No+Images"
            
            encoded_album = quote(album)
            album_html += (
                f'<a href="?album={encoded_album}" target="_self" class="album-card">'
                f'<img src="{img_src}" alt="{album}" />'
                f'<div class="album-info">'
                f'<div class="album-title">📁 {album}</div>'
                f'<div class="album-count">{len(images)} รูปภาพ</div>'
                f'</div>'
                f'</a>'
            )
        album_html += '</div>'
        st.markdown(album_html, unsafe_allow_html=True)

# 2. หน้าแสดงรูปภาพในอัลบั้ม (คลิกรูปเพื่อซูมทันที)
else:
    current_album = st.session_state.active_album
    
    # ตรวจสอบว่ามีการคลิกรูปเพื่อซูมหรือไม่
    if "zoom" in st.query_params:
        zoom_file = unquote(st.query_params["zoom"])
        del st.query_params["zoom"]
        zoom_path = os.path.join(GALLERY_DIR, current_album, zoom_file)
        if os.path.exists(zoom_path):
            show_image_modal(zoom_path, zoom_file, current_album)

    st.title(f"📁 อัลบั้ม: {current_album}")
    
    if st.session_state.is_admin:
        with st.expander("📤 อัปโหลดรูปภาพใหม่เข้าอัลบั้มนี้", expanded=False):
            # ใช้ key แบบไดนามิกเพื่อให้ reset ตัว file_uploader ได้
            uploaded_files = st.file_uploader(
                "เลือกรูปภาพ", 
                type=['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                accept_multiple_files=True,
                key=f"uploader_{st.session_state.uploader_key}"
            )
            if st.button("บันทึกรูปภาพ"):
                if uploaded_files:
                    target_dir = os.path.join(GALLERY_DIR, current_album)
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(target_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    st.toast("อัปโหลดรูปภาพสำเร็จ!")
                    # เพิ่มค่า uploader_key เพื่อบังคับรีเซ็ตช่องไฟล์
                    st.session_state.uploader_key += 1
                    st.rerun()

    images = get_images(current_album)
    if not images:
        st.warning("ยังไม่มีรูปภาพในอัลบั้มนี้")
    else:
        st.caption("💡 คลิกที่ตัวรูปภาพใดก็ได้เพื่อขยายดูภาพใหญ่")
        
        gallery_html = '<div class="photo-gallery">'
        for img_name in images:
            img_path = os.path.join(GALLERY_DIR, current_album, img_name)
            img_b64, mime_type = get_image_base64(img_path)
            img_src = f"data:{mime_type};base64,{img_b64}"
            
            encoded_album = quote(current_album)
            encoded_img = quote(img_name)
            gallery_html += (
                f'<a href="?album={encoded_album}&zoom={encoded_img}" target="_self" class="photo-card" title="คลิกเพื่อขยายดูรูป">'
                f'<img src="{img_src}" alt="{img_name}" />'
                f'</a>'
            )
        gallery_html += '</div>'
        
        st.markdown(gallery_html, unsafe_allow_html=True)