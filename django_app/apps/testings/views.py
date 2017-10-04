import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View

from learn.models import WordBook, WordUnit
from testings.forms import CreateQuizForm
from testings.models import Quiz, QuizQuestion
from users.models import UserGroup, Group
from utils import parse_bool


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
        try:
            quiz = Quiz.objects.filter(id=quiz_id).get()
            my_groups = UserGroup.objects.filter(user=request.user).values("group_id", "group__description")
            units = WordUnit.objects.filter(book=quiz.book).order_by("order").all()
            return render(request, 'quiz_edit.html', {
                "page": "testings",
                "quiz": quiz,
                "groups": my_groups,
                "units": units
            })
        except IndexError:
            raise Http404()


class AjaxGetQuizDataView(View):
    def get(self, request, quiz_id):
        try:
            questions = QuizQuestion.objects.filter(quiz_id=quiz_id).all()
            result = []
            for question in questions:
                w = question.word
                result.append({
                    "id": w.id,
                    "simple_meaning": w.simple_meaning,
                    "spelling": w.word.spelling,
                    "pronounciation_us": w.word.pronounciation_us,
                    "pronounciation_uk": w.word.pronounciation_uk,
                    "mp3_us_url": w.word.mp3_us_url,
                    "mp3_uk_url": w.word.mp3_uk_url,
                    "short_meaning_in_dict": w.word.short_meaning,
                    "detailed_meaning_in_dict": w.word.detailed_meanings,
                    "quiz_format": question.quiz_format
                })
            return JsonResponse({
                "status": "ok",
                "data": result
            })
        except:
            return JsonResponse({
                "status": "fail"
            })


class AjaxSaveQuiz(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            quiz_id = data["quiz_id"]
            words = data["words"]
            word_ids = [x["id"] for x in words]

            # delete all words whose id is not in word_ids
            QuizQuestion.objects.filter(Q(quiz_id=quiz_id) & ~Q(word_id__in=word_ids)).delete()
            # then add the words.
            # TODO: possibly optimize it?
            for word in words:
                if not QuizQuestion.objects.filter(quiz_id=quiz_id, word_id=word["id"]).count():
                    question = QuizQuestion()
                    question.quiz_id = quiz_id
                    question.word_id = word["id"]
                    question.quiz_format = word.get("quiz_format", 0)
                    question.save()
            return JsonResponse({
                "status": "ok"
            })
        except:
            return JsonResponse({
                "status": "fail"
            })


class AjaxShareQuizView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            quiz_id = data["quiz_id"]
            group_ids = data["group_ids"]

            quiz = Quiz.objects.filter(id=quiz_id).get()

            quiz.groups.set(group_ids)
            return JsonResponse({
                "status": "ok",
                "groups": [{"id": x.id, "description": x.description} for x in quiz.groups.all()]
            })
        except:
            return JsonResponse({
                "status": "fail"
            })