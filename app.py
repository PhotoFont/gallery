import os
import streamlit as st

st.set_page_config(page_title="Photo Gallery", layout="wide")

GALLERY_DIR = os.path.join(os.path.dirname(__file__), 'gallery')
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def get_albums():
    if not os.path.exists(GALLERY_DIR):
        os.makedirs(GALLERY_DIR)
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

albums = get_albums()

if not albums:
    st.info("ไม่พบอัลบั้มรูปภาพในโฟลเดอร์ gallery")
else:
    # Sidebar สำหรับเลือกอัลบั้ม
    selected_album = st.sidebar.selectbox("เลือกอัลบั้ม", albums)
    
    if selected_album:
        st.header(f"📁 อัลบั้ม: {selected_album}")
        images = get_images(selected_album)
        
        if not images:
            st.warning("ไม่มีรูปภาพในอัลบั้มนี้")
        else:
            # แสดงรูปเป็น Grid 3 คอลัมน์
            cols = st.columns(3)
            for idx, img_name in enumerate(images):
                img_path = os.path.join(GALLERY_DIR, selected_album, img_name)
                with cols[idx % 3]:
                    st.image(img_path, caption=img_name, use_container_width=True)