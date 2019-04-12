"""
This module is responsible for event handling and management.
"""
import requests

from celery import Celery
from mongoengine import connect

from teamserver.integrations.integration import Integration

from teamserver.config import INTEGRATIONS
from teamserver.config import CELERY_MAIN_NAME, CELERY_RESULT_BACKEND, CELERY_BROKER_URL
from teamserver.config import CELERY_BROKER_TRANSPORT
from teamserver.config import DB_NAME, DB_HOST, DB_PORT

app = Celery(  # pylint: disable=invalid-name
    CELERY_MAIN_NAME,
    backend=CELERY_RESULT_BACKEND,
    broker=CELERY_BROKER_URL,
    broker_transport_options=CELERY_BROKER_TRANSPORT,
)
connect(DB_NAME, host=DB_HOST, port=DB_PORT)

PWNBOARD = None
if "PWNBOARD_CONFIG" in INTEGRATIONS and INTEGRATIONS['PWNBOARD_CONFIG']['URL']:
    from teamserver.integrations.pwnboard import PwnboardIntegration

    PWNBOARD = PwnboardIntegration(INTEGRATIONS["PWNBOARD_CONFIG"])

SYSLOG = None
if "SYSLOG" in INTEGRATIONS and INTEGRATIONS["SYSLOG"]["host"]:
    from teamserver.integrations.syslog import SyslogIntegration
    SYSLOG = SyslogIntegration(INTEGRATIONS['SYSLOG'])

@app.task
def trigger_event(**kwargs):
    """
    Trigger an event, and notify subscribers.
    """
    event = kwargs.get("event")
    if event:
        if isinstance(SYSLOG, Integration):
            SYSLOG.run(kwargs)
        if isinstance(PWNBOARD, Integration):
            PWNBOARD.run(kwargs)
