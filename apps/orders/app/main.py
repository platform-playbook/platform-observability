import os
import uuid
import time
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY
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
    start = time.perf_counter()
    request_id = x_request_id or str(uuid.uuid4())
    order_id = str(uuid4())
    try:

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
        REQUEST_COUNT.labels(
                service="orders",
                method="POST",
                route="/orders",
                status="200",
            ).inc()
        return {
            "request_id": request_id,
            "order_id": order_id,
            "product_id": order.product_id,
            "quantity": order.quantity,
            "payment": payment_response.json(),
            "fraud": fraud_response.json(),
            "status": "created",
        }

    finally:
        REQUEST_LATENCY.labels(
            service="orders",
            method="POST",
            route="/orders",
        ).observe(time.perf_counter() - start)
