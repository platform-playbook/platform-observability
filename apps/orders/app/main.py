from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Orders Service")


class OrderRequest(BaseModel):
    product_id: str
    quantity: int


@app.get("/health")
def health():
    return {"status": "UP"}


@app.post("/orders")
def create_order(order: OrderRequest):
    return {
        "order_id": str(uuid4()),
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "created",
    }
