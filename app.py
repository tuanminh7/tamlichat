from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import json
from datetime import datetime
import hashlib
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-this'

# Cấu hình Gemini API
# Cấu hình Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # ← Thay đổi

if not GEMINI_API_KEY:
    raise ValueError(" GEMINI_API_KEY không được tìm thấy trong file .env!")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# File lưu trữ dữ liệu
USERS_FILE = 'users.json'
DATA_FILE = 'data.json'

# Khởi tạo dữ liệu mẫu
def init_data():
    # File users.json - chỉ chứa thông tin đăng nhập
    if not os.path.exists(USERS_FILE):
        users = {
            "users": {
                "gv_toan": {
                    "password": "toan123",
                    "role": "teacher",
                    "name": "Nguyễn Thị Mai"
                },
                "ht_truong": {
                    "password": "ht123",
                    "role": "admin",
                    "name": "Trần Văn Hùng"
                }
            },
            "students": {}
        }
        save_users(users)
    
    # File data.json - chỉ chứa dữ liệu trò chuyện và cảnh báo
    if not os.path.exists(DATA_FILE):
        data = {
            "conversations": {},
            "alerts": []
        }
        save_data(data)

def load_users():
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Decorator kiểm tra đăng nhập
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Phân tích tâm lý bằng Gemini
def analyze_mental_state(message, conversation_history):
    prompt = f"""
    Bạn là chuyên gia tâm lý học đường. Phân tích tin nhắn sau của học sinh và lịch sử trò chuyện để đánh giá trạng thái tâm lý:
    
    Tin nhắn mới: {message}
    
    Lịch sử: {conversation_history[-5:] if len(conversation_history) > 5 else conversation_history}
    
    Phân loại theo 3 mức độ:
    - "normal": Tâm lý bình thường, không có dấu hiệu đáng lo ngại
    - "monitor": Có dấu hiệu căng thẳng, stress, cần theo dõi (như: buồn chán kéo dài, lo âu, áp lực học tập)
    - "danger": Nguy hiểm, có dấu hiệu tự hại, tự tử, trầm cảm nghiêm trọng (từ khóa: tự tử, muốn chết, không muốn sống, tự hại, vô vọng hoàn toàn)
    
    Trả về JSON với format:
    {{
        "status": "normal/monitor/danger",
        "reason": "Lý do đánh giá",
        "keywords": ["từ khóa phát hiện"],
        "response": "Câu trả lời tư vấn cho học sinh (ấm áp, động viên, chuyên nghiệp)"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        return result
    except Exception as e:
        # FALLBACK: Phát hiện từ khóa nguy hiểm đơn giản
        danger_keywords = ['tự sát', 'tự tử', 'muốn chết', 'không muốn sống', 'tự hại', 'kết thúc cuộc đời']
        monitor_keywords = ['buồn', 'stress', 'áp lực', 'mệt mỏi', 'chán nản', 'lo lắng']
        
        message_lower = message.lower()
        
        # Kiểm tra nguy hiểm
        for keyword in danger_keywords:
            if keyword in message_lower:
                return {
                    "status": "danger",
                    "reason": f"Phát hiện từ khóa nguy hiểm: '{keyword}'. Cần can thiệp khẩn cấp!",
                    "keywords": [keyword],
                    "response": "Em ơi, thầy/cô rất lo lắng về em. Thầy/cô hiểu em đang gặp khó khăn lớn. Hãy nhớ rằng em không đơn độc, luôn có người sẵn sàng giúp đỡ em. Thầy/cô muốn nói chuyện trực tiếp với em ngay bây giờ. Em có thể gọi ngay cho thầy/cô hoặc đến phòng tư vấn được không? Sức khỏe và sự an toàn của em là điều quan trọng nhất. 📞 Hotline hỗ trợ tâm lý 24/7: 1800-xxxx"
                }
        
        # Kiểm tra cần theo dõi
        for keyword in monitor_keywords:
            if keyword in message_lower:
                return {
                    "status": "monitor",
                    "reason": f"Phát hiện dấu hiệu căng thẳng: '{keyword}'",
                    "keywords": [keyword],
                    "response": f"Thầy/cô cảm nhận được em đang có chút {keyword}. Điều này hoàn toàn bình thường, nhưng thầy/cô muốn lắng nghe và hỗ trợ em. Em có muốn chia sẻ thêm về điều gì đang làm em cảm thấy như vậy không?"
                }
        
        # Trường hợp lỗi và không có từ khóa
        return {
            "status": "normal",
            "reason": f"Lỗi phân tích AI ({str(e)}), không phát hiện từ khóa nguy hiểm",
            "keywords": [],
            "response": "Cảm ơn em đã chia sẻ. Thầy cô luôn sẵn sàng lắng nghe và hỗ trợ em bất cứ lúc nào em cần nhé!"
        }

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'student':
            return redirect(url_for('student_dashboard'))
        elif role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['user_id']
        password = request.form['password']
        
        # Kiểm tra giáo viên/admin theo username
        if username in users['users'] and users['users'][username]['password'] == password:
            session['user_id'] = username
            session['role'] = users['users'][username]['role']
            session['name'] = users['users'][username]['name']
            return redirect(url_for('index'))
        
        # Kiểm tra học sinh theo MSSV
        if username in users['students']:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if users['students'][username]['password'] == password_hash:
                session['user_id'] = username
                session['role'] = 'student'
                session['name'] = users['students'][username]['name']
                return redirect(url_for('student_dashboard'))
        
        return render_template('login.html', error='Sai tài khoản hoặc mật khẩu')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        user_id = request.form['user_id']
        
        if user_id in users['students'] or user_id in users['users']:
            return render_template('register.html', error='Tài khoản đã tồn tại')
        
        users['students'][user_id] = {
            'password': hashlib.sha256(request.form['password'].encode()).hexdigest(),
            'name': request.form['name'],
            'class': request.form['class'],
            'phone': request.form['phone'],
            'created_at': datetime.now().isoformat()
        }
        save_users(users)
        
        # Khởi tạo conversation rỗng cho học sinh
        data = load_data()
        data['conversations'][user_id] = []
        save_data(data)
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    return render_template('student_dashboard.html', name=session.get('name'))

@app.route('/student/chat', methods=['POST'])
@login_required
def student_chat():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = load_data()
    users = load_users()
    user_id = session['user_id']
    message = request.json.get('message')
    
    # Lấy lịch sử trò chuyện
    conversation_history = data['conversations'].get(user_id, [])
    
    # Phân tích tâm lý
    analysis = analyze_mental_state(message, conversation_history)
    
    # Lưu tin nhắn
    conversation_entry = {
        'timestamp': datetime.now().isoformat(),
        'student_message': message,
        'bot_response': analysis['response'],
        'status': analysis['status'],
        'reason': analysis['reason'],
        'keywords': analysis['keywords']
    }
    conversation_history.append(conversation_entry)
    data['conversations'][user_id] = conversation_history
    
    # Tạo cảnh báo nếu nguy hiểm
    if analysis['status'] == 'danger':
        alert = {
            'student_id': user_id,
            'student_info': users['students'][user_id],
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'analysis': analysis,
            'status': 'pending'
        }
        data['alerts'].append(alert)
    
    save_data(data)
    
    return jsonify({
        'response': analysis['response'],
        'status': analysis['status']
    })

@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('index'))
    
    data = load_data()
    # Lọc các cảnh báo chưa xử lý
    pending_alerts = [a for a in data['alerts'] if a['status'] == 'pending']
    
    return render_template('teacher_dashboard.html', 
                         name=session.get('name'),
                         alerts=pending_alerts)

@app.route('/teacher/intervene/<student_id>')
@login_required
def teacher_intervene(student_id):
    if session.get('role') != 'teacher':
        return redirect(url_for('index'))
    
    users = load_users()
    data = load_data()
    student_info = users['students'].get(student_id)
    conversation = data['conversations'].get(student_id, [])
    
    return render_template('teacher_intervene.html',
                         student_id=student_id,
                         student_info=student_info,
                         conversation=conversation)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    data = load_data()
    users = load_users()
    
    # Khởi tạo stats
    stats = {
        'normal': 0,
        'monitor': 0,
        'danger': 0
    }
    
    # Khởi tạo danh sách học sinh theo trạng thái
    students_by_status = {
        'normal': [],
        'monitor': [],
        'danger': []
    }
    
    # Lấy danh sách học sinh có cảnh báo nguy hiểm (pending)
    danger_student_ids = set()
    for alert in data['alerts']:
        if alert['status'] == 'pending':
            danger_student_ids.add(alert['student_id'])
    
    # Phân loại học sinh
    for student_id, conversations in data['conversations'].items():
        if not conversations:
            continue
        
        # Kiểm tra xem có trong danh sách nguy hiểm không
        if student_id in danger_student_ids:
            final_status = 'danger'
        else:
            # Lấy 10 tin nhắn gần nhất để phân tích
            recent_conversations = conversations[-10:]
            statuses = [conv.get('status', 'normal') for conv in recent_conversations]
            
            # Ưu tiên: danger > monitor > normal
            if 'danger' in statuses:
                final_status = 'danger'
            elif 'monitor' in statuses:
                final_status = 'monitor'
            else:
                final_status = 'normal'
        
        # Cập nhật thống kê
        stats[final_status] = stats.get(final_status, 0) + 1
        
        # Tạo student_data
        student_data = {
            'id': student_id,
            'info': users['students'].get(student_id) if final_status == 'danger' else None
        }
        students_by_status[final_status].append(student_data)
    
    return render_template('admin_dashboard.html',
                         name=session.get('name'),
                         stats=stats,
                         students=students_by_status,
                         alerts=data['alerts'])



############
@app.route('/student/pet')
@login_required
def student_pet():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    return render_template('student_pet.html', name=session.get('name'))


if __name__ == '__main__':
    init_data()
    app.run(debug=True)