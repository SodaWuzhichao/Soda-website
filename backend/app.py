import flask, sqlite3, os, json, datetime, shutil
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_sock import Sock

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 媒体目录：优先使用扩展盘，回退到本地
_MEDIA_PATH_LOCAL = os.path.join(BASE_DIR, 'media')
_MEDIA_PATH_EXT = '/Volumes/SodaMedia/Media'
if os.path.exists(_MEDIA_PATH_EXT):
    MEDIA_DIR = _MEDIA_PATH_EXT
    print(f"[INFO] 使用扩展盘媒体目录: {MEDIA_DIR}")
else:
    MEDIA_DIR = _MEDIA_PATH_LOCAL
    print(f"[INFO] 使用本地媒体目录: {MEDIA_DIR}")
DB_PATH = os.path.join(BASE_DIR, 'soda.db')

app = Flask(__name__)
sock = Sock(app)
CORS(app)

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'images'), filename)

@app.route('/media/videos/<path:filename>')
def serve_videos(filename):
    return send_from_directory(os.path.join(MEDIA_DIR, 'videos'), filename)

@app.route('/media/thumbnails/<path:filename>')
def serve_thumbnails(filename):
    return send_from_directory(os.path.join(MEDIA_DIR, 'thumbnails'), filename)

@app.route('/media/photos/<path:filename>')
def serve_photos(filename):
    return send_from_directory(os.path.join(MEDIA_DIR, 'photos'), filename)

@sock.route('/voice')
def voice_handle(ws):
    print('🎙️ 语音对讲连接成功')
    while True:
        data = ws.receive()
        if data: ws.send(f"小五收到音频数据，大小: {len(data)} 字节")

@app.route('/voice')
def serve_voice_page():
    return send_file("voice.html")

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        res = flask.Response()
        origin = request.headers.get('Origin')
        if origin: res.headers['Access-Control-Allow-Origin'] = origin
        res.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS,DELETE,PATCH'
        res.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        res.headers['Access-Control-Allow-Credentials'] = 'true'
        return res

@app.route('/admin')
@app.route('/')
def serve_admin():
    return send_file("admin_new.html")

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    if data.get('username') == 'soda' and data.get('password') == 'soda567':
        return jsonify({'status': 'ok', 'token': 'soda-token-2024'})
    return jsonify({'status': 'error'}), 401

@app.route('/api/upload_chunk', methods=['POST'])
def upload_chunk():
    file = request.files['file']
    file_id = request.form.get('file_id')
    index = int(request.form.get('part_index', 0))
    total_parts = int(request.form.get('total_parts', 1))
    temp_dir = os.path.join(MEDIA_DIR, 'temp', file_id)
    os.makedirs(temp_dir, exist_ok=True)
    file.save(os.path.join(temp_dir, str(index)))
    return jsonify({'status': 'ok'})

@app.route('/api/merge_chunks', methods=['POST'])
def merge_chunks():
    data = request.json or {}
    file_id = data.get('file_id')
    filename = data.get('filename')
    temp_dir = os.path.join(MEDIA_DIR, 'temp', file_id)
    target_path = os.path.join(MEDIA_DIR, 'videos', filename)
    with open(target_path, 'wb') as target_file:
        for i in range(len(os.listdir(temp_dir))):
            with open(os.path.join(temp_dir, str(i)), 'rb') as f:
                target_file.write(f.read())
    shutil.rmtree(temp_dir)
    return jsonify({'status': 'ok', 'path': f'/media/videos/{filename}'})

@app.route('/api/works', methods=['GET', 'POST', 'DELETE', 'HEAD'])
def handle_works():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if request.method == 'GET' or request.method == 'HEAD':
        cursor.execute('SELECT * FROM works ORDER BY sort_order ASC, year DESC, id DESC')
        columns = [column[0] for column in cursor.description]
        works = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return jsonify(works)
    if request.method == 'POST':
        data = request.form if request.content_type and 'multipart' in request.content_type else (request.json or {})
        file_id = data.get('file_id')
        filename = data.get('filename')
        thumbnail = request.files.get('thumbnail')
        
        # 只有上传了文件才处理文件移动
        if file_id and filename:
            temp_dir = os.path.join(MEDIA_DIR, 'temp', file_id)
            target_path = os.path.join(MEDIA_DIR, 'videos', filename)
            with open(target_path, 'wb') as tf:
                for i in range(len(os.listdir(temp_dir))):
                    with open(os.path.join(temp_dir, str(i)), 'rb') as f:
                        tf.write(f.read())
            shutil.rmtree(temp_dir)
            if thumbnail:
                thumb_path = os.path.join(MEDIA_DIR, 'thumbnails', filename.rsplit('.', 1)[0] + '.jpg')
                thumbnail.save(thumb_path)
        
        # 只有提供了 title 才入库
        if data.get('title'):
            work_id = filename.split('.')[0] if filename else data.get('title')[:8]
            cursor.execute('INSERT INTO works (id, title, type, year, status, description, source_url, filename) VALUES (?,?,?,?,?,?,?,?)',
                           (work_id, data.get('title'), data.get('type'), data.get('year'), data.get('status'), data.get('description'), data.get('source_url', ''), filename or ''))
        conn.commit()
        return jsonify({'status': 'ok'})
        conn.commit()
        return jsonify({'status': 'ok'})
    if request.method == 'DELETE':
        # Delete a work by ID in URL path
        work_id = request.view_args.get('id') if request.view_args else None
        if not work_id:
            # Try to get from JSON body
            data = request.json or {}
            work_id = data.get('id')
        if work_id:
            cursor.execute('DELETE FROM works WHERE id = ?', (work_id,))
            conn.commit()
            return jsonify({'status': 'ok'})
        return jsonify({'status': 'error', 'message': 'No work ID provided'}), 400

@app.route('/api/works/reorder', methods=['POST'])
def reorder_works():
    """批量更新作品排序"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    data = request.json or {}
    order_list = data.get('order', [])
    for idx, work_id in enumerate(order_list):
        cursor.execute('UPDATE works SET sort_order = ? WHERE id = ?', (idx, work_id))
    conn.commit()
    return jsonify({'status': 'ok'})

@app.route('/api/health')
def health(): return jsonify({'status': 'ok'})


@app.route('/api/works/<work_id>', methods=['DELETE'])
def delete_work(work_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM works WHERE id = ?', (work_id,))
    conn.commit()
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    for d in ['videos', 'photos', 'temp']: os.makedirs(os.path.join(MEDIA_DIR, d), exist_ok=True)
    app.run(host='0.0.0.0', port=5001, debug=False)
