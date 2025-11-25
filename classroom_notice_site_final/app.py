
from flask import Flask, render_template, request, redirect, session, url_for, jsonify, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room, send
from datetime import datetime, timedelta
import os
import time

app = Flask(__name__)
app.secret_key = 'devkey'
socketio = SocketIO(app)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

valid_users = {}
leaders = {str(i): {"leader": "", "subleader": ""} for i in range(1, 10)}
attendance = {str(i): set() for i in range(1, 10)}
notices = {str(i): [] for i in range(1, 10)}
last_upload_time = {}

for cls in range(1, 10):
    for num in range(1, 25):
        user_id = f"phhs{cls}{num:02d}"
        valid_users[user_id] = user_id + "!!"
    master_id = f"master{cls}"
    valid_users[master_id] = master_id + "**"

def validate_login(user_id, password):
    return user_id in valid_users and valid_users[user_id] == password

def get_class_id(user_id):
    return user_id[4] if user_id.startswith("phhs") else user_id[-1]

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('classroom', class_id=get_class_id(session['user_id'])))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['user_id']
    password = request.form['password']
    if validate_login(user_id, password):
        session['user_id'] = user_id
        return redirect(url_for('classroom', class_id=get_class_id(user_id)))
    return "로그인 실패"

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/class/<class_id>')
def classroom(class_id):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return render_template('classroom.html', class_id=class_id)

@app.route('/attendance/<class_id>', methods=['POST'])
def mark_attendance(class_id):
    if 'user_id' in session:
        attendance[class_id].add(session['user_id'])
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'unauthorized'})

@app.route('/attendance/<class_id>', methods=['GET'])
def get_attendance(class_id):
    return jsonify(list(attendance[class_id]))

@app.route('/notice/<class_id>', methods=['GET'])
def get_notice(class_id):
    return jsonify(notices[class_id])

@app.route('/notice/<class_id>', methods=['POST'])
def post_notice(class_id):
    if 'user_id' not in session:
        return jsonify({'status': 'unauthorized'})
    user_id = session['user_id']
    class_id = str(class_id)
    leaders_in_class = leaders[class_id]
    if not (user_id.startswith('master') or user_id == leaders_in_class['leader'] or user_id == leaders_in_class['subleader']):
        return jsonify({'status': 'unauthorized'})
    data = request.get_json()
    message = data.get('message', '')
    notices[class_id].append(message)
    return jsonify({'status': 'ok'})

@app.route('/set_leader/<class_id>', methods=['POST'])
def set_leader(class_id):
    if 'user_id' not in session or not session['user_id'].startswith('master'):
        return jsonify({'status': 'unauthorized'})
    data = request.get_json()
    leaders[class_id]['leader'] = data.get('leader', '')
    leaders[class_id]['subleader'] = data.get('subleader', '')
    return jsonify({'status': 'ok'})

@app.route('/upload/<class_id>', methods=['POST'])
def upload_file(class_id):
    if 'user_id' not in session:
        return jsonify({'status': 'unauthorized'})
    user_id = session['user_id']
    now = time.time()
    if user_id in last_upload_time and now - last_upload_time[user_id] < 30:
        return jsonify({'status': 'wait'})
    file = request.files.get('file')
    if file:
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], class_id)
        os.makedirs(save_path, exist_ok=True)
        filename = f"{int(now)}_{file.filename}"
        filepath = os.path.join(save_path, filename)
        file.save(filepath)
        last_upload_time[user_id] = now
        return jsonify({'status': 'ok', 'filename': filename})
    return jsonify({'status': 'nofile'})

@app.route('/uploads/<class_id>/<filename>')
def uploaded_file(class_id, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], class_id), filename)

@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    send(f"{session['user_id']}님이 입장했습니다.", to=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    msg = data['message']
    timestamp = datetime.now().strftime('%H:%M:%S')
    send(f"[{timestamp}] {session['user_id']}: {msg}", to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
