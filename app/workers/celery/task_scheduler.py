import sys

sys.path.append(".")
import logging
from celery import Celery
from kombu.serialization import registry
from kombu import Exchange, Queue
from celery.schedules import crontab

from configs.config import settings

from database.redis_db import redis_db


CELERY_CONFIG = {
    "enable_utc": True,
    "task_serializer": "pickle",
    "event_serializer": "pickle",
    "result_serializer": "pickle",
    "accept_content": ["application/json", "application/x-python-serialize"],
    "task_acks_late": True,
    "result_expires": 60 * 30,
    "celeryd_prefetch_multiplier": 1,
    "result_extended": True,
}


CELERY_REDIS_URL = f"redis://@127.0.0.1:{settings.REDIS_PORT}/0"


celery = Celery(__name__)
registry.enable("pickle")
celery.conf.broker_url = CELERY_REDIS_URL
celery.conf.result_backend = CELERY_REDIS_URL
celery.conf.broker_transport_options = {
    "queue_order_strategy": "priority",
    "visibility_timeout": 86400,
}
celery.conf.critical_queues = [
    Queue(
        "critical",
        Exchange("critical"),
        routing_key="critical",
        queue_arguments={"x-max-priority": 6},
    )
]

celery.conf.update(**CELERY_CONFIG)

celery.conf.beat_schedule = {
    "schedule_deployments": {
        "task": "workers.celery.task_scheduler.schedule_deployment",
        "schedule": crontab(),
        "options": {"queue": "critical"},
    },
    "complete_deployments": {
        "task": "workers.celery.task_scheduler.complete_deployment",
        "schedule": crontab(),
        "options": {"queue": "critical"},
    },
}


@celery.task(bind=True, max_retries=0, retry_backoff=True)
def schedule_deployment(self):

    from services.deployment.tasks.schedule_deployment import schedule_deployment
    from database.celery_db import get_celery_db

    try:
        db = get_celery_db()
        response = schedule_deployment(db=db, redis_db=redis_db)
        db.commit()
        return response | {"success": True}
    except Exception as exc:
        response = {"success": False, "error": str(exc)}
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
    finally:
        db.close()
        return response


@celery.task(bind=True, max_retries=0, retry_backoff=True)
def complete_deployment(self):

    from services.deployment.tasks.complete_deployment import complete_deployment
    from database.celery_db import get_celery_db

    try:
        db = get_celery_db()
        response = complete_deployment(db=db)
        return response | {"success": True}
    except Exception as exc:
        response = {"success": False, "error": str(exc)}
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
    finally:
        db.close()
        return response
