from datetime import datetime

from learn.models import WordUnit, LearningPlan, LearningRecord
from learn.user_learn import UserLearn
from operations.models import GroupLearningPlan
from users.models import Group, UserProfile
from utils.time_util import get_now


class UserPlan(object):
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
            print(f"Added {unit} to {user}'s plan")

    def deploy_group_plans_for_today(self):
        today_group_plans = GroupLearningPlan.objects.filter(start_date=datetime.today()).all()
        for group_plan in today_group_plans:
            group_members = UserProfile.objects.filter(usergroup__group=group_plan.group, usergroup__role=1).all()
            for user in group_members:
                self.add_plan_for_user(user, group_plan.unit)

    def deploy_all_group_plans(self):
        groups = Group.objects.all()
        print(f"There are {groups.count()}")
        for group in groups:
            self.add_all_plans_for_group(group)

    def populate_today_tasks(self):
        for user in UserProfile.objects.all():
            user_learn = UserLearn(user.id)
            user_learn.populate_today_tasks()
