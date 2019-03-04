import json
import logging
import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.http import JsonResponse
from django.views.generic import View

from learn.models import WordInUnit, Word, WordUnit, WordBook
from utils import lookup_word_in_db

logger = logging.getLogger(__name__)


class AjaxNewUnitView(LoginRequiredMixin, View):
    def post(self, request):
        book_id = request.POST.get("book_id", 0)
        description = request.POST.get("description", "")

        try:
            if description:
                book = WordBook.objects.filter(id=book_id).get()
                max_order = WordUnit.objects.filter(book=book).aggregate(Max("order"))["order__max"]
                if not max_order:
                    max_order = 0
                unit = WordUnit()
                unit.book = book
                unit.description = description
                unit.order = max_order + 1
                unit.save()

                return JsonResponse({
                    "status": "ok",
                    "unit_id": unit.id
                })

        except:
            pass
        return JsonResponse({
            "status": "fail",
            "reason": "输入不对"
        })

def get_next_unit_name(name):
    regex = re.compile(r"(\D*)(\d+)(\D*)")
    m = regex.match(name)
    if m:
        index = int(m.group(2)) + 1
        return m.group(1) + str(index) + m.group(3)
    else:
        return name + "1"


class AjaxBatchAddUnitView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        book_id = data.get('book_id', None)
        first_unit_name = data.get('first_unit_name', None)
        unit_size_limit = int(data.get('unit_size_limit', 20))
        text = data.get('text', "")

        failed_lines = []
        try:
            parsed_words = []

            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                good = False

                try:
                    parsed = parse_word_line(line)
                    if parsed:
                        parsed_words.append(parsed)
                        good = True
                except:
                    pass
                if not good:
                    failed_lines.append(line)
            # generate data to be added
            units_to_add = []
            unit_name = first_unit_name
            book = WordBook.objects.filter(id=book_id).get()
            max_order = WordUnit.objects.filter(book=book).aggregate(Max("order"))["order__max"]
            if not max_order:
                max_order = 0
            order = max_order + 1
            while len(parsed_words) > 0:
                words = parsed_words[:unit_size_limit]
                unit = {
                    'name': unit_name,
                    'order': order,
                    'words': words
                }
                units_to_add.append(unit)
                parsed_words = parsed_words[unit_size_limit:]
                unit_name = get_next_unit_name(unit_name)
                order += 1
            # now create the units
            for unit in units_to_add:
                wordunit = WordUnit()
                wordunit.book = book
                wordunit.description = unit['name']
                wordunit.order = unit['order']
                wordunit.save()
                # generate the words
                for word in unit['words']:
                    add_word_to_unit(wordunit.id, word['word'], word['meaning'])
            return JsonResponse({
                'status': 'ok',
                'failed_lines': failed_lines
            })
        except:
            logger.exception("Faled to add word")
            return JsonResponse({
                'status': 'fail'
            })


class AjaxEditUnitView(LoginRequiredMixin, View):
    def post(self, request):
        unit_id = request.POST.get("unit_id", 0)
        description = request.POST.get('description', "")
        order = request.POST.get("order", 0)
        try:
            if description:
                unit = WordUnit.objects.filter(id=unit_id).get()
                unit.description = description
                unit.order = int(order)
                unit.save()
                return JsonResponse({
                    "status": "ok"
                })
        except:
            pass
        return JsonResponse({
            "status": "fail",
            "reason": "输入不对"
        })


class AjaxDeleteUnitView(LoginRequiredMixin, View):
    def post(self, request):
        unit_id = request.POST.get("unit_id", 0)
        WordUnit.objects.filter(id=unit_id).delete()
        return JsonResponse({
            "status": "ok"
        })


def add_word_to_unit(unit_id, spelling, meaning, detailed_meaning=""):
    """
    把单词添加到单元里
    :param unit_id:
    :param spelling:
    :param meaning:
    :param detailed_meaning:
    :return:
    """
    unit = WordUnit.objects.filter(id=unit_id).get()

    # in case the word already exists
    if not WordInUnit.objects.filter(unit=unit, word__spelling=spelling).count():
        unit_word = WordInUnit()
        max_order = WordInUnit.objects.filter(unit=unit).aggregate(Max("order"))["order__max"]
        if not max_order:
            max_order = 0
        if spelling and meaning:
            # try to find the word first
            word = lookup_word_in_db.find_word(spelling)
            if not word:
                word = Word()
                word.spelling = spelling
                word.short_meaning = meaning
                word.detailed_meanings = "{}"
                word.save()

        unit_word.word = word
        unit_word.unit = unit
        unit_word.simple_meaning = meaning
        unit_word.detailed_meaning = detailed_meaning
        unit_word.order = max_order + 1
        unit_word.save()


class AjaxNewWordInUnitView(LoginRequiredMixin, View):
    def post(self, request):
        spelling = request.POST.get("spelling", "")
        meaning = request.POST.get("meaning", "")
        detailed_meaning = request.POST.get("detailed_meaning", "")
        unit_id = request.POST.get("unit_id", "")

        try:
            add_word_to_unit(unit_id, spelling, meaning, detailed_meaning)
            return JsonResponse({
                "status": "ok"
            })

        except:
            pass
        return JsonResponse({
            "status": "fail"
        })


line_word_re = re.compile("(.*)(\t| {4})(.*)")


def parse_word_line(line):
    m = line_word_re.match(line)
    if m:
        word = m.group(1).strip()
        meaning = m.group(3).strip()
        return {
            "word": word,
            "meaning": meaning
        }
    return None

class AjaxBatchInputWordView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        unit_id = data.get('unit_id', None)
        text = data.get('text', '')

        if not unit_id or not text:
            return JsonResponse({
                "status": "fail"
            })
        failed_lines = []
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            good = False

            try:
                parsed = parse_word_line(line)

                if parsed:
                    word = parsed["word"]
                    meaning = parsed["meaning"]
                    add_word_to_unit(unit_id, word, meaning)
                    good = True
            except:
                pass
            if not good:
                failed_lines.append(line)

        return JsonResponse({
            "status": "ok",
            "failed_lines": failed_lines
        })


class AjaxDeleteWordInUnitView(LoginRequiredMixin, View):
    def post(self, request):
        unit_words = request.POST.get("unit_word_ids", "")
        words = unit_words.split(",")
        for id in words:
            WordInUnit.objects.filter(id=id).delete()
        return JsonResponse({
            "status": "ok"
        })

