from django.shortcuts import render
from django.views.generic import View


class TestIndexView(View):
    def get(self, request):
        return render(request, 'todo.html', {
            "page": "testings"
        })