#!/usr/bin/env python

import collections
import sqlite3

DB_FILENAME = './full-db.sql'
/Users/sayerrippey/Desktop/school/artificial intelligence/bee.rs/bee.rs/processing/process.py
connection = sqlite3.connect(DB_FILENAME)

cursor = connection.cursor()

cursor.execute('select * from reviews')

item = cursor.fetchone()

counter = collections.Counter()

i = 0
print('Starting...')
while item is not None:
    i += 1
    if i % 100000 == 0:
        print('At number: %s' % i)
    text = map(lambda s: s.lower().strip('.;,:!"?\'(){}[]'), item[5].split())
    for word in text:
        counter[word] += 1
    item = cursor.fetchone()

import pprint
pprint.pprint(counter.most_common(400))
