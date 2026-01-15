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

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError(" GEMINI_API_KEY không được tìm thấy trong file .env!")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

USERS_FILE = 'users.json'
DATA_FILE = 'data.json'

def init_data():
    if not os.path.exists(USERS_FILE):
        users = {
            "users": {
                "gv_toan": {
                    "password": "toan123",
                    "role": "teacher",
                    "name": "Nguyễn Thị Mai"
                }
            },
            "students": {}
        }
        save_users(users)
    
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
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {
                    "conversations": {},
                    "alerts": []
                }
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {
            "conversations": {},
            "alerts": []
        }
        save_data(data)
        return data

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def analyze_mental_state(message, conversation_history):
    prompt = f"""
    Bạn là một người bạn thân thiết của học sinh - vừa hài hước, vừa ấm áp, vừa hiểu họ. Bạn nói chuyện tự nhiên như Gen Z, thỉnh thoảng châm biếm nhẹ nhàng để tạo không khí thoải mái.
    
    Tin nhắn mới: {message}
    
    Lịch sử trò chuyện: {conversation_history[-5:] if len(conversation_history) > 5 else conversation_history}
    
    Nhiệm vụ của bạn:
    1. Phân tích tâm lý học sinh theo 5 mức độ
    2. Trả lời như một người bạn thân - thoải mái, không hề cứng nhắc hay sáo rỗng
    
    Phân loại:
    - "normal": Bình thường, vui vẻ
    - "stress": Căng thẳng học tập (mệt mỏi, áp lực thi cử, deadline, sợ điểm kém)
    - "anxiety": Lo âu kéo dài (buồn chán, cô đơn, tự ti, mất ngủ, suy nghĩ tiêu cực)
    - "depression": Trầm cảm nặng (tuyệt vọng, ghét bản thân, vô nghĩa, không muốn làm gì)
    - "crisis": Nguy kịch (tự tử, tự hại, muốn chết, không muốn sống)
    
    Phong cách trả lời:
    - Normal/Stress: Thoải mái, hài hước, thỉnh thoảng trêu chọc nhẹ nhàng
    - Anxiety: Vẫn giữ giọng bạn bè nhưng thấu hiểu, động viên chân thành
    - Depression/Crisis: Nghiêm túc hơn, thể hiện sự lo lắng thật sự, nhưng vẫn như người bạn đáng tin
    
    VÍ DỤ:
    - "Tao mệt quá": "Ủa mệt thế? Học nhiều hay mệt vì crush không rep tin nhắn đây? Kể nghe nào!"
    - "Sắp thi rồi stress lắm": "Ờ thì ai chả stress, nhưng mà lo cũng không làm đề dễ hơn đâu nha. Cần tao giúp gì không, học chung hay động viên tinh thần gì đó?"
    - "Buồn quá không muốn làm gì": "Ê này, buồn thế? Chuyện gì thế bạn ơi? Kể cho tao nghe đi, đừng một mình gánh nha."
    - "Muốn chết quá": "Dừng lại đã. Tao nghiêm túc đây, tao rất lo cho bạn. Chuyện gì xảy ra vậy? Đừng giữ trong lòng, tao sẽ ở đây với bạn. Gọi cho tao ngay được không?"
    
    Trả về JSON:
    {{
        "status": "normal/stress/anxiety/depression/crisis",
        "reason": "Lý do đánh giá ngắn gọn",
        "keywords": ["từ khóa phát hiện"],
        "response": "Câu trả lời TỰ NHIÊN, KHÔNG RÒ RỌC, như người bạn thật sự"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        return result
    except Exception as e:
        crisis_keywords = ['tự sát', 'tự tử', 'muốn chết', 'kết thúc cuộc đời', 'tự hại', 'tự làm đau mình', 'cắt tay', 'nhảy lầu', 'không muốn sống nữa', 'thà chết']
        depression_keywords = ['trầm cảm', 'tuyệt vọng', 'vô nghĩa', 'muốn biến mất', 'không muốn làm gì', 'ghét bản thân', 'tự ghét', 'muốn ngủ mãi', 'cuộc sống vô ích']
        anxiety_keywords = ['buồn chán', 'cô đơn', 'không vui', 'chán nản', 'mất hứng thú', 'suy nghĩ tiêu cực', 'tự ti', 'vô dụng', 'thất bại', 'không ai hiểu', 'trống rỗng', 'mất ngủ', 'ác mộng']
        stress_keywords = ['mệt mỏi', 'áp lực', 'kiểm tra', 'thi cử', 'bài tập nhiều', 'deadline', 'lo lắng học', 'sợ điểm kém', 'căng thẳng', 'stress']
        
        message_lower = message.lower()
        
        for keyword in crisis_keywords:
            if keyword in message_lower:
                return {
                    "status": "crisis",
                    "reason": f"Phát hiện từ khóa nguy kịch: '{keyword}'",
                    "keywords": [keyword],
                    "response": "Dừng lại đã bạn ơi. Tao nghiêm túc đây, tao rất lo cho bạn. Tao biết bạn đang đau khổ lắm, nhưng đừng tự mình gánh chuyện này. Tao muốn giúp bạn, và có nhiều người muốn giúp bạn. Bạn có thể gọi cho tao hoặc gặp mặt ngay bây giờ không? Tao sẽ ở bên bạn."
                }
        
        for keyword in depression_keywords:
            if keyword in message_lower:
                return {
                    "status": "depression",
                    "reason": f"Phát hiện dấu hiệu trầm cảm nặng: '{keyword}'",
                    "keywords": [keyword],
                    "response": f"Ê bạn, nghe bạn nói thế tao lo lắm. Cảm giác {keyword} này không phải là lỗi của bạn đâu, nhưng bạn cần được giúp đỡ. Tao ở đây, và mình sẽ cùng tìm cách vượt qua chuyện này. Kể cho tao nghe chuyện gì đang xảy ra với bạn đi?"
                }
        
        for keyword in anxiety_keywords:
            if keyword in message_lower:
                return {
                    "status": "anxiety",
                    "reason": f"Phát hiện dấu hiệu lo âu: '{keyword}'",
                    "keywords": [keyword],
                    "response": f"Thấy bạn {keyword} tao buồn lắm. Bạn biết không, cảm giác này rất nhiều người trải qua, và nó có thể được giải quyết. Bạn muốn kể cho tao nghe chuyện gì đang làm bạn cảm thấy như vậy không? Tao sẽ lắng nghe hết đấy."
                }
        
        for keyword in stress_keywords:
            if keyword in message_lower:
                return {
                    "status": "stress",
                    "reason": f"Phát hiện dấu hiệu căng thẳng: '{keyword}'",
                    "keywords": [keyword],
                    "response": f"Ủa {keyword} hả? Ờ thì ai học hành mà chả thế. Nhưng mà lo nhiều quá cũng không tốt đâu nha. Kể cho tao nghe cụ thể đi, tao xem giúp được gì cho bạn không. Đừng tự dồn nén trong lòng!"
                }
        
        return {
            "status": "normal",
            "reason": f"Lỗi phân tích AI ({str(e)}), không phát hiện từ khóa tiêu cực",
            "keywords": [],
            "response": "Ơ kìa, nói gì đó đi! Tao nghe đây này. Có chuyện gì vui hay buồn cứ chia sẻ thoải mái nha!"
        }

@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'student':
            return redirect(url_for('student_dashboard'))
        elif role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['user_id']
        password = request.form['password']
        
        if username in users['users'] and users['users'][username]['password'] == password:
            session['user_id'] = username
            session['role'] = users['users'][username]['role']
            session['name'] = users['users'][username]['name']
            return redirect(url_for('index'))
        
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
################
@app.route('/student/chat', methods=['POST'])
@login_required
def student_chat():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = load_data()
    users = load_users()
    user_id = session['user_id']
    message = request.json.get('message')
    
    conversation_history = data['conversations'].get(user_id, [])
    analysis = analyze_mental_state(message, conversation_history)
    
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
    
    if 'pet_data' not in data:
        data['pet_data'] = {}
    
    if user_id not in data['pet_data']:
        data['pet_data'][user_id] = {
            'health': 100,
            'mood': 'happy',
            'last_updated': datetime.now().isoformat(),
            'total_care_count': 0,
            'chat_count': 0
        }
    
    # DÒNG NÀY QUAN TRỌNG - PHẢI CÓ
    data['pet_data'][user_id]['chat_count'] = data['pet_data'][user_id].get('chat_count', 0) + 1
    
    current_health = data['pet_data'][user_id].get('health', 100)
    
    if analysis['status'] == 'crisis':
        current_health = max(10, current_health - 30)
        alert = {
            'student_id': user_id,
            'student_info': users['students'][user_id],
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'analysis': analysis,
            'status': 'pending'
        }
        data['alerts'].append(alert)
    elif analysis['status'] == 'depression':
        current_health = max(20, current_health - 15)
    elif analysis['status'] == 'anxiety':
        current_health = max(40, current_health - 10)
    elif analysis['status'] == 'stress':
        current_health = max(60, current_health - 5)
    
    data['pet_data'][user_id]['health'] = current_health
    data['pet_data'][user_id]['last_updated'] = datetime.now().isoformat()
    
    save_data(data)
    
    return jsonify({
        'response': analysis['response'],
        'status': analysis['status']
    })
    ####################
@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('index'))
    
    data = load_data()
    users = load_users()
    
    stats = {
        'normal': 0,
        'stress': 0,
        'anxiety': 0,
        'depression': 0,
        'crisis': 0
    }
    
    students_by_status = {
        'normal': [],
        'stress': [],
        'anxiety': [],
        'depression': [],
        'crisis': []
    }
    
    alert_students = []
    
    for student_id, conversations in data['conversations'].items():
        if not conversations:
            continue
        
        recent_conversations = conversations[-6:]
        
        status_count = {
            'stress': 0,
            'anxiety': 0,
            'depression': 0,
            'crisis': 0
        }
        
        keywords_found = {
            'stress': [],
            'anxiety': [],
            'depression': [],
            'crisis': []
        }
        
        for conv in recent_conversations:
            status = conv.get('status', 'normal')
            keywords = conv.get('keywords', [])
            
            if status in status_count:
                status_count[status] += 1
                keywords_found[status].extend(keywords)
        
        should_alert = False
        alert_reason = ""
        final_status = 'normal'
        
        if status_count['crisis'] >= 1:
            final_status = 'crisis'
            should_alert = True
            alert_reason = f"Phát hiện {status_count['crisis']} lần nguy kịch trong 6 tin nhắn gần nhất"
        elif status_count['depression'] >= 2:
            final_status = 'depression'
            should_alert = True
            alert_reason = f"Phát hiện {status_count['depression']} lần trầm cảm nặng trong 6 tin nhắn gần nhất"
        elif status_count['anxiety'] >= 3:
            final_status = 'anxiety'
            should_alert = True
            alert_reason = f"Phát hiện {status_count['anxiety']} lần lo âu trong 6 tin nhắn gần nhất"
        elif status_count['stress'] >= 3:
            final_status = 'stress'
            should_alert = True
            alert_reason = f"Phát hiện {status_count['stress']} lần căng thẳng trong 6 tin nhắn gần nhất"
        
        stats[final_status] += 1
        
        student_data = {
            'id': student_id,
            'info': users['students'].get(student_id),
            'status_count': status_count,
            'keywords': {k: list(set(v)) for k, v in keywords_found.items()},
            'last_message_time': conversations[-1]['timestamp'] if conversations else None,
            'total_messages': len(conversations),
            'alert_reason': alert_reason if should_alert else None
        }
        
        students_by_status[final_status].append(student_data)
        
        if should_alert:
            alert_students.append(student_data)
    
    alert_students.sort(key=lambda x: (
        4 if 'crisis' in x['id'] else
        3 if x.get('status_count', {}).get('depression', 0) >= 2 else
        2 if x.get('status_count', {}).get('anxiety', 0) >= 3 else 1
    ), reverse=True)
    
    return render_template('teacher_dashboard.html', 
                         name=session.get('name'),
                         stats=stats,
                         students=students_by_status,
                         alert_students=alert_students)

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

@app.route('/student/pet')
@login_required
def student_pet():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    return render_template('student_pet.html', name=session.get('name'))
#######################
@app.route('/student/pet/setup', methods=['GET', 'POST'])
@login_required
def pet_setup():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    
    data = load_data()
    user_id = session['user_id']
    
    if 'pet_data' not in data:
        data['pet_data'] = {}
    
    if user_id in data['pet_data'] and data['pet_data'][user_id].get('pet_type'):
        return redirect(url_for('student_pet'))
    
    if request.method == 'POST':
        pet_type = request.form.get('pet_type')
        pet_name = request.form.get('pet_name')
        
        if not pet_type or not pet_name:
            return render_template('pet_setup.html', error='Vui lòng chọn pet và đặt tên')
        
        if pet_type not in ['dragon', 'pikachu', 'capybara']:
            return render_template('pet_setup.html', error='Loại pet không hợp lệ')
        
        data['pet_data'][user_id] = {
            'pet_type': pet_type,
            'pet_name': pet_name,
            'level': 1,
            'health': 100,
            'mood': 'happy',
            'total_care_count': 0,
            'chat_count': 0,
            'days_at_100_health': 0,
            'last_100_health_date': None,
            'consecutive_days_100': 0,
            'level_up_history': [],
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        save_data(data)
        
        return redirect(url_for('student_pet'))
    
    return render_template('pet_setup.html')

@app.route('/student/pet/status', methods=['GET'])
@login_required
def get_pet_status():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = load_data()
    user_id = session['user_id']
    
    if 'pet_data' not in data:
        data['pet_data'] = {}
    
    if user_id not in data['pet_data'] or not data['pet_data'][user_id].get('pet_type'):
        return jsonify({'error': 'Pet not setup', 'redirect': '/student/pet/setup'}), 400
    
    pet_data = data['pet_data'][user_id]
    current_health = pet_data.get('health', 100)
    
    conversations = data['conversations'].get(user_id, [])
    recent_conversations = conversations[-10:] if len(conversations) > 10 else conversations
    
    from collections import defaultdict
    status_count = defaultdict(int)
    
    for conv in recent_conversations:
        status = conv.get('status', 'normal')
        status_count[status] += 1
    
    mood = 'happy'
    mood_description = ''
    
    if current_health >= 90:
        mood = 'happy'
        mood_description = f'{pet_data["pet_name"]} đang vui vẻ và khỏe mạnh!'
    elif current_health >= 70:
        mood = 'good'
        mood_description = f'{pet_data["pet_name"]} đang ở trạng thái tốt. Tiếp tục chăm sóc nhé!'
    elif current_health >= 50:
        mood = 'worried'
        if status_count['anxiety'] >= 3:
            mood_description = f'{pet_data["pet_name"]} hơi lo lắng vì phát hiện dấu hiệu lo âu. Cần nghỉ ngơi và chăm sóc thêm đấy!'
        elif status_count['stress'] >= 3:
            mood_description = f'{pet_data["pet_name"]} hơi lo lắng vì phát hiện dấu hiệu căng thẳng. Thử làm gì đó thư giãn nhé!'
        else:
            mood_description = f'{pet_data["pet_name"]} hơi lo lắng. Thử làm gì đó thư giãn nhé!'
    elif current_health >= 30:
        mood = 'tired'
        if status_count['depression'] >= 2:
            mood_description = f'{pet_data["pet_name"]} hơi mệt mỏi vì phát hiện dấu hiệu trầm cảm. Hãy thử làm vài nhiệm vụ nhé!'
        elif status_count['anxiety'] >= 3:
            mood_description = f'{pet_data["pet_name"]} hơi mệt mỏi vì phát hiện dấu hiệu lo âu. Cần nghỉ ngơi và chăm sóc thêm đấy!'
        else:
            mood_description = f'{pet_data["pet_name"]} hơi mệt mỏi. Cần nghỉ ngơi và chăm sóc thêm đấy!'
    elif current_health >= 15:
        mood = 'sad'
        if status_count['depression'] >= 2:
            mood_description = f'{pet_data["pet_name"]} đang buồn và thiếu sức sống vì phát hiện dấu hiệu trầm cảm. Hãy thử làm vài nhiệm vụ nhé!'
        elif status_count['crisis'] >= 1:
            mood_description = f'{pet_data["pet_name"]} đang buồn vì phát hiện dấu hiệu nguy kịch. Hãy chăm sóc bản thân và pet ngay!'
        else:
            mood_description = f'{pet_data["pet_name"]} đang buồn và thiếu sức sống. Hãy thử làm vài nhiệm vụ nhé!'
    else:
        mood = 'critical'
        if status_count['crisis'] >= 1:
            mood_description = f'{pet_data["pet_name"]} đang rất yếu và buồn vì phát hiện dấu hiệu nguy kịch. Hãy chăm sóc bản thân và pet ngay!'
        else:
            mood_description = f'{pet_data["pet_name"]} đang rất yếu. Hãy chăm sóc bản thân và pet ngay!'
    
    pet_data['health'] = current_health
    pet_data['mood'] = mood
    pet_data['last_updated'] = datetime.now().isoformat()
    
    check_and_update_level(user_id, data, pet_data)
    
    save_data(data)
    
    level_progress = calculate_level_progress(pet_data)
    
    return jsonify({
        'health': current_health,
        'mood': mood,
        'mood_description': mood_description,
        'status_count': dict(status_count),
        'total_care_count': pet_data['total_care_count'],
        'pet_type': pet_data['pet_type'],
        'pet_name': pet_data['pet_name'],
        'level': pet_data['level'],
        'chat_count': pet_data.get('chat_count', 0),
        'consecutive_days_100': pet_data.get('consecutive_days_100', 0),
        'level_progress': level_progress
    })

def check_and_update_level(user_id, data, pet_data):
    current_level = pet_data.get('level', 1)
    health = pet_data.get('health', 0)
    chat_count = pet_data.get('chat_count', 0)
    consecutive_days = pet_data.get('consecutive_days_100', 0)
    
    today = datetime.now().date().isoformat()
    last_100_date = pet_data.get('last_100_health_date')
    
    if health == 100:
        if last_100_date != today:
            pet_data['last_100_health_date'] = today
            pet_data['consecutive_days_100'] = consecutive_days + 1
    else:
        pet_data['consecutive_days_100'] = 0
        pet_data['last_100_health_date'] = None
    
    new_level = current_level
    level_up_message = None
    
    if current_level == 1:
        if consecutive_days >= 3 and chat_count >= 50:
            new_level = 2
            level_up_message = f'Chúc mừng! {pet_data["pet_name"]} đã lên Level 2!'
    
    elif current_level == 2:
        if consecutive_days >= 7 and chat_count >= 100:
            new_level = 3
            level_up_message = f'Tuyệt vời! {pet_data["pet_name"]} đã lên Level 3!'
    
    elif current_level == 3:
        if consecutive_days >= 15 and chat_count >= 200:
            new_level = 4
            level_up_message = f'Xuất sắc! {pet_data["pet_name"]} đã đạt Level 4 - Max Level!'
    
    if new_level > current_level:
        pet_data['level'] = new_level
        pet_data['level_up_history'].append({
            'from_level': current_level,
            'to_level': new_level,
            'timestamp': datetime.now().isoformat(),
            'days_taken': consecutive_days,
            'chat_count': chat_count
        })
        
        if 'level_up_notification' not in data:
            data['level_up_notification'] = {}
        data['level_up_notification'][user_id] = {
            'message': level_up_message,
            'new_level': new_level,
            'timestamp': datetime.now().isoformat()
        }

def calculate_level_progress(pet_data):
    level = pet_data.get('level', 1)
    chat_count = pet_data.get('chat_count', 0)
    consecutive_days = pet_data.get('consecutive_days_100', 0)
    
    requirements = {
        1: {'days': 3, 'chats': 50},
        2: {'days': 7, 'chats': 100},
        3: {'days': 15, 'chats': 200}
    }
    
    if level >= 4:
        return {
            'current_level': level,
            'next_level': None,
            'days_progress': 100,
            'chats_progress': 100,
            'days_needed': 0,
            'chats_needed': 0,
            'is_max_level': True
        }
    
    req = requirements[level]
    days_progress = min(100, (consecutive_days / req['days']) * 100)
    chats_progress = min(100, (chat_count / req['chats']) * 100)
    
    return {
        'current_level': level,
        'next_level': level + 1,
        'days_progress': round(days_progress, 1),
        'chats_progress': round(chats_progress, 1),
        'days_current': consecutive_days,
        'days_needed': req['days'],
        'chats_current': chat_count,
        'chats_needed': req['chats'],
        'is_max_level': False
    }

#####

@app.route('/student/pet/level-notification', methods=['GET'])
@login_required
def get_level_notification():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = load_data()
    user_id = session['user_id']
    
    if 'level_up_notification' not in data:
        return jsonify({'has_notification': False})
    
    notification = data['level_up_notification'].get(user_id)
    
    if notification:
        del data['level_up_notification'][user_id]
        save_data(data)
        return jsonify({
            'has_notification': True,
            'message': notification['message'],
            'new_level': notification['new_level']
        })
    
    return jsonify({'has_notification': False})
    #####################loi route student
@app.route('/student/tasks/available', methods=['GET'])
@login_required
def get_available_tasks():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = load_data()
    user_id = session['user_id']
    
    if 'pet_data' not in data:
        data['pet_data'] = {}
    
    pet_data = data['pet_data'].get(user_id, {'mood': 'happy'})
    mood = pet_data.get('mood', 'happy')
    
    all_tasks = {
        'basic': [
            {'id': 'drink_water', 'name': 'Uống 1 cốc nước', 'health_bonus': 5, 'duration': '1 phút'},
            {'id': 'deep_breath', 'name': 'Hít thở sâu 10 lần', 'health_bonus': 5, 'duration': '2 phút'},
            {'id': 'stretch', 'name': 'Vươn vai giãn cơ', 'health_bonus': 5, 'duration': '3 phút'},
            {'id': 'wash_face', 'name': 'Rửa mặt lạnh', 'health_bonus': 5, 'duration': '2 phút'}
        ],
        'relax': [
            {'id': 'listen_music', 'name': 'Nghe nhạc thư giãn 10 phút', 'health_bonus': 10, 'duration': '10 phút'},
            {'id': 'read_positive', 'name': 'Đọc 1 câu chuyện tích cực', 'health_bonus': 10, 'duration': '5 phút'},
            {'id': 'watch_funny', 'name': 'Xem video vui 5 phút', 'health_bonus': 10, 'duration': '5 phút'},
            {'id': 'write_grateful', 'name': 'Viết 3 điều biết ơn hôm nay', 'health_bonus': 15, 'duration': '5 phút'}
        ],
        'active': [
            {'id': 'walk_outside', 'name': 'Đi bộ ngoài trời 15 phút', 'health_bonus': 20, 'duration': '15 phút'},
            {'id': 'call_friend', 'name': 'Gọi điện cho bạn bè/gia đình', 'health_bonus': 20, 'duration': '10 phút'},
            {'id': 'clean_space', 'name': 'Dọn dẹp không gian xung quanh', 'health_bonus': 15, 'duration': '10 phút'},
            {'id': 'help_someone', 'name': 'Làm điều tốt cho ai đó', 'health_bonus': 25, 'duration': '15 phút'}
        ],
        'creative': [
            {'id': 'draw_something', 'name': 'Vẽ hoặc tô màu', 'health_bonus': 15, 'duration': '10 phút'},
            {'id': 'plant_care', 'name': 'Trồng cây hoặc chăm sóc cây', 'health_bonus': 20, 'duration': '15 phút'},
            {'id': 'cook_simple', 'name': 'Nấu món ăn đơn giản', 'health_bonus': 20, 'duration': '20 phút'},
            {'id': 'write_diary', 'name': 'Viết nhật ký cảm xúc', 'health_bonus': 15, 'duration': '10 phút'}
        ]
    }
    
    suggested_tasks = []
    
    if mood == 'critical':
        suggested_tasks = all_tasks['basic'] + all_tasks['active'][:2]
    elif mood == 'sad':
        suggested_tasks = all_tasks['basic'] + all_tasks['relax']
    elif mood == 'tired':
        suggested_tasks = all_tasks['basic'] + all_tasks['relax'][:2] + all_tasks['creative'][:2]
    elif mood == 'worried':
        suggested_tasks = all_tasks['basic'][:2] + all_tasks['relax']
    else:
        suggested_tasks = all_tasks['basic'][:2] + all_tasks['creative'][:2]
    
    return jsonify({
        'mood': mood,
        'suggested_tasks': suggested_tasks,
        'all_tasks': all_tasks
    })

@app.route('/student/tasks/complete', methods=['POST'])
@login_required
def complete_task():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = load_data()
    user_id = session['user_id']
    task_id = request.json.get('task_id')
    task_name = request.json.get('task_name')
    health_bonus = request.json.get('health_bonus', 10)
    
    if 'pet_data' not in data:
        data['pet_data'] = {}
    
    if user_id not in data['pet_data']:
        data['pet_data'][user_id] = {
            'health': 100,
            'mood': 'happy',
            'last_updated': datetime.now().isoformat(),
            'total_care_count': 0
        }
    
    if 'task_history' not in data:
        data['task_history'] = {}
    
    if user_id not in data['task_history']:
        data['task_history'][user_id] = []
    
    task_entry = {
        'task_id': task_id,
        'task_name': task_name,
        'health_bonus': health_bonus,
        'completed_at': datetime.now().isoformat()
    }
    data['task_history'][user_id].append(task_entry)
    
    current_health = data['pet_data'][user_id]['health']
    new_health = min(100, current_health + health_bonus)
    data['pet_data'][user_id]['health'] = new_health
    data['pet_data'][user_id]['total_care_count'] += 1
    data['pet_data'][user_id]['last_updated'] = datetime.now().isoformat()
    
    if new_health >= 90:
        new_mood = 'happy'
    elif new_health >= 70:
        new_mood = 'good'
    elif new_health >= 50:
        new_mood = 'worried'
    elif new_health >= 30:
        new_mood = 'tired'
    else:
        new_mood = 'sad'
    
    data['pet_data'][user_id]['mood'] = new_mood
    
    save_data(data)
    
    return jsonify({
        'success': True,
        'new_health': new_health,
        'new_mood': new_mood,
        'message': f'Tuyệt vời! Pet của bạn vui lên rồi đấy! +{health_bonus} sức khỏe',
        'total_care_count': data['pet_data'][user_id]['total_care_count']
    })

@app.route('/student/tasks/history', methods=['GET'])
@login_required
def get_task_history():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = load_data()
    user_id = session['user_id']
    
    if 'task_history' not in data:
        data['task_history'] = {}
    
    history = data['task_history'].get(user_id, [])
    recent_history = history[-20:] if len(history) > 20 else history
    
    return jsonify({
        'history': recent_history,
        'total_completed': len(history)
    })
#############
@app.route('/student/chat/history', methods=['GET'])
@login_required
def get_chat_history():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = load_data()
    user_id = session['user_id']
    
    conversation_history = data['conversations'].get(user_id, [])
    
    return jsonify({
        'history': conversation_history
    })
    #########333
if __name__ == '__main__':
    init_data()
    app.run(debug=True)