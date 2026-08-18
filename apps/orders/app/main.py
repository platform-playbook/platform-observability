import os
import uuid
from uuid import uuid4
from typing import Optional
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Header
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
