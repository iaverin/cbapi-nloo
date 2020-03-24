import copy
import requests
import logging
from pprint import pformat
import threading
import json


logger_config = {
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s:%(threadName)s: %(message)s',
        }},
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },

            'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default',
            'level': 'INFO'},

            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'reporter.log',
                'formatter': 'default',
                'level': 'INFO',
                'maxBytes': 1024000000,
                'backupCount': 5
            }

        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi', 'file']
        },
        'loggers': {
            'application':{
                'propagate': False,
                'handlers': ['console', 'file'],
            }
        }
    }

logger = None
config = None
lock = None


def init(configuration,  logger_to_use=None):
    global config
    global lock
    global logger

    config = configuration

    lock = threading.Lock()

    if logger_to_use:
        logger = logger_to_use
    else:
        logger = logging.getLogger()


def _format_log_string(user_id="", event="", message=""):
    out = "userId: {user} {event}: {msg}".format(user=user_id, event=event, msg=message)
    return out


def log(user_id="", event="", message=""):
    logger.info(_format_log_string(user_id, event, message))


def log_error(user_id="", event="", message=""):
    logger.error(_format_log_string(user_id, event, message))


def report(user_id=None, timestamp=None, component="NLOO", event=None, payload: dict = None, report_data=None):
    global config

    if not (getattr(config, "REPORTER", False) and config.REPORTER.get("service")):
        return False

    timeout = config.REPORTER.get("timeout", None)

    if timeout == 0:
        timeout = None

    reporter_service = config.REPORTER.get("service")
    report_payload = {
        "userId": user_id or getattr(report_data, "user_id", None),
        "timestamp": timestamp or getattr(report_data, "timestamp", None),
        "component": component or getattr(report_data, "component", None),
        "event": event or getattr(report_data, "event", None),
        "payload": payload or getattr(report_data, "payload", None)
    }
    try:
        r = requests.post(reporter_service+"/event", json=report_payload, timeout=timeout)

        if r.status_code != 200:
            logger.warning(_format_log_string(user_id, event, 'Could not call report service ' + r.text))
            return False

    except Exception as e:
        logger.warning(_format_log_string(user_id, event, 'Could not call report service: ' + str(e.args)))
        return False

    return True
