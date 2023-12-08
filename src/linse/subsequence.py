"""
Sequence operations that yield various forms of substrings and subsequences.
"""
from functools import partial


def _affixes(slicer, sequence):
    """
    Return all possible affixes in sequence.
    """
    out = [sequence]
    for i in range(1, len(sequence)):
        out += slicer(sequence, i)
    return out


affixes = partial(_affixes, lambda x, i: [x[:-i], x[i:]])
prefixes = partial(_affixes, lambda x, i: [x[:-i]])
suffixes = partial(_affixes, lambda x, i: [x[i:]])


def substrings(sequence, sort=False):
    """
    Function returns all possible n-grams of a given sequence.

    Parameters
    ----------
    sequence : list or str
        The sequence that shall be converted into it's ngram-representation.

    Returns
    -------
    out : list
        A list of all ngrams of the input word, sorted in decreasing order of
        length.

    Examples
    --------
    >>> get_all_ngrams('abcde')
    ['abcde', 'bcde', 'abcd', 'cde', 'abc', 'bcd', 'ab', 'de', 'cd', 'bc', 'a', 'e', 'b', 'd', 'c']

    """

    # get the length of the word
    l = len(sequence)

    # make dummy sequence with numbers as indices
    numeric = tuple(range(len(sequence)))

    # determine the starting point
    i = 0
    out = []

    # loop in branching style over all subsequences
    while i != l and i < l:
        # copy the sequence
        new_sequence = numeric[i:l]

        # append the sequence to the output list
        out += [new_sequence]

        # loop over the new sequence
        for j in range(1, len(new_sequence)):
            out += [new_sequence[:j]]
            out += [new_sequence[j:]]

        # increment i and decrement l
        i += 1
        l -= 1
    
    # sort by size: this sorting guarantees a "logical" order starting from
    # longest prefix, to longest suffix, etc.
    out = sorted(out, key=lambda x: (len(x), -x[0]), reverse=True)

    sort = sort or list

    return sort([sequence[subs[0] : subs[-1] + 1] for subs in out])
