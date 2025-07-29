import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.user import User, Role
from app.core.security import get_password_hash

db = SessionLocal()

# Kiểm tra role admin đã có chưa
admin_role = db.query(Role).filter_by(name="admin").first()
if not admin_role:
    admin_role = Role(name="admin")
    db.add(admin_role)
    db.commit()
    db.refresh(admin_role)

# Tạo admin nếu chưa có
admin_email = "admin@example.com"
existing = db.query(User).filter_by(email=admin_email).first()
if not existing:
    admin_user = User(
        username="admin",
        fullname="Admin FIS",
        phone="+84123456",
        email=admin_email,
        hashed_password=get_password_hash("admin123"),
        role_id=admin_role.id,
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    print("✅ Admin user created.")
else:
    print("⚠️ Admin user already exists.")

db.close()
