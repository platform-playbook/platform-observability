from uuid import uuid4
import time
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Header
from app.logging_config import configure_logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

logger = configure_logging("payments")

app = FastAPI(title="Payments Service")


class PaymentRequest(BaseModel):
    order_id: str   
    amount: float


@app.get("/health")
def health():
    return {"status": "UP"}


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )




@app.post("/payments")
def process_payment(payment: PaymentRequest,x_request_id: Optional[str] = Header(default=None),):
    start = time.perf_counter()
    try:
        logger.info(
            "Payment completed",
            extra={
                "event": "payment_completed",
                "request_id": x_request_id,
                "order_id": payment.order_id,
            },
        )
        REQUEST_COUNT.labels(
        service="payments",
        method="POST",
        route="/payments",
        status="200",
        ).inc()
        return {
            "request_id": x_request_id,
            "payment_id": str(uuid4()),
            "order_id": payment.order_id,
            "status": "approved",
        }
    finally:
        REQUEST_LATENCY.labels(
            service="payments",
            method="POST",
            route="/payments",
        ).observe(time.perf_counter() - start)
