from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.models.transaction import Transaction, TransactionType
from app.models.category import Category
from app.models.user import User
from app.core.deps import get_current_active_user
import uuid

router = APIRouter()


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new transaction"""
    # Verify category belongs to user
    category_query = select(Category).where(
        Category.id == transaction.category_id,
        Category.user_id == current_user.id
    )
    category_result = await db.execute(category_query)
    category = category_result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    db_transaction = Transaction(
        **transaction.dict(),
        user_id=current_user.id
    )
    
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    
    return db_transaction


@router.get("/", response_model=List[TransactionResponse])
async def read_transactions(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[uuid.UUID] = Query(None),
    transaction_type: Optional[TransactionType] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all transactions for current user with optional filters"""
    query = select(Transaction).where(Transaction.user_id == current_user.id)
    
    # Apply filters
    if category_id:
        query = query.where(Transaction.category_id == category_id)
    
    if transaction_type:
        query = query.where(Transaction.transaction_type == transaction_type)
    
    if start_date:
        query = query.where(Transaction.transaction_date >= start_date)
    
    if end_date:
        query = query.where(Transaction.transaction_date <= end_date)
    
    query = query.offset(skip).limit(limit).order_by(Transaction.transaction_date.desc())
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def read_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific transaction"""
    query = select(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    )
    result = await db.execute(query)
    transaction = result.scalar_one_or_none()
    
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: uuid.UUID,
    transaction_update: TransactionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a transaction"""
    query = select(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    )
    result = await db.execute(query)
    transaction = result.scalar_one_or_none()
    
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    update_data = transaction_update.dict(exclude_unset=True)
    
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
    
    # Update transaction fields
    for field, value in update_data.items():
        setattr(transaction, field, value)
    
    await db.commit()
    await db.refresh(transaction)
    
    return transaction


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a transaction"""
    query = select(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    )
    result = await db.execute(query)
    transaction = result.scalar_one_or_none()
    
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    await db.delete(transaction)
    await db.commit()
    
    return {"message": "Transaction deleted successfully"}