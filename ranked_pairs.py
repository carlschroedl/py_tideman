#!/usr/bin/python
import json, sys, itertools
from collections import defaultdict as ddict
import networkx

class Majority:
    def __init__(self, winner, loser, margin):
        self.winner = winner
        self.loser = loser
        self.margin = margin
        assert(margin > 0)

    def __str__(self):
        return '%s beats %s by %d votes' % (self.winner, self.loser, self.margin)

def load(path):
    with open(path) as f:
        return json.load(f)

def get_candidates(ballots):
    candidates = set()
    for ballot in ballots:
        for group in ballot:
            for candidate in group:
                candidates.add(candidate)
    return candidates
                        
# return majorities
def count_ballots(ballots, skip):
    # count difference between every pair
    sums = ddict(int)
    for ballot in ballots:
        for i in range(len(ballot)):
            for j in range(i, len(ballot)):
                better = ballot[i]
                worse = ballot[j]

                for b in better:
                    for w in worse:
                        if b in skip or w in skip:
                            continue
                        sums[(b,w)] += 1
                        sums[(w,b)] -= 1

    # produce majority pairs
    majorities = []
    for (a,b), votes in sums.iteritems():
        if votes > 0:
            majorities.append(Majority(winner=a, loser=b, margin=votes))

    return majorities
                        
def get_partial_ranking(majorities):
    majorities.sort(key=lambda m: m.margin, reverse=True) # ties?
    majority_groups = []
    for m in majorities:
        if len(majority_groups) > 0 and majority_groups[-1][-1].margin == m.margin:
            # this majority tied with the last added majority, so add
            # the new one to the same group
            majority_groups[-1].append(m)
        else:
            # no ties with previous, so add to a new group
            majority_groups.append([m])
    return majority_groups
            
def get_complete_rankings(partial_ranking):
    rankings = [[]]
    # this has opportunity for combinatoric blowup!
    for group in partial_ranking:
        new_rankings = []
        for ranking in rankings:
            # consider each permutation that resolves ties within this group
            for permutation in itertools.permutations(group):
                new_rankings.append(ranking + list(permutation))
        rankings = new_rankings
    return rankings

def find_winners(candidates, complete_ranking):
    # edges point from winners to losers
    G = networkx.DiGraph()

    for c in candidates:
        G.add_node(c)

    # add edges as possible, without creating cycles, from strongest to weakest
    for majority in complete_ranking:
        descendants = networkx.algorithms.dag.descendants(G, majority.loser)
        if majority.winner not in descendants:
            # good, no cycle if we include this ranked pair
            G.add_edge(majority.winner, majority.loser)

    # if nobody points an edge at you (i.e., nobody beat you), you're a winner!
    winners = set()
    for c in candidates:
        beat_by = G.in_edges(c)
        if len(beat_by) == 0:
            winners.add(c)
    return winners

# run ranked pair once to get a since winner (or group who tie as winner)
def ranked_pair_single_output(ballots, skip=set()):
    candidates = get_candidates(ballots) - skip
    
    # consider each head-to-head pairing against ballots and get >=1
    # margin majorities.
    majorities = count_ballots(ballots, skip)
    
    # sort by largest margin (there may be ties!)
    partial_ranking = get_partial_ranking(majorities)

    # resolve ties in every possible way
    complete_rankings = get_complete_rankings(partial_ranking)

    # consider winners for every way we resolved ties
    winners = set()
    for complete_ranking in complete_rankings:
        permutation_winners = find_winners(candidates, complete_ranking)
        winners |= permutation_winners
    winners = sorted(winners)
    return winners

# run ranked pair iteratively to break candidates into a set of ranked groups
def ranked_pair_multi_output(ballots):
    candidates = get_candidates(ballots)
    skip = set()
    results = []
    while len(skip) < len(candidates):
        winners = ranked_pair_single_output(ballots, skip)
        results.append(winners)
        skip |= set(winners)

    rank = 1
    for group in results:
        print 'Rank %d: %s' % (rank, ', '.join(group))
        rank += len(group)

def main():
    path = sys.argv[1]
    ballots = load(path)
    ranked_pair_multi_output(ballots)
        
if __name__ == '__main__':
    main()
