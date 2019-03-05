from django.core.management.base import BaseCommand

from utils.user_plan import UserPlan


class Command(BaseCommand):
    help = "Generate learning plans for all students which are in groups"

    def add_arguments(self, parser):
        parser.add_argument('--today', action='store_true', dest='today', help="Only generate today's plans")

    def handle(self, *args, **options):
        # find all groups
        user_plan = UserPlan()
        if options["today"]:
            user_plan.deploy_group_plans_for_today()
        else:
            user_plan.deploy_all_group_plans()

