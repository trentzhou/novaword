# -*- coding: utf-8 -*-
import datetime
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.db.models import Count, Q, Max
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.generic import View

from learn.models import WordBook, WordUnit, WordInUnit, LearningPlan, LearningRecord, ErrorWord, Word
from operations.models import GroupLearningPlan
from testings.models import QuizResult
from users.models import UserGroup
from users.templatetags.user_info import is_teacher


class BookListView(View):
    def get(self, request):
        wordbooks = WordBook.objects.all()

        return render(request, 'wordbook_list.html', {
            "page": "books",
            "wordbooks": wordbooks
        })


def make_string_groups(m):
    """
    Taken a dict[str, object], return a tree.
    Example:

    strings = {
        "1 2 3 4": "first",
        "1 2 3 3": "second",
        "1 2 4 4": "third",
        "1 2 4 3": "fourth",
        "1 2": "fifth",
        "1 3 3": "sixth"
    }
    result = make_string_groups(strings)

    Now the result looks like:
    {
        "1": {
            "2": {
                "3": {
                    "3": "second",
                    "4": "first"
                },
                "4": {
                    "3": "fourth",
                    "4": "third"
                },
                "___": "fifth"
            },
            "3": {
                "3": "sixth"
            }
        }
    }

    :param dict[str, object] m: the map object which has key as ' ' separated string
    :return tree
    """
    result = {}
    for k, v in m.items():
        container = result
        row = k.split(' ')
        for folder in row[:-1]:
            if folder not in container:
                container[folder] = {}
            container = container[folder]
        final = row[-1]
        if final in container:
            container[final]["___"] = v
        else:
            container[row[-1]] = v
    return result


class AjaxBookTreeView(View):
    def get(self, request):
        wordbooks = WordBook.objects.all()
        wordbook_map = {}
        for book in wordbooks:
            wordbook_map[book.description] = {
                "description": book.description,
                "id": book.id
            }
        # construct a map
        book_tree = make_string_groups(wordbook_map)
        return JsonResponse({
            "status": "ok",
            "books": book_tree
        })


class AjaxBookListView(View):
    def get(self, request):
        wordbooks = WordBook.objects.order_by("description").values("id", "description").all()
        return JsonResponse({
            "status": "ok",
            "books": [x for x in wordbooks]
        })


class AjaxBookUnitsView(View):
    def get(self, request, book_id):
        units = WordUnit.objects.filter(book_id=book_id).order_by("order").values("id", "description")
        return JsonResponse({
            "status": "ok",
            "units": [x for x in units]
        })


class AjaxNewBookView(View):
    def post(self, request):
        description = request.POST.get("description", "")
        if description:
            book = WordBook()
            book.description = description
            book.uploaded_by = request.user
            book.save()
            return JsonResponse({
                "status": "ok",
                "book_id": book.id
            })
        else:
            return JsonResponse({
                "status": "fail",
                "reason": "标题不对"
            })


class AjaxEditBookView(View):
    def post(self, request):
        book_id = request.POST.get("book_id", 0)
        description = request.POST.get("description", "")

        try:
            if description:
                book = WordBook.objects.filter(id=book_id).get()
                book.description = description
                book.save()
                return JsonResponse({
                    "status": "ok"
                })
        except:
            pass

        return JsonResponse({
            "status": "fail",
            "reason": "输入不对"
        })


class AjaxDeleteBookView(View):
    def post(self, request):
        book_id = request.POST.get("book_id", 0)
        WordBook.objects.filter(id=book_id).delete()
        return JsonResponse({
            "status": "ok"
        })


class AjaxNewUnitView(View):
    def post(self, request):
        book_id = request.POST.get("book_id", 0)
        description = request.POST.get("description", "")

        try:
            if description:
                book = WordBook.objects.filter(id=book_id).get()
                max_order = WordUnit.objects.filter(book=book).aggregate(Max("order"))["order__max"]
                if not max_order:
                    max_order = 0
                unit = WordUnit()
                unit.book = book
                unit.description = description
                unit.order = max_order + 1
                unit.save()

                return JsonResponse({
                    "status": "ok",
                    "unit_id": unit.id
                })

        except:
            pass
        return JsonResponse({
            "status": "fail",
            "reason": "输入不对"
        })


class AjaxEditUnitView(View):
    def post(self, request):
        unit_id = request.POST.get("unit_id", 0)
        description = request.POST.get('description', "")
        order = request.POST.get("order", 0)
        try:
            if description:
                unit = WordUnit.objects.filter(id=unit_id).get()
                unit.description = description
                unit.order = int(order)
                unit.save()
                return JsonResponse({
                    "status": "ok"
                })
        except:
            pass
        return JsonResponse({
            "status": "fail",
            "reason": "输入不对"
        })


class AjaxDeleteUnitView(View):
    def post(self, request):
        unit_id = request.POST.get("unit_id", 0)
        WordUnit.objects.filter(id=unit_id).delete()
        return JsonResponse({
            "status": "ok"
        })


class AjaxNewWordInUnitView(View):
    def post(self, request):
        spelling = request.POST.get("spelling", "")
        meaning = request.POST.get("meaning", "")
        unit_id = request.POST.get("unit_id", "")

        try:
            unit = WordUnit.objects.filter(id=unit_id).get()

            if spelling and meaning:
                # try to find the word first
                word = Word.objects.filter(spelling=spelling).first()
                if not word:
                    word = Word()
                    word.spelling = spelling
                    word.short_meaning = meaning
                    word.save()

            unit_word = WordInUnit()
            max_order = WordInUnit.objects.filter(unit=unit).aggregate(Max("order"))["order__max"]
            if not max_order:
                max_order = 0
            unit_word.word = word
            unit_word.unit = unit
            unit_word.simple_meaning = meaning
            unit_word.order = max_order + 1
            unit_word.save()

            return JsonResponse({
                "status": "ok"
            })

        except:
            pass
        return JsonResponse({
            "status": "fail"
        })


class AjaxDeleteWordInUnitView(View):
    def post(self, request):
        unit_words = request.POST.get("unit_word_ids", "")
        words = unit_words.split(",")
        for id in words:
            WordInUnit.objects.filter(id=id).delete()
        return JsonResponse({
            "status": "ok"
        })


class BookDetailView(View):
    def get(self, request, book_id):
        wordbook = WordBook.objects.filter(id=book_id).get()
        if not wordbook:
            raise Http404()

        units = WordUnit.objects.filter(book_id=book_id).order_by("order").all()
        return render(request, 'wordbook_detail.html', {
            "page": "books",
            "book": wordbook,
            "units": units
        })


class UnitListView(View):
    # list all units which are in the learning plan
    def get(self, request):
        plans = LearningPlan.objects.filter(user=request.user).order_by("unit__book", "unit__order").all()
        units = [x.unit for x in plans]
        for u in units:
            u.learn_times = u.learn_count(request.user)
            u.review_times = u.review_count(request.user)

        return render(request, 'unit_list.html', {
            "page": "units",
            "units": units
        })


class UnitDetailView(View):
    def get(self, request, unit_id):
        unit = WordUnit.objects.filter(id=unit_id).get()
        if not unit:
            raise Http404()

        words = WordInUnit.objects.filter(unit=unit).order_by("order").all()
        records = LearningRecord.objects.filter(unit=unit, user=request.user).order_by("-learn_time").all()
        return render(request, 'unit_detail.html', {
            "page": "units",
            "unit": unit,
            "records": records,
            "words": words,
            "is_planned": unit.is_planned(request.user)
        })


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
    user_groups = UserGroup.objects.filter(user_id=user_id).values("group")
    group_units = GroupLearningPlan.objects.filter(group__in=user_groups).values("unit_id").distinct().all()
    for u in group_units:
        active_units[u["unit_id"]] = True
    return active_units.keys()


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
    return True


def get_todays_units(user_id):
    """
    Get list of today's pending units
    :param int user_id:
    :return list: list of unit ids for today's learning
    """
    active_units = get_active_units(user_id)
    result = [x for x in active_units if not has_learned_today(user_id, x) and is_unit_for_today(user_id, x)]
    return result


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
    def get(self, request):
        learn_count = LearningRecord.objects.filter(user=request.user).count()
        quiz_count = QuizResult.objects.filter(user=request.user).count()
        erroneous_words = ErrorWord.objects.filter(user=request.user, amend_count__lt=2).count()
        # get recent learned units
        active_units = get_active_units(request.user.id)
        today_units = get_todays_units(request.user.id)
        '''
        
        recent_units = LearningRecord.objects\
            .filter(user=request.user)\
            .values("unit_id").annotate(learn_count=Count("unit_id"))\
            .order_by("learn_count")\
            .values("unit_id", "unit__book_id", "unit__book__description", "unit__description", "learn_count").all()
        '''
        recent_units = []
        for u in active_units:
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
        mastered_unit_count = sum(1 for x in recent_units if x["learn_count"] > 5)
        all_my_learned_units = LearningRecord.objects.filter(user=request.user).values("unit_id")
        backlog_units = LearningPlan.objects\
            .filter(user=request.user)\
            .filter(~Q(unit_id__in=all_my_learned_units))\
            .order_by("unit__book_id", "unit__order").all()
        return render(request, 'index.html', {
            "page": "overview",
            "learn_count": learn_count,
            "quiz_count": quiz_count,
            "erroneous_words": erroneous_words,
            "today_units": today_units,
            "backlog_units": backlog_units,
            "recent_units": recent_units[:10],
            "mastered_unit_count": mastered_unit_count
        })


class LearningView(LoginRequiredMixin, View):
    def get(self, request):
        records = LearningRecord.objects.filter(user=request.user).order_by("-learn_time").all()

        return render(request, 'learn_records.html', {
            "page": "learning",
            "records": records
        })


class ReviewView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'todo.html', {
            "page": "review"
        })


class AjaxUnitDataView(View):
    def get(self, request, unit_id):
        words_in_unit = WordInUnit.objects.filter(unit_id=unit_id).order_by("order").all()
        if not words_in_unit:
            return JsonResponse({
                "status": "failure"
            })
        result = []
        for w in words_in_unit:
            result.append({
                "id": w.id,
                "simple_meaning": w.simple_meaning,
                "spelling": w.word.spelling,
                "pronounciation_us": w.word.pronounciation_us,
                "pronounciation_uk": w.word.pronounciation_uk,
                "mp3_us_url": w.word.mp3_us_url,
                "mp3_uk_url": w.word.mp3_uk_url,
                "short_meaning_in_dict": w.word.short_meaning,
                "detailed_meaning_in_dict": w.word.detailed_meanings
            })
        return JsonResponse({
            "data": result
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
            return render(request, 'unit_learn.html', {
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

        if not unit_id or not type:
            return JsonResponse({
                "status": "fail"
            })
        try:
            unit = WordUnit.objects.filter(id=unit_id).get()
            record = LearningRecord()
            record.user = request.user
            record.unit = unit
            record.type = type
            record.correct_rate = correct_rate
            record.save()
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
                    error_record.latest_error_time = datetime.datetime.now()
                    error_record.save()
            return JsonResponse({
                "status": "success"
            })
        except:
            return JsonResponse({
                "status": "fail"
            })


class UnitReviewView(View):
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


class ErrorWordListView(View):
    def get(self, request):
        error_words = ErrorWord.objects.filter(user=request.user).order_by("-latest_error_time").all()
        return render(request, "error_word_list.html", {
            "page": "error_words",
            "error_words": error_words
        })


class AmendErrorWordView(View):
    def get(self, request):
        return render(request, 'unit_learn.html', {
            "page": "learning",
            "page_title": u"错词重测",
            "type": 2,
            "data_url": reverse('learn.ajax_error_words'),
            "save_url": reverse('learn.ajax_amend_error_words')
        })


class AjaxErrorWordsView(View):
    def get(self, request):
        error_words = ErrorWord.objects.filter(user=request.user, amend_count__lt=2).order_by("-latest_error_time").all()
        result = []
        for error_word in error_words:
            w = error_word.word
            result.append({
                "id": w.id,
                "simple_meaning": w.simple_meaning,
                "spelling": w.word.spelling,
                "pronounciation_us": w.word.pronounciation_us,
                "pronounciation_uk": w.word.pronounciation_uk,
                "mp3_us_url": w.word.mp3_us_url,
                "mp3_uk_url": w.word.mp3_uk_url,
                "short_meaning_in_dict": w.word.short_meaning,
                "detailed_meaning_in_dict": w.word.detailed_meanings
            })
        return JsonResponse({
            "data": result
        })


class AjaxAmendErrorWordsView(View):
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
                error_record.latest_error_time = datetime.datetime.now()
                error_record.save()
        return JsonResponse({
            "status": "success"
        })
