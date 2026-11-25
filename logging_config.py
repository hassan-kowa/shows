import logging
import re
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog

LOG_DIR = Path(__file__).parent / "logs"
LOG_FILE = LOG_DIR / "app.log"

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


class _WerkzeugFilter(logging.Filter):
    """Quiet werkzeug, but keep the line that says where the server is running.

    werkzeug's per-request access lines duplicate our own request logging and
    contain ANSI color codes, so drop them. The startup line ("Running on
    http://...") is the only way to see which address to open, so let it
    through with the color codes removed. Warnings and errors always pass.
    """

    def filter(self, record):
        if record.levelno >= logging.WARNING:
            return True
        message = _ANSI.sub("", record.getMessage())
        if "Running on" in message:
            record.msg, record.args = message, ()
            return True
        return False


def setup_logging(level=logging.INFO):
    """Configure structlog: JSON to a rotating file, plain text to the console.

    Call once at program startup.
    """
    LOG_DIR.mkdir(exist_ok=True)

    # Processors that run on every event, whether it came from structlog
    # or from stdlib logging (Flask, werkzeug, etc.).
    shared = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    structlog.configure(
        processors=shared + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
        )
    )

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.dev.ConsoleRenderer(),
            ],
        )
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(file_handler)
    root.addHandler(console_handler)
    root.setLevel(level)

    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.setLevel(logging.INFO)
    werkzeug_logger.addFilter(_WerkzeugFilter())
