# app/routers/compliance.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.compliance import CompliancePolicy, EmployeeCompliance
from app.models.user import User
from app.models.employee import Employee
from app.schemas.compliance import (
    CompliancePolicyCreate,
    CompliancePolicyUpdate,
    CompliancePolicyOut,
    CompliancePolicyWithStatus,
    EmployeeComplianceOut,
)
from app.security import get_current_admin, get_current_employee

router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"],
)

# ========== ADMIN – QUẢN LÝ POLICY ==========


@router.post("/policies", response_model=CompliancePolicyOut)
def create_policy(
    payload: CompliancePolicyCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    # nếu có code và trùng -> báo lỗi
    if payload.code:
        exists = (
            db.query(CompliancePolicy)
            .filter(CompliancePolicy.code == payload.code)
            .first()
        )
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã policy đã tồn tại",
            )

    policy = CompliancePolicy(**payload.model_fields_set, **payload.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.get("/policies", response_model=List[CompliancePolicyOut])
def list_policies(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    policies = (
        db.query(CompliancePolicy)
        .order_by(CompliancePolicy.effective_date.desc())
        .all()
    )
    return policies


@router.get("/policies/{policy_id}", response_model=CompliancePolicyOut)
def get_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    policy = db.query(CompliancePolicy).get(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Không tìm thấy policy")
    return policy


@router.put("/policies/{policy_id}", response_model=CompliancePolicyOut)
def update_policy(
    policy_id: int,
    payload: CompliancePolicyUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    policy = db.query(CompliancePolicy).get(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Không tìm thấy policy")

    update_data = payload.model_dump(exclude_unset=True)

    # nếu đổi code thì check trùng
    if "code" in update_data and update_data["code"]:
        exists = (
            db.query(CompliancePolicy)
            .filter(
                CompliancePolicy.code == update_data["code"],
                CompliancePolicy.id != policy_id,
            )
            .first()
        )
        if exists:
raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã policy đã tồn tại",
            )

    for field, value in update_data.items():
        setattr(policy, field, value)

    db.commit()
    db.refresh(policy)
    return policy


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    policy = db.query(CompliancePolicy).get(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Không tìm thấy policy")

    db.delete(policy)
    db.commit()
    return None


@router.get(
    "/policies/{policy_id}/acknowledgements",
    response_model=List[EmployeeComplianceOut],
)
def list_acknowledgements(
    policy_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    policy = db.query(CompliancePolicy).get(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Không tìm thấy policy")

    acks = (
        db.query(EmployeeCompliance)
        .filter(EmployeeCompliance.policy_id == policy_id)
        .all()
    )
    return acks


# ========== EMPLOYEE – XEM POLICY + ACKNOWLEDGE ==========


@router.get("/my-policies", response_model=List[CompliancePolicyWithStatus])
def get_my_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_employee),
):
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa gắn với nhân viên",
        )

    # lấy tất cả policy đang active
    policies = (
        db.query(CompliancePolicy)
        .filter(CompliancePolicy.is_active == True)
        .order_by(CompliancePolicy.effective_date.desc())
        .all()
    )

    # lấy danh sách policy đã ack của nhân viên này
    acks = (
        db.query(EmployeeCompliance)
        .filter(EmployeeCompliance.employee_id == current_user.employee_id)
        .all()
    )
    ack_map = {a.policy_id: a for a in acks}

    result: list[CompliancePolicyWithStatus] = []
    for p in policies:
        ack = ack_map.get(p.id)
        result.append(
            CompliancePolicyWithStatus(
                id=p.id,
                title=p.title,
                code=p.code,
                description=p.description,
                effective_date=p.effective_date,
                is_active=p.is_active,
                created_at=p.created_at,
                updated_at=p.updated_at,
                is_acknowledged=ack is not None,
                acknowledged_at=ack.acknowledged_at if ack else None,
            )
        )

    return result


@router.post(
    "/policies/{policy_id}/acknowledge",
    status_code=status.HTTP_204_NO_CONTENT,
)
def acknowledge_policy(
    policy_id: int,
db: Session = Depends(get_db),
    current_user: User = Depends(get_current_employee),
):
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản chưa gắn với nhân viên",
        )

    policy = db.query(CompliancePolicy).get(policy_id)
    if not policy or not policy.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy không tồn tại hoặc không còn hiệu lực",
        )

    # đã acknowledge rồi thì thôi, có thể update timestamp nếu muốn
    ack = (
        db.query(EmployeeCompliance)
        .filter(
            EmployeeCompliance.employee_id == current_user.employee_id,
            EmployeeCompliance.policy_id == policy_id,
        )
        .first()
    )
    if ack:
        # nếu muốn update lại thời gian:
        # ack.acknowledged_at = datetime.utcnow()
        # db.commit()
        return None

    ack = EmployeeCompliance(
        employee_id=current_user.employee_id,
        policy_id=policy_id,
    )
    db.add(ack)
    db.commit()
    return None
