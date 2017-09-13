#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from lookup_word_in_db import setup_django_env, find_word

class Unit(object):
    unit_regex = re.compile(r'(\d[AB])(\d+)')

    @staticmethod
    def create_unit(title):
        "create unit object from string"
        m = Unit.unit_regex.match(title)
        if m:
            return Unit(m.group(1), m.group(2))
        return None

    def __init__(self, book, unit):
        self.book = book
        self.unit = unit

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"{0}{1}".format(self.book, self.unit)


class Word(object):
    word_regex = re.compile(r'([a-zA-Z\, \'\?\.!\-]+)(.*) \((.*)\)')

    @staticmethod
    def create_word(line):
        "create a word object from a line"
        m = Word.word_regex.match(line.strip())
        if m:
            return Word(m.group(1), m.group(2), m.group(3))
        return None

    def __init__(self, spelling, meaning, unit_titles):
        self.spelling = spelling.strip()
        self.meaning = meaning
        unit_titles = unit_titles.replace(";", ",").replace(" ", "")
        units = unit_titles.split(',')
        self.units = []
        for u in units:
            o = Unit.create_unit(u)
            if o:
                self.units.append(o)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"'{0}' in unit [{1}]".format(self.spelling, ",".join(str(x) for x in self.units))


def parse_wordbook(bookname):
    unit_map = {}
    book_map = {}
    with open(bookname) as f:
        while True:
            line = f.readline()
            if not line:
                break
            word = Word.create_word(line)
            if word:
                for unit in word.units:
                    unit_title = str(unit)
                    if unit_title not in unit_map:
                        unit_map[unit_title] = []
                    unit_map[unit_title].append(word)
    # ok, now we have built the unit map. build the book map
    for unit_title in unit_map.keys():
        unit = Unit.create_unit(unit_title)
        book = unit.book
        if book not in book_map:
            book_map[book] = []
        book_map[book].append(unit_title)

    setup_django_env()
    from learn.models import Word as W, WordBook, WordUnit, WordInUnit
    from users.models import UserProfile

    user = UserProfile.objects.all()[0]
    # create books
    for book_title in sorted(book_map.keys()):
        description = u"江苏小学" + book_title
        if not WordBook.objects.filter(description=description).count():
            book = WordBook()
            book.description = description
            book.uploaded_by = user
            book.save()
            # create the units
            for unit_title in book_map[book_title]:
                unit = Unit.create_unit(unit_title)
                description = "Unit " + str(unit.unit)
                unit_obj = WordUnit()
                unit_obj.book = book
                unit_obj.description = description
                unit_obj.order = unit.unit
                unit_obj.save()
                # create the words
                for index, word in enumerate(unit_map[unit_title]):
                    word_obj = find_word(word.spelling)
                    if not word_obj:
                        print(u"Cannot find word {0} from iciba.com".format(str(word)))
                        # create a new Word object
                        word_obj = W()
                        word_obj.spelling = word.spelling
                        word_obj.short_meaning = word.meaning
                        word_obj.save()
                    wiu = WordInUnit()
                    wiu.word = word_obj
                    wiu.unit = unit_obj
                    wiu.order = index
                    wiu.simple_meaning = word.meaning
                    wiu.save()


def main():
    parse_wordbook("data/jiangsu_primary_school.txt")

if __name__ == '__main__':
    main()
