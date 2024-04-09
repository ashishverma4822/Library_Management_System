from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from typing import List, Optional

app = FastAPI()


try:
    client = MongoClient("mongodb+srv://vashishk0602:jaCDL3NLjQ8K9vXy@cluster0.mtt1isj.mongodb.net/")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error connecting to MongoDB: {str(e)}")
db = client.get_database("library")
students_collection = db.get_collection("students")

# Pydantic models
class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

class StudentOut(Student):
    _id: Optional[str]


@app.get("/favicon.ico")
async def get_favicon():
    raise HTTPException(status_code=404)

# Root endpoint
@app.get("/")
async def read_root():
    return {"Welcome to the Library Management API"}

# API Endpoints
@app.post("/students", response_model=StudentOut, status_code=201)
async def create_student(student: Student):
    try:
        student_data = student.dict()
        result = students_collection.insert_one(student_data)
        student_data["_id"] = str(result.inserted_id)
        return StudentOut(**student_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/students", response_model=List[StudentOut])
async def list_students(country: Optional[str] = None, age: Optional[int] = None):
    try:
        query = {}
        if country:
            query["address.country"] = country
        if age:
            query["age"] = {"$gte": age}
        students = students_collection.find(query)
        student_objects = [StudentOut(**student) for student in students]  # List comprehension
        return student_objects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/students/{id}", response_model=StudentOut)
async def fetch_student(id: str):
    try:
        student = students_collection.find_one({"_id": ObjectId(id)})
        if student:
            student['_id'] = str(student['_id'])
            return StudentOut(**student)
        else:
            raise HTTPException(status_code=404, detail="Student not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.patch("/students/{id}")
async def update_student(id: str, student: Student):
    try:
        student_data = student.dict(exclude_unset=True)
        if student_data:
            result = students_collection.update_one({"_id": ObjectId(id)}, {"$set": student_data})
            if result.modified_count == 1:
                return {"message": "Student updated successfully"}
            else:
                raise HTTPException(status_code=404, detail="Student not found")
        else:
            raise HTTPException(status_code=400, detail="No data provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.delete("/students/{id}")
async def delete_student(id: str):
    try:
        result = students_collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 1:
            return {"message": "Student deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Student not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


