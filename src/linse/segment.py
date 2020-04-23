"""
Segmenting is the process of converting a written word to a sequence of tokens.

This module provides functions to segment various kinds of text.

An alternative method to segment text - based on orthography profiles - is implemented
in the `segments` package.
"""
import re

__all__ = ['ipa', 'asjp']

from linse.models import *


def valid_word(string):
    if not isinstance(string, str):
        raise ValueError('Invalid type for word: {0}'.format(string))
    if len(string.split()) > 1:
        raise ValueError('Invalid multi-word string: {0}'.format(string))
    return string


def ipa(istring,
        diacritics=DIACRITICS,
        vowels=VOWELS,
        tones=TONES,
        combiners="\u0361\u035c",
        breaks="-.",
        nasals='ãũẽĩõ',
        nasal_char = "\u0303",
        nogos = "_◦+",
        merge_vowels=True,
        merge_geminates=False,
        expand_nasals=False,
        semi_diacritics='',
        stress="ˈˌ'",
        nasal_placeholder="∼"):
    """
    Segment IPA-encoded text.

    text : str
        The input sequence that shall be tokenized.

    diacritics : {iterable}
        A string containing all diacritics which shall be considered in the
        respective analysis.

    vowels : {iterable}
        A string containing all vowel symbols which shall be considered in the
        respective analysis.

    tones : {iterable}
        A string indicating all tone letter symbals which shall be considered
        in the respective analysis.

    combiners : str
        A string with characters that are used to combine two separate
        characters (compare affricates such as t͡s).

    breaks : str
        A string containing the characters that indicate that a new token
        starts right after them. These can be used to indicate that two
        consecutive vowels should not be treated as diphtongs or for diacritics
        that are put before the following letter.

    merge_vowels : bool (default=False)
        Indicate, whether vowels should be merged into diphtongs
        (default=True), or whether each vowel symbol should be considered
        separately.

    merge_geminates : bool (default=False)
        Indicate, whether identical symbols should be merged into one token, or
        rather be kept separate.

    expand_nasals : bool (default=False)

    semi_diacritics: str (default='')
        Indicate which symbols shall be treated as "semi-diacritics", that is,
        as symbols which can occur on their own, but which eventually, when
        preceded by a consonant, will form clusters with it. If you want to
        disable this features, just set the keyword to an empty string.

    clean_string : bool (default=False)
        Conduct a rough string-cleaning strategy by which all items between
        brackets are removed along with the brackets, and

    Returns
    -------
    tokens : list
        A list of IPA tokens.
    """
    out = []

    # set initial state of the parser:
    vowel = False  # no vowel
    tone = False  # no tone
    merge = False  # no merge command
    start = True  # start of unit
    nasal = False

    for char in valid_word(istring):
        if nasal:
            if char not in vowels and char not in diacritics:
                out.append(nasal_placeholder)
                nasal = False

        # check for breaks first, since they force us to start anew
        if char in breaks:
            start = True
            vowel = False
            tone = False
            merge = False

        elif char in combiners:
            # add the combiner to the previous entry in `out`; if there is no previous characters
            # (i.e., sequence starts with a combiner, which is something we perhaps should not
            # accept, see discussion at https://github.com/lingpy/lingpy/issues/365, append the
            # combiner to a null phoneme glyph.
            if not out:
                # empty list, i.e., no previous entry
                out = ['\u2205' + char]
                merge = False
            else:
                out[-1] += char
                merge = True

        elif char in stress:
            out.append(char)
            # FIXME: be careful about canceling the start-flag here, but seems to make sense so far!
            merge = True
            tone = False
            vowel = False
            start = False

        elif merge:
            out[-1] += char
            if char in vowels:
                vowel = True
            merge = False

        # check for nasals in NFC normalization and non-normalizable nasals
        elif expand_nasals and char == nasal_char and vowel:
            out[-1] += char
            start = False
            nasal = True

        # check for weak diacritics
        elif char in semi_diacritics and not start and not vowel \
                and not tone and out[-1] not in nogos:
            out[-1] += char

        elif char in diacritics:
            if not start:
                out[-1] += char
            else:
                out.append(char)
                start = False
                merge = True

        elif char in vowels:
            if vowel and merge_vowels:
                out[-1] += char
            else:
                out.append(char)
                vowel = True
            start = False
            tone = False

            if expand_nasals and char in nasals:
                nasal = True

        elif char in tones:
            vowel = False
            if tone:
                out[-1] += char
            else:
                out.append(char)
                tone = True
            start = False

        else:  # consonants
            vowel = False
            out.append(char)
            start = False
            tone = False

    if nasal:
        out.append(nasal_placeholder)

    if merge_geminates:
        new_out = [out[0]]
        for i in range(len(out) - 1):
            outA = out[i]
            outB = out[i + 1]
            if outA == outB:
                new_out[-1] += outB
            else:
                new_out += [outB]
        return new_out

    return out


def asjp(word, merge_vowels=True):
    if not word:
        return []
    tokens = ' '.join(
        ipa(
            word,
            diacritics=frozenset('*$~"'),
            vowels='aeiouE3',
            tones='',
            combiners='',
            merge_vowels=merge_vowels
        )
    )
    tokens = re.sub(r'([^ ]) ([^ ])~', r'\1\2~', tokens)
    tokens = re.sub(r'([^ ]) ([^ ]) ([^ ])\$', r'\1\2\3$', tokens)
    return tokens.split(' ')


def sampa(text):
    raise NotImplementedError