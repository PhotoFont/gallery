import os
from flask import Flask, render_template, send_from_directory, abort

app = Flask(__name__)

GALLERY_DIR = os.path.join(os.path.dirname(__file__), 'gallery')
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def get_albums():
    if not os.path.exists(GALLERY_DIR):
        os.makedirs(GALLERY_DIR)
    return [
        d for d in os.listdir(GALLERY_DIR) 
        if os.path.isdir(os.path.join(GALLERY_DIR, d)) and not d.startswith('.')
    ]

@app.route('/')
def index():
    albums = get_albums()
    album_data = []
    for album in albums:
        album_path = os.path.join(GALLERY_DIR, album)
        images = [
            f for f in os.listdir(album_path) 
            if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS
        ]
        cover = images[0] if images else None
        album_data.append({
            'name': album,
            'count': len(images),
            'cover': cover
        })
    return render_template('index.html', albums=album_data)

@app.route('/album/<album_name>')
def show_album(album_name):
    album_path = os.path.join(GALLERY_DIR, album_name)
    if not os.path.exists(album_path) or not os.path.isdir(album_path):
        abort(404)
    
    images = [
        f for f in os.listdir(album_path) 
        if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS
    ]
    return render_template('album.html', album_name=album_name, images=images)

@app.route('/gallery/<album_name>/<filename>')
def serve_image(album_name, filename):
    return send_from_directory(os.path.join(GALLERY_DIR, album_name), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)