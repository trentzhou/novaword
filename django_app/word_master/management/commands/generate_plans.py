from django.core.management.base import BaseCommand, CommandError

from learn.models import WordUnit, LearningPlan, LearningRecord
from users.models import Group, UserProfile
from utils.time_util import get_now


class Command(BaseCommand):
    help = "Generate learning plans for all students which are in groups"

    def add_all_plans_for_group(self, group):
        now = get_now()
        group_members = UserProfile.objects.filter(usergroup__group=group, usergroup__role=1).all()
        group_units = WordUnit.objects.filter(grouplearningplan__group=group, grouplearningplan__start_date__lt=now).all()
        # we have found all units for the group, now print out
        for unit in group_units:
            print(f"Group {group} is learning {unit}")
            for user in group_members:
                self.add_plan_for_user(user, unit)

    def add_plan_for_user(self, user, unit):
        existing = LearningPlan.objects.filter(user=user, unit=unit).count()
        if not existing:
            plan = LearningPlan()
            plan.user = user
            plan.unit = unit
            # is this plan finished yet?
            records = LearningRecord.objects.filter(user=user, unit=unit).count()
            finished = False
            if records > 5:
                finished = True
            plan.finished = finished
            plan.save()

    def handle(self, *args, **options):
        # find all groups
        groups = Group.objects.all()
        print(f"There are {groups.count()}")
        for group in groups:
            self.add_all_plans_for_group(group)
