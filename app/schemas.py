from pydantic import BaseModel
from typing import Optional

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None

class Category(CategoryBase):
    id: int
    user_id: Optional[int]

    class Config:
        orm_mode = True
    
    
# Expense Schemas
from datetime import date
from pydantic import validator, Field

class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be positive")
    date: date
    description: Optional[str] = None
    category_id: int
    user_id: int

    @validator('date')
    def date_not_in_future(cls, v):
        from datetime import date as dt_date
        if v > dt_date.today():
            raise ValueError('Date cannot be in the future')
        return v

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    date: Optional[date]
    description: Optional[str]
    category_id: Optional[int]
    user_id: Optional[int]

    @validator('date')
    def date_not_in_future(cls, v):
        if v is not None:
            from datetime import date as dt_date
            if v > dt_date.today():
                raise ValueError('Date cannot be in the future')
        return v

class Expense(ExpenseBase):
    id: int

    class Config:
        orm_mode = True
