from django.shortcuts import render
from django.views.generic import View


class BookListView(View):
    def get(self, request):
        return render(request, 'todo.html', {
            "page": "books"
        })


class UnitListView(View):
    def get(self, request):
        return render(request, 'todo.html', {
            "page": "units"
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

