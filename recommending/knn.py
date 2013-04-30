import sqlite3
import pprint
import sys

def edit_distance(s1, s2):
    """
    Returns the Levenshtein distance between the two strings. For use
    where the user has entered a beer that isn't in the database.
    """
    # Initialize the DP table.
    table = [[0 for i in range(len(s2))] for j in range(len(s1))]
    for i in range(len(s1)):
        table[i][0] = i
    for i in range(len(s2)):
        table[0][i] = i
    # Bam! Dynamic brogramming.
    for i in range(1, len(s1)):
        for j in range(1, len(s2)):
            table[i][j] = min(table[i - 1][j], table[i][j - 1], table[i - 1][j - 1]) + (1 if s1[i] != s2[j] else 0)
    return table[len(s1) - 1][len(s2) - 1]

def longest_common_subsequence(s1, s2):
    '''
    Returns the longest common subsequence of the two beernames --
    might work better than Levenshtein distance?
    '''
    table = [[0 for i in range(len(s2))] for j in range(len(s1))]
    for i in range(len(s1)):
        table[i][0] = 0
    for i in range(len(s2)):
        table[0][i] = 0
    for i in range(1, len(s1)):
        for j in range(1, len(s2)):
            if s1[i] == s2[j]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])
    return table[len(s1) - 1][len(s2) - 1]

def similar_beernames(beer, beers):
    '''
    Returns a set of beers with a name similar to the input beer --
    for example, the database contains "90 Minute IPA", but not "90
    Minute". So if the user searches for a beer that's not there, we
    can print a list of better choices to search for.
    '''
    similars = set()
    for b in beers:
        if edit_distance(beer, b.strip()) < 3 or beer in b:
            similars.add(b)
        if longest_common_subsequence(beer, b.strip()) > .75*len(beer):
            similars.add(b)
    return similars

def manhattan_distance(x1,x2):
	'''
	Returns the Manhattan distance between a pair of attribute vectors.
	'''
	if len(x1) != len(x2):
		return -1
	distance = 0
	for i in xrange(len(x1)):
		distance += abs(x1[i] - x2[i])
	return distance


def nearest_neighbors(k, query, dataset):
    '''
    Returns a list of the k most similar beers to the input beer in terms
    of Manhattan distance.
    '''
    neighbors = []
    for example in dataset:
        vector = dataset[example]
        if len(neighbors) < k:
            neighbors.append((example, manhattan_distance(vector, query)))
        else:
            dist = manhattan_distance(vector, query)
            if dist < neighbors[k-1][1] and dist != 0:
                neighbors[k-1] = (example, dist)
                neighbors.sort(key=lambda x: x[1])
    return neighbors

def main():
    # Grab the beer names and attribute vectors from the database.
    connection = sqlite3.connect('../processing/beers-db.sql')
    cursor = connection.cursor()
    cursor.execute('select * from beers')
    
    beers = {}
    
    item = cursor.fetchone()
    while item is not None:
	beername = unicode(item[0].strip())
        beers[beername] = item[1:]
        item = cursor.fetchone()
        
    connection.close()

    # Ask the user for an input beer.
    input_beer = raw_input(u'Please enter the name of a beer that you like: ')

    # If the input beer isn't in our database, give the user some similar beer names.
    if input_beer not in beers:
        possibilities = similar_beernames(input_beer, beers)
        while not possibilities:
            input_beer = raw_input(u'We could not recognize this beer. Please enter another: ')
            possibilities = similar_beernames(input_beer, beers)
        for possibility in possibilities:
            feedback = raw_input(u'Did you mean ' + possibility.encode(sys.stdout.encoding) + u'? (y/n) ')
            if u'y' in feedback:
                input_beer = possibility
                break
        if input_beer not in beers:
            print(u'We could not find the beer you were looking for. Please try again.')
            quit()

    # Ask the user for k. 
    k = int(raw_input(u'How many similar beers would you like to see?: '))

    nearest_beers = nearest_neighbors(k, beers[input_beer], beers)	
    pprint.pprint(nearest_beers)

if __name__ == '__main__':
    main()
