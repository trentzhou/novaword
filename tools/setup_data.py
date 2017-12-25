#!/usr/bin/env python

import yaml
from multiprocessing.dummy import Pool
import lookup_word_in_db


def setup_word_database():
    yaml_files = [
        'data/primary_school.yaml',
        'data/midschool.yaml',
        'data/high_school.yaml',
        'data/cet4.yaml',
        'data/cet6.yaml'
    ]
    pool = Pool(20)
    for file_name in yaml_files:
        print("Processing {0}".format(file_name))
        words = yaml.load(open(file_name))
        pool.map(lookup_word_in_db.find_word, (x[0].lower() for x in words))


def main():
    lookup_word_in_db.setup_django_env()
    setup_word_database()


if __name__ == '__main__':
    main()
