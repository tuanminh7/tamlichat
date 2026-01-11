# Hệ thống Giám sát Tâm lý Học sinh

## 📋 Mục lục
1. [Cài đặt](#cài-đặt)
2. [Cấu hình](#cấu-hình)
3. [Chạy ứng dụng](#chạy-ứng-dụng)
4. [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
5. [Tài khoản mặc định](#tài-khoản-mặc-định)

## 🔧 Cài đặt

### Bước 1: Cài đặt Python
Đảm bảo bạn đã cài Python 3.8 trở lên

### Bước 2: Tạo thư mục dự án
```bash
mkdir mental_health_system
cd mental_health_system
```

### Bước 3: Tạo cấu trúc thư mục
```
mental_health_system/
├── app.py
├── users.json (tự động tạo - chứa thông tin đăng nhập)
├── data.json (tự động tạo - chứa lịch sử chat & cảnh báo)
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    ├── student_dashboard.html
    ├── teacher_dashboard.html
    ├── teacher_intervene.html
    └── admin_dashboard.html
```

### Bước 4: Cài đặt thư viện
```bash
pip install flask google-generativeai
```

## ⚙️ Cấu hình

### 1. Lấy Gemini API Key
1. Truy cập: https://aistudio.google.com/app/apikey
2. Đăng nhập bằng tài khoản Google
3. Nhấn "Create API Key"
4. Copy API key

### 2. Cấu hình trong app.py
Mở file `app.py` và thay đổi:
```python
GEMINI_API_KEY = 'YOUR_GEMINI_API_KEY_HERE'  # Thay bằng API key của bạn
app.secret_key = 'your-secret-key-here-change-this'  # Đổi thành chuỗi bất kỳ
```

### 3. Tùy chỉnh tài khoản giáo viên và admin
Trong file `app.py`, tìm hàm `init_data()` và sửa:
```python
"users": {
    "gv_toan": {  # Username để đăng nhập
        "password": "toan123",
        "role": "teacher",
        "name": "Nguyễn Thị Mai"  # Tên hiển thị
    },
    "gv_ly": {
        "password": "ly123",
        "role": "teacher",
        "name": "Trần Văn Phú"
    },
    "ht_truong": {
        "password": "ht123",
        "role": "admin",
        "name": "Lê Thị Hoa"
    }
}
```

Hoặc chỉnh trực tiếp file `data.json` sau khi chạy app lần đầu.

## 🚀 Chạy ứng dụng

```bash
python app.py
```

Sau đó truy cập: http://127.0.0.1:5000

## 📖 Hướng dẫn sử dụng

### Đối với Học sinh 👨‍🎓

1. **Đăng ký tài khoản**
   - Nhấn "Đăng ký ngay" tại trang đăng nhập
   - Điền đầy đủ thông tin: MSSV, mật khẩu, họ tên, lớp, số điện thoại
   - Nhấn "Đăng ký"

2. **Đăng nhập**
   - Nhập MSSV và mật khẩu
   - Nhấn "Đăng nhập"

3. **Tư vấn tâm lý**
   - Chat với bot tư vấn tâm lý
   - Chia sẻ cảm xúc, suy nghĩ của bạn
   - Bot sẽ lắng nghe và tư vấn
   - **Lưu ý**: Hệ thống tự động phân tích và cảnh báo nếu phát hiện dấu hiệu nguy hiểm

### Đối với Giáo viên (Chuyên gia Tâm lý) 👨‍⚕️

1. **Đăng nhập**
   - Username: `gv_toan`
   - Password: `toan123`

2. **Xem cảnh báo**
   - Hệ thống hiển thị học sinh ở trạng thái NGUY HIỂM
   - Xem đầy đủ thông tin: họ tên, lớp, số điện thoại, nội dung chat

3. **Can thiệp**
   - Nhấn "Can thiệp ngay"
   - Xem lịch sử trò chuyện đầy đủ
   - Liên hệ trực tiếp với học sinh

### Đối với Nhà trường (Admin) 🏫

1. **Đăng nhập**
   - Username: `ht_truong`
   - Password: `ht123`

2. **Xem thống kê**
   - Biểu đồ tổng quan: Bình thường / Theo dõi / Nguy hiểm
   - Danh sách học sinh theo từng trạng thái

3. **Bảo mật thông tin**
   - **Bình thường**: Chỉ hiển thị ID
   - **Theo dõi**: Chỉ hiển thị ID
   - **Nguy hiểm**: Hiển thị đầy đủ thông tin (để xử lý khẩn cấp)

## 🔐 Tài khoản mặc định

### Giáo viên
- **Tài khoản**: teacher1
- **Mật khẩu**: teacher123

### Nhà trường (Admin)
- **Tài khoản**: admin1
- **Mật khẩu**: admin123

### Học sinh
- Cần đăng ký tài khoản mới

## 🎯 Nguyên lý hoạt động

### Phân loại trạng thái tâm lý

1. **Bình thường (Normal)** ✅
   - Không có dấu hiệu bất thường
   - Chỉ hiển thị ID cho admin

2. **Theo dõi (Monitor)** ⚠️
   - Có dấu hiệu: stress, lo âu, áp lực học tập
   - Chỉ hiển thị ID cho admin
   - Cần theo dõi thêm

3. **Nguy hiểm (Danger)** 🚨
   - Phát hiện từ khóa: tự tử, muốn chết, tự hại, vô vọng
   - **Gửi cảnh báo ngay cho giáo viên và nhà trường**
   - Hiển thị đầy đủ thông tin học sinh
   - Giáo viên can thiệp trực tiếp

### Quy trình xử lý

```
Học sinh chat với bot
    ↓
Gemini 2.5 phân tích tâm lý
    ↓
Phân loại: Normal / Monitor / Danger
    ↓
Nếu Danger → Cảnh báo ngay
    ↓
Giáo viên can thiệp
    ↓
Admin giám sát tổng quan
```

## 🛡️ Bảo mật

- **Tách biệt dữ liệu**: 
  - `users.json`: Chỉ chứa thông tin đăng nhập (giáo viên, admin, học sinh)
  - `data.json`: Chứa lịch sử chat và cảnh báo (tách riêng để bảo mật)
- **Mật khẩu học sinh**: Được mã hóa SHA-256 trước khi lưu
- **Mật khẩu giáo viên/admin**: Lưu dạng plain text để dễ quản lý
- **Quyền truy cập**: Chỉ admin và giáo viên mới thấy thông tin nhạy cảm
- **Session-based authentication**: Kiểm soát truy cập chặt chẽ

## 💡 Lưu ý quan trọng

1. **Không share API key** của Gemini
2. **Đổi secret_key** trong app.py trước khi deploy
3. **Backup 2 file JSON** định kỳ:
   - `users.json`: Thông tin đăng nhập
   - `data.json`: Lịch sử chat & cảnh báo
4. **Theo dõi cảnh báo** thường xuyên
5. Hệ thống chỉ là **công cụ hỗ trợ**, cần kết hợp tư vấn trực tiếp
6. **Phân quyền file**: Chỉ admin server mới được truy cập 2 file JSON

## 🐛 Xử lý lỗi

### Lỗi: "Invalid API Key"
- Kiểm tra lại GEMINI_API_KEY
- Đảm bảo đã kích hoạt API tại Google AI Studio

### Lỗi: "Module not found"
- Chạy lại: `pip install flask google-generativeai`

### Lỗi: "Template not found"
- Kiểm tra cấu trúc thư mục templates/
- Đảm bảo tất cả file HTML đã được tạo

### Lỗi: "File not found"
- Kiểm tra xem `users.json` và `data.json` đã được tạo chưa
- Xóa 2 file này và chạy lại app để tạo mới

## 📞 Hỗ trợ

Nếu cần hỗ trợ thêm, hãy kiểm tra:
- Log trong terminal khi chạy app
- File `users.json` để debug thông tin đăng nhập
- File `data.json` để debug lịch sử chat
- Console trong trình duyệt (F12) để xem lỗi frontend