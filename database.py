from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import io
import models, database

MYSQL_URL = "mysql+pymysql://root:root@localhost:3306/student_db"

engine = create_engine(MYSQL_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI to get DB session
def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

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
