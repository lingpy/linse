"""
Transformations convert a sequence of tokens to new data structure.
"""
from linse.models import STRESS, DIACRITICS

from linse.typedsequence import ints
from linse.annotate import soundclass

__all__ = ['syllables', 'morphemes']


def _iter_syllables(sequence, profile, gap_symbol):
    syllable, vowelcount = [], 0

    # Augment the sonority profile to make sure there's always left and right context:
    tuples = [('#', 0)] + list(zip(sequence, profile)) + [('$', 0)]
    for i, (char, p2) in enumerate(tuples[1:-1], start=1):
        p1, j, p3, k = -1, i, -1, i
        while p1 == -1:  # get left context in the sonority profile, skipping gaps
            j -= 1
            p1 = tuples[j][1]

        while p3 == -1:  # get right context in the sonority profile, skipping gaps
            k += 1
            p3 = tuples[k][1]

        if char == gap_symbol:
            syllable.append(char)
            continue

        # simple rule: we start a new syllable at a local minimum of prosody.
        if p1 >= p2 < p3:
            if p3 == 8 or p3 == 9:  # unless there's a tone following
                pass
            # don't break if we are in the initial and no vowel followed
            # can be expanded to general "vowel needs to follow"-rule
            elif p1 != 7 and p2 != 7 and i == 2:
                pass
            else:
                if syllable:
                    yield syllable
                syllable = []
        # break always if there's a tone
        if p1 == 8:
            if syllable:
                yield syllable
            syllable = []

        syllable.append(char)

    if syllable:
        yield syllable


def syllables(sequence,
              model='art',
              gap_symbol="-",
              stress=STRESS,
              diacritics=DIACRITICS,
              cldf=False):
    """
    Carry out a simple syllabification of a sequence, using sonority as a proxy.

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
    profile = ints(soundclass(seq, model=model, cldf=cldf, stress=stress, diacritics=diacritics))

    # re-insert gaps into sonority profile:
    for i in gaps:
        profile.insert(i, -1)

    return list(_iter_syllables(sequence, profile, gap_symbol))


def morphemes(sequence,
              split_on_tones=True,
              tone='T',
              morpheme_separator='+',
              morpheme_separators="◦+→←",
              word_separator='_',
              word_separators='_#',
              cldf=False):
    """
    Split a string into morphemes if it contains separators.

    Notes
    -----
    Function splits a list of tokens into subsequent lists of morphemes if the list
    contains morpheme separators. If no separators are found, but tonemarkers,
    it will still split the string according to the tones. If you want to avoid
    this behavior, set the keyword **split_on_tones** to False.

    Returns
    -------
    morphemes : list
        A nested list of the original segments split into morphemes.
    """
    if not split_on_tones:
        tone = ''

    def split_morphemes_on_tone(seq, cv, tone):
        morpheme = []
        for i, token in enumerate(seq):
            morpheme.append(token)
            if cv[i] == tone:
                if morpheme:
                    yield morpheme
                morpheme = []
        if morpheme:
            yield morpheme

    if (morpheme_separator not in sequence) and (word_separator not in sequence):
        # check for other hints than the clean separators in the data
        cv_seq = soundclass(sequence, 'cv', cldf=cldf)
        if tone in cv_seq and '+' not in cv_seq and '_' not in cv_seq:
            return list(split_morphemes_on_tone(sequence, cv_seq, tone))

    def split_on_sep(seq):
        morpheme = []
        for token in seq:
            if token not in \
                    morpheme_separator + morpheme_separators + word_separator + word_separators:
                morpheme.append(token)
            else:
                if morpheme:
                    yield morpheme
                morpheme = []
        if morpheme:
            yield morpheme

    return list(split_on_sep(sequence))
