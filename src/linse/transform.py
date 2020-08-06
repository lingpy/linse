"""
Transformations convert a sequence of tokens to new data structure.
"""
from linse.models import STRESS, DIACRITICS

from linse.typedsequence import ints
from linse.annotate import soundclass, prosody

from collections import defaultdict

__all__ = ['syllables', 'morphemes', 'flatten', 'syllable_inventories']


def _iter_syllables(
        sequence, prosodies, vowels=(7,), tones=(8,), max_vowels=2):
    """
    Find syllable breakpoints for a set of tokens, based on their prosody.

    :param vowels: all numbers that represent a vowel class
    :param tones: all tones reresenting a tone class
    :param max_vowels: start new syllable if maximum of vowels is reached

    :note: Vowels need to be presence in a syllable, which is why they are
    assigned a specific value (default 7, as in the "art" sound class model).
    If more complex prosodic models are used, one needs to indicate what is a
    vowel, and also what class is reserved for a tone.
    """
    tuples = [('#', 0)] + list(zip(sequence, prosodies)) + [('$', 0)]
    syllable, vowel_count = [], 0
    for i, (char, pro) in enumerate(tuples[1:-1], start=1):
        pchar, ppro = tuples[i - 1]
        fchar, fpro = tuples[i + 1]
        if pro in vowels:
            vowel_count += 1
        if fpro not in tones:
            if (ppro >= pro < fpro and vowel_count and 7 in prosodies[i:]) or\
                    ppro in tones:
                yield syllable
                syllable, vowel_count = [], 0
            elif vowel_count > max_vowels and pro in vowels:
                yield syllable
                syllable, vowel_count = [], 0
        syllable.append(char)
    if syllable:
        yield syllable


def syllables(sequence,
              model='art',
              gap_symbol="-",
              stress=STRESS,
              diacritics=DIACRITICS,
              cldf=True,
              vowels=(7,),
              tones=(8,),
              max_vowels=2):
    """
    Carry out a simple syllabification analysis using sonority as a proxy.

    Parameters
    ----------

    Notes
    -----

    When analyzing the sequence, we start a new syllable in all cases where we
    reach a deepest point in the sonority hierarchy of the sonority profile of
    the sequence. When passing an aligned string to this function, the gaps
    will be ignored when computing boundaries, but later on re-introduced, if
    the alignment is passed in segmented form.

    Returns
    -------
    syllables : sequence of lists
    """
    gaps = []
    seq = []
    for i, c in enumerate(sequence):
        if c == gap_symbol:
            gaps.append(i)
        else:
            seq.append(c)

    # get the sonority profile for the sequence
    profile = ints(soundclass(
        seq, model=model, cldf=cldf, stress=stress, diacritics=diacritics))
    syls = [list(syllable) for syllable in _iter_syllables(
        seq, profile, max_vowels=max_vowels, vowels=vowels, tones=tones)]

    # re-insert gaps into sonority profile:
    if gaps:
        count = 0
        for syllable in syls:
            for i in range(len(syllable)):
                if count in gaps:
                    syllable.insert(i, gap_symbol)
                    count += 1
                count += 1
    return syls


def morphemes(sequence,
              separators=("+", "_", '#'),
              split_on_tones=False,
              cldf=True):
    """
    Split a string into morphemes if it contains separators.

    Notes
    -----
    Function splits a list of tokens into subsequent lists of morphemes if the
    list contains morpheme separators. If no separators are found, but
    tonemarkers, it will still split the string according to the tones. If you
    want to avoid this behavior, set the keyword **split_on_tones** to False.

    Returns
    -------
    morphemes : list
        A nested list of the original segments split into morphemes.
    """
    if split_on_tones:
        return syllables(sequence, cldf=cldf)

    def split_on_sep(seq):
        morpheme = []
        for token in seq:
            if token not in \
                    separators:
                morpheme.append(token)
            else:
                if morpheme:
                    yield morpheme
                morpheme = []
        if morpheme:
            yield morpheme

    return list(split_on_sep(sequence))


def flatten(list_of_morphemes, separator='+'):
    """
    Return a linear representation of a nested sequence of morphemes.
    """
    true_morphemes = [m for m in list_of_morphemes if m]
    out = []
    for morpheme in true_morphemes[:-1]:
        if morpheme:
            out.extend(morpheme)
            out.append(separator)
    out.extend(true_morphemes[-1])
    return out


def syllable_inventories(
        forms,
        segments='Segments',
        doculect='Language_ID',
        ID='ID',
        format='CcV',
        **kw):
    """
    Retrieve inventory with syllable from a bunch of segments.
    """
    D = {}
    for form in forms:
        if form[doculect] not in D:
            D[form[doculect]] = defaultdict(lambda : defaultdict(list))
        for morpheme in morphemes(form[segments]):
            for syl in syllables(morpheme):
                cv = prosody(syl, format=format)
                template = ''.join(cv)
                for i, (s, c) in enumerate(zip(syl, cv)):
                    tpl = template[:i]+'**'+template[i]+'**'+template[i+1:]
                    D[form[doculect]][s][tpl] += [form[ID]]
    return D

