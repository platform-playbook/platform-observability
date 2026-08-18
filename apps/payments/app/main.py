from uuid import uuid4
import time
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY
from typing import Optional
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Header
from app.logging_config import configure_logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

logger = configure_logging("payments")

app = FastAPI(title="Payments Service")

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.perf_counter()

    try:
        response = await call_next(request)
        status = response.status_code

    except Exception:
        status = 500
        raise

    finally:
        duration = time.perf_counter() - start

        route = request.scope.get("route")

        if route:
            route = route.path
        else:
            route = request.url.path

        REQUEST_COUNT.labels(
            service="payments",
            method=request.method,
            route=route,
            status=str(status),
        ).inc()

        REQUEST_LATENCY.labels(
            service="payments",
            method=request.method,
            route=route,
        ).observe(duration)

    return response


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
