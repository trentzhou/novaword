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


class AjaxAddBookToLearningPlanView(View):
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


class AjaxAddUnitToLearningPlanView(View):
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


class AjaxDeleteUnitFromLearningPlanView(View):
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


class AjaxIsUnitInLearningPlan(View):
    def get(self, request, unit_id):
        if LearningPlan.objects.filter(unit_id=unit_id, user=request.user).get():
            return JsonResponse({
                "result": "yes"
            })
        else:
            return JsonResponse({
                "result": "no"
            })


class LearningView(View):
    def get(self, request):
        return render(request, 'todo.html', {
            "page": "learning"
        })

class ReviewView(View):
    def get(self, request):
        return render(request, 'todo.html', {
            "page": "review"
        })

