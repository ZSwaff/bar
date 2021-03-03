import random


def weighted_choice(vals, weights):
    rnd = random.random() * sum(weights)
    for e, w in zip(vals, weights):
        rnd -= w
        if rnd <= 0:
            return e


def calc_dist_between(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5


def do_segments_overlap(l1, l2):
    # todo implement
    return True


def find_min_dist_to_connect_without_overlapping(start, others):
    # todo implement
    return 0
