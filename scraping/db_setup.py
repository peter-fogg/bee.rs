#!/usr/bin/env python

'''
Sets up the database for our beer reviews. The format (right now) is that a review has:

an author (string),
a score (float),
review text (string),
look, smell, taste, feel, overall (floats)
'''

import os
import sqlite3

if not os.path.exists('./new_db_file'):
    f = open('./new_db_file', 'w')
    f.close()

connection = sqlite3.connect('./db_file')

cursor = connection.cursor()

cursor.execute('CREATE TABLE reviews (beername text, brewery text, author text, score real, review text)')
#, look float, smell float, taste float, feel float, overall float)')
connection.commit()
