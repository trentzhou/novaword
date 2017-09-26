# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Max
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.generic import View

from learn.models import WordBook, WordUnit, WordInUnit, LearningPlan, LearningRecord
from testings.models import QuizResult


class BookListView(View):
    def get(self, request):
        wordbooks = WordBook.objects.all()
        return render(request, 'wordbook_list.html', {
            "page": "books",
            "wordbooks": wordbooks
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

        words = WordInUnit.objects.filter(unit=unit).all()
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


class LearningOverviewView(LoginRequiredMixin, View):
    def get(self, request):
        learn_count = LearningRecord.objects.filter(user=request.user).count()
        quiz_count = QuizResult.objects.filter(user=request.user).count()
        erroneous_words = 0
        # get recent learned units
        recent_units = LearningRecord.objects\
            .filter(user=request.user)\
            .values("unit_id").annotate(learn_count=Count("unit_id"))\
            .order_by("learn_count")\
            .values("unit_id", "unit__book_id", "unit__book__description", "unit__description", "learn_count").all()
        mastered_unit_count = sum(1 for x in recent_units if x["learn_count"] > 5)
        return render(request, 'index.html', {
            "page": "overview",
            "learn_count": learn_count,
            "quiz_count": quiz_count,
            "erroneous_words": erroneous_words,
            "recent_units": recent_units[:5],
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
            "words": result
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
                "title": u"单元学习",
                "type": 1
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
                "title": u"单元测试",
                "type": 2
            })
        except:
            raise Http404()


class AjaxSaveLearnRecordView(LoginRequiredMixin, View):
    def post(self, request):
        unit_id = request.POST.get("unit_id", None)
        type = request.POST.get("type", None)
        correct_rate = request.POST.get("correct_rate", 0)

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
                "title": u"单元复习"
            })
        except KeyError:
            raise Http404()
