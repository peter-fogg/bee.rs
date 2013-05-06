"""Code shared between knn and knn2."""

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
              'a_b_v',
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
    return lcs + ((3.0/edit) if edit else 0)

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
