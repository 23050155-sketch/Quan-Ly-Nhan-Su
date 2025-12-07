from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    gender = Column(String(10))
    birth_date = Column(Date)
    position = Column(String(50))
    department = Column(String(50))
    start_date = Column(Date)
