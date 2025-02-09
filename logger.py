import logging

def get_logger(name: str) -> logging.Logger:
    """
    Loggeri :)
    """
    logger = logging.getLogger(name)
    return logger

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)