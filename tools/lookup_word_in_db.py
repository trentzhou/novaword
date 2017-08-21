#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Lookup word.
# It first finds the word from the database.
# If the word does not exist in database, it will try to find the word
# from iciba.com, then insert it into the database
#
# Output is displayed in json format
import sys
import os
import django
import json

from lookup_iciba_word import lookup_iciba_word


def setup_django_env():
    word_master_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    django_project_path = os.path.join(word_master_dir, 'django_app')
    sys.path.append(django_project_path)
    sys.path.append(os.path.join(django_project_path, 'apps'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "word_master.settings")

    django.setup()


def find_word_in_db(word):
    from learn.models import Word
    word_in_db = Word.objects.filter(spelling=word)
    result = None
    if word_in_db:
        result = word_in_db[0]
    return result


def find_word(word):
    """
    Find word from DB, or iciba.com
    """
    from learn.models import Word

    try:
        result = find_word_in_db(word)
        if not result:
            xx = lookup_iciba_word(word)
            if xx and 'meaning' in xx and xx['meaning']:
                result = Word()
                result.spelling = word
                result.pronounciation_us = xx['us_pronounciation']
                result.pronounciation_uk = xx['uk_pronounciation']
                result.mp3_us_url = xx['us_mp3']
                result.mp3_uk_url = xx['uk_mp3']
                result.short_meaning = xx['meaning']
                result.save()
    except:
        return None
    return result


def main():
    setup_django_env()

    word = sys.argv[1]
    # look up the database
    result = find_word(word)
    json.dump({
        'spelling': word,
        'us_pronounciation': result.pronounciation_us,
        'uk_pronounciation': result.pronounciation_uk,
        'us_mp3': result.mp3_us_url,
        'uk_mp3': result.mp3_uk_url,
        'meaning': result.short_meaning
    }, sys.stdout, indent=4)


if __name__ == '__main__':
    main()
