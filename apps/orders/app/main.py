import os
import uuid
import time
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4
from typing import Optional
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Header
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from app.logging_config import configure_logging

logger = configure_logging("orders")

app = FastAPI(title="Orders Service")

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
            service="orders",
            method=request.method,
            route=route,
            status=str(status),
        ).inc()

        REQUEST_LATENCY.labels(
            service="orders",
            method=request.method,
            route=route,
        ).observe(duration)

    return response

PAYMENTS_URL = os.getenv(
    "PAYMENTS_URL",
    "http://payments:8000",
)

FRAUD_URL = os.getenv(
    "FRAUD_URL",
    "http://fraud:8000",
)


class OrderRequest(BaseModel):
    product_id: str
    quantity: int


@app.get("/health")
def health():
    return {"status": "UP"}


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.post("/orders")
async def create_order(order: OrderRequest,
    x_request_id:  Optional[str] = Header(default=None),):
    request_id = x_request_id or str(uuid.uuid4())
    order_id = str(uuid4())


    headers = {
        "X-Request-ID": request_id,
    }

    async with httpx.AsyncClient() as client:

        payment_response = await client.post(
            f"{PAYMENTS_URL}/payments",
            json={
                "order_id": order_id,
                "amount": 100.0 * order.quantity,
            },
        headers=headers,
        )

        fraud_response = await client.post(
            f"{FRAUD_URL}/fraud/check",
            json={
                "order_id": order_id,
            },
        headers=headers,
        )

    logger.info(
    "Order created",
    extra={
        "event": "order_created",
        "request_id": request_id,
        "order_id": order_id,
    },
    )
    return {
        "request_id": request_id,
        "order_id": order_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "payment": payment_response.json(),
        "fraud": fraud_response.json(),
        "status": "created",
    }


