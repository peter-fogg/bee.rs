import sqlite3

# connection = sqlite3.connect('../processing/beers-db.sql')
# cursor = connection.cursor()

beers = []

input_beer = "foo"

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

def manhattan_distance(x1, x2):
    pass

def nearest_neighbors(k, examples):
    pass
