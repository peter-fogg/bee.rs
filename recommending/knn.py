import sqlite3
import pprint

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
