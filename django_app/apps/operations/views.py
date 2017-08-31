from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.views.generic import View

from utils.lookup_word_in_db import find_word


class MessageView(View):
    def get(self, request, message_id):
        return render(request, 'todo.html', {
            "page": "messages"
        })


class MessageListView(View):
    def get(self, request):
        return render(request, 'todo.html', {
            "page": "messages"
        })


class DictionaryView(View):
    def get(self, request, spelling):
        # lookup the word
        word = find_word(spelling)
        if not word:
            raise Http404()
        return render(request, "dictionary.html", {
            "word": word
        })


class DictionaryFormView(View):
    def post(self, request):
        spelling = request.POST.get("spelling", "")
        return HttpResponseRedirect(reverse("operations.dictionary", kwargs={"spelling":spelling}))


class HighscoreView(View):
    def get(self, request):
        return render(request, 'todo.html', {
            "page": "highscore"
        })