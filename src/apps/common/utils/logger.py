import logging
from src.apps.common.models import Log

logger = logging.getLogger(__name__)

def log_action(user, action, level="INFO", ip=None):
    if level == "INFO":
        logger.info(action)
    elif level == "WARNING":
        logger.warning(action)
    else:
        logger.error(action)

    Log.objects.create(user=user, action=action, level=level, ip_address=ip)
