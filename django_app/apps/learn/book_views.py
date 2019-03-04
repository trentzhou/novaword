import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.views.generic import View

from learn.models import WordBook, WordUnit
from users.models import UserProfile

logger = logging.getLogger(__name__)


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

    :param dict[str, object] m: the map object which has key as '/' separated string
    :return tree
    """
    result = {}
    for k, v in m.items():
        container = result
        row = k.split('/')
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
                "description": book.description.split('/')[-1],
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


class AjaxBookAddMaintainer(View):
    def post(self, request):
        book_id = request.POST.get("book_id")
        user_name = request.POST.get("user_name")
        try:
            maintainer = UserProfile.objects.filter(Q(email=user_name) | Q(mobile_phone=user_name)).get()
            book = WordBook.objects.filter(id=book_id).get()
            book.maintainers.add(maintainer)
            book.save()
        except:
            logger.exception("Failed to add maintainer")
            return JsonResponse({
                "status": "fail"
            })
        return JsonResponse({
            "status": "ok"
        })


class AjaxBookDeleteMaintainer(View):
    def post(self, request):
        book_id = request.POST.get("book_id")
        user_id = request.POST.get("user_id")
        try:
            book = WordBook.objects.filter(id=book_id).get()
            book.maintainers.remove(UserProfile.objects.get(id=user_id))
            book.save()
        except:
            return JsonResponse({
                "status": "fail"
            })
        return JsonResponse({
            "status": "ok"
        })


class AjaxBookUnitsView(View):
    def get(self, request, book_id):
        units = WordUnit.objects.filter(book_id=book_id).order_by("order").values("id", "description")
        return JsonResponse({
            "status": "ok",
            "units": [x for x in units]
        })


class AjaxNewBookView(LoginRequiredMixin, View):
    def post(self, request):
        description = request.POST.get("description", "")
        if description:
            # 是否重名？
            if WordBook.objects.filter(description=description).count():
                return JsonResponse({
                    "status": "fail",
                    "reason": "名为'{0}'的单词书已经存在了".format(description)
                })
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


class AjaxEditBookView(LoginRequiredMixin, View):
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


class AjaxDeleteBookView(LoginRequiredMixin, View):
    def post(self, request):
        book_id = request.POST.get("book_id", 0)
        WordBook.objects.filter(id=book_id).delete()
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
