import sqlite3
import pprint

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
              'num_reviews']

beers = {}

connection = sqlite3.connect('full-db.sql')
cursor = connection.cursor()
cursor.execute('select * from reviews')

i = 0
item = cursor.fetchone()
while item is not None:
    if i % 10000 == 0:
        print('On review %s...' % i)
    i += 1
    beername, brewery, _, score, abv, review = item
    if beername not in beers:
        beers[beername] = {attribute: 0 for attribute in attributes}
        beers[beername]['score'] = 0
        beers[beername]['brewery'] = brewery
        beers[beername]['a_b_v'] = float(abv)/20.0
    beers[beername]['num_reviews'] += 1
    beers[beername]['score'] += score
    for attribute in attributes:
        if attribute in review:
            beers[beername][attribute] += 1
    item = cursor.fetchone()

normalized_beers = {}

for beername in beers:
    normalized_beers[beername] = {attribute: float(beers[beername][attribute])/beers[beername]['num_reviews']
                                  for attribute in attributes}
    del normalized_beers[beername]['num_reviews']
    normalized_beers[beername]['score'] = beers[beername]['score']/(5.0 * beers[beername]['num_reviews'])
    normalized_beers[beername]['a_b_v'] = beers[beername]['a_b_v']
    normalized_beers[beername]['brewery'] = beers[beername]['brewery']

attributes.pop()

connection = sqlite3.connect('breweries-db.sql')
cursor = connection.cursor()
cursor.execute('CREATE TABLE beers (beername text, brewery text, %s real)' % ' real, '.join(attributes + ['a_b_v', 'score']))
connection.commit()
for beer in normalized_beers:
    cursor.execute('INSERT INTO beers VALUES (%s)' % ', '.join(['?'] * (len(attributes) + 4)),
                   tuple([beer, normalized_beers[beer]['brewery']] +  [normalized_beers[beer][attribute]
                                                                      for attribute in attributes + ['a_b_v', 'score']]))
    connection.commit()

connection.close()
