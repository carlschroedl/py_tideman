from tideman import Ranking
from tideman import build_margins

# Test data from T.M. Zavist, T.N. Tideman 1988. Social Choice and Welfare. Page 170.
test_data = [
        (1,[["d"],["e"],["b"],["b'"],["f"],["a"],["c"]]),
        (1,[["e"],["b"],["b'"],["f"],["c"],["a"],["d"]]),
        (1,[["b"],["b'"],["f"],["c"],["a"],["d"],["e"]]),
        (1,[["c"],["f"],["a"],["d"],["e"],["b"],["b'"]]),
        (1,[["d"],["c"],["a"],["e"],["b"],["b'"],["f"]]),
        (1,[["a"],["b'"],["b"],["c"],["d"],["e"],["f"]]),
        (1,[["a"],["c"],["b'"],["b"],["d"],["e"],["f"]]),
        (1,[["f"],["e"],["a"],["c"],["b'"],["b"],["d"]]),
        (1,[["f"],["e"],["b'"],["b"],["d"],["c"],["a"]]),
]

def datum_to_ranking(test_datum):
    return Ranking(test_datum[1], test_datum[0])


rankings = map(datum_to_ranking, test_data)

print(build_margins(rankings))
    
