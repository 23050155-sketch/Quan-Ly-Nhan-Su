# app/models/compliance.py
from datetime import datetime, date

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.employee import Employee


class CompliancePolicy(Base):
    __tablename__ = "compliance_policies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=True)  # mã policy, ví dụ: SEC-001
    description = Column(Text, nullable=True)
    effective_date = Column(Date, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    acknowledgements = relationship(
        "EmployeeCompliance",
        back_populates="policy",
        cascade="all, delete-orphan",
    )


class EmployeeCompliance(Base):
    __tablename__ = "employee_compliances"
    __table_args__ = (
        UniqueConstraint("employee_id", "policy_id", name="uq_employee_policy"),
    )

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    policy_id = Column(Integer, ForeignKey("compliance_policies.id"), nullable=False)
    acknowledged_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship(Employee, backref="compliance_records")
    policy = relationship("CompliancePolicy", back_populates="acknowledgements")