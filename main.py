from fastapi import FastAPI, Request, Depends, Form, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import pandas as pd
import io

import models, schemas, crud
from database import SessionLocal, engine, Base

# -------------------------------
# Setup
# -------------------------------
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create DB tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------
# Helpers
# -------------------------------
def _get_student_row(row):
    """Normalize Excel row into StudentCreate schema"""
    def get_val(keys):
        for k in keys:
            if k in row:
                return row[k]
        return ""
    return schemas.StudentCreate(
        name=str(get_val(["name", "Name"])),
        email=str(get_val(["email", "Email"])),
        phone=str(get_val(["phone", "Phone"])),
        password=str(get_val(["password", "Password"]))
    )

# -------------------------------
# Home
# -------------------------------
@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    students = crud.get_students(db)
    return templates.TemplateResponse(
        "students.html", {"request": request, "students": students}
    )

# -------------------------------
# Register
# -------------------------------
@app.get("/register")
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_student(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # Check for duplicate email
    existing = db.query(models.Student).filter(models.Student.email == email).first()
    if existing:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "❌ This email is already registered."}
        )

    # Create student
    student = crud.create_student(db, schemas.StudentCreate(
        name=name, email=email, phone=phone, password=password
    ))

    # Optional: save uploaded file
    if file:
        file_data = await file.read()
        if file_data:
            crud.save_file(db, filename=file.filename,
                           content_type=file.content_type,
                           data=file_data,
                           student_id=student.id)

    return RedirectResponse(url="/", status_code=303)

# -------------------------------
# Login
# -------------------------------
@app.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_student(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_email_password(db, email, password)
    if student:
        return templates.TemplateResponse("profile.html", {"request": request, "student": student})
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "❌ Invalid credentials"}
    )

# -------------------------------
# Password-protected view
# -------------------------------
@app.get("/student/{student_id}/verify")
def student_password_form(student_id: int, request: Request, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    return templates.TemplateResponse("student_password.html", {"request": request, "student": student})

@app.post("/student/{student_id}/verify")
def student_password_check(student_id: int, request: Request, password: str = Form(...), db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if student and student.password == password:
        return templates.TemplateResponse("student_detail.html", {"request": request, "student": student})
    return templates.TemplateResponse("student_password.html", {"request": request, "student": student, "error": "❌ Incorrect password."})

# -------------------------------
# Upload Excel
# -------------------------------
@app.get("/upload_excel")
def upload_excel_form(request: Request):
    return templates.TemplateResponse("upload_excel.html", {"request": request})

@app.post("/upload_excel")
async def upload_excel(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))

    duplicate_emails = []
    added_emails = []

    for _, row in df.iterrows():
        student_data = _get_student_row(row)
        existing = db.query(models.Student).filter(models.Student.email == student_data.email).first()
        if existing:
            duplicate_emails.append(student_data.email)
        else:
            try:
                crud.create_student(db, student_data)
                added_emails.append(student_data.email)
            except Exception as e:
                print(f"Error inserting {student_data.email}: {e}")
                continue

    messages = []
    if added_emails:
        messages.append(f"✅ Added: {', '.join(added_emails)}")
    if duplicate_emails:
        messages.append(f"❌ Skipped duplicates: {', '.join(duplicate_emails)}")
    # Always pass a list to messages, even if empty
    return templates.TemplateResponse(
        "upload_excel.html",
        {"request": request, "messages": messages}
        

          
    )
print("program run mannuely")

# -------------------------------
# Students List + Search + CRUD
# -------------------------------
@app.get("/students/", response_class=HTMLResponse)
def show_students(request: Request, db: Session = Depends(get_db)):
    students = crud.get_students(db)
    return templates.TemplateResponse("students.html", {"request": request, "students": students})

@app.get("/students/search/", response_class=HTMLResponse)
def search_students(request: Request, query: str, db: Session = Depends(get_db)):
    students = crud.search_students(db, query)
    return templates.TemplateResponse("students.html", {"request": request, "students": students, "query": query})

@app.get("/student/{student_id}/edit/")
def edit_student_form(request: Request, student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    return templates.TemplateResponse("edit_student.html", {"request": request, "student": student})

@app.post("/student/{student_id}/edit/")
def update_student(
    request: Request,
    student_id: int,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    crud.update_student(db, student_id, name, email, phone, password)
    return RedirectResponse(url="/", status_code=303)

@app.get("/student/{student_id}/delete")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    crud.delete_student(db, student_id)
    return RedirectResponse(url="/", status_code=303)
