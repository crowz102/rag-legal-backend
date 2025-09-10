# 📚 RAG Legal Backend

Backend của hệ thống **RAG Legal** được phát triển bằng **FastAPI**, sử dụng **MySQL**, **Celery**, **RabbitMQ**, và tích hợp với **Angular Frontend**.  
Dự án hướng tới việc xây dựng một nền tảng quản lý và khai thác dữ liệu văn bản pháp lý, kết hợp các kỹ thuật **RAG (Retrieval-Augmented Generation)** và AI.

---

## 🚀 Tính năng chính

- **Xác thực & Phân quyền**  
  - Đăng ký/đăng nhập bằng JWT.  
  - Quản lý vai trò: `Uploader`, `Reviewer`, `Admin`.  

- **Quản lý hội thoại (Chat)**  
  - Lưu session & message trong cơ sở dữ liệu.  
  - Tích hợp chatbot AI (qua Celery Worker).  

- **Quản lý tài liệu**  
  - Uploader tải tài liệu (PDF/DOCX).  
  - Reviewer duyệt hoặc từ chối tài liệu (`pending`, `approved`, `rejected`).  
  - Lưu thông tin tài liệu: URL, loại, cơ quan ban hành, trạng thái.  

- **Xử lý nền (Background Tasks)**  
  - Tách biệt frontend ↔ backend bằng RabbitMQ + Celery.  
  - Hỗ trợ xử lý trích xuất nội dung tài liệu.  

- **Bảo mật**  
  - JWT cho xác thực.  
  - Bcrypt để mã hóa mật khẩu.  
  - Rate limiting và validation dữ liệu với Pydantic.  

---

## 🛠️ Công nghệ sử dụng

- FastAPI – Web framework chính.  
- MySQL – Cơ sở dữ liệu quan hệ.  
- SQLAlchemy – ORM quản lý DB.  
- Celery – Task queue.  
- RabbitMQ – Message broker.  
- Redis – Caching & rate limiting.  
- Docker (dự kiến triển khai) – Container hóa.  

---

## ⚡ Cách chạy dự án

### 1. Cài đặt môi trường
```bash
git clone https://github.com/your-org/rag-legal-backend.git
cd rag-legal-backend
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### 2. Cấu hình môi trường
Tạo file `.env` với nội dung ví dụ:
```env
DATABASE_URL=mysql+pymysql://user:password@localhost/rag_legal_db
SECRET_KEY=your_secret_key
RABBITMQ_URL=amqp://guest:guest@localhost:5672//
```
### 3. Chạy FastAPI
```bash
uvicorn main:app --reload
```
Truy cập tại: http://localhost:8000/docs

### 4. Chạy Celery worker
```bash
celery -A app.core.celery_app worker --loglevel=info
```