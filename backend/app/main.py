from fastapi import FastAPI

app = FastAPI(title="Loan Scenario Calculator")

@app.get("/health")
def health():
    return {"status": "ok"}
