from pydantic import BaseModel, validator
from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid


class BudgetBase(BaseModel):
    name: str
    amount: Decimal
    period: str
    start_date: datetime
    end_date: datetime
    category_id: uuid.UUID

    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Budget name cannot be empty')
        if len(v) > 100:
            raise ValueError('Budget name cannot exceed 100 characters')
        return v.strip()

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Budget amount must be greater than 0')
        if v > Decimal('999999999.99'):
            raise ValueError('Budget amount cannot exceed 999,999,999.99')
        if v.as_tuple().exponent < -2:
            raise ValueError('Budget amount cannot have more than 2 decimal places')
        return v

    @validator('period')
    def validate_period(cls, v):
        valid_periods = ['daily', 'weekly', 'monthly', 'yearly']
        if v.lower() not in valid_periods:
            raise ValueError(f'Period must be one of: {", ".join(valid_periods)}')
        return v.lower()

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[Decimal] = None
    period: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category_id: Optional[uuid.UUID] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if len(v.strip()) < 1:
                raise ValueError('Budget name cannot be empty')
            if len(v) > 100:
                raise ValueError('Budget name cannot exceed 100 characters')
            return v.strip()
        return v

    @validator('amount')
    def validate_amount(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Budget amount must be greater than 0')
            if v > Decimal('999999999.99'):
                raise ValueError('Budget amount cannot exceed 999,999,999.99')
            if v.as_tuple().exponent < -2:
                raise ValueError('Budget amount cannot have more than 2 decimal places')
        return v

    @validator('period')
    def validate_period(cls, v):
        if v is not None:
            valid_periods = ['daily', 'weekly', 'monthly', 'yearly']
            if v.lower() not in valid_periods:
                raise ValueError(f'Period must be one of: {", ".join(valid_periods)}')
            return v.lower()
        return v


class BudgetResponse(BudgetBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True