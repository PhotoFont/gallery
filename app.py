import os
import streamlit as st

st.set_page_config(page_title="Photo Gallery", layout="wide")

GALLERY_DIR = os.path.join(os.path.dirname(__file__), 'gallery')
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

# สร้างโฟลเดอร์ gallery หลักหากยังไม่มี
if not os.path.exists(GALLERY_DIR):
    os.makedirs(GALLERY_DIR)

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

# --- SIDEBAR: เมนูจัดการอัลบั้มและอัปโหลด ---
st.sidebar.header("⚙️ จัดการอัลบั้ม")

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

# 2. เลือกอัลบั้มปัจจุบัน
albums = get_albums()

if not albums:
    st.info("ยังไม่มีอัลบั้มรูปภาพ กรุณาสร้างอัลบั้มใหม่ที่ Sidebar ด้านซ้าย")
else:
    selected_album = st.sidebar.selectbox("📁 เลือกอัลบั้ม", albums)

    # 3. ฟอร์มอัปโหลดรูปภาพลงอัลบั้มที่เลือก
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

    # --- MAIN CONTENT: แสดงรูปในอัลบั้ม ---
    if selected_album:
        st.header(f"📁 อัลบั้ม: {selected_album}")
        images = get_images(selected_album)

        if not images:
            st.warning("ไม่มีรูปภาพในอัลบั้มนี้ ลองอัปโหลดรูปผ่าน Sidebar ด้านซ้ายดูครับ")
        else:
            # แสดงรูปเป็น Grid 3 คอลัมน์
            cols = st.columns(3)
            for idx, img_name in enumerate(images):
                img_path = os.path.join(GALLERY_DIR, selected_album, img_name)
                with cols[idx % 3]:
                    st.image(img_path, caption=img_name, use_container_width=True)