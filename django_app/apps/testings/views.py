# -*- coding: utf-8 -*-
import json
import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View

from learn.models import WordBook, WordUnit
from testings.forms import CreateQuizForm
from testings.models import Quiz, QuizQuestion, QuizResult
from users.models import UserGroup


class TestIndexView(LoginRequiredMixin, View):
    def get(self, request):
        # created by me
        quiz_created_by_me = Quiz.objects.filter(author=request.user).all()
        # shared to me
        my_groups = UserGroup.objects.filter(user=request.user).values("group")
        quiz_shared_to_me = Quiz.objects.filter(groups__in=my_groups).distinct()

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


class AjaxSaveQuizInfo(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            quiz_id = data["quiz_id"]
            description = data.get("description", None)
            max_total_time = data.get("max_total_time", None)
            max_word_time = data.get("max_word_time", None)

            # update the quiz name
            quiz = Quiz.objects.filter(id=quiz_id).get()
            if description:
                quiz.description = description
            if max_total_time:
                quiz.max_total_time = max_total_time
            if max_word_time:
                quiz.max_word_time = max_word_time
            quiz.save()

            return JsonResponse({
                "status": "ok"
            })
        except:
            return JsonResponse({
                "status": "fail"
            })


class AjaxSaveQuizWords(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            quiz_id = data["quiz_id"]
            words = data["words"]
            word_ids = [x["id"] for x in words]
            description = data.get("description", None)

            if description:
                # update the quiz name
                quiz = Quiz.objects.filter(id=quiz_id).get()
                if quiz.description != description:
                    quiz.description = description
                quiz.save()

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
            data = json.loads(request.body.decode("utf-8"))
            quiz_id = data["quiz_id"]
            group_ids = data["group_ids"]

            quiz = Quiz.objects.filter(id=quiz_id).get()

            quiz.groups.set(group_ids)
            return JsonResponse({
                "status": "ok",
                "groups": [{"id": x.id, "description": x.description} for x in quiz.groups.all()]
            })
        except IndexError:
            return JsonResponse({
                "status": "fail"
            })


class AjaxDeleteQuizView(View):
    def post(self, request):
        try:
            quiz_id = request.POST["quiz_id"]

            Quiz.objects.filter(id=quiz_id).delete()
            return JsonResponse({
                "status": "ok"
            })
        except IndexError:
            return JsonResponse({
                "status": "fail"
            })


class QuizStateView(View):
    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.filter(id=quiz_id).get()
            quiz_results = QuizResult.objects.filter(user=request.user, quiz=quiz).order_by("-finish_time").all()

            return render(request, 'quiz_state.html', {
                "quiz_results": quiz_results,
                "quiz": quiz,
                "question_count": quiz.quizquestion_set.count()
            })
        except:
            raise Http404()


class QuizTakeView(View):
    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.filter(id=quiz_id).get()
            return render(request, 'unit_learn.html', {
                "page": "learning",
                "quiz": quiz,
                "title": u"答卷",
                "type": 2,
                "data_url": reverse('testings.ajax_get_quiz_data', kwargs={"quiz_id": quiz_id}),
                "save_url": reverse('testings.ajax_save_quiz_result')
            })
        except:
            raise Http404()


class AjaxSaveQuizResultView(View):
    def post(self, request):
        quiz_id = request.POST.get("quiz_id", None)
        correct_count = request.POST.get("correct_count", 0)
        seconds_used = request.POST.get("seconds_used", 0)

        if not quiz_id:
            return JsonResponse({
                "status": "fail"
            })
        try:
            record = QuizResult()
            record.user = request.user
            record.quiz_id = quiz_id
            record.finish_time = datetime.datetime.now()
            record.correct_count = int(correct_count)
            record.start_time = record.finish_time - datetime.timedelta(seconds=int(seconds_used))
            record.save()
            return JsonResponse({
                "status": "success"
            })
        except:
            return JsonResponse({
                "status": "fail"
            })
