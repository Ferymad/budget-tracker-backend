from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.models.category import Category
from app.models.user import User
from app.core.deps import get_current_active_user
import uuid

router = APIRouter()


@router.post("/", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new category"""
    # Check if category name already exists for this user
    query = select(Category).where(
        Category.user_id == current_user.id,
        Category.name == category.name
    )
    result = await db.execute(query)
    existing_category = result.scalar_one_or_none()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    db_category = Category(
        **category.dict(),
        user_id=current_user.id
    )
    
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    
    return db_category


@router.get("/", response_model=List[CategoryResponse])
async def read_categories(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all categories for current user"""
    query = select(Category).where(
        Category.user_id == current_user.id
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    categories = result.scalars().all()
    
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def read_category(
    category_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific category"""
    query = select(Category).where(
        Category.id == category_id,
        Category.user_id == current_user.id
    )
    result = await db.execute(query)
    category = result.scalar_one_or_none()
    
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a category"""
    query = select(Category).where(
        Category.id == category_id,
        Category.user_id == current_user.id
    )
    result = await db.execute(query)
    category = result.scalar_one_or_none()
    
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    update_data = category_update.dict(exclude_unset=True)
    
    # Check if name is being updated and if it already exists
    if "name" in update_data:
        name_query = select(Category).where(
            Category.user_id == current_user.id,
            Category.name == update_data["name"],
            Category.id != category_id
        )
        name_result = await db.execute(name_query)
        existing_category = name_result.scalar_one_or_none()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
    
    # Update category fields
    for field, value in update_data.items():
        setattr(category, field, value)
    
    await db.commit()
    await db.refresh(category)
    
    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a category"""
    query = select(Category).where(
        Category.id == category_id,
        Category.user_id == current_user.id
    )
    result = await db.execute(query)
    category = result.scalar_one_or_none()
    
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if category has associated transactions or budgets
    from app.models.transaction import Transaction
    from app.models.budget import Budget
    
    transaction_query = select(Transaction).where(Transaction.category_id == category_id)
    transaction_result = await db.execute(transaction_query)
    has_transactions = transaction_result.scalar_one_or_none() is not None
    
    budget_query = select(Budget).where(Budget.category_id == category_id)
    budget_result = await db.execute(budget_query)
    has_budgets = budget_result.scalar_one_or_none() is not None
    
    if has_transactions or has_budgets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with associated transactions or budgets"
        )
    
    await db.delete(category)
    await db.commit()
    
    return {"message": "Category deleted successfully"}