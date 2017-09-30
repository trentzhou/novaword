from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import View

from learn.models import WordBook
from testings.forms import CreateQuizForm
from testings.models import Quiz
from users.models import UserGroup


class TestIndexView(LoginRequiredMixin, View):
    def get(self, request):
        # created by me
        quiz_created_by_me = Quiz.objects.filter(author=request.user).all()
        # shared to me
        my_groups = UserGroup.objects.filter(user=request.user).values("group")
        quiz_shared_to_me = Quiz.objects.filter(groups__in=my_groups).all()

        return render(request, 'quiz_list.html', {
            "page": "testings",
            "quiz_created_by_me": quiz_created_by_me,
            "quiz_shared_to_me": quiz_shared_to_me
        })


class CreateQuizView(LoginRequiredMixin, View):
    def get(self, request):
        wordbooks = WordBook.objects.all()
        return render(request, 'quiz_create.html', {
            "page": "testings",
            "wordbooks": wordbooks
        })

    def post(self, request):
        form = CreateQuizForm(request.POST)
        if form.is_valid():
            # save the quiz object
            quiz = Quiz()
            quiz.author = request.user
            quiz.max_word_time = form.data["max_word_time"]
            quiz.max_total_time = form.data["max_total_time"]
            quiz.password = ""
            quiz.description = form.data["description"]
            quiz.book_id = form.data["book_id"]
            quiz.save()
            # do nothing
            return redirect(reverse('testings.edit_quiz', kwargs={
                "quiz_id": quiz.id
            }))
        else:
            # invalid form
            wordbooks = WordBook.objects.all()
            return render(request, 'quiz_create.html', {
                "page": "testings",
                "wordbooks": wordbooks
            })


class EditQuizView(View):
    def get(self, request, quiz_id):
        return render(request, 'quiz_edit.html', {
            "page": "testings"
        })
