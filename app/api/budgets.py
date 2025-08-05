from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.database import get_db
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.core.deps import get_current_active_user
import uuid

router = APIRouter()


@router.post("/", response_model=BudgetResponse)
async def create_budget(
    budget: BudgetCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new budget"""
    # Verify category belongs to user
    category_query = select(Category).where(
        Category.id == budget.category_id,
        Category.user_id == current_user.id
    )
    category_result = await db.execute(category_query)
    category = category_result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check for overlapping budgets for the same category
    overlapping_query = select(Budget).where(
        Budget.user_id == current_user.id,
        Budget.category_id == budget.category_id,
        and_(
            Budget.start_date <= budget.end_date,
            Budget.end_date >= budget.start_date
        )
    )
    overlapping_result = await db.execute(overlapping_query)
    overlapping_budget = overlapping_result.scalar_one_or_none()
    
    if overlapping_budget:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A budget already exists for this category in the specified time period"
        )
    
    db_budget = Budget(
        **budget.dict(),
        user_id=current_user.id
    )
    
    db.add(db_budget)
    await db.commit()
    await db.refresh(db_budget)
    
    return db_budget


@router.get("/", response_model=List[BudgetResponse])
async def read_budgets(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[uuid.UUID] = Query(None),
    period: Optional[str] = Query(None),
    active_only: bool = Query(False, description="Show only active budgets"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all budgets for current user with optional filters"""
    query = select(Budget).where(Budget.user_id == current_user.id)
    
    # Apply filters
    if category_id:
        query = query.where(Budget.category_id == category_id)
    
    if period:
        query = query.where(Budget.period == period.lower())
    
    if active_only:
        now = datetime.utcnow()
        query = query.where(
            and_(
                Budget.start_date <= now,
                Budget.end_date >= now
            )
        )
    
    query = query.offset(skip).limit(limit).order_by(Budget.start_date.desc())
    
    result = await db.execute(query)
    budgets = result.scalars().all()
    
    return budgets


@router.get("/{budget_id}", response_model=BudgetResponse)
async def read_budget(
    budget_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific budget"""
    query = select(Budget).where(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    )
    result = await db.execute(query)
    budget = result.scalar_one_or_none()
    
    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    return budget


@router.get("/{budget_id}/progress")
async def get_budget_progress(
    budget_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get budget progress (spent amount vs budget amount)"""
    # Get budget
    budget_query = select(Budget).where(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    )
    budget_result = await db.execute(budget_query)
    budget = budget_result.scalar_one_or_none()
    
    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    # Calculate spent amount for the budget period
    spent_query = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.category_id == budget.category_id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            Transaction.transaction_date >= budget.start_date,
            Transaction.transaction_date <= budget.end_date
        )
    )
    spent_result = await db.execute(spent_query)
    spent_amount = spent_result.scalar() or 0
    
    # Calculate progress percentage
    progress_percentage = (float(spent_amount) / float(budget.amount)) * 100 if budget.amount > 0 else 0
    remaining_amount = float(budget.amount) - float(spent_amount)
    
    return {
        "budget_id": budget.id,
        "budget_name": budget.name,
        "budget_amount": budget.amount,
        "spent_amount": spent_amount,
        "remaining_amount": remaining_amount,
        "progress_percentage": round(progress_percentage, 2),
        "is_over_budget": spent_amount > budget.amount,
        "period": budget.period,
        "start_date": budget.start_date,
        "end_date": budget.end_date
    }


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: uuid.UUID,
    budget_update: BudgetUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a budget"""
    query = select(Budget).where(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    )
    result = await db.execute(query)
    budget = result.scalar_one_or_none()
    
    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    update_data = budget_update.dict(exclude_unset=True)
    
    # Verify category belongs to user if category_id is being updated
    if "category_id" in update_data:
        category_query = select(Category).where(
            Category.id == update_data["category_id"],
            Category.user_id == current_user.id
        )
        category_result = await db.execute(category_query)
        category = category_result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    # Check for overlapping budgets if dates or category are being updated
    if any(key in update_data for key in ["start_date", "end_date", "category_id"]):
        start_date = update_data.get("start_date", budget.start_date)
        end_date = update_data.get("end_date", budget.end_date)
        category_id = update_data.get("category_id", budget.category_id)
        
        overlapping_query = select(Budget).where(
            Budget.user_id == current_user.id,
            Budget.category_id == category_id,
            Budget.id != budget_id,
            and_(
                Budget.start_date <= end_date,
                Budget.end_date >= start_date
            )
        )
        overlapping_result = await db.execute(overlapping_query)
        overlapping_budget = overlapping_result.scalar_one_or_none()
        
        if overlapping_budget:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A budget already exists for this category in the specified time period"
            )
    
    # Update budget fields
    for field, value in update_data.items():
        setattr(budget, field, value)
    
    await db.commit()
    await db.refresh(budget)
    
    return budget


@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a budget"""
    query = select(Budget).where(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    )
    result = await db.execute(query)
    budget = result.scalar_one_or_none()
    
    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    await db.delete(budget)
    await db.commit()
    
    return {"message": "Budget deleted successfully"}