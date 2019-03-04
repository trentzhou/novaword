from learn.models import LearningPlan, LearningRecord, UserTask


class UserLearn(object):
    MAX_PENDING_TASK_COUNT = 5

    def __init__(self, user):
        """
        Constructor
        :param users.models.UserProfile user:
        """
        self.user = user

    def get_ongoing_plan(self):
        """
        Get all ongoing units in the user's plan.
        :return: list of planned units
        """
        unfinished_plan = LearningPlan.objects.filter(user=self.user, finished=False).order_by("added_time").all()
        return unfinished_plan

    def has_unit_learned(self, unit):
        """
        Has a unit been learned
        :param unit:
        :return Boolean:
        """
        return LearningRecord.objects.filter(user=self.user, unit=unit).count()

    def populate_today_tasks(self):
        """
        Populate today's tasks.
        :return:
        """
        existing_tasks = UserTask.objects.filter(user=self.user, finished=False).all()
        task_count = existing_tasks.count()

        if task_count >= UserLearn.MAX_PENDING_TASK_COUNT:
            return

        ongoing_plan = self.get_ongoing_plan()

        for plan in ongoing_plan:
            type = 1
            if self.has_unit_learned(plan.unit):
                type = 3

            task = UserTask()
            task.user = self.user
            task.unit = plan.unit
            task.finished = False
            task.type = type
            task.save()
            task_count += 1
            if task_count >= UserLearn.MAX_PENDING_TASK_COUNT:
                return

    def finish_unit(self, unit):
        """
        Finish a unit. This sets the LearningPlan for the unit as finished.
        :param unit:
        :return:
        """
        try:
            plan = LearningPlan.objects.filter(user=self.user, unit=unit, finished=False).get()
            plan.finished = True
            plan.save()
        except:
            pass

    def save_learning_record(self, record):
        """
        Save a learning record.
        :param learn.models.LearningRecord record:
        :return None:
        """
        # 如果这个单元不在计划中，那么加入计划
        try:
            plan = LearningPlan.objects.filter(unit_id=record.unit_id, user=self.user).get()
            if LearningRecord.objects.filter(user=self.user, unit_id=record.unit_id).count() > 5:
                plan.finished = True
                plan.save()
        except LearningPlan.DoesNotExist:
            plan = LearningPlan()
            plan.user = self.user
            plan.unit = record.unit
            plan.finished = False
            plan.save()

        # 完成今日任务
        try:
            task = UserTask.objects.filter(user=self.user, unit=record.unit, finished=False).get()
            task.finished = True
            task.save()
        except:
            pass
