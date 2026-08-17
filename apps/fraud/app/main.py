from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Header
from typing import Optional
app = FastAPI(title="Fraud Service")


class FraudRequest(BaseModel):
    order_id: str


@app.get("/health")
def health():
    return {"status": "UP"}


@app.post("/fraud/check")
def check_fraud(request: FraudRequest, x_request_id: Optional[str] = Header(default=None),):
    return {
        "request_id": x_request_id,
        "order_id": request.order_id,
        "status": "approved",
    }
