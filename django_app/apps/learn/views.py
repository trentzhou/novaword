# -*- coding: utf-8 -*-
import datetime
import json
import logging
import re
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.db.models import Count, Q, Max
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View

from learn.models import WordBook, WordUnit, WordInUnit, LearningPlan, LearningRecord, ErrorWord, Word
from testings.models import QuizResult
from users.models import UserGroup, UserProfile, Group
from users.templatetags.user_info import is_teacher
from utils import lookup_word_in_db
from utils.time_util import get_now
from .tasks import do_add


class LearningPlanView(LoginRequiredMixin, View):
    # list all units which are in the learning plan
    def get(self, request, user_id):
        my_plans = LearningPlan.objects.filter(user_id=user_id).values("unit_id").all()

        all_planned_units = {}
        for u in my_plans:
            unit_id = u["unit_id"]
            all_planned_units[unit_id] = True

        units = WordUnit.objects.filter(id__in=all_planned_units.keys()).all()
        for u in units:
            u.learn_times = u.learn_count(user_id)
            u.review_times = u.review_count(user_id)

        return render(request, 'unit_list.html', {
            "page": "units",
            "units": units
        })

def is_unit_in_plan(unit_id, user_id):
    """
    判断是否某个单元在某人的计划中
    :param int unit_id: unit id
    :param int user_id: user id
    :return:
    """
    if LearningPlan.objects.filter(unit_id=unit_id, user_id=user_id).count():
        return True
    return False


class UnitDetailView(View):
    def get(self, request, unit_id):
        unit = WordUnit.objects.filter(id=unit_id).get()
        if not unit:
            raise Http404()

        words = WordInUnit.objects.filter(unit=unit).order_by("order").all()

        is_planned = False
        records = None
        if request.user.is_authenticated():
            is_planned = is_unit_in_plan(unit_id, request.user.id)
            records = LearningRecord.objects.filter(unit_id=unit_id, user=request.user).all()
        return render(request, 'unit_detail.html', {
            "records": records,
            "page": "books",
            "unit": unit,
            "words": words,
            "is_planned": is_planned
        })


class UnitWordsTextView(View):
    def get(self, request, unit_id):
        unit = WordUnit.objects.filter(id=unit_id).get()
        if not unit:
            raise Http404()

        words = WordInUnit.objects.filter(unit=unit).order_by("order").all()
        result = ""
        for w in words:
            spelling = w.word.spelling
            meaning = w.simple_meaning
            line = "%-20s    %s\r\n" % (spelling, meaning)
            result += line
        return HttpResponse(result, **{"content_type": "application/text"})


class AjaxChangeUnitWordMeaningView(View):
    def post(self, request):
        unit_word_id = request.POST.get("unit_word_id")
        simple_meaning = request.POST.get("simple_meaning")

        unit_word = WordInUnit.objects.filter(id=unit_word_id).get()
        unit_word.simple_meaning = simple_meaning
        unit_word.save()
        return JsonResponse({"status": "success"})


class AjaxAddBookToLearningPlanView(LoginRequiredMixin, View):
    def post(self, request):
        book_id = request.POST.get("book_id", None)
        if not book_id:
            return JsonResponse({
                "status": "failure"
            })
        units = WordUnit.objects.filter(book_id=book_id).all()
        for unit in units:
            if not LearningPlan.objects.filter(unit=unit, user=request.user).count():
                plan = LearningPlan()
                plan.unit = unit
                plan.user = request.user
                plan.save()
        return JsonResponse({
            "status": "success"
        })


class AjaxAddUnitToLearningPlanView(LoginRequiredMixin, View):
    def post(self, request):
        unit_id = request.POST.get("unit_id", None)
        if not unit_id:
            return JsonResponse({
                "status": "failure"
            })
        if not LearningPlan.objects.filter(unit_id=unit_id, user=request.user).count():
            plan = LearningPlan()
            plan.unit_id = unit_id
            plan.user = request.user
            plan.save()
        return JsonResponse({
            "status": "success"
        })


class AjaxDeleteUnitFromLearningPlanView(LoginRequiredMixin, View):
    def post(self, request):
        unit_id = request.POST.get("unit_id", None)
        if not unit_id:
            return JsonResponse({
                "status": "failure"
            })
        LearningPlan.objects.filter(unit_id=unit_id, user=request.user).delete()
        return JsonResponse({
            "status": "success"
        })


class AjaxIsUnitInLearningPlan(LoginRequiredMixin, View):
    def get(self, request, unit_id):
        if LearningPlan.objects.filter(unit_id=unit_id, user=request.user).get():
            return JsonResponse({
                "result": "yes"
            })
        else:
            return JsonResponse({
                "result": "no"
            })


def get_active_units(user_id):
    """
    Get a list of active units for a given user.
    A unit is active if it meets any of the following criteria:
    - it has been learned at least once
    - it is in GroupLearningPlan
    :param int user_id: user id
    :return list: list of active units
    """
    active_units = {}
    learned_units = LearningRecord.objects.filter(user_id=user_id).values("unit_id").distinct().all()
    for u in learned_units:
        active_units[u["unit_id"]] = True
    all_active_units = active_units.keys()
    # if we have finished this unit, delete it
    result = [x for x in all_active_units if get_unit_learn_count(user_id, x) < 6]
    # if it's too small?
    if len(result) < 3:
        # the load for today is too small, try to add more units
        num_to_add = 3 - len(result)
        my_plan = LearningPlan.objects.filter(user_id=user_id).order_by("id").all()
        for p in my_plan:
            if not p.unit_id in all_active_units:
                result.append(p.unit_id)
                if len(result) >= 3:
                    break
    return {
        "all_active_units": all_active_units,
        "result": result
    }


def get_unit_learn_count(user_id, unit_id):
    """
    Get learning count for a given unit.
    :param int user_id: user id
    :param int unit_id: unit id
    :return int: learned count
    """
    return LearningRecord.objects.filter(user_id=user_id, unit_id=unit_id).count()


def has_learned_today(user_id, unit_id):
    """
    Determine whether a unit has been learned today
    :param int user_id: user id
    :param int unit_id: unit id
    :return bool: true if the unit has been learned today
    """
    return LearningRecord.objects.filter(user_id=user_id, unit_id=unit_id, learn_time__date=datetime.datetime.today()).count()


def is_unit_for_today(user_id, unit_id):
    """
    判断今天是不是需要学习某一个单元
    :param int user_id: user id
    :param int unit_id: unit id
    :return bool:
    """
    learn_count = get_unit_learn_count(user_id, unit_id)
    if learn_count > 5:
        return False
    if learn_count > 0:
        last_learn = LearningRecord \
            .objects\
            .filter(user_id=user_id, unit_id=unit_id)\
            .order_by("-learn_time").first()
        today = datetime.datetime.today().date()
        last_learned_date = last_learn.learn_time.date()
        delta = today - last_learned_date
        # 计算最后一次学习距离今天有多少天
        delta_days = delta.days
        learning_curve = [1, 1, 2, 3, 8]
        if delta_days >= learning_curve[learn_count - 1]:
            return True
        return False
    return True


def get_todays_units(user_id):
    """
    Get list of today's pending units
    :param int user_id:
    :return list: list of unit ids for today's learning
    """
    active_units = get_active_units(user_id)["result"]
    result = [x for x in active_units if not has_learned_today(user_id, x) and is_unit_for_today(user_id, x)]
    return result[:5]


class StartLearnView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'learn_start.html', {
            'user': request.user
        })


class AjaxGetTodayUnitsView(LoginRequiredMixin, View):
    def get(self, request):
        units = get_todays_units(request.user.id)
        return JsonResponse({
            "status": "ok",
            "units": units
        })


class LearningOverviewView(LoginRequiredMixin, View):
    def get_for_student(self, request):
        learn_count = LearningRecord.objects.filter(user=request.user).count()
        quiz_count = QuizResult.objects.filter(user=request.user).count()
        erroneous_words = ErrorWord.objects.filter(user=request.user, amend_count__lt=2).count()
        # get recent learned units

        active_units = get_active_units(request.user.id)
        today_units = get_todays_units(request.user.id)
        recent_units = []
        for u in active_units["result"]:
            unit = WordUnit.objects.get(id=u)
            obj = {
                'unit_id': unit.id,
                'unit__book_id': unit.book.id,
                'unit__book__description': unit.book.description,
                'unit__description': unit.description,
                'learn_count': get_unit_learn_count(request.user.id, unit.id)
            }
            recent_units.append(obj)
        recent_units = sorted(recent_units, key=lambda x: x['learn_count'])

        # try to get progress for the units
        for u in recent_units:
            count = int(u["learn_count"])
            if count > 5:
                u["progress"] = 100
            else:
                u["progress"] = int(100 * count / 6)
        mastered_unit_count = len(active_units["all_active_units"]) - len(active_units["result"])

        groups = Group.objects.filter(usergroup__user=request.user).all()
        return render(request, 'index.html', {
            "page": "overview",
            "learn_count": learn_count,
            "quiz_count": quiz_count,
            "erroneous_words": erroneous_words,
            "today_units": today_units,
            "recent_units": recent_units[:10],
            "mastered_unit_count": mastered_unit_count,
            "groups": groups
        })

    def get_for_teacher(self, request):
        return redirect(reverse('user.my_groups'))

    def get(self, request):
        if is_teacher(request.user.id):
            return self.get_for_teacher(request)
        else:
            return self.get_for_student(request)


class LearningView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = UserProfile.objects.filter(id=user_id).get()
        records = LearningRecord.objects.filter(user=user).order_by("-learn_time").all()
        # 取得最近一个月学习记录
        today = datetime.date.today()
        recent_learning_times = []
        for i in range(30):
            d = today - datetime.timedelta(days=29-i)
            count = LearningRecord.objects.filter(user=user, learn_time__year = d.year,
                                                  learn_time__month=d.month,
                                                  learn_time__day=d.day).count()
            recent_learning_times.append({
                "date": d.isoformat(),
                "count": count
            })

        # 获取最近学习过的10个单元
        recent_units = LearningRecord\
            .objects\
            .filter(user=user) \
            .values('unit_id', "unit__description").distinct()\
            .annotate(recent_learn_time=Max("learn_time")).order_by("-recent_learn_time")[:10]
        # 获取每个单元里面的错词
        error_table = []
        for u in recent_units:
            unit_id = u['unit_id']
            error_words = ErrorWord.objects.filter(user_id=user.id, word__unit_id=unit_id).values('word_id', 'word__word__spelling', 'word__simple_meaning').distinct()
            error_table.append({
                "unit_id": unit_id,
                "unit_title": u["unit__description"],
                "error_words": [{
                    "id": x["word_id"],
                    "spelling": x["word__word__spelling"],
                    "meaning": x["word__simple_meaning"]
                } for x in error_words]
            })

            # 计算最近单元的百分比
            active_units = get_active_units(user_id)
            recent_units = []
            for u in active_units["result"]:
                unit = WordUnit.objects.get(id=u)
                obj = {
                    'unit_id': unit.id,
                    'unit__book_id': unit.book.id,
                    'unit__book__description': unit.book.description,
                    'unit__description': unit.description,
                    'learn_count': get_unit_learn_count(user_id, unit.id)
                }
                recent_units.append(obj)
            recent_units = sorted(recent_units, key=lambda x: x['learn_count'])

            # try to get progress for the units
            for u in recent_units:
                count = int(u["learn_count"])
                if count > 5:
                    u["progress"] = 100
                else:
                    u["progress"] = int(100 * count / 6)
        return render(request, 'learn_records.html', {
            "user": user,
            "recent_records": recent_learning_times,
            "page": "learning",
            "recent_units": recent_units[:10],
            "recent_error_records": error_table
        })


class ReviewView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'todo.html', {
            "page": "review"
        })


class AjaxUnitDataView(LoginRequiredMixin, View):
    def get(self, request, unit_id):
        words_in_unit = WordInUnit.objects.filter(unit_id=unit_id).order_by("order").all()
        if not words_in_unit:
            return JsonResponse({
                "status": "failure"
            })
        unit = WordUnit.objects.filter(id=unit_id).get()
        result = []
        for w in words_in_unit:
            detailed_meaning = {}
            if w.word.detailed_meanings:
                detailed_meaning = json.loads(w.word.detailed_meanings)
            result.append({
                "id": w.id,
                "simple_meaning": w.simple_meaning,
                "detailed_meaning": w.detailed_meaning,
                "spelling": w.word.spelling,
                "pronounciation_us": w.word.pronounciation_us,
                "pronounciation_uk": w.word.pronounciation_uk,
                "mp3_us_url": w.word.mp3_us_url,
                "mp3_uk_url": w.word.mp3_uk_url,
                "short_meaning_in_dict": w.word.short_meaning,
                "detailed_meaning_in_dict": detailed_meaning
            })
        return JsonResponse({
            "data": result,
            "title": str(unit),
            "learn_count": get_unit_learn_count(request.user.id, unit_id)
        })


class UnitWalkThroughView(LoginRequiredMixin, View):
    def get(self, request, unit_id):
        try:
            unit = WordUnit.objects.filter(id=unit_id).get()
            return render(request, 'unit_walkthrough.html', {
                "page": "learning",
                "unit": unit
            })
        except KeyError:
            raise Http404()


class UnitLearnView(LoginRequiredMixin, View):
    def get(self, request, unit_id):
        try:
            unit = WordUnit.objects.filter(id=unit_id).get()
            return render(request, 'unit_learn.html', {
                "page": "learning",
                "unit": unit,
                "page_title": u"单元学习",
                "type": 1,
                "data_url": reverse('learn.ajax_unit_data', kwargs={"unit_id": unit_id}),
                "save_url": reverse('learn.save_record')
            })
        except:
            raise Http404()


class UnitTestView(LoginRequiredMixin, View):
    def get(self, request, unit_id):
        try:
            unit = WordUnit.objects.filter(id=unit_id).get()
            return render(request, 'unit_spelling_test.html', {
                "page": "learning",
                "unit": unit,
                "page_title": u"单元测试",
                "type": 2,
                "data_url": reverse('learn.ajax_unit_data', kwargs={"unit_id": unit_id}),
                "save_url": reverse('learn.save_record')
            })
        except:
            raise Http404()


class AjaxSaveLearnRecordView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        unit_id = data.get("unit_id", None)
        type = data.get("type", None)
        correct_rate = data.get("correct_rate", 0)
        seconds_used = data.get("seconds_used", 0)

        word_count = WordInUnit.objects.filter(unit_id=unit_id).count()
        if seconds_used < word_count: # 一个单词算1秒钟
            # 时间不可靠
            return JsonResponse({
                "status": "fail",
                "reason": "速度太快了，结果看上去不真实"
            })
        if not unit_id or not type:
            return JsonResponse({
                "status": "fail",
                "reason": "输入错误"
            })
        try:
            unit = WordUnit.objects.filter(id=unit_id).get()
            record = LearningRecord()
            record.user = request.user
            record.unit = unit
            record.type = type
            record.correct_rate = correct_rate
            record.duration = seconds_used
            record.save()
            # 如果这个单元不在计划中，那么加入计划
            try:
                plan = LearningPlan.objects.filter(unit_id=unit_id, user=request.user).get()
                if LearningRecord.objects.filter(user=request.user, unit_id=unit_id).count() > 5:
                    plan.finished = True
                    plan.save()
            except LearningPlan.DoesNotExist:
                plan = LearningPlan()
                plan.user = request.user
                plan.unit = unit
                plan.finished = False
                plan.save()
            if "error_words" in data:
                error_words = data["error_words"]
                for w in error_words:
                    error_records = ErrorWord.objects.filter(user=request.user, word_id=w).all()
                    if len(error_records):
                        error_record = error_records[0]
                    else:
                        error_record = ErrorWord()
                    error_record.user = request.user
                    error_record.word_id = w
                    error_record.error_count += 1
                    error_record.latest_error_time = get_now()
                    error_record.save()
            return JsonResponse({
                "status": "success"
            })
        except:
            return JsonResponse({
                "status": "fail"
            })


class UnitReviewView(LoginRequiredMixin, View):
    def get(self, request, unit_id):
        try:
            unit = WordUnit.objects.filter(id=unit_id).get()
            return render(request, 'unit_learn.html', {
                "page": "learning",
                "unit": unit,
                "type": 3,
                "page_title": u"单元复习",
                "data_url": reverse('learn.ajax_unit_data', kwargs={"unit_id": unit_id}),
                "save_url": reverse('learn.save_record')
            })
        except KeyError:
            raise Http404()


class ErrorWordListView(LoginRequiredMixin, View):
    def get(self, request):
        error_words = ErrorWord.objects.filter(user=request.user).order_by("-latest_error_time").all()
        return render(request, "error_word_list.html", {
            "page": "error_words",
            "error_words": error_words
        })


class ErrorWordTextView(LoginRequiredMixin, View):
    def get(self, request):
        error_words = ErrorWord.objects.filter(user=request.user).order_by("-latest_error_time").all()
        result = ""
        for e in error_words:
            spelling = e.word.word.spelling
            meaning = e.word.simple_meaning
            line = "%-20s  %s\r\n" % (spelling, meaning)
            result += line
        return HttpResponse(result, **{"content_type": "application/text"})


class AmendErrorWordView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'unit_learn.html', {
            "page": "learning",
            "page_title": u"错词重测",
            "type": 2,
            "data_url": reverse('learn.ajax_error_words'),
            "save_url": reverse('learn.ajax_amend_error_words')
        })


class AjaxErrorWordsView(LoginRequiredMixin, View):
    def get(self, request):
        error_words = ErrorWord.objects.filter(user=request.user, amend_count__lt=2).order_by("-latest_error_time").all()
        result = []
        for error_word in error_words:
            w = error_word.word
            detailed_meaning = {}
            if w.word.detailed_meanings:
                detailed_meaning = json.loads(w.word.detailed_meanings)
            result.append({
                "id": w.id,
                "simple_meaning": w.simple_meaning,
                "detailed_meaning": w.detailed_meaning,
                "spelling": w.word.spelling,
                "pronounciation_us": w.word.pronounciation_us,
                "pronounciation_uk": w.word.pronounciation_uk,
                "mp3_us_url": w.word.mp3_us_url,
                "mp3_uk_url": w.word.mp3_uk_url,
                "short_meaning_in_dict": w.word.short_meaning,
                "detailed_meaning_in_dict": detailed_meaning
            })
        return JsonResponse({
            "data": result
        })


class AjaxAmendErrorWordsView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        if "correct_words" in data:
            for wid in data["correct_words"]:
                error_record = ErrorWord.objects.filter(user=request.user, word_id=wid).get()
                error_record.amend_count += 1
                error_record.save()
        if "error_words" in data:
            for wid in data["error_words"]:
                error_record = ErrorWord.objects.filter(user=request.user, word_id=wid).get()
                error_record.error_count += 1
                error_record.latest_error_time = get_now()
                error_record.save()
        return JsonResponse({
            "status": "success"
        })
