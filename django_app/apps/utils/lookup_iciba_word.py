#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Lookup words from iciba.com.
# Usage:
#   lookup_iciba_word.py [word]
#
# It prints json formatted explanation of the word

import sys
import json
import requests
import bs4


def lookup_iciba_word(word):
    url = "http://www.iciba.com/{0}".format(word)
    content = requests.get(url).content
    soup = bs4.BeautifulSoup(content, 'lxml')
    result = {
        'us_pronounciation': '',
        'uk_pronounciation': '',
        'us_mp3': '',
        'uk_mp3': ''
    }
    # get pronounciation and voice
    voice_divs = soup.select('.base-speak')
    if voice_divs:
        voice_div = voice_divs[0]
        for voice_span in voice_div:
            if type(voice_span) is bs4.element.Tag:
                text = voice_span.get_text().strip()
                mp3_url = ''
                mp3_tags = voice_span.find_all(lambda x:
                                               x.has_attr('ms-on-mouseover'))
                if mp3_tags:
                    mp3_url = mp3_tags[0]['ms-on-mouseover']
                    mp3_url = mp3_url.split("'")[1]
                if u"美" in text:
                    result['us_pronounciation'] = text.replace(u"美 ", '')
                    result['us_mp3'] = mp3_url
                elif u"英" in text:
                    result['uk_pronounciation'] = text.replace(u"英 ", '')
                    result['uk_mp3'] = mp3_url
    # get meaning
    meaning_divs = soup.select('.base-list')
    if meaning_divs:
        result['meaning'] = meaning_divs[0]. \
                                get_text(). \
                                strip(). \
                                replace("\n", " "). \
                                replace("  ", " ")
    return result


if __name__ == '__main__':
    result = lookup_iciba_word(sys.argv[1])
    json.dump(result, sys.stdout, indent=4, sort_keys=True)
