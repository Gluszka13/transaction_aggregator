import logging
from celery import shared_task
from transactions.services.csv_importer import import_csv_from_string

logger = logging.getLogger(__name__)


@shared_task
def import_csv_task(content: str, filename: str = "upload.csv"):
    result = import_csv_from_string(content)
    logger.info("CSV import complete: %s", result)
    return result

