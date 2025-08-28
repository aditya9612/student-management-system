from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import io
import models, database


class StudentBase(BaseModel):
    name: str
    email: str
    phone: str

class StudentCreate(StudentBase):
    password: str

class Student(StudentBase):
    id: int

    class Config:
        from_attributes = True   # ✅ correct for Pydantic v2
# File schemas
class FileBase(BaseModel):
    filename: str
    content_type: str


class File(FileBase):
    id: int

    class Config:
        from_attributes = True

router = APIRouter()

@router.get("/files/{file_id}")
def get_file(file_id: int, db: Session = Depends(database.get_db)):
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return StreamingResponse(
        io.BytesIO(db_file.data),
        media_type=db_file.content_type,
        headers={"Content-Disposition": f"attachment; filename={db_file.filename}"}
    )
