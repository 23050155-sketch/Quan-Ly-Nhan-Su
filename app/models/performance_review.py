# app/models/performance_review.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.employee import Employee
from app.models.user import User


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # ví dụ: "2025-Q1", "2025-01", "2025"
    period = Column(String(20), nullable=False)

    # điểm đánh giá 1–5
    score = Column(Integer, nullable=False)

    # vài field mô tả
    summary = Column(String(255), nullable=True)
    strengths = Column(String(255), nullable=True)
    improvements = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    employee = relationship(Employee, backref="performance_reviews")
    reviewer = relationship(User)
    # reviewer = relationship(User, backref="performance_reviews")