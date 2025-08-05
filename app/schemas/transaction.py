from pydantic import BaseModel, validator
from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid
from app.models.transaction import TransactionType


class TransactionBase(BaseModel):
    amount: Decimal
    description: str
    transaction_type: TransactionType
    transaction_date: datetime
    category_id: uuid.UUID

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > Decimal('999999999.99'):
            raise ValueError('Amount cannot exceed 999,999,999.99')
        # Ensure max 2 decimal places
        if v.as_tuple().exponent < -2:
            raise ValueError('Amount cannot have more than 2 decimal places')
        return v

    @validator('description')
    def validate_description(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Description cannot be empty')
        if len(v) > 500:
            raise ValueError('Description cannot exceed 500 characters')
        return v.strip()


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    transaction_type: Optional[TransactionType] = None
    transaction_date: Optional[datetime] = None
    category_id: Optional[uuid.UUID] = None

    @validator('amount')
    def validate_amount(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Amount must be greater than 0')
            if v > Decimal('999999999.99'):
                raise ValueError('Amount cannot exceed 999,999,999.99')
            if v.as_tuple().exponent < -2:
                raise ValueError('Amount cannot have more than 2 decimal places')
        return v

    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            if len(v.strip()) < 1:
                raise ValueError('Description cannot be empty')
            if len(v) > 500:
                raise ValueError('Description cannot exceed 500 characters')
            return v.strip()
        return v


class TransactionResponse(TransactionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True