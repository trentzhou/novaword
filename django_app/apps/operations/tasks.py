from celery.schedules import crontab
from celery.task import periodic_task
from celery.utils.log import get_task_logger

from utils.user_plan import UserPlan

logger = get_task_logger(__name__)


@periodic_task(run_every=(crontab(hour='*/2')), name="deploy_today_group_plans", ignore_result=True)
def deploy_today_group_plans():
    logger.info("Deploying today's learning plans")
    user_plan = UserPlan()
    user_plan.deploy_group_plans_for_today()

@periodic_task(run_every=(crontab(hour='*/4')), name="populate_today_tasks", ignore_result=True)
def populate_today_tasks():
    logger.info("Populating today's tasks")
    user_plan = UserPlan()
    user_plan.populate_today_tasks()

