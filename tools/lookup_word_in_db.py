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

from lookup_iciba_word import lookup_iciba_word_api


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
    try:
        from learn.models import Word
        result = find_word_in_db(word)
        if not result or not result.detailed_meanings:
            xx = lookup_iciba_word_api(word)
            if xx:
                if not result:
                    result = Word()
                result.spelling = word
                if "ph_am" in xx["symbols"][0]:
                    result.pronounciation_us = xx["symbols"][0]["ph_am"]
                if "ph_en" in xx["symbols"][0]:
                    result.pronounciation_uk = xx["symbols"][0]["ph_en"]
                if "ph_am_mp3" in xx["symbols"][0]:
                    result.mp3_us_url = xx["symbols"][0]["ph_am_mp3"]
                if "ph_en_mp3" in xx["symbols"][0]:
                    result.mp3_uk_url = xx["symbols"][0]["ph_en_mp3"]
                meanings = []
                for part in xx["symbols"][0]["parts"]:
                    meaning = part["part"] + ";".join(part["means"])
                    meanings.append(meaning)
                result.short_meaning = "\n".join(meanings)
                result.detailed_meanings = json.dumps(xx, indent=4, sort_keys=True)
                print("Saving {0}".format(result.spelling))
                result.save()

        return result
    except:
        print("Failed to look up word {0}".format(word))
        return None


def main():
    setup_django_env()

    word = sys.argv[1]
    # look up the database
    result = find_word(word)
    if result:
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
