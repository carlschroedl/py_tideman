from itertools import chain
from itertools import combinations
from collections import defaultdict
# This file uses terminology consistent with Stanford's Plato Encyclopedia
# entry on Arrow's Impossibility Theorem:
# https://plato.stanford.edu/entries/arrows-theorem/
# and with T.M. Zavist, T.N. Tideman 1988.

# ballot structure
# To express A > B > C = D :
# [["A"], ["B"], ["C", "D"]]


# an NBallot associates a ballot with a count of the number of voters who submitted an identical ballot

class Candidate:
    '''
    Also known as an Alternative
    '''
    
    def __init__(self, id, name=id):
        '''
        Parameters
        ----------
        id : String
            programattic identifier
        name : String
            Optional human-facing name. Defaults to `id` if not specified.
        '''
        
        self.id = id
        self.name = name 

class Ranking:
    '''
    Associates an ordered list of candidates with a count.
    The count corresponds to the number of voters who
    submitted the same ranking.
    '''
    
    def __init__(self, order, count=1):
        '''
        order - list of lists of strings.
            Each string identifies a candidate.
            Most of the inner lists are expected to have just one String item.
            Ties are represented by placing multiple Strings in the same inner list
            example: [['A'], ['B'], ['C'], ['D','E']]
            is the way to represent the order A > B > C > D = E
        '''
        self.order = order 
        self.count = count
        

def get_candidates(rankings):
    '''
    Given a sequence of rankings, return a set of unique candidates
    '''
    
    candidates = set()
    for ranking in rankings:
        for candidate in chain.from_iterable(ranking.order):
            candidates.add(candidate)
    return candidates

def get_index_map(ranking):
    '''
    Build a dictionary mapping candidates to their index within a ranking
    '''
    candidate_to_index = {}
    for rank, candidate_group in enumerate(ranking.order):
        for candidate in candidate_group:
            #This loop usually only executes once, except in the case of ties
            candidate_to_index[candidate] = rank
    
    return candidate_to_index
    
def build_margins(rankings):
    '''
    Given a sequence of Ranking objects, produce a dictionary describing the margins.
    The dictionary's keys are a tuple of the ordered pairs. The value associated with
    (x,y) would be the margin of voters who prefer x over y, whereas (y, x) would be
    the margin of voters who prefer y over x.

    build_margins(some_rankings)[(x,y) == -1 * build_margins(some_rankings)[(x,y)]
    '''
    margins = defaultdict(int)
    candidates = get_candidates(rankings)
    candidate_pairs = combinations(candidates, 2)
    for (x, y) in candidate_pairs:
        for ranking in rankings:
            index_of = get_index_map(ranking)
            if index_of[x] < index_of[y]:
                margins[(x, y)] += ranking.count
                margins[(y, x)] -= ranking.count
            elif index_of[x] > index_of[y]:
                margins[(x, y)] -= ranking.count
                margins[(y, x)] += ranking.count
            # else they are equal; Do nothing.
    return margins
