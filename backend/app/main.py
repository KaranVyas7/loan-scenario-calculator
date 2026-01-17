from decimal import Decimal

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select, desc

from app.db import create_db_and_tables, get_session
from app.models import LoanScenario
from app.schemas import LoanCreate, LoanOut, LoanDetail
from app.loan_math import compute_monthly_payment, compute_schedule_preview
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Loan Scenario Calculator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/loans", response_model=LoanOut)
def create_loan(payload: LoanCreate, session: Session = Depends(get_session)):
    monthly_payment = float(
        compute_monthly_payment(
            Decimal(str(payload.amount)),
            Decimal(str(payload.apr)),
            payload.term_months,
        )
    )

    loan = LoanScenario(
        amount=payload.amount,
        apr=payload.apr,
        term_months=payload.term_months,
        monthly_payment=monthly_payment,
    )
    session.add(loan)
    session.commit()
    session.refresh(loan)

    return LoanOut(
        id=loan.id,
        amount=loan.amount,
        apr=loan.apr,
        term_months=loan.term_months,
        monthly_payment=loan.monthly_payment,
    )


@app.get("/loans", response_model=list[LoanOut])
def list_loans(session: Session = Depends(get_session)):
    stmt = select(LoanScenario).order_by(desc(LoanScenario.created_at))
    loans = session.exec(stmt).all()

    return [
        LoanOut(
            id=l.id,
            amount=l.amount,
            apr=l.apr,
            term_months=l.term_months,
            monthly_payment=l.monthly_payment,
        )
        for l in loans
    ]


@app.get("/loans/{loan_id}", response_model=LoanDetail)
def get_loan(loan_id: int, session: Session = Depends(get_session)):
    loan = session.get(LoanScenario, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    monthly_payment, preview = compute_schedule_preview(
        Decimal(str(loan.amount)),
        Decimal(str(loan.apr)),
        loan.term_months,
        preview_months=12,
    )

    return LoanDetail(
        id=loan.id,
        amount=loan.amount,
        apr=loan.apr,
        term_months=loan.term_months,
        monthly_payment=monthly_payment,
        schedule_preview=preview,
    )
