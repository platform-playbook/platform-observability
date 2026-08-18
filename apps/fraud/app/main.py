from fastapi import FastAPI
import time
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY
from pydantic import BaseModel
from fastapi import Header
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from app.logging_config import configure_logging


logger = configure_logging("fraud")

app = FastAPI(title="Fraud Service")

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
            service="fraud",
            method=request.method,
            route=route,
            status=str(status),
        ).inc()

        REQUEST_LATENCY.labels(
            service="fraud",
            method=request.method,
            route=route,
        ).observe(duration)

    return response


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