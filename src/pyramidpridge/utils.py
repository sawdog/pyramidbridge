"""
utils

"""
import logging
import sys

from .yamlcfg import yamlcfg


ARROW_DATETIME_FMT = yamlcfg.handlers.datetime.arrow_format
ARROW_DATE_FMT = yamlcfg.handlers.date.arrow_format
DATETIME_DEFAULT_FMT = yamlcfg.handlers.datetime.default_format
DATE_DEFAULT_FMT = yamlcfg.handlers.date.default_format
QUERY_FMT = yamlcfg.handlers.date.query_format
LOGGER_NAME = yamlcfg.logging.name
LOG_LEVEL = yamlcfg.logging.level


def setup_logger():
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(getattr(logging, LOG_LEVEL))
    formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
