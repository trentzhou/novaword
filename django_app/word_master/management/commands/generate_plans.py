from django.core.management.base import BaseCommand

from utils.user_plan import UserPlan


class Command(BaseCommand):
    help = "Generate learning plans for all students which are in groups"

    def handle(self, *args, **options):
        # find all groups
        user_plan = UserPlan()
        user_plan.deploy_all_group_plans()

