from pydantic import BaseModel
from datetime import date
from typing import Optional

class ExpenseCreate(BaseModel):
    trip_id: str
    user_id: str
    amount: float
    base_currency: str = 'SGD'
    description: Optional[str] = None

class ExpenseResponse(ExpenseCreate):
    trip_id: str
    date: date
    is_paid: bool