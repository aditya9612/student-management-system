from sqlalchemy import Column, Integer, String,LargeBinary
from database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(15), nullable=False)
    password = Column(String(100), nullable=False)

# File model for uploaded files
class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    data = Column(LargeBinary, nullable=False)
    student_id = Column(Integer, nullable=True)  # Optional: link to student if needed


