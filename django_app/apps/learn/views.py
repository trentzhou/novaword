from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.generic import View

from learn.models import WordBook, WordUnit, WordInUnit, LearningPlan


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
        return render(request, 'unit_detail.html', {
            "page": "units",
            "unit": unit,
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


class LearningView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'todo.html', {
            "page": "learning"
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
                "unit": unit
            })
        except:
            raise Http404()


class UnitTestView(LoginRequiredMixin, View):
    def get(self, request, unit_id):
        try:
            unit = WordUnit.objects.filter(id=unit_id).get()
            return render(request, 'unit_test.html', {
                "page": "learning",
                "unit": unit
            })
        except:
            raise Http404()
