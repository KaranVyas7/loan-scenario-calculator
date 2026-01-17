from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, getcontext

getcontext().prec = 28  # stable precision for money math

CENT = Decimal("0.01")


def q2(x: Decimal) -> Decimal:
    """Round to cents using HALF_UP for consistency."""
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


def compute_monthly_payment(amount: Decimal, apr: Decimal, term_months: int) -> Decimal:
    """
    Monthly payment rounded to cents.
    apr is annual percentage rate like 5.5 for 5.5%.
    Must handle 0% APR loans.
    """
    if term_months <= 0:
        raise ValueError("term_months must be > 0")
    if amount <= 0:
        raise ValueError("amount must be > 0")

    if apr == 0:
        return q2(amount / Decimal(term_months))

    r = (apr / Decimal("100")) / Decimal("12")  # monthly rate
    n = Decimal(term_months)

    one_plus_r_pow_n = (Decimal("1") + r) ** n
    payment = amount * r * one_plus_r_pow_n / (one_plus_r_pow_n - Decimal("1"))
    return q2(payment)


def compute_schedule_preview(
    amount: Decimal, apr: Decimal, term_months: int, preview_months: int = 12
):
    """
    Return (monthly_payment, schedule_preview_rows).
    Preview: first 12 months, or full schedule if the loan term is less than 12 months.
    """
    payment = compute_monthly_payment(amount, apr, term_months)
    balance = q2(amount)

    r = Decimal("0") if apr == 0 else (apr / Decimal("100")) / Decimal("12")
    limit = min(term_months, preview_months)

    rows = []
    for month in range(1, limit + 1):
        interest = q2(balance * r)
        principal = q2(payment - interest)

        if principal > balance:
            principal = balance

        balance = q2(balance - principal)

        rows.append(
            {
                "month": month,
                "interest_paid": float(interest),
                "principal_paid": float(principal),
                "remaining_balance": float(balance),
            }
        )

    return float(payment), rows
