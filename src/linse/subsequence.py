"""
Sequence operations that yield various forms of substrings and subsequences.
"""
import typing
import functools
import itertools


def _affixes(slicer, sequence):
    """
    Return all possible affixes in sequence.
    """
    out = [sequence]
    for i in range(1, len(sequence)):
        out += slicer(sequence, i)
    return out


affixes = functools.partial(_affixes, lambda x, i: [x[:-i], x[i:]])
prefixes = functools.partial(_affixes, lambda x, i: [x[:-i]])
suffixes = functools.partial(_affixes, lambda x, i: [x[i:]])


def substrings(sequence: typing.Sequence) -> typing.List[typing.Sequence]:
    """
    Returns all contiguous subsequences (of length > 0) of a given sequence.

    Parameters
    ----------
    sequence : list or str
        The sequence that shall be converted into it's list of subsequences.

    Returns
    -------
    out : list
        A list of all ngrams of the input word, sorted in decreasing order of
        length.

    Examples
    --------
    >>> substrings('hallo')
    ['hallo', 'hall', 'allo', 'hal', 'all', 'llo', 'ha', 'al', 'll', 'lo', 'h', 'a', 'l', 'l', 'o']
    """
    return [
        sequence[x:y] for x, y in sorted(
            itertools.combinations(range(len(sequence) + 1), 2),
            key=lambda x: (x[0] - x[1], x[0]))]
