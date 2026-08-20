import os
import streamlit as st

st.set_page_config(page_title="Photo Gallery", layout="wide")

GALLERY_DIR = os.path.join(os.path.dirname(__file__), 'gallery')
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

# กำหนดรหัสผ่าน Admin (ตั้งค่าตามต้องการ)
ADMIN_PASSWORD = "21020166"

# สร้างโฟลเดอร์ gallery หลักหากยังไม่มี
if not os.path.exists(GALLERY_DIR):
    os.makedirs(GALLERY_DIR)

# จัดการ Session State สำหรับระบบ Authentication
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

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

st.title("📷 Photo Gallery")

# --- SIDEBAR: ระบบล็อกอิน Admin ---
st.sidebar.header("🔐 เข้าสู่ระบบ Admin")

if not st.session_state.is_admin:
    password_input = st.sidebar.text_input("รหัสผ่าน Admin", type="password")
    if st.sidebar.button("Login"):
        if password_input == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.sidebar.success("เข้าสู่ระบบ Admin สำเร็จ!")
            st.rerun()
        else:
            st.sidebar.error("รหัสผ่านไม่ถูกต้อง")
else:
    st.sidebar.success("🟢 สถานะ: Admin")
    if st.sidebar.button("Logout"):
        st.session_state.is_admin = False
        st.rerun()

st.sidebar.divider()

# --- SIDEBAR: เมนูจัดการอัลบั้ม (เปิดให้เฉพาะ Admin เท่านั้น) ---
if st.session_state.is_admin:
    st.sidebar.header("⚙️ จัดการอัลบั้ม (Admin Only)")
    
    # 1. ฟอร์มสร้างอัลบั้มใหม่
    new_album_name = st.sidebar.text_input("➕ สร้างอัลบั้มใหม่")
    if st.sidebar.button("สร้างอัลบั้ม"):
        if new_album_name.strip():
            new_album_path = os.path.join(GALLERY_DIR, new_album_name.strip())
            if not os.path.exists(new_album_path):
                os.makedirs(new_album_path)
                st.sidebar.success(f"สร้างอัลบั้ม '{new_album_name}' เรียบร้อย!")
                st.rerun()
            else:
                st.sidebar.warning("มีอัลบั้มชื่อนี้อยู่แล้ว")
        else:
            st.sidebar.error("กรุณากรอกชื่ออัลบั้ม")

    st.sidebar.divider()

# --- MAIN CONTENT & ALBUM DISPLAY ---
albums = get_albums()

if not albums:
    st.info("ยังไม่มีอัลบั้มรูปภาพ")
else:
    selected_album = st.sidebar.selectbox("📁 เลือกอัลบั้ม", albums)

    # 2. ฟอร์มอัปโหลดรูปภาพ (เฉพาะ Admin)
    if st.session_state.is_admin and selected_album:
        st.sidebar.subheader(f"📤 อัปโหลดรูปไปที่ {selected_album}")
        uploaded_files = st.sidebar.file_uploader(
            "เลือกรูปภาพ", 
            type=['jpg', 'jpeg', 'png', 'gif', 'webp'], 
            accept_multiple_files=True
        )

        if st.sidebar.button("บันทึกรูปภาพ"):
            if uploaded_files:
                target_dir = os.path.join(GALLERY_DIR, selected_album)
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(target_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                st.sidebar.success(f"อัปโหลดสำเร็จ {len(uploaded_files)} รูป!")
                st.rerun()
            else:
                st.sidebar.error("กรุณาเลือกรูปภาพก่อนกดอัปโหลด")

    # แสดงรูปในอัลบั้ม
    if selected_album:
        st.header(f"📁 อัลบั้ม: {selected_album}")
        images = get_images(selected_album)

        if not images:
            st.warning("ไม่มีรูปภาพในอัลบั้มนี้")
        else:
            cols = st.columns(3)
            for idx, img_name in enumerate(images):
                img_path = os.path.join(GALLERY_DIR, selected_album, img_name)
                with cols[idx % 3]:
                    st.image(img_path, caption=img_name, use_container_width=True)
                    
                    # ปุ่มลบรูปภาพ (แสดงเฉพาะ Admin)
                    if st.session_state.is_admin:
                        if st.button(f"🗑️ ลบรูป", key=f"del_{selected_album}_{img_name}"):
                            os.remove(img_path)
                            st.success(f"ลบรูป {img_name} แล้ว")
                            st.rerun()