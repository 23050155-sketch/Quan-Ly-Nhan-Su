# app/schemas/compliance.py
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel


class CompliancePolicyBase(BaseModel):
    title: str
    code: Optional[str] = None
    description: Optional[str] = None
    effective_date: date
    is_active: bool = True


class CompliancePolicyCreate(CompliancePolicyBase):
    pass


class CompliancePolicyUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    effective_date: Optional[date] = None
    is_active: Optional[bool] = None


class CompliancePolicyOut(CompliancePolicyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompliancePolicyWithStatus(CompliancePolicyOut):
    is_acknowledged: bool
    acknowledged_at: Optional[datetime] = None


class EmployeeComplianceOut(BaseModel):
    id: int
    employee_id: int
    policy_id: int
    acknowledged_at: datetime

    class Config:
        from_attributes = True