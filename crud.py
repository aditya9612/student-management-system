# crud.py
from sqlalchemy.orm import Session
import models, schemas
from twilio.rest import Client

# -----------------------------
# File Upload Related
# -----------------------------
def save_file(db: Session, filename: str, content_type: str, data: bytes, student_id: int = None):
    """
    Save uploaded file (Excel, PDF, CSV, etc.) in the database
    """
    db_file = models.File(
        filename=filename,
        content_type=content_type,
        data=data,
        student_id=student_id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


# -----------------------------
# Student Related
# -----------------------------
def create_student(db: Session, student: schemas.StudentCreate):
    """
    Create a single student manually from form data
    """
    db_student = models.Student(
        name=student.name,
        email=student.email,
        phone=student.phone,
        password=student.password
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_students(db: Session):
    """
    Get all students
    """
    return db.query(models.Student).all()


def get_student(db: Session, student_id: int):
    """
    Get a single student by ID
    """
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def get_student_by_email_password(db: Session, email: str, password: str):
    """
    Login check: Find student by email + password
    """
    return db.query(models.Student).filter(
        models.Student.email == email,
        models.Student.password == password
    ).first()

def search_students(db: Session, query: str):
    return db.query(models.Student).filter(
        (models.Student.name.ilike(f"%{query}%")) |
        (models.Student.email.ilike(f"%{query}%"))
    ).all()
def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def update_student(db: Session, student_id: int, name: str, email: str, phone: str, password: str):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student:
        student.name = name
        student.email = email
        student.phone = phone
        student.password = password
        db.commit()
        db.refresh(student)
        # Send SMS notification for update
        send_sms(student.phone, student.name, action="updated")
    return student

def delete_student(db: Session, student_id: int):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student:
        # Send SMS notification before deleting
        send_sms(student.phone, student.name, action="deleted")
        db.delete(student)
        db.commit()
# crud.py
from sqlalchemy.orm import Session
import models, schemas
from twilio.rest import Client


# -----------------------------
# Register Student + SMS
# -----------------------------
def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(
        name=student.name,
        email=student.email,
        phone=student.phone,
        password=student.password
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    # Send welcome SMS
    send_sms(student.phone, student.name)

    return db_student


# -----------------------------
# SMS Function (Twilio)
# -----------------------------
def send_sms(to_phone: str, name: str, action: str = "registered"):
    account_sid = "your_twilio_account_sid"
    auth_token = "your_twilio_auth_token"
    client = Client(account_sid, auth_token)

    if action == "registered":
        body = f"Hi {name}, ✅ Welcome! Your registration is successful in the Student Management System."
    elif action == "updated":
        body = f"Hi {name}, your student profile has been updated."
    elif action == "deleted":
        body = f"Hi {name}, your student profile has been deleted from the system."
    else:
        body = f"Hi {name}, notification from Student Management System."

    try:
        message = client.messages.create(
            body=body,
            from_="+9960486848",   # Your Twilio phone number
            to=to_phone           # Example: "+91XXXXXXXXXX"
        )
        print(f"✅ SMS sent to {to_phone}, SID: {message.sid}")
    except Exception as e:
        print(f"❌ Failed to send SMS: {e}")



