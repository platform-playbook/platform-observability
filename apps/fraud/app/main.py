from fastapi import FastAPI
import time
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY
from pydantic import BaseModel
from fastapi import Header
from typing import Optional
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from app.logging_config import configure_logging


logger = configure_logging("fraud")

app = FastAPI(title="Fraud Service")


class FraudRequest(BaseModel):
    order_id: str


@app.get("/health")
def health():
    return {"status": "UP"}

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )



@app.post("/fraud/check")
def check_fraud(request: FraudRequest, x_request_id: Optional[str] = Header(default=None),):
    start = time.perf_counter()
    try:
        logger.info(
            "Fraud check completed",
            extra={
                "event": "fraud_check_completed",
                "request_id": x_request_id,
                "order_id": request.order_id,
            },
        )
        REQUEST_COUNT.labels(
        service="fraud",
        method="POST",
        route="/fraud/check",
        status="200",
        ).inc()        
        return {
            "request_id": x_request_id,
            "order_id": request.order_id,
            "status": "approved",
        }
    finally:
        REQUEST_LATENCY.labels(
            service="payments",
            method="POST",
            route="/payments",
        ).observe(time.perf_counter() - start)