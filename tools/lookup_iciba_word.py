#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Lookup words from iciba.com.
# Usage:
#   lookup_iciba_word.py [word]
#
# It prints json formatted explanation of the word

import sys
import json
try:
    import urllib2
except:
    import urllib.parse as urllib2
import requests
import bs4
from lxml import etree


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



def lookup_iciba_word_api(word, api_key="5F843722A010097F76053C819EA9DF49"):
    """
    使用开放接口从金山词霸获取单词解释
    :param str word: 要查询的单词
    :param str api_key: 适用于 http://open.iciba.com/?c=api 的查词 API key
    :return dict: 单词的详细解释。例子如下：

    {
    "symbols" : [
        {
            "parts" : [
                {
                "means" : [
                    "毛衣，运动衫",
                    "出汗（过多）的人，发汗剂",
                    "榨取别人血汗的人（或工厂、公司等）"
                ],
                "part" : "n."
                },
                {
                "part" : "adj.",
                "means" : [
                    "运动衫的",
                    "运动衫式的"
                ]
                }
            ],
            "ph_en_mp3" : "http://res.iciba.com/resource/amp3/oxford/0/92/fb/92fbb012e16e5f5002f5aeede2471faa.mp3",
            "ph_am" : "ˈswɛtɚ",
            "ph_am_mp3" : "http://res.iciba.com/resource/amp3/1/0/94/6c/946c28f72272e09d162a79cd6f496ab4.mp3",
            "ph_other" : "",
            "ph_en" : "ˈswetə(r)",
            "ph_tts_mp3" : "http://res-tts.iciba.com/9/4/6/946c28f72272e09d162a79cd6f496ab4.mp3"
        }
    ],
    "items" : [
        ""
    ],
    "word_name" : "sweater",
    "sentenses" : [
        {
            "trans" : "她穿着白色的毛衣, 白色的毛衣, 白色的毛衣.",
            "orig" : "She's wearing a white sweater, a white sweater, a white sweater."
        },
        {
            "trans" : "它是毛衣. 它是毛衣.",
            "orig" : "It's a sweater. It's a sweater."
        },
        {
            "orig" : "He wore a noisy sweater.",
            "trans" : "他穿了件颜色十分鲜艳的毛衣."
        },
        {
            "trans" : "这个年轻人穿着一件柔软的灰色运动衫.",
            "orig" : "This young man is wearing a limp grey sweater."
        },
        {
            "trans" : "我穿着这件衣服去出席了一个午餐会,会上时装界人士济济一堂.",
            "orig" : "I wore the sweater to a luncheon which people in the fashion business would attend."
        }
    ],
    "exchange" : {
        "word_er" : "",
        "word_past" : "",
        "word_done" : "",
        "word_pl" : [
            "sweaters"
        ],
        "word_est" : "",
        "word_ing" : "",
        "word_third" : ""
    },
    "is_CRI" : 1
    }

    """
    data = {}
    # 先试图使用json来获取一些信息
    url = "http://dict-co.iciba.com/api/dictionary.php?w={0}&key={1}&type=json".format(urllib2.quote(word), api_key)
    result = requests.get(url)
    if result.status_code == 200:
        data = result.json()
    # 现在尝试使用xml方式来获取例句
    url = "http://dict-co.iciba.com/api/dictionary.php?w={0}&key={1}&type=xml".format(urllib2.quote(word), api_key)
    result = requests.get(url)
    if result.status_code == 200:
        text = b"\n".join(result.content.split(b"\n")[1:])
        parser = etree.XMLParser(encoding="utf-8")
        tree = etree.fromstring(text, parser=parser)

        sentenses = []
        for setense in tree.findall("sent"):
            orig = setense.find("orig").text.strip()
            trans = setense.find("trans").text.strip()
            
            sentenses.append({
                "orig": orig,
                "trans": trans
            })
        data["sentenses"] = sentenses
    return data


if __name__ == '__main__':
    result = lookup_iciba_word_api(sys.argv[1])
    json.dump(result, sys.stdout, indent=4, sort_keys=True)
