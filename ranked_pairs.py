#!/usr/bin/python
import json, sys, itertools
from collections import defaultdict as ddict
import networkx
import random

class Majority:
    def __init__(self, winner, loser, margin):
        self.winner = winner
        self.loser = loser
        self.margin = margin
        assert(margin > 0)

    def __str__(self):
        return '%s beats %s by %d votes' % (self.winner, self.loser, self.margin)

def get_tie_breaking_ballot(ballots):
    """
    ballots - a sequence of ballots
    returns a randomly-selected ballot for tie-breaking. The ballot may contain ties.
    """
    return random.choice(ballots)

def get_tie_breaking_ranking_of_candidates(tie_breaking_ballot):
    """
    tie_breaking_ballot - a ballot that may contain ties
    returns a ballot whose ties have been resolved randomly. This corresponds to Tideman's TBRC.
    """
    tbrc = []
    for group in ballot:
        if len(group) == 1:
            #There are no ties for this position. Add the only candidate.
            candidate = group[0]
            tbrc.append(candidate)
        else:
            #There are ties for this position. Resolve them randomly.
            tied_candidates_in_random_order = random.sample(group, len(group))
            for candidate in tied_candidates_in_random_order:
                tbrc.append(candidate)
            
       
       
    return tbrc

def get_tie_breaking_ranking_of_pairs(pair_a, pair_b, tie_breaking_ranking_of_candidates):
    """
    pair_a - a Majority
    pair_b - a Majority
    tie_breaking_ranking_of_candidates - a flat list of candidates. This list cannot contain any ties
    returns a Majority, the Majority who wins the tie according to the tie breaking ranking of candidates
    """
    #recall that a higher ranking is a lower index, so we use the 'min' function
    highest_rank_in_pair_A = min(tie_breaking_ranking_of_candidates.index(pair_a.winner), tie_breaking_ranking_of_candidates.index(pair_a.loser))
    highest_rank_in_pair_B = min(tie_breaking_ranking_of_candidates.index(pair_b.winner), tie_breaking_ranking_of_candidates.index(pair_b.loser))
    if higest_rank_in_pair_A < highest_rank_in_pair_B:
        return pair_a
    elif highest_rank_in_pair_A > highest_rank_in_pair_B:
        return pair_b
    else:
        #The highest-rankied elements of each pair are the same
        #Choose the pair whose second-highest ranked element is greater
        second_highest_rank_in_pair_A = max(tie_breaking_ranking_of_candidates.index(pair_a.winner), tie_breaking_ranking_of_candidates.index(pair_a.winner))
        second_highest_rank_in_pair_B = max(tie_breaking_ranking_of_candidates.index(pair_b.winner), tie_breaking_ranking_of_candidates.index(pair_b.winner))
        if second_highest_rank_in_pair_A < second_highest_rank_in_pair_B:
            return pair_a
        elif second_highest_rank_in_pair_A > second_highest_rank_in_pair_B:
            return pair_b
        else:
            #if this is true then we are breaking a tie between two identical pairs
            raise ValueError('This should never happen')

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
