from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Header
from typing import Optional
from app.logging_config import configure_logging


logger = configure_logging("fraud")

app = FastAPI(title="Fraud Service")


class FraudRequest(BaseModel):
    order_id: str


@app.get("/health")
def health():
    return {"status": "UP"}


@app.post("/fraud/check")
def check_fraud(request: FraudRequest, x_request_id: Optional[str] = Header(default=None),):
    logger.info(
        "Fraud check completed",
        extra={
            "event": "fraud_check_completed",
            "request_id": x_request_id,
            "order_id": request.order_id,
        },
    )
    return {
        "request_id": x_request_id,
        "order_id": request.order_id,
        "status": "approved",
    }
