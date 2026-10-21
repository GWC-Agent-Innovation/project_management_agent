"""Centralized logging setup so every module gets consistent formatting."""
import logging


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    # Quiet noisy third-party loggers unless the user asked for DEBUG.
    if level.upper() != "DEBUG":
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("slack_sdk").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
