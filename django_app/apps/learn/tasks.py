from celery import task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@task(name="do_add")
def do_add(a, b):
    """sends an email when feedback form is filled successfully"""
    logger.info("Calculating add {0} + {1}".format(a, b))
    return a + b