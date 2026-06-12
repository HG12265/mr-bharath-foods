import json
import logging
import sys
from contextvars import ContextVar
from typing import Any

# Context variable to hold the unique correlation ID for requests in async contexts
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "correlation_id": correlation_id_ctx.get(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def setup_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clean up any existing handlers to prevent duplicate entries
    logger.handlers = []

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

# Export standard logger instantiation hook
setup_logging()
logger = logging.getLogger("bharath-delight-foods")
