import os
import base64
import mimetypes
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
    /* 1. ดันเนื้อหาหลักทั้งหมดขึ้นด้านบนสุด */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* ซ่อน Header / Space ด้านบนของ Streamlit */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* 2. บีบระยะห่างปุ่มเมนู Sidebar ให้ชิดกันแน่นสวยงาม */
    div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        gap: 0.2rem !important;
    }

    div[data-testid="stSidebar"] div[data-testid="stElementContainer"] {
        margin-bottom: -0.2rem !important;
    }

    div[data-testid="stSidebar"] button {
        width: 100% !important;
        text-align: left !important;
        border: 1px solid #e9ecef !important;
        background: #ffffff !important;
        padding: 6px 12px !important;
        font-size: 0.9rem !important;
        border-radius: 6px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
    }

    div[data-testid="stSidebar"] button:hover {
        background-color: #e9ecef !important;
        color: #0066cc !important;
        border-color: #0066cc !important;
    }

    /* การจัดวางการ์ดแกลเลอรี */
    .photo-card-btn {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 6px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    
    .album-card-box {
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #e9ecef;
        padding: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        text-align: center;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, 'gallery')
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ADMIN_PASSWORD = "adminsecretpass"

if not os.path.exists(GALLERY_DIR):
    os.makedirs(GALLERY_DIR, exist_ok=True)

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "active_album" not in st.session_state:
    st.session_state.active_album = None

if "selected_image" not in st.session_state:
    st.session_state.selected_image = None

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
        if st.session_state.is_admin:
            if st.button("🗑️ ลบรูปภาพนี้", type="primary", use_container_width=True):
                if os.path.exists(img_path):
                    os.remove(img_path)
                    st.toast("ลบรูปภาพเรียบร้อยแล้ว!")
                    st.session_state.selected_image = None
                    st.rerun()

# --- SIDEBAR ---
st.sidebar.title("📷 Gallery Menu")

if st.sidebar.button("🏠 กลับหน้าหลัก"):
    st.session_state.active_album = None
    st.session_state.selected_image = None
    st.rerun()

albums_list = get_albums()
st.sidebar.subheader("📁 อัลบั้มทั้งหมด")

if not albums_list:
    st.sidebar.caption("ยังไม่มีอัลบั้ม")
else:
    for alb in albums_list:
        icon = "📂" if st.session_state.active_album == alb else "📁"
        if st.sidebar.button(f"{icon} {alb}", key=f"sb_alb_{alb}"):
            st.session_state.active_album = alb
            st.session_state.selected_image = None
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
                os.makedirs(new_album_path, exist_ok=True)
                st.sidebar.success(f"สร้างอัลบั้ม '{new_album_name}' แล้ว")
                st.rerun()
            else:
                st.sidebar.warning("มีชื่ออัลบั้มนี้อยู่แล้ว")

# --- MAIN PAGE RENDERING ---

# 1. หน้าหลัก - แสดงรายการอัลบั้มแบบ Grid
if st.session_state.active_album is None:
    st.title("📁 อัลบั้มรูปภาพ")
    st.caption("คลิกเลือกอัลบั้มที่ต้องการเพื่อเข้าชมรูปภาพภายใน")

    if not albums_list:
        st.info("ยังไม่มีอัลบั้มรูปภาพ")
    else:
        cols = st.columns(4)
        for idx, album in enumerate(albums_list):
            images = get_images(album)
            cover_img_path = os.path.join(GALLERY_DIR, album, images[0]) if images else None
            
            with cols[idx % 4]:
                st.markdown('<div class="album-card-box">', unsafe_allow_html=True)
                if cover_img_path and os.path.exists(cover_img_path):
                    st.image(cover_img_path, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/400x300?text=No+Images", use_container_width=True)
                
                if st.button(f"📁 {album} ({len(images)})", key=f"main_alb_{album}", use_container_width=True):
                    st.session_state.active_album = album
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# 2. หน้าแสดงรูปภาพในอัลบั้ม
else:
    current_album = st.session_state.active_album

    if st.session_state.selected_image:
        zoom_path = os.path.join(GALLERY_DIR, current_album, st.session_state.selected_image)
        if os.path.exists(zoom_path):
            show_image_modal(zoom_path, st.session_state.selected_image, current_album)

    st.title(f"📁 อัลบั้ม: {current_album}")
    
    if st.session_state.is_admin:
        with st.expander("📤 อัปโหลดรูปภาพใหม่เข้าอัลบั้มนี้", expanded=False):
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
                    st.session_state.uploader_key += 1
                    st.rerun()

    images = get_images(current_album)
    if not images:
        st.warning("ยังไม่มีรูปภาพในอัลบั้มนี้")
    else:
        st.caption("💡 คลิกที่ปุ่มใตักรอกรูปภาพเพื่อขยายดูภาพใหญ่")
        
        cols = st.columns(5)
        for idx, img_name in enumerate(images):
            img_path = os.path.join(GALLERY_DIR, current_album, img_name)
            
            with cols[idx % 5]:
                st.markdown('<div class="photo-card-btn">', unsafe_allow_html=True)
                st.image(img_path, use_container_width=True)
                if st.button("🔍 ขยายรูป", key=f"btn_img_{img_name}", use_container_width=True):
                    st.session_state.selected_image = img_name
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)