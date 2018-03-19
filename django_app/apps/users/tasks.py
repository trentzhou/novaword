from celery import task
from celery.utils.log import get_task_logger

from utils.email_send import send_register_email

logger = get_task_logger(__name__)


@task(name="send_register_email_async")
def send_register_email_async(email, send_type="register", host="localhost:8000"):
    send_register_email(email, send_type, host)