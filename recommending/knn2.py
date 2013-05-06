import sqlite3
import pprint
import sys

from knn_utils import *

def important_attributes(vector):
    """
        Given a vector representing a beer's attributes, returns a list
        of the most relevant ones.
        """
    atts = []
    for i in xrange(len(vector)):
        if len(atts) < 3:
            atts.append((attributes[i], vector[i]))
            atts.sort(key=lambda x: x[1], reverse = True)
        else:
            if vector[i] > atts[2][1]:
                if attributes[i] in ('score', 'a_b_v'):
                    continue
                atts[2] = (attributes[i], vector[i])
                atts.sort(key=lambda x: x[1], reverse = True)
    return atts

def expand_class(beerslist, input):
    """
        Given a beer name, find other beers liked by similar users
        """
    beers = {}
    fans = []
    connection = sqlite3.connect('../processing/full-db.sql')
    cursor = connection.cursor()
    cursor.execute('select * from reviews where beername=?', ((input+' '),))

    item = cursor.fetchone()

    #build the list of fans of the beer
    while item is not None:
        if  item[3] > 4:
            fans.append(item[2])
        item = cursor.fetchone()

    #now build the beers they like
    index = 0
    for fan in fans:
        cursor.execute('select * from reviews where author = ?', (fan,))
        item = cursor.fetchone()
        while item is not None:
            author = item[2]
            if item[3] > 4:
                cur = item[0].strip()
                if item[0] not in beers:
                    beers[cur] = {'beername': cur, 'brewery': beerslist[cur]['brewery'], 'score': beerslist[cur]['score'], 'fans': [author]}
                else:
                    old = beers[cur]['fans']
                    old.append(author)
                    beers[cur]['fans'] = old
            if (index%1000) == 0:
                print index
            index = index + 1
            item = cursor.fetchone()
    connection.close()
    return beers

def order_by_rank(likedlist):
    #sort the list of liked beers by score
    return [likedlist[beer] for beer in sorted(likedlist, key=lambda x: -likedlist[str(x)]['score'])]

def main():
    # Grab the beer names and attribute vectors from the database.
    connection = sqlite3.connect('../processing/breweries-db.sql')
    cursor = connection.cursor()
    cursor.execute('select * from beers')
    
    beers = {}
    
    item = cursor.fetchone()
    while item is not None:
        beername = unicode(item[0].strip())
        brewery = unicode(item[1].strip())
        beers[beername] = {'brewery': brewery,
            'attributes': item[2:], 'score':item[-1], 'beername': beername}
        item = cursor.fetchone()
    
    connection.close()
    
    # Ask the user for an input beer.
    input_beer = raw_input(u'Please enter the name of a beer that you like: ')
    
    # If the input beer isn't in our database, give the user some similar beer names.
    if input_beer not in beers:
        print("That's not a beer I know. Lemme check for similar ones...")
        possibilities = similar_beernames(input_beer, beers)
        while not possibilities:
            input_beer = raw_input(u'We could not recognize this beer. Please enter another: ')
            possibilities = similar_beernames(input_beer, beers)
        for i, possibility in enumerate(possibilities):
            print(u'%d. Did you mean %s? (y/n) ' % (i, possibility)),
            feedback = raw_input('')
            if u'y' in feedback:
                input_beer = possibility
                break
        if input_beer not in beers:
            print(u'We could not find the beer you were looking for. Please try again.')
            quit()
    
    # Ask the user for k.
    k = int(raw_input(u'How many similar beers would you like to see?: '))

    search_attributes = important_attributes(beers[input_beer]['attributes'])
    print('\nSearching for beers with attributes like:'),
    print(', '.join(map(lambda x: x[0], search_attributes)))

    #build class of liked beers
    liked_class = order_by_rank(expand_class(beers, input_beer))
    
    print '\nYou might like:'
    rank = 1
    for beer in liked_class:
        if rank <= k:
            print('%s. %s -- %s (liked by: %s)' % (rank, beer['beername'], beer['brewery'], ', '.join(map(lambda x: x, beer['fans']))))
        rank += 1

if __name__ == '__main__':
    main()
