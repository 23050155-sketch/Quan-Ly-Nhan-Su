# app/routers/performance_review.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.performance_review import PerformanceReview
from app.models.employee import Employee
from app.models.user import User
from app.schemas.performance_review import (
    PerformanceReviewCreate,
    PerformanceReviewUpdate,
    PerformanceReviewOut,
)
from app.core.security import get_current_user, get_current_admin

router = APIRouter(
    prefix="/performance-reviews",
    tags=["Performance Reviews"],
)


# ========== LIST ==========
@router.get("/", response_model=List[PerformanceReviewOut])
def list_performance_reviews(
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    - Admin: xem tất cả, có thể filter theo employee_id.
    - Employee: chỉ xem được review của chính mình (bỏ qua query employee_id).
    """
    query = db.query(PerformanceReview)

    if current_user.role == "admin":
        if employee_id:
            query = query.filter(PerformanceReview.employee_id == employee_id)
    else:
        if not current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tài khoản này chưa gắn với nhân viên nào",
            )
        query = query.filter(
            PerformanceReview.employee_id == current_user.employee_id
        )

    reviews = query.order_by(PerformanceReview.created_at.desc()).all()
    return reviews


# ========== DETAIL ==========
@router.get("/{review_id}", response_model=PerformanceReviewOut)
def get_performance_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = db.query(PerformanceReview).filter(PerformanceReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Không tìm thấy đánh giá")

    # Employee chỉ xem được của chính mình
    if current_user.role != "admin":
        if (
            not current_user.employee_id
            or review.employee_id != current_user.employee_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền xem đánh giá này",
            )

    return review


# ========== CREATE (ADMIN) ==========
@router.post("/", response_model=PerformanceReviewOut)
def create_performance_review(
    review_in: PerformanceReviewCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    # check employee tồn tại
    emp = db.query(Employee).filter(Employee.id == review_in.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")

    review = PerformanceReview(
employee_id=review_in.employee_id,
        reviewer_id=current_admin.id,
        period=review_in.period,
        score=review_in.score,
        summary=review_in.summary,
        strengths=review_in.strengths,
        improvements=review_in.improvements,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


# ========== UPDATE (ADMIN) ==========
@router.put("/{review_id}", response_model=PerformanceReviewOut)
def update_performance_review(
    review_id: int,
    review_in: PerformanceReviewUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    review = db.query(PerformanceReview).filter(PerformanceReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Không tìm thấy đánh giá")

    data = review_in.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(review, field, value)

    db.commit()
    db.refresh(review)
    return review


# ========== DELETE (ADMIN) ==========
@router.delete("/{review_id}")
def delete_performance_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    review = db.query(PerformanceReview).filter(PerformanceReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Không tìm thấy đánh giá")

    db.delete(review)
    db.commit()
    return {"deleted": True, "id": review_id}