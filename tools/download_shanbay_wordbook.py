#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This tool can download all words from a shanbay.com word book. The downloaded information is stored in
# yaml format.
#
# Example:
#
#   download_shanbay_wordbook.py https://www.shanbay.com/wordbook/176890/
#
# Output as:
#
#   - ["impetus", "n. 动力,推动力"]
#   ...
#
# The output is printed on stdout.
import itertools
import requests
import bs4
import json
import sys
from multiprocessing.dummy import Pool


class ShanbayWordlistFetcher(object):
    def __init__(self):
        self.pool = Pool(10)

    def __del__(self):
        self.pool.close()

    def fetch_word_unit(self, wordunit_url):
        page_index = 1
        while True:
            url = "{0}?page={1}".format(wordunit_url, page_index)
            data = requests.get(url).content
            soup = bs4.BeautifulSoup(data, "lxml")
            table = soup.select(".table-striped")
            rows = table[0].find_all("tr")
            if len(rows) == 0:
                break
            for row in rows:
                cols = row.find_all("td")
                word = cols[0].get_text()
                explain = cols[1].get_text().strip()
                yield word.encode('utf-8'), explain.encode('utf-8')
            page_index += 1

    def fetch_wordbook(self, wordbook_url):
        data = requests.get(wordbook_url).content
        soup = bs4.BeautifulSoup(data, "lxml")
        divs = soup.select(".wordbook-create-wordlist-title")
        wordunit_urls = ["https://www.shanbay.com" + x.find("a")["href"] for x in divs]
        wordlist_list = self.pool.map(self.fetch_word_unit, wordunit_urls)
        result = reduce(itertools.chain, wordlist_list)
        return result


def main():
    wordbook_url = sys.argv[1]
    if not wordbook_url.startswith("https://www.shanbay.com/wordbook/"):
        raise ValueError("Wordbook URL should start with https://www.shanbay.com/wordbook/")

    wordlist = ShanbayWordlistFetcher().fetch_wordbook(wordbook_url)
    for word, explain in wordlist:
        print "- [\"{0}\", {1}]".format(word, json.dumps(explain))


if __name__ == '__main__':
    main()
