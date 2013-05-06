import sqlite3
import pprint
import sys

from knn_utils import *

def manhattan_distance(x1,x2):
    '''
    Returns a tuple of the Manhattan distance between a pair of attribute vectors
    and a tuple of the three attributes on which the two vectors are the most similar.
    '''
    relevant_attributes = []
    if len(x1) != len(x2):
    	return -1
    distance = 0
    for i in xrange(len(x1)):
	distance += abs(x1[i] - x2[i])
        if x1[i] != 0 or x2[i] != 0:
            if len(relevant_attributes) < 3:
                relevant_attributes.append((i, abs(x1[i] - x2[i])))
                relevant_attributes.sort(key=lambda x: x[1])
            else:
                if abs(x1[i] - x2[i]) < relevant_attributes[2][1]:
                    relevant_attributes[2] = (i, abs(x1[i] - x2[i]))
                    relevant_attributes.sort(key=lambda x: x[1])
    return (distance, tuple(relevant_attributes))

def nearest_neighbors(k, query, dataset):
    '''
    Returns a list of the k most similar beers to the input beer in terms
    of Manhattan distance.
    '''
    neighbors = []
    for example in dataset:
        vector = dataset[example]['attributes']
        dist, relevant_attributes = manhattan_distance(vector, query)
        if len(neighbors) < k:
            neighbors.append((example, dist, relevant_attributes))
            neighbors.sort(key=lambda x: x[1])
        else:
            if dist < neighbors[k-1][1] and dist != 0:
                neighbors[k-1] = (example, dist, relevant_attributes)
                neighbors.sort(key=lambda x: x[1])
    return neighbors

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
                           'attributes': item[2:]}
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
            print(u'%d. Did you mean %s? (y/n) ' % (i + 1, possibility)),
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
    
    nearest_beers = nearest_neighbors(k, beers[input_beer]['attributes'], beers)
    print '\nYou might like:'
    rank = 1
    for beer in nearest_beers:
        print('%s. %s -- %s (similar attributes: %s)' % (rank,
                                                        beer[0],
                                                        beers[beer[0]]['brewery'],
                                                        ', '.join(map(lambda x: attributes[x[0]], beer[2]))))
        rank += 1

if __name__ == '__main__':
    main()
