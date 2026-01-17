from pydantic import BaseModel, Field


class LoanCreate(BaseModel):
    amount: float = Field(..., gt=0)
    apr: float = Field(..., ge=0, le=100)
    term_months: int = Field(..., ge=1, le=480)


class LoanOut(BaseModel):
    id: int
    amount: float
    apr: float
    term_months: int
    monthly_payment: float


class ScheduleRow(BaseModel):
    month: int
    interest_paid: float
    principal_paid: float
    remaining_balance: float


class LoanDetail(LoanOut):
    schedule_preview: list[ScheduleRow]
