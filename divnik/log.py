import logging

def configure_logging():
    package_logger = logging.getLogger(__package__)
    package_logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[%(asctime)s] (%(name)s) [%(levelname)s] %(message)s",
                          datefmt="%Y-%m-%d %H:%M:%S")
    )
    package_logger.setLevel(logging.DEBUG)
    package_logger.addHandler(handler)