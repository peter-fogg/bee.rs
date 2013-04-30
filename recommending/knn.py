import sqlite3
import pprint

def similar_beernames(beer, comparison_func=edit_distance):
    '''
    Returns beers with a name similar to the input beer -- for
    example, the database contains "90 Minute IPA", but not "90
    Minute". So if the user searches for a beer that's not there, we
    can print a list of better choices to search for.
    '''
    connection = sqlite3.connect('../processing/beers-db.sql')
    cursor = connection.cursor()
    similars = []
    cursor.execute('select * from beers')
    item = cursor.fetchone()
    while item is not None:
        if comparison_func(beer, item[0].strip()) > 10 or beer in item[0]:
            similars.append(item[0])
        item = cursor.fetchone()
    return similars

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

def manhattan_distance(x1,x2):
	if len(x1) != len(x2):
		return -1
	distance = 0
	for i in xrange(len(x1)):
		distance += abs(x1[i] - x2[i])
	return distance


def nearest_neighbors(k, query, dataset):
	neighbors = []
	for example in dataset:
		vector = dataset[example]
		if len(neighbors) < k:
			neighbors.append((example, manhattan_distance(vector, query)))
		else:
			dist = manhattan_distance(vector, query)
			if dist < manhattan_distance(neighbors[k-1], query):
				neighbors[k-1] = (example, dist)
				neighbors.sort()
	return neighbors

connection = sqlite3.connect('beers-db.sql')
cursor = connection.cursor()
cursor.execute('select * from beers')

beers = {}

item = cursor.fetchone()
while item is not None:
	beername = item[0]
	beers[beername] = item[1:]
	item = cursor.fetchone()

connection.close()

input_beer = raw_input('Please enter the name of a beer that you like: ')

k = int(raw_input('How many similar beers would you like to see?: '))

nearest_beers = nearest_neighbors(k, input_beer, beers)	

pprint.pprint(nearest_beers)
