MINDBUDDY - Hệ thống Hỗ trợ Sức khỏe Tâm lý Học sinh
Hệ thống web application hỗ trợ theo dõi và can thiệp sớm các vấn đề sức khỏe tâm lý của học sinh thông qua chatbot AI và hệ thống pet ảo động viên.

Tổng quan dự án
Đây là một ứng dụng web Flask được thiết kế để giúp giáo viên theo dõi tình trạng tâm lý của học sinh thông qua các cuộc trò chuyện với chatbot AI. Hệ thống sử dụng Google Gemini AI để phân tích cảm xúc và phát hiện sớm các dấu hiệu bất thường về tâm lý.

Các tính năng chính

Hệ thống xác thực người dùng

Đăng nhập/đăng ký cho học sinh và giáo viên
Phân quyền theo vai trò (student/teacher)
Mã hóa mật khẩu bằng SHA-256


Chatbot hỗ trợ tâm lý

Trò chuyện với học sinh bằng giọng điệu Gen Z thân thiện
Phân tích tự động trạng thái tâm lý qua 5 mức độ
Phát hiện từ khóa nguy hiểm và cảnh báo


Hệ thống pet ảo

Học sinh nuôi pet ảo (dragon/pikachu/capybara)
Sức khỏe pet phản ánh tình trạng tâm lý của học sinh
Hệ thống level từ 1-4 dựa trên việc chăm sóc bản thân
Tasks (nhiệm vụ) để cải thiện sức khỏe pet và tâm lý


Dashboard giáo viên

Theo dõi tổng quan tình trạng tâm lý các học sinh
Hệ thống cảnh báo tự động
Xem chi tiết lịch sử trò chuyện
Can thiệp kịp thời khi phát hiện dấu hiệu nguy hiểm




Cấu trúc thư mục
project/
├── app.py                 (File backend chính)
├── users.json            (Dữ liệu người dùng)
├── data.json             (Dữ liệu hội thoại, cảnh báo, pet)
├── .env                  (API keys và cấu hình)
├── templates/            (HTML templates)
│   ├── login.html
│   ├── register.html
│   ├── student_dashboard.html
│   ├── student_pet.html
│   ├── pet_setup.html
│   ├── teacher_dashboard.html
│   └── teacher_intervene.html
└── static/               (CSS, JS, images)

Yêu cầu hệ thống
Phiên bản Python: 3.7 trở lên
Các thư viện cần thiết:
Flask==2.3.0
google-generativeai==0.3.1
python-dotenv==1.0.0

Cài đặt
Bước 1: Clone repository hoặc tải source code
Bước 2: Tạo môi trường ảo (khuyến nghị)
bashpython -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
Bước 3: Cài đặt dependencies
bashpip install -r requirements.txt
```

Bước 4: Tạo file .env và cấu hình API key
```
GEMINI_API_KEY=your_google_gemini_api_key_here
Lấy API key tại: https://makersuite.google.com/app/apikey
Bước 5: Chạy ứng dụng
bashpython app.py
Ứng dụng sẽ chạy tại: http://localhost:5000

Hướng dẫn sử dụng
DÀNH CHO HỌC SINH

Đăng ký tài khoản

Truy cập /register
Điền thông tin: Mã số học sinh, họ tên, lớp, số điện thoại
Tạo mật khẩu


Đăng nhập và thiết lập pet

Chọn loại pet (dragon/pikachu/capybara)
Đặt tên cho pet


Trò chuyện với chatbot

Chia sẻ cảm xúc, tâm trạng hàng ngày
Chatbot sẽ phân tích và phản hồi thân thiện
Sức khỏe pet thay đổi theo trạng thái tâm lý


Chăm sóc pet

Làm các nhiệm vụ (tasks) để tăng sức khỏe pet
Duy trì sức khỏe 100% liên tục để nâng cấp level
Level tối đa: 4



DÀNH CHO GIÁO VIÊN

Đăng nhập

Tài khoản mặc định: gv_toan / toan123


Dashboard tổng quan

Xem thống kê học sinh theo 5 mức độ
Danh sách cảnh báo học sinh cần can thiệp
Phân loại: Normal, Stress, Anxiety, Depression, Crisis


Can thiệp

Click vào học sinh để xem chi tiết
Đọc lịch sử trò chuyện
Liên hệ trực tiếp khi cần thiết




Phân tích trạng thái tâm lý
Hệ thống phân loại tâm lý thành 5 mức độ:

NORMAL - Bình thường

Không có dấu hiệu bất thường
Tâm trạng ổn định, vui vẻ


STRESS - Căng thẳng học tập

Từ khóa: mệt mỏi, áp lực, deadline, thi cử
Giảm 5 điểm sức khỏe pet
Cần theo dõi


ANXIETY - Lo âu

Từ khóa: buồn chán, cô đơn, mất ngủ, tự ti
Giảm 10 điểm sức khỏe pet
Cần can thiệp nhẹ


DEPRESSION - Trầm cảm

Từ khóa: tuyệt vọng, vô nghĩa, ghét bản thân
Giảm 15 điểm sức khỏe pet
Cần can thiệp nghiêm túc


CRISIS - Nguy kịch

Từ khóa: tự tử, tự hại, muốn chết
Giảm 30 điểm sức khỏe pet
Cảnh báo khẩn cấp cho giáo viên




Hệ thống cảnh báo tự động
Giáo viên nhận cảnh báo khi:

1 lần phát hiện crisis trong 6 tin nhắn gần nhất
2 lần phát hiện depression trong 6 tin nhắn gần nhất
3 lần phát hiện anxiety trong 6 tin nhắn gần nhất
3 lần phát hiện stress trong 6 tin nhắn gần nhất


Hệ thống Pet và Leveling
CÁC CHỈ SỐ PET

Health (Sức khỏe): 0-100
Mood (Tâm trạng): happy, good, worried, tired, sad, critical
Level: 1-4
Chat count: Số lượng tin nhắn đã gửi
Consecutive days at 100 health: Số ngày liên tục duy trì sức khỏe 100%

YÊU CẦU NÂNG CẤP LEVEL
Level 1 -> Level 2:

3 ngày liên tục sức khỏe 100%
50 tin nhắn trở lên

Level 2 -> Level 3:

7 ngày liên tục sức khỏe 100%
100 tin nhắn trở lên

Level 3 -> Level 4 (Max):

15 ngày liên tục sức khỏe 100%
200 tin nhắn trở lên


Hệ thống Tasks (Nhiệm vụ)
BASIC TASKS (Cơ bản)

Uống 1 cốc nước: +5 health
Hít thở sâu 10 lần: +5 health
Vươn vai giãn cơ: +5 health
Rửa mặt lạnh: +5 health

RELAX TASKS (Thư giãn)

Nghe nhạc thư giãn 10 phút: +10 health
Đọc câu chuyện tích cực: +10 health
Xem video vui 5 phút: +10 health
Viết 3 điều biết ơn: +15 health

ACTIVE TASKS (Năng động)

Đi bộ ngoài trời 15 phút: +20 health
Gọi điện bạn bè/gia đình: +20 health
Dọn dẹp không gian: +15 health
Làm điều tốt cho ai đó: +25 health

CREATIVE TASKS (Sáng tạo)

Vẽ hoặc tô màu: +15 health
Chăm sóc cây: +20 health
Nấu món ăn đơn giản: +20 health
Viết nhật ký cảm xúc: +15 health


API Endpoints
AUTHENTICATION
POST /login - Đăng nhập
POST /register - Đăng ký học sinh
GET /logout - Đăng xuất
STUDENT ENDPOINTS
GET /student/dashboard - Trang chủ học sinh
POST /student/chat - Gửi tin nhắn chatbot
GET /student/chat/history - Lịch sử trò chuyện
GET /student/pet - Trang pet
GET /student/pet/setup - Thiết lập pet lần đầu
POST /student/pet/setup - Lưu cấu hình pet
GET /student/pet/status - Lấy trạng thái pet
GET /student/pet/level-notification - Kiểm tra thông báo lên level
GET /student/tasks/available - Lấy danh sách tasks
POST /student/tasks/complete - Hoàn thành task
GET /student/tasks/history - Lịch sử tasks
TEACHER ENDPOINTS
GET /teacher/dashboard - Dashboard giáo viên
GET /teacher/intervene/<student_id> - Chi tiết học sinh

Cấu trúc dữ liệu
FILE users.json
json{
  "users": {
    "gv_toan": {
      "password": "toan123",
      "role": "teacher",
      "name": "Nguyễn Thị Mai"
    }
  },
  "students": {
    "hs001": {
      "password": "hashed_password",
      "name": "Nguyễn Văn A",
      "class": "10A1",
      "phone": "0123456789",
      "created_at": "2024-01-15T10:30:00"
    }
  }
}
FILE data.json
json{
  "conversations": {
    "hs001": [
      {
        "timestamp": "2024-01-15T10:30:00",
        "student_message": "Em stress quá",
        "bot_response": "Ủa stress thế?...",
        "status": "stress",
        "reason": "Phát hiện từ khóa căng thẳng",
        "keywords": ["stress"]
      }
    ]
  },
  "pet_data": {
    "hs001": {
      "pet_type": "dragon",
      "pet_name": "Rồng Xanh",
      "level": 2,
      "health": 85,
      "mood": "good",
      "chat_count": 67,
      "consecutive_days_100": 5,
      "total_care_count": 12
    }
  },
  "task_history": {
    "hs001": [
      {
        "task_id": "drink_water",
        "task_name": "Uống 1 cốc nước",
        "health_bonus": 5,
        "completed_at": "2024-01-15T11:00:00"
      }
    ]
  },
  "alerts": []
}

Bảo mật

Mật khẩu học sinh được mã hóa SHA-256
Session-based authentication với secret key
Role-based access control (RBAC)
API key được lưu trong .env (không commit lên git)

LƯU Ý: Trong môi trường production, nên:

Sử dụng HTTPS
Thay đổi secret_key mạnh hơn
Sử dụng database thay vì JSON files
Implement password hashing mạnh hơn (bcrypt, argon2)


Xử lý lỗi
Hệ thống có fallback mechanism khi AI không phân tích được:

Sử dụng keyword matching dự phòng
Trả về response mặc định an toàn
Log lỗi để debug


Mở rộng trong tương lai

Tích hợp database (PostgreSQL/MySQL)
Real-time notifications (WebSocket)
Export báo cáo PDF
Biểu đồ thống kê chi tiết
Mobile app (React Native/Flutter)
Tích hợp với hệ thống quản lý học sinh hiện có
Đa ngôn ngữ
Phân tích sentiment nâng cao hơn


Liên hệ và đóng góp
Nếu phát hiện lỗi hoặc có đề xuất cải tiến, vui lòng:

Tạo issue trên repository
Gửi pull request với mô tả chi tiết
Liên hệ qua email support


License
Dự án này được phát triển cho mục đích giáo dục và hỗ trợ sức khỏe tâm lý học sinh.

Lưu ý quan trọng
Hệ thống này là công cụ hỗ trợ, KHÔNG THAY THẾ được:

Tư vấn tâm lý chuyên nghiệp
Can thiệp y tế khi cần thiết
Sự quan tâm của gia đình và thầy cô

Khi phát hiện tình huống nguy hiểm, cần:

Liên hệ ngay với gia đình học sinh
Thông báo cho chuyên gia tâm lý trường học
Gọi đường dây nóng hỗ trợ tâm lý nếu cần
