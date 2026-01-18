from decimal import Decimal

from app.loan_math import compute_monthly_payment, compute_schedule_preview

def test_monthly_payment_matches_example():
    pmt = compute_monthly_payment(Decimal("250000"), Decimal("5.5"), 360)
    assert pmt == Decimal("1419.47")

def test_monthly_payment_zero_apr():
    pmt = compute_monthly_payment(Decimal("1200"), Decimal("0"), 12)
    assert pmt == Decimal("100.00")

def test_schedule_preview_length_and_fields():
    payment, rows = compute_schedule_preview(
        Decimal("1000"), Decimal("0"), 6, preview_months=12
    )
    assert payment == 166.67 
    assert len(rows) == 6  
    first = rows[0]
    assert set(first.keys()) == {
        "month",
        "interest_paid",
        "principal_paid",
        "remaining_balance",
    }
    assert first["month"] == 1
