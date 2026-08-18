from uuid import uuid4
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Header
from app.logging_config import configure_logging
logger = configure_logging("payments")

app = FastAPI(title="Payments Service")


class PaymentRequest(BaseModel):
    order_id: str   
    amount: float


@app.get("/health")
def health():
    return {"status": "UP"}


@app.post("/payments")
def process_payment(payment: PaymentRequest,x_request_id: Optional[str] = Header(default=None),):
    logger.info(
        "Payment completed",
        extra={
            "event": "payment_completed",
            "request_id": x_request_id,
            "order_id": payment.order_id,
        },
    )
    return {
        "request_id": x_request_id,
        "payment_id": str(uuid4()),
        "order_id": payment.order_id,
        "status": "approved",
    }
