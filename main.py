import utils.session
from fastapi import FastAPI
from pydantic import BaseModel, validator
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
import re
from typing import List

app = FastAPI()

DATABASE_URL = "sqlite:///./uni.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, index=True)
    age = Column(Integer)
    courses = Column(String)

Base.metadata.create_all(bind=engine)

class StudentCreate(BaseModel):
    name: str
    email: str
    age: int
    courses: List[str]

    @validator('name')
    def validate_name(cls, v):
        if not re.match("^[A-Za-z ]*$", v):
            raise ValueError('Name must contain only alphabets and spaces.')
        if len(v) < 1 or len(v) > 50:
            raise ValueError('Name must be between 1 and 50 characters.')
        return v

    @validator('age')
    def validate_age(cls, v):
        if v < 18 or v > 30:
            raise ValueError('Age must be between 18 and 30.')
        return v

    @validator('courses')
    def validate_courses(cls, v):
        if len(v) < 1 or len(v) > 5:
            raise ValueError('There must be between 1 and 5 courses.')
        if len(set(v)) != len(v):
            raise ValueError('Course names must be unique.')
        for course in v:
            if len(course) < 5 or len(course) > 30:
                raise ValueError('Each course name must be between 5 and 30 characters.')
        return v




@app.get("/")
def home():
    return 'Welcome to App'

@app.post("/student/register")
def register(data: dict):
    
    try:
        student= StudentCreate(**data)
        db = SessionLocal()
        db_student = db.query(Student).filter(Student.email == student.email).first()
        id = (db.query(Student).count() + 1000)
        if db_student:
            raise ValueError("Email Already Exists")
        new_student = Student(
            id=id,
            name=student.name,
            email=student.email,
            age=student.age,
            courses=",".join(student.courses)
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return new_student
    
    except Exception as e:
        return {
            "message": str(e),
            "status": "error",
            "data" : []
        }

@app.get("/student/{student_id}")
def get(student_id: int):
    try:
        if student_id < 1000 or student_id > 9999:
            raise ValueError("Invalid Id")
        db = SessionLocal()
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return {
                "message": "invalid ID",
                "status": "error",
                "data" : None
            }
        student.courses = student.courses.split(',')
        return {
                "message": "Sucess",
                "status": "success",
                "data" : student
            }
    
    except Exception as e:
        return {
            "message": str(e),
            "status": "error",
            "data" : []
        }
    

@app.put("/student/{student_id}/email")
def update(student_id: int,data: dict):
    # return data['email']
    try:
        
        if student_id < 1000 or student_id > 9999:
            raise ValueError("Invalid Id")
        db = SessionLocal()
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return {
                "message": "invalid ID",
                "status": "error",
                "data" : None
            }
        
        student.email = data['email']
        db.commit()
        db.refresh(student)
        student.courses = student.courses.split(',')
        return {
                "message": "Student Email Updated",
                "status": "success",
                "data" : student
            }
    
    except Exception as e:
        return {
            "message": str(e),
            "status": "error",
            "data" : []
        }