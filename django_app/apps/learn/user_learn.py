from learn.models import LearningPlan, LearningRecord, UserTask


class UserLearn(object):
    MAX_PENDING_TASK_COUNT = 5

    def __init__(self, user_id):
        """
        Constructor
        :param users.models.UserProfile user:
        """
        self.user_id = user_id

    def get_ongoing_plan(self):
        """
        Get all ongoing units in the user's plan.
        :return: list of planned units
        """
        unfinished_plan = LearningPlan.objects.filter(user_id=self.user_id, finished=False).order_by("added_time").all()
        return unfinished_plan

    def unit_learn_count(self, unit):
        """
        Has a unit been learned
        :param unit:
        :return Boolean:
        """
        return LearningRecord.objects.filter(user_id=self.user_id, unit=unit).count()

    def get_active_tasks(self):
        """
        Get active tasks.
        :return list[UserTask]: active tasks
        """
        return UserTask.objects.filter(user_id=self.user_id).all()

    def populate_today_tasks(self):
        """
        Populate today's tasks.
        :return list[int]: active unit ids
        """
        existing_tasks = UserTask.objects.filter(user_id=self.user_id).all()
        task_count = existing_tasks.count()
        result = [task.unit_id for task in existing_tasks]

        if task_count >= UserLearn.MAX_PENDING_TASK_COUNT:
            return result

        ongoing_plan = self.get_ongoing_plan()

        for plan in ongoing_plan:
            type = 1
            if self.unit_learn_count(plan.unit):
                type = 3

            task = UserTask()
            task.user_id = self.user_id
            task.unit_id = plan.unit_id
            task.type = type
            task.save()
            result.append(plan.unit_id)
            task_count += 1
            if task_count >= UserLearn.MAX_PENDING_TASK_COUNT:
                return result
        return result

    def finish_unit(self, unit):
        """
        Finish a unit. This sets the LearningPlan for the unit as finished.
        :param unit:
        :return:
        """
        try:
            plan = LearningPlan.objects.filter(user_id=self.user_id, unit=unit, finished=False).get()
            plan.finished = True
            plan.save()
        except:
            pass

    def is_unit_in_plan(self, unit_id):
        """
        判断是否某个单元在某人的计划中
        :param int unit_id: unit id
        :param int user_id: user id
        :return:
        """
        if LearningPlan.objects.filter(unit_id=unit_id, user_id=self.user_id).count():
            return True
        return False

    def save_learning_record(self, record):
        """
        Save a learning record.
        :param learn.models.LearningRecord record:
        :return None:
        """
        # 如果这个单元不在计划中，那么加入计划
        try:
            plan = LearningPlan.objects.filter(unit_id=record.unit_id, user_id=self.user_id).get()
            # If the unit is all correct, then finish the unit
            if record.correct_rate == 100 or LearningRecord.objects.filter(user_id=self.user_id, unit_id=record.unit_id).count() > 5:
                plan.finished = True
                plan.save()
        except LearningPlan.DoesNotExist:
            plan = LearningPlan()
            plan.user_id = self.user_id
            plan.unit = record.unit
            plan.finished = False
            plan.save()

        # 完成今日任务
        try:
            task = UserTask.objects.filter(user_id=self.user_id, unit=record.unit).get()
            task.delete()
        except:
            pass
