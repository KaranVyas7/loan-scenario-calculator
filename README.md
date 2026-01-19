# Project Overview: Loan Scenario Calculator
This is a Full-stack project for a Loan Scenario Calculator. Users can create loan scenarios, see the monthly payment, and view an amortization schedule preview. Scenarios are saved and can be viewed later.

## Requirements Covered
- Backend API (FastAPI)
  - `POST /loans` creates a scenario and returns monthly payment
  - `GET /loans` lists saved scenarios (most recent first)
  - `GET /loans/{id}` returns scenario details + amortization schedule preview (first 12 months, or full schedule if term < 12)
  - Input validation: amount > 0, apr 0–100, term_months 1–480
  - 404 returned if loan id does not exist
  - 0% APR loans supported
- Frontend (HTML/CSS/JS)
  - Create loan form
  - Saved scenarios list
  - Click to view detail + schedule preview
- Tests
  - Unit tests for loan math
  - API test for `POST /loans` and `GET /loans/{id}`

## Tech Stack
- Backend: FastAPI (Python) + SQLModel
- Database: SQLite (local file)
  - I used SQLite for quick local setup. The persistence layer uses SQLModel, so switching to PostgreSQL (if preferred) would mainly involve updating the database URL.
- Frontend: HTML/CSS/JavaScript (fetch)
- Tests: pytest

## Loan Calculation and Rounding
- Uses Python `Decimal` for stable money calculations
- Rounds to cents with `ROUND_HALF_UP`
- 0% APR: payment is `amount / term_months` rounded to cents
- I round to cents using Decimal.quantize(0.01, ROUND_HALF_UP) and apply it consistently after each monthly interest/principal calculation.

## Project Structure
- `backend/app/` FastAPI app, DB, models, schemas, loan math
- `backend/tests/` pytest unit + API tests
- `frontend/` static frontend (index.html, app.js, styles.css)

## Tradeoffs / Assumptions
- Used SQLite for fast local setup and simplicity (no external database required).
- Schedule preview is limited to the first 12 months to keep responses lightweight.

## Setup and Run

### Backend
From the project root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
### Backend URLs:
- Health: http://127.0.0.1:8000/health
- Swagger docs: http://127.0.0.1:8000/docs

### Frontend
In a new terminal from the project root:
```bash
cd frontend
python3 -m http.server 5500
```
Open:
- http://127.0.0.1:5500

Frontend expects backend at:
- http://127.0.0.1:8000

### Running Tests
From the project root:
```bash
cd backend
source .venv/bin/activate
pytest -q
```
## API Example

### Create a loan scenario
`POST /loans`

**Request**
```json

{ "amount": 250000, "apr": 5.5, "term_months": 360 }
```
**Response**
```json
{
  "id": 1,
  "amount": 250000,
  "apr": 5.5,
  "term_months": 360,
  "monthly_payment": 1419.47
}
``` 