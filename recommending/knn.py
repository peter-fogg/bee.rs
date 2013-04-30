import sqlite3
import pprint
import sys

attributes = ['spices',
              'bite',
              'cocao',
              'lighter',
              'soft',
              'pineapple',
              'molasses',
              'burnt',
              'grain',
              'cloudy',
              'roast',
              'wine',
              'banana',
              'apple',
              'cherry',
              'foamy',
              'bright',
              'booze',
              'piney',
              'herbal',
              'toasted',
              'rye',
              'grassy',
              'copper',
              'tropical',
              'subtle',
              'honey',
              'toffee',
              'bread',
              'red',
              'sticky',
              'tart',
              'refreshing',
              'complex',
              'spice',
              'belgian',
              'spicy',
              'fruits',
              'bready',
              'sugar',
              'wheat',
              'clean',
              'deep',
              'tan',
              'rich',
              'sour',
              'oak',
              'leaves',
              'fresh',
              'hoppy',
              'malty',
              'lemon',
              'hazy',
              'fruity',
              'crisp',
              'bourbon',
              'full',
              'mild',
              'pale',
              'golden',
              'floral',
              'balanced',
              'amber',
              'vanilla',
              'yeast',
              'grapefruit',
              'thick',
              'creamy',
              'roasted',
              'pine',
              'black',
              'fruit',
              'orange',
              'smooth',
              'brown',
              'bitter',
              'coffee',
              'caramel',
              'chocolate',
              'citrus',
              'hop',
              'dark',
              'sweet',
              'malt',
              'light',
              'score']

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

def distance_heuristic(edit, lcs):
    '''
    A heuristic to determine how close beernames are based on LCS
    and Levenshtein distance.
    '''
    return lcs + (3.0/edit)

def similar_beernames(beer, beers):
    '''
    Returns a set of beers with a name similar to the input beer --
    for example, the database contains "90 Minute IPA", but not "90
    Minute". So if the user searches for a beer that's not there, we
    can print a list of better choices to search for.
    '''
    beer = beer.strip().lower()
    similars = set()
    for b in beers:
        lcs = longest_common_subsequence(beer, b.strip().lower())
        dist = edit_distance(beer, b.strip().lower())
        if dist < 3 or lcs > .75*len(beer):
            similars.add((b, distance_heuristic(dist, lcs)))
        if beer in b.strip().lower():
            similars.add((b, 0))
    return map(lambda x: x[0], sorted(list(similars), key=lambda x: x[1]))

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
            neighbors.sort(key=lambda x: x[1])
        else:
            dist = manhattan_distance(vector, query)
            if dist < neighbors[k-1][1] and dist != 0:
                neighbors[k-1] = (example, dist)
                neighbors.sort(key=lambda x: x[1])
    return neighbors

def important_attributes(vector):
    atts = []
    for i in xrange(len(vector)):
        if len(atts) < 3:
            atts.append((attributes[i], vector[i]))
            atts.sort(key=lambda x: x[1], reverse = True)
        else:
            if vector[i] > atts[2][1]:
                if attributes[i] == 'score':
                    continue
                atts[2] = (attributes[i], vector[i])
                atts.sort(key=lambda x: x[1], reverse = True)
    return atts

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

    search_attributes = important_attributes(beers[input_beer])
    print('\nSearching for beers with attributes like:'),
    print(', '.join(map(lambda x: x[0], search_attributes)))
    
    nearest_beers = nearest_neighbors(k, beers[input_beer], beers)
    print '\nYou might like:'
    rank = 1
    for beer in nearest_beers:
        print(str(rank) + '. ' + beer[0])
        rank += 1

if __name__ == '__main__':
    main()
