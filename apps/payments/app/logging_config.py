import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "request_id"):
            log["request_id"] = record.request_id
    
        if hasattr(record, "order_id"):
            log["order_id"] = record.order_id

        if hasattr(record, "event"):
            log["event"] = record.event

        return json.dumps(log)


def configure_logging(service_name):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False

    return logger