from pathlib import Path
from loguru import logger

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger.add(
    LOG_DIR / "audit.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO",
    enqueue=True,
    format=(
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level} | "
        "{message}"
    ),
)


class AuditLogger:

    @staticmethod
    def log(
        username: str,
        role: str,
        action: str,
        status: str,
        details: str = "",
    ):

        logger.info(
            f"user={username} | "
            f"role={role} | "
            f"action={action} | "
            f"status={status} | "
            f"{details}"
        )