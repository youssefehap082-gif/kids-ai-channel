import logging

logging.basicConfig(filename="outputs/log.txt", level=logging.INFO)

def log_error(message, video=None):
    logging.error(f"{message} | Video: {video if video else ''}")

def log_success(message):
    logging.info(message)
