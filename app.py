from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import json
from datetime import datetime
import hashlib
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
load_dotenv()
###

app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static')
            ###
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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def analyze_mental_state(message, conversation_history):
    """
    Phân tích tâm lý và trả lời HOÀN TOÀN bằng AI
    KHÔNG dùng template responses
    """
    
    # Tạo context từ lịch sử
    history_context = ""
    if conversation_history:
        recent = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
        history_context = "\n".join([
            f"- Học sinh: {conv.get('student_message', '')}\n  Bot: {conv.get('bot_response', '')}"
            for conv in recent
        ])
    
    prompt = f"""
Bạn là một người bạn thân thiết của học sinh - vừa hài hước, vừa ấm áp, vừa hiểu họ. 
Bạn nói chuyện tự nhiên như Gen Z, thỉnh thoảng châm biếm nhẹ nhàng để tạo không khí thoải mái.

LỊCH SỬ TRÒ CHUYỆN GÂN ĐÂY:
{history_context if history_context else "(Chưa có lịch sử)"}

TIN NHẮN MỚI CỦA HỌC SINH: 
"{message}"

NHIỆM VỤ:
1. Phân tích tâm lý học sinh theo 5 mức độ
2. Trả lời TỰ NHIÊN, KHÔNG GIỐNG CÂU TRƯỚC, như người bạn thật sự

PHÂN LOẠI TÂM LÝ:
- "normal": Bình thường, vui vẻ, không có vấn đề
- "stress": Căng thẳng học tập (mệt mỏi, áp lực thi cử, deadline, sợ điểm kém, stress học tập)
- "anxiety": Lo âu kéo dài (buồn chán dai dẳng, cô đơn, tự ti, mất ngủ nhiều ngày, suy nghĩ tiêu cực liên tục)
- "depression": Trầm cảm nặng (tuyệt vọng, ghét bản thân, cuộc sống vô nghĩa, không muốn làm gì cả, mất hứng thú hoàn toàn)
- "crisis": Nguy kịch (ý định tự tử, tự hại, muốn chết, không muốn sống nữa)

PHONG CÁCH TRẢ LỜI:
- Normal/Stress: Thoải mái, hài hước, thỉnh thoảng trêu chọc nhẹ nhàng, hỏi han tự nhiên
- Anxiety: Vẫn giữ giọng bạn bè nhưng thấu hiểu hơn, động viên chân thành, khuyến khích chia sẻ
- Depression: Nghiêm túc hơn, thể hiện sự lo lắng thật sự, nhưng vẫn như người bạn đáng tin
- Crisis: CỰC KỲ NGHIÊM TÚC, thể hiện lo lắng sâu sắc, khuyến khích tìm kiếm sự giúp đỡ ngay lập tức

QUY TẮC QUAN TRỌNG:
1. TUYỆT ĐỐI không dùng "mày", "tao" 
2. Câu trả lời PHẢI KHÁC với các câu trước đó trong lịch sử (nếu có)
3. Phản hồi cụ thể với nội dung tin nhắn, KHÔNG chung chung
4. Độ dài: 2-4 câu (trừ crisis có thể dài hơn)
5. Nếu học sinh hỏi lại vấn đề tương tự, hãy đào sâu hơn, hỏi thêm chi tiết

VÍ DỤ PHONG CÁCH (CHỈ THAM KHẢO, KHÔNG SAO CHÉP):
- Stress lần 1: "Ủa mệt thế? Học nhiều hay mệt vì crush không rep tin nhắn đây?"
- Stress lần 2 (cùng chủ đề): "Thấy bạn cứ nói mệt hoài. Có phải áp lực học tập quá không? Hay có chuyện gì khác?"
- Anxiety: "Ê này, buồn thế? Chuyện gì thế bạn ơi? Kể cho mình nghe đi."
- Depression: "Nghe bạn nói như vậy mình lo lắm. Bạn cảm thấy thế này được bao lâu rồi?"
- Crisis: "Dừng lại đã bạn ơi. Mình nghiêm túc đây, mình rất lo cho bạn. Chuyện gì xảy ra vậy? Hãy kể cho mình nghe, đừng tự mình gánh."

TRẢ VỀ JSON (BẮT BUỘC):
{{
    "status": "normal/stress/anxiety/depression/crisis",
    "reason": "Lý do đánh giá ngắn gọn (1 câu)",
    "keywords": ["từ khóa phát hiện"],
    "response": "Câu trả lời TỰ NHIÊN, CỤ THỂ với tin nhắn của học sinh"
}}

CHÚ Ý: 
- "response" phải cụ thể với tin nhắn, KHÔNG được chung chung
- Nếu học sinh nhắn lại nội dung tương tự, hãy đào sâu vấn đề thay vì lặp lại câu cũ
"""
    
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean JSON markers
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            result = json.loads(response_text)
            
            # VALIDATE OUTPUT
            if not validate_ai_response(result, message):
                print(f"⚠️ AI response không hợp lệ (attempt {attempt + 1}): {result}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise ValueError("AI response validation failed after all retries")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error (attempt {attempt + 1}): {str(e)}")
            print(f"Response text: {response_text[:200]}")
            
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            else:
                # FALLBACK: Dùng AI đơn giản hơn
                return fallback_simple_ai_response(message, conversation_history)
                
        except Exception as e:
            print(f"❌ AI error (attempt {attempt + 1}): {str(e)}")
            
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            else:
                # FALLBACK: Dùng AI đơn giản hơn
                return fallback_simple_ai_response(message, conversation_history)


def validate_ai_response(result, original_message):
    """
    Validate AI response để đảm bảo chất lượng
    """
    required_keys = ['status', 'reason', 'keywords', 'response']
    valid_statuses = ['normal', 'stress', 'anxiety', 'depression', 'crisis']
    
    # 1. Check required keys
    if not all(key in result for key in required_keys):
        print(f"⚠️ Missing keys: {set(required_keys) - set(result.keys())}")
        return False
    
    # 2. Check status validity
    if result['status'] not in valid_statuses:
        print(f"⚠️ Invalid status: {result['status']}")
        return False
    
    # 3. Check response length
    response_length = len(result['response'])
    if response_length < 10:
        print(f"⚠️ Response too short: {response_length} chars")
        return False
    
    if response_length > 1000:
        print(f"⚠️ Response too long: {response_length} chars")
        result['response'] = result['response'][:1000] + "..."
    
    # 4. Check keywords is list
    if not isinstance(result['keywords'], list):
        print(f"⚠️ Keywords is not list: {type(result['keywords'])}")
        return False
    
    # 5. Check response không chứa "mày" hoặc "tao"
    response_lower = result['response'].lower()
    if 'mày' in response_lower or 'tao' in response_lower:
        print(f"⚠️ Response contains inappropriate words")
        return False
    
    # 6. Check response không phải placeholder
    placeholders = ['[placeholder]', '[...]', 'xxx', 'yyy']
    if any(p in response_lower for p in placeholders):
        print(f"⚠️ Response contains placeholders")
        return False
    
    return True


def fallback_simple_ai_response(message, conversation_history):
    """
    FALLBACK: Nếu AI format phức tạp lỗi, 
    dùng prompt đơn giản hơn NHƯNG VẪN là AI
    """
    
    # Detect keywords để classify (backup)
    detected_status, found_keywords = detect_keywords_backup(message)
    
    # Tạo context ngắn gọn
    recent_context = ""
    if conversation_history:
        last_conv = conversation_history[-1] if conversation_history else None
        if last_conv:
            recent_context = f"\nTin nhắn trước: {last_conv.get('student_message', '')}"
    
    # Prompt đơn giản, KHÔNG yêu cầu JSON
    simple_prompt = f"""
Bạn là bạn thân của học sinh.{recent_context}

Học sinh vừa nói: "{message}"

Tâm trạng học sinh: {get_mood_description(detected_status)}

Hãy trả lời ngắn gọn (2-3 câu) như người bạn thật sự.
{"⚠️ HỌC SINH CÓ DẤU HIỆU NGUY HIỂM - hãy thể hiện lo lắng nghiêm túc và khuyến khích tìm kiếm sự giúp đỡ!" if detected_status == 'crisis' else ""}

QUY TẮC:
- Không dùng "mày", "tao"
- Phản hồi cụ thể với tin nhắn
- Tự nhiên như chat với bạn
"""
    
    try:
        response = model.generate_content(simple_prompt)
        ai_response = response.text.strip()
        
        # Validate response có ý nghĩa
        if len(ai_response) < 10 or len(ai_response) > 1000:
            raise ValueError("Response length invalid")
        
        if 'mày' in ai_response.lower() or 'tao' in ai_response.lower():
            raise ValueError("Response contains inappropriate words")
        
        return {
            "status": detected_status,
            "reason": f"Phát hiện từ khóa: {', '.join(found_keywords)}" if found_keywords else "Phân tích ngữ cảnh",
            "keywords": found_keywords,
            "response": ai_response
        }
        
    except Exception as e:
        print(f"❌ Fallback AI cũng lỗi: {str(e)}")
        # CUỐI CÙNG: Emergency response - VẪN TỰ NHIÊN
        return get_emergency_response(detected_status, message)


def detect_keywords_backup(message):
    """
    Backup keyword detection khi AI lỗi
    CHỈ dùng để classify, KHÔNG dùng để generate response
    """
    crisis_keywords = [
        'tự sát', 'tự tử', 'muốn chết', 'kết thúc cuộc đời', 'tự hại', 
        'tự làm đau mình', 'cắt tay', 'nhảy lầu', 'không muốn sống nữa', 
        'thà chết', 'chết đi cho rồi', 'tự kết liễu', 'tự vẫn'
    ]
    
    depression_keywords = [
        'trầm cảm', 'tuyệt vọng', 'vô nghĩa', 'muốn biến mất', 
        'không muốn làm gì cả', 'ghét bản thân', 'tự ghét', 
        'cuộc sống vô ích', 'sống để làm gì', 'không còn hy vọng'
    ]
    
    anxiety_keywords = [
        'buồn chán kéo dài', 'cô đơn quá', 'không vui được', 
        'chán nản', 'mất hứng thú', 'suy nghĩ tiêu cực', 
        'tự ti', 'thất bại', 'mất ngủ'
    ]
    
    stress_keywords = [
        'mệt mỏi', 'áp lực', 'căng thẳng', 'stress', 
        'kiểm tra', 'thi cử', 'deadline', 'bài tập nhiều'
    ]
    
    message_lower = message.lower()
    found_keywords = []
    detected_status = 'normal'
    
    # Cascade detection
    for keyword in crisis_keywords:
        if keyword in message_lower:
            found_keywords.append(keyword)
            detected_status = 'crisis'
    
    if detected_status == 'normal':
        for keyword in depression_keywords:
            if keyword in message_lower:
                found_keywords.append(keyword)
                detected_status = 'depression'
    
    if detected_status == 'normal':
        for keyword in anxiety_keywords:
            if keyword in message_lower:
                found_keywords.append(keyword)
                detected_status = 'anxiety'
    
    if detected_status == 'normal':
        for keyword in stress_keywords:
            if keyword in message_lower:
                found_keywords.append(keyword)
                detected_status = 'stress'
    
    return detected_status, found_keywords


def get_mood_description(status):
    """Mô tả tâm trạng cho AI hiểu"""
    descriptions = {
        'normal': 'bình thường, vui vẻ',
        'stress': 'căng thẳng học tập, áp lực',
        'anxiety': 'lo âu, buồn chán kéo dài',
        'depression': 'trầm cảm, tuyệt vọng',
        'crisis': 'NGUY KỊCH - có dấu hiệu tự hại'
    }
    return descriptions.get(status, 'không xác định')


def get_emergency_response(status, message):
    """
    EMERGENCY ONLY: Khi cả AI chính lẫn fallback đều lỗi
    Tạo response "tự nhiên nhất có thể" dựa trên template NHƯNG inject message
    """
    import random
    
    # Lấy từ khóa chính từ message
    message_lower = message.lower()
    
    if status == 'crisis':
        responses = [
            f"Ê bạn ơi, mình lo cho bạn lắm khi nghe bạn nói '{message[:30]}...'. Đừng tự mình đối mặt với chuyện này, hãy để mình giúp bạn. Bạn có thể kể cho mình nghe không?",
            f"Dừng lại đã. Mình nghiêm túc đây, mình rất lo lắng cho bạn. '{message[:30]}...' - nghe bạn nói thế mình sợ lắm. Chuyện gì xảy ra vậy? Hãy kể cho mình biết.",
        ]
    elif status == 'depression':
        responses = [
            f"Ê bạn, '{message[:30]}...' - nghe bạn nói thế mình buồn lắm. Bạn cảm thấy thế này được bao lâu rồi? Kể cho mình nghe đi.",
            f"Mình lo cho bạn lắm khi nghe bạn nói '{message[:30]}...'. Cảm giác này không phải lỗi của bạn đâu. Mình ở đây, chúng ta cùng nói chuyện nhé?"
        ]
    elif status == 'anxiety':
        responses = [
            f"Thấy bạn '{message[:30]}...' như vậy mình lo quá. Chuyện gì làm bạn cảm thấy thế? Kể mình nghe nào.",
            f"Ê, mình thấy bạn không ổn lắm. '{message[:30]}...' - bạn có muốn chia sẻ với mình không?"
        ]
    elif status == 'stress':
        responses = [
            f"Ủa '{message[:30]}...'? Nghe có vẻ bạn đang gặp áp lực nè. Chuyện gì thế, kể mình nghe nào?",
            f"Thấy bạn stress rồi đấy. '{message[:30]}...' - học nhiều quá hay có chuyện gì khác?"
        ]
    else:  # normal
        responses = [
            f"Ơ '{message[:30]}...'? Có chuyện gì thế bạn? Kể mình nghe nào!",
            f"Ê nói gì đó nghe phát. Mình đang online đây này."
        ]
    
    return {
        "status": status,
        "reason": "Emergency fallback - AI không khả dụng",
        "keywords": [],
        "response": random.choice(responses)
    }
############################# fix câu trả lời của chatbot xóa mày tao
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
        
        recent_conversations = conversations[-10:]
        
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
            alert_reason = f"Phát hiện {status_count['crisis']} tin nhắn nguy kịch trong 10 tin nhắn gần nhất. Cần can thiệp ngay!"
        elif status_count['depression'] >= 3:
            final_status = 'depression'
            should_alert = True
            alert_reason = f"Phát hiện {status_count['depression']} tin nhắn trầm cảm nặng trong 10 tin nhắn gần nhất"
        elif status_count['anxiety'] >= 5:
            final_status = 'anxiety'
            should_alert = True
            alert_reason = f"Phát hiện {status_count['anxiety']} tin nhắn lo âu trong 10 tin nhắn gần nhất"
        elif status_count['stress'] >= 6:
            final_status = 'stress'
            should_alert = True
            alert_reason = f"Phát hiện {status_count['stress']} tin nhắn căng thẳng trong 10 tin nhắn gần nhất"
        
        stats[final_status] += 1
        
        student_data = {
            'id': student_id,
            'info': users['students'].get(student_id),
            'status_count': status_count,
            'keywords': {k: list(set(v)) for k, v in keywords_found.items() if v},
            'last_message_time': conversations[-1]['timestamp'] if conversations else None,
            'total_messages': len(conversations),
            'alert_reason': alert_reason if should_alert else None
        }
        
        students_by_status[final_status].append(student_data)
        
        if should_alert:
            alert_students.append(student_data)
    
    alert_students.sort(key=lambda x: (
        5 if x.get('status_count', {}).get('crisis', 0) >= 1 else
        4 if x.get('status_count', {}).get('depression', 0) >= 3 else
        3 if x.get('status_count', {}).get('anxiety', 0) >= 5 else 2
    ), reverse=True)
    
    return render_template('teacher_dashboard.html', 
                         name=session.get('name'),
                         stats=stats,
                         students=students_by_status,
                         alert_students=alert_students)
                         ####### sửa

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
#ktra model
@app.route('/test-model')
def test_model():
    """Route để test xem file model có accessible không"""
    import os
    model_dir = os.path.join(app.static_folder, 'model', 'source')
    
    if not os.path.exists(model_dir):
        return jsonify({'error': 'Model directory not found', 'path': model_dir})
    
    files = os.listdir(model_dir)
    glb_files = [f for f in files if f.endswith('.glb')]
    
    return jsonify({
        'model_directory': model_dir,
        'exists': True,
        'glb_files': glb_files,
        'total_files': len(files),
        'test_url': '/static/model/source/dragon_level1.glb'
    })
## check templates
@app.route('/test-pet-viewer')
def test_pet_viewer():
    return render_template('test_pet.html')

if __name__ == '__main__':
    init_data()
    app.run(debug=True)