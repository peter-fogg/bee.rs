#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

'''
Scraper for BeerAdvocate. This is real quick and hacky, all the way
through. Wooooo.
'''

import bs4
import re
import urllib2

BA_DOMAIN = 'http://beeradvocate.com'
START_URL = 'http://beeradvocate.com/beer/reviews'
REVIEW_ID = 'rating_fullview_content_2'
TEST_URL = 'http://beeradvocate.com/beer/profile/345/1005/?'

test_page = bs4.BeautifulSoup(urllib2.urlopen(START_URL))

def get_next_page(page):
    '''
    Given a soup of a page, returns the URL of the next page, or
    None if we're at the last one.
    '''
    next_string = u'next ›'
    def tags_filter(tag):
        return tag.text == next_string
    next_tag = page.find(tags_filter)
    return (BA_DOMAIN + next_tag['href']) if next_tag is not None else None

def get_beer_urls(page):
    '''
    Given a soup of a page, returns a list of all the beer review URLs
    on that page.
    '''
    regex = re.compile('/beer/profile/[0-9]+/[0-9]+/.*')
    return [BA_DOMAIN + link.get('href') for link in page.find_all('a') if regex.match(link.get('href'))]

def strip_url_params(url):
    '''
    Removes any GET parameters from a URL. For some reason certain
    params prevent beer reviews from being rendered on BA, which is
    bad.
    '''
    return url.split('?')[0]

def get_beer_page(url):
    '''
    Given a URL for a beer on BA, returns a dictionary consisting of
    all relevant info about said beer.
    '''
    html = urllib2.urlopen(strip_url_params(url)).read()
    parsed = bs4.BeautifulSoup(html)
    reviews = filter(lambda x: x['id'] == REVIEW_ID if 'id' in x.attrs.keys() else False, parsed.find_all('div'))
    ret = []
    for review in reviews:
        try:
            ret.append(get_review_attributes(review))
        except Exception:
            pass
    return ret

def get_review_attributes(review):
    '''
    Given the soup for a review, returns all the important attributes
    of said review -- overall rating, review text, etc.
    '''
    review_strings = [s for s in review.strings] # turn the generator into a list
    final = {}
    final['score'] = float(review.span.string)
    final['author'] = review.h6.a.string
    particulars = filter(lambda x: x.startswith('look'), review_strings)[0]
    review_strings.remove(particulars)
    particulars = particulars.split('|')
    total = {}
    for particular in particulars: # parsing look, smell, taste, etc.
        pieces = particular.split(':')
        total[pieces[0]] = float(pieces[1])
    final['particulars'] = total
    final['review'] = u'\n'.join(review_strings)
    return final
    # for line in review.strings:
    #     if line.startswith(('A', 'S', 'T', 'M', 'O')):
    #         review_dict.update(get_review_line(line))
        
            
# def get_review_line(line):
#     '''
#     Splits a line like
    
#     "A: a deep copper colored ale"
    
#     into "A" and "a deep copper colored ale", and returns a dict.
#     '''
#     pieces = line.split(':')
#     if len(pieces) = 1:
#         pieces = line.split('-')
#     return {pieces[0]: pieces[1].strip()}

if __name__ == '__main__':
    import pprint
    import sqlite3
    connection = sqlite3.connect('./db_file')
    cursor = connection.cursor()
    url = START_URL
    count = 0
    while url is not None:
        soup = bs4.BeautifulSoup(urllib2.urlopen(url).read())
        for link in get_beer_urls(soup):
            for review in get_beer_page(link):
                print('On review number: %d' % count)
                count += 1
                try:
                    cursor.execute('INSERT INTO reviews VALUES (?, ?, ?)',
                                   (review['author'],
                                    review['score'],
                                    review['review']))
                                   # review['particulars']['look'],
                                   # review['particulars']['smell'],
                                   # review['particulars']['taste'],
                                   # review['particulars']['feel'],
                                   # review['particulars']['overall'])
                    connection.commit()
                except Exception as e:
                    print('bad! %s' % e)
                    pprint.pprint(review)
        url = get_next_page(soup)
    connection.close()
