"""
Annotating a sequence means creating a list of annotations for a sequence.
"""
import typing
import warnings
import functools

from linse.models import *  # noqa: F401, F403
from linse.typedsequence import ints, floats
from linse.util import get_NORMALIZE
from linse.subsequence import subsequences

__all__ = [
    'soundclass', 'REPLACEMENT', 'prosody', 'prosodic_weight',
    'codepoints', 'normalize', 'clts', 'bipa', 'NORM', 'seallable']

REPLACEMENT = '\ufffd'
NORM = get_NORMALIZE()


def _token2soundclass(token, model, slash=True, strict=False):
    """
    Convert a single token into a sound-class item.
    """
    token = _norm(token)

    if slash:
        a, sep, b = token.partition('/')
        if sep:
            token = b or '?'

    if not isinstance(model, (Model, dict)):
        model = MODELS[model]

    if strict:
        return model[token] if token in model else REPLACEMENT

    for s in subsequences(token):
        if s in model:
            return model[s]
    return REPLACEMENT


def soundclass(tokens: typing.Union[typing.Tuple[str, ...], typing.List[str]],
               model='dolgo',
               slash=True,
               strict=False) -> list:
    """
    Convert tokenized IPA strings into their respective class strings.
    """
    # raise value error if input is not an iterable (tuple or list)
    if not isinstance(tokens, (tuple, list)):
        raise ValueError("Need tuple or list as input.")

    out = []
    for token in tokens:
        out.append(_token2soundclass(token, model, slash=slash, strict=strict))
    if out.count(REPLACEMENT) == len(out):
        warnings.warn("[i] your sequence {0} contains only unknown characters".format(tokens))
    return out


clts = functools.partial(soundclass, model="clts")
bipa = functools.partial(soundclass, model="bipa")


PROSODY_FORMATS = {
    'cv': {
        "A": "C",
        "B": "C",
        "C": "C",
        "M": "C",
        "L": "C",
        "N": "C",
        "X": "V",
        "Y": "V",
        "Z": "V",
        "T": "T",
        "_": "_",
    },
    'CcV': {
        "A": "C",
        "B": "C",
        "C": "C",
        "M": "c",
        "L": "c",
        "N": "c",
        "X": "V",
        "Y": "V",
        "Z": "v",
        "T": "T",
        "_": "_",
    },
    None: {
        "A": "#",
        "B": "C",
        "C": "C",
        "M": "c",
        "L": "c",
        "N": "$",
        "X": "V",
        "Y": "v",
        "Z": ">"
    }
}


def _process_prosody(sonority):
    """
    Low-level processing of prosodic strings.
    """
    assert 9 not in sonority[1:-1]
    assert sonority[0] == sonority[-1] == 9

    # create the output values
    psequence = []
    first = True  # stores whether first syllable is currently being processed

    for i in range(1, len(sonority) - 1):
        # get a segment with context
        a, b, c = sonority[i - 1], sonority[i], sonority[i + 1]

        if b == 7:  # a vowel
            if first:
                psequence.append('X')
                first = False
            elif c == 9:  # last
                psequence.append('Z')
            else:
                psequence.append('Y')
        elif b == 8:  # a tone
            psequence.append('T')
        elif c == 8:  # sound before tone, not a vowel
            psequence.append("L")
        elif a >= b >= c:  # descending
            if first:
                first = False
                psequence.append('A')
            else:
                psequence.append('L')
        elif b < c or a > b <= c or a < b <= c:  # ascending
            # check for syllable first
            if a == 9:
                psequence.append('A')
            elif a >= b:
                if c == 9:
                    psequence.append('N')
                else:
                    if psequence[-1] != 'A':
                        psequence = psequence[:-1] + [psequence[-1].replace('L', 'M')] + ['B']
                    else:
                        psequence.append('C')
            else:
                psequence.append('C')
        elif a < b > c:  # consonant peak
            if first:
                psequence.append('X')
                first = False
            else:
                psequence.append('Y')
    return psequence


def prosody(sequence: typing.List[str], format=True, slash=True, strict=False) -> list:
    """
    Create a prosodic string of the sonority profile of a sequence.

    Parameters
    ----------

    sequence : list
        A list of characters indicating the sonority of the tokens of the
        underlying sequence.

    Returns
    -------
    prostring : string
        A prosodic string corresponding to the sonority profile of the
        underlying sequence.

    See also
    --------

    prosodic weight

    Notes
    -----

    A prosodic string is a sequence of specific characters indicating their resprective prosodic
    context (see :evobib:`List2012` or :evobib:`List2012a` for a detailed description).
    The scheme distinguishes 9 prosodic positions:

    * ``A``: sequence-initial consonant
    * ``B``: syllable-initial, non-sequence initial consonant in a context of
      ascending sonority
    * ``C``: non-syllable, non-initial consonant in ascending sonority context
    * ``L``: non-syllable-final consonant in descending environment
    * ``M``: syllable-final consonant in descending environment
    * ``N``: word-final consonant
    * ``X``: first vowel in a word
    * ``Y``: non-final vowel in a word
    * ``Z``: vowel occuring in the last position of a word
    * ``T``: tone
    * ``_``: word break

    Examples
    --------
    >>> import linse.typedsequence
    >>> prosody(linse.typedsequence.Morpheme('ts ɔy ɡ ə'))
    'AXBZ'

    """
    if not sequence:
        return []

    # get the sonority profile
    sonority = [9] + ints(soundclass(sequence, model='art', slash=slash, strict=strict)) + [9]
    psequence = _process_prosody(sonority)

    assert len(psequence) == len(sequence)
    conv = PROSODY_FORMATS.get(format, {})
    return [conv.get(x, x) for x in psequence]


def prosodic_weight(sequence: typing.List[str],
                    _transform: typing.Optional[typing.Dict[str, float]] = None,
                    slash=True,
                    strict=False) -> typing.List[float]:
    """
    Calculate prosodic weights for each position of a sequence.

    Parameters
    ----------

    sequence : list
        A prosodic string as it is returned by :py:func:`prosodic_string`.
    _transform : dict
        A dictionary that determines how prosodic strings should be transformed
        into prosodic weights. Use this dictionary to adjust the prosodic
        strings to your own user-defined prosodic weight schema.

    Returns
    -------
    weights : list
        A list of floats reflecting the modification of the weight for each position.

    Notes
    -----

    Prosodic weights are specific scaling factors which decrease or increase
    the gap score of a given segment in alignment analyses (see :evobib:`List2012` or
    :evobib:`List2012a` for a detailed description).

    Examples
    --------
    >>> from linse.annotate import prosodic_weight
    >>> prostring = '#vC>'
    >>> prosodic_weight(list(prostring))
    [2.0, 1.3, 1.5, 0.7]

    See also
    --------
    prosodic_string

    """
    psequence = prosody(sequence, slash=slash, strict=strict)

    # check for transformer
    if _transform:
        transform = _transform
    elif 'T' in psequence:  # default scale for tonal languages
        transform = {
            '#': 1.6,
            'V': 3.0,
            'c': 1.1,
            'v': 3.0,  # raise the cost for the gapping of vowels
            '<': 0.8,
            '$': 0.5,
            '>': 0.7,
            # new values for alternative prostrings
            'A': 1.6,  # initial
            'B': 1.3,  # syllable-initial
            'C': 1.2,  # ascending

            'L': 1.1,  # descending
            'M': 1.1,  # syllable-descending
            'N': 0.5,  # final

            'X': 3.0,  # vowel in initial syllable
            'Y': 3.0,  # vowel in non-final syllable
            'Z': 0.7,  # vowel in final syllable
            'T': 1.0,  # Tone
            '_': 0.0  # break character
        }
    else:  # default scale for other languages
        transform = {
            '#': 2.0,
            'V': 1.5,
            'c': 1.1,
            'v': 1.3,
            '<': 0.8,
            '$': 0.8,
            '>': 0.7,

            # new values for alternative prostrings
            'A': 2.0,  # initial
            'B': 1.75,  # syllable-initial
            'C': 1.5,  # ascending

            'L': 1.1,  # descending
            'M': 1.1,  # syllable-descending
            'N': 0.8,  # final

            'X': 1.5,  # vowel in initial syllable
            'Y': 1.3,  # vowel in non-final syllable
            'Z': 0.8,  # vowel in final syllable
            'T': 0.0,  # Tone
            '_': 0.0  # break character
        }

    return floats([transform[i] for i in psequence])


def _codepoint(c):
    return 'U+' + hex(ord(c))[2:].upper().zfill(4)


def codepoints(sequence):
    return [' '.join(_codepoint(c) for c in s) for s in sequence]


def _norm(segment):
    return ''.join([NORM.get(s, s) for s in segment])


def normalize(sequence):
    """
    Normalize obvious and frequent miscodings of IPA.
    """
    return [_norm(s) for s in sequence]


def seallable(sequence,
              medials={
                  'j', 'w', 'jw', 'wj', 'i̯', 'u̯', 'i̯u̯', 'u̯i̯', 'iu', 'ui', 'y', 'ɥ', 'l',
                  'lj', 'lʲ', 'r', 'rj', 'rʲ', 'ʐ', 'ʑ', 'ʂ', 'ʂ'},
              vowels=VOWELS,
              tones=TONES,
              slash=True,
              unknown=REPLACEMENT):
    """
    Check if a syllable conforms to the basic SEA syllable.
    """
    if not sequence:
        raise ValueError('empty sequence passed to function')
    if len(sequence) > 5:
        return len(sequence) * [unknown]

    cv = soundclass(sequence, model='cv', slash=slash)

    ini, med, nuc, cod, ton = 5 * [False]

    if 3 <= len(sequence) <= 5:
        # first element must be the initial
        ini = 'i' if cv[0] == 'C' else '?'
        # last element must be tone
        ton = 't' if cv[-1] == 'T' else '?'
        # medial and coda can be missing
        med, nuc, cod = 3 * [False]

    # scenario the sequence has 5 elements, all slots must be filled
    if len(sequence) == 5:
        med = 'm' if sequence[1] in medials else '?'
        cod = 'c' if cv[3] == 'C' else '?'
        nuc = 'n' if cv[2] == 'V' else '?'

    # scenario the sequence has four slots filled, one must be missing, either
    # coda or medial
    elif len(sequence) == 4:
        med = 'm' if sequence[1] in medials else False
        if not med:
            nuc = 'n' if cv[1] == 'V' else '?'
            cod = 'c' if cv[2] == 'C' else '?'
        else:
            nuc = 'n' if cv[2] == 'V' else '?'

    # scenario where the sequence has three slots filled,
    # case 1 : "ma¹³". The second token must be a vowel
    # case 2 : "am¹³". The first token must be a vowel
    elif len(sequence) == 3:
        if cv[1] == 'V':
            ini = 'i' if cv[0] == 'C' else '?'
            nuc = 'n'
        elif cv[0] == 'V':
            ini = False
            nuc = 'n'
            cod = 'c' if cv[1] == 'C' else '?'

    # scenario with two elements only, means that the first element should be a
    # consonant
    elif len(sequence) == 2:
        nuc = 'n' if cv[0] == 'V' else '?'
        ton = 't' if cv[1] == 'T' else '?'

    # if only one segment is given, it must be the vowel
    else:
        nuc = 'n' if cv[0] == 'V' else '?'

    return [s for s in [ini, med, nuc, cod, ton] if s]
