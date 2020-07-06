"""
Annotating a sequence means creating a list of annotations for a sequence.
"""
from linse.models import *  # noqa: F401, F403
from linse.typedsequence import ints, floats
from linse.util import get_CLTS, get_NORMALIZE

__all__ = ['soundclass', 'REPLACEMENT', 'prosody', 'prosodic_weight',
        'codepoints', 'normalize', 'clts', 'bipa', 'CLTS', 'NORM', 'seallable']

REPLACEMENT = '\ufffd'
CLTS = get_CLTS()
NORM = get_NORMALIZE()


def _token2soundclass(token, model, stress=STRESS, diacritics=DIACRITICS, cldf=True):
    """
    Convert a single token into a sound-class.

    tokens : str
        A token (phonetic segment).

    model : :py:class:`~lingpy.data.model.Model`
        A :py:class:`~lingpy.data.model.Model` object.

    stress : str (default=rcParams['stress'])
        A string containing the stress symbols used in the analysis. Defaults
        to the stress as defined in ~lingpy.settings.rcParams.

    diacritics : str (default=rcParams['diacritics'])
        A string containing diacritic symbols used in the analysis. Defaults to
        the diacritic symbolds defined in ~lingpy.settings.rcParams.

    cldf : bool (default=False)
        If set to True, this will allow for a specific treatment of phonetic
        symbols which cannot be completely resolved (e.g., laryngeal h₂ in
        Indo-European). Following the `CLDF <http://cldf.clld.org>`_
        specifications (in particular the specifications for writing
        transcriptions in segmented strings, as employed by the `CLTS
        <http://calc.digling.org/clts/>`_ initiative), in cases of insecurity
        of pronunciation, users can adopt a ```source/target``` style, where
        the source is the symbol used, e.g., in a reconstruction system, and
        the target is a proposed phonetic interpretation. This practice is also
        accepted by the `EDICTOR <http://edictor.digling.org>`_ tool.

    Returns
    -------

    sound_class : str
        A sound-class representation of the phonetic segment. If the segment
        cannot be resolved, the respective string will be rendered as "0"
        (zero).
    """
    if cldf:
        a, sep, b = token.partition('/')
        if sep:
            token = b or '?'

    if not isinstance(model, Model):
        model = MODELS[model]

    try:
        return model[token]
    except KeyError:
        try:
            return model[token[0]]
        except IndexError:
            return REPLACEMENT
        except KeyError:
            # check for stressed syllables
            if token[0] in stress and len(token) > 1:
                try:
                    return model[token[1:]]
                except KeyError:
                    try:
                        return model[token[1]]
                    except KeyError:
                        # new character for missing data and spurious items
                        return REPLACEMENT
            elif token[0] in diacritics:
                if len(token) > 1:
                    try:
                        return model[token[1:]]
                    except KeyError:
                        try:
                            return model[token[1]]
                        except KeyError:
                            return REPLACEMENT
                else:
                    return REPLACEMENT
            else:
                # new character for missing data and spurious items
                return REPLACEMENT


def soundclass(tokens, model='dolgo', stress=STRESS, diacritics=DIACRITICS, cldf=True):
    """
    Convert tokenized IPA strings into their respective class strings.

    Parameters
    ----------

    tokens : list
        A list of tokens as they are returned from :py:func:`ipa2tokens`.

    model : :py:class:`~lingpy.data.model.Model`
        A :py:class:`~lingpy.data.model.Model` object.

    stress : str (default=rcParams['stress'])
        A string containing the stress symbols used in the analysis. Defaults
        to the stress as defined in ~lingpy.settings.rcParams.

    diacritics : str (default=rcParams['diacritics'])
        A string containing diacritic symbols used in the analysis. Defaults to
        the diacritic symbolds defined in ~lingpy.settings.rcParams.

    cldf : bool (default=True)
        If set to True, as by default, this will allow for a specific treatment
        of phonetic
        symbols which cannot be completely resolved (e.g., laryngeal h₂ in
        Indo-European). Following the `CLDF <http://cldf.clld.org>`_
        specifications (in particular the
        specifications for writing transcriptions in segmented strings, as
        employed by the `CLTS <http://calc.digling.org/clts/>`_ initiative), in
        cases of insecurity of pronunciation, users can adopt a
        ```source/target``` style, where the source is the symbol used, e.g.,
        in a reconstruction system, and the target is a proposed phonetic
        interpretation. This practice is also accepted by the `EDICTOR
        <http://edictor.digling.org>`_ tool.

    Returns
    -------

    classes : list
        A sound-class representation of the tokenized IPA string in form of a
        list. If sound classes cannot be resolved, the respective string will
        be rendered as "0" (zero).

    Notes
    -----
    The function ~lingpy.sequence.sound_classes.token2class returns a "0"
    (zero) if the sound is not recognized by LingPy's sound class models. While
    an unknown sound in a longer sequence is no problem for alignment
    algorithms, we have some unwanted and often even unforeseeable behavior,
    if the sequence is completely unknown. For this reason, this function
    raises a ValueError, if a resulting sequence only contains unknown sounds.

    Examples
    --------
    >>> from lingpy import *
    >>> tokens = ipa2tokens('t͡sɔyɡə')
    >>> classes = tokens2class(tokens,'sca')
    >>> print(classes)
    CUKE
    """
    # raise value error if input is not an iterable (tuple or list)
    if not isinstance(tokens, (tuple, list)):
        raise ValueError("Need tuple or list as input.")

    out = []
    for token in tokens:
        out.append(_token2soundclass(token, model, stress=stress, diacritics=diacritics, cldf=cldf))
    if out.count(REPLACEMENT) == len(out):
        raise ValueError("[!] your sequence contains only unknown characters")
    return out


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
        elif a >= b >= c or c == 8:  # descending
            if c == 9:  # word final position
                psequence.append('Z' if b == 7 else 'N')  # vowel or consonant
            else:
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
        else:
            raise ValueError(
                "Conversion to prosodic string failed due to a condition which was not "
                "defined in the convertion, for details compare the numerical string "
                "{0} with the profile string {1}".format(sonority, psequence))
    return psequence


def prosody(sequence, format=True, stress=STRESS, diacritics=DIACRITICS,
        cldf=True):
    """
    Create a prosodic string of the sonority profile of a sequence.

    Parameters
    ----------

    seq : list
        A list of integers indicating the sonority of the tokens of the
        underlying sequence.

    stress : str (default=rcParams['stress'])
        A string containing the stress symbols used in the analysis. Defaults
        to the stress as defined in ~lingpy.settings.rcParams.

    diacritics : str (default=rcParams['diacritics'])
        A string containing diacritic symbols used in the analysis. Defaults to
        the diacritic symbolds defined in ~lingpy.settings.rcParams.

    cldf : bool (default=False)
        If set to True, this will allow for a specific treatment of phonetic
        symbols which cannot be completely resolved (e.g., laryngeal h₂ in
        Indo-European). Following the `CLDF <http://cldf.clld.org>`_
        specifications (in particular the specifications for writing
        transcriptions in segmented strings, as employed by the `CLTS
        <http://calc.digling.org/clts/>`_ initiative), in cases of insecurity
        of pronunciation, users can adopt a ```source/target``` style, where
        the source is the symbol used, e.g., in a reconstruction system, and
        the target is a proposed phonetic interpretation. This practice is also
        accepted by the `EDICTOR <http://edictor.digling.org>`_ tool.

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

    A prosodic string is a sequence of specific characters which indicating
    their resprective prosodic context (see :evobib:`List2012` or
    :evobib:`List2012a` for a detailed description).
    In contrast to the previous model, the current implementation allows for a
    more fine-graded distinction between different prosodic segments. The
    current scheme distinguishes 9 prosodic positions:

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
    >>> prosodic_string(ipa2tokens('t͡sɔyɡə')
    'AXBZ'

    """
    if not sequence:
        return []

    # get the sonority profile
    sonority = [9] + \
        ints(soundclass(
            sequence, model='art', stress=stress, diacritics=diacritics, cldf=cldf)) + \
        [9]
    psequence = _process_prosody(sonority)

    assert len(psequence) == len(sequence)
    conv = PROSODY_FORMATS.get(format, {})
    return [conv.get(x, x) for x in psequence]


def prosodic_weight(sequence, _transform=None, stress=STRESS,
        diacritics=DIACRITICS, cldf=True):
    """
    Calculate prosodic weights for each position of a sequence.

    Parameters
    ----------

    prostring : string
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
    >>> from lingpy import *
    >>> prostring = '#vC>'
    >>> prosodic_weight(prostring)
    [2.0, 1.3, 1.5, 0.7]

    See also
    --------
    prosodic_string

    """
    psequence = prosody(sequence, stress=stress, diacritics=diacritics,
            cldf=cldf)

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


def _token2clts(segment):
    return CLTS.get(
            _norm(segment),
            CLTS.get(
                _norm(segment[0]) if segment else '?',
                ['?', '?']
                )
            )


def bipa(sequence):
    """
    Convert a sequence in supposed IPA to the B(road)IPA of CLTS.

    Notes
    -----
    The mapping is not guaranteed to work as well as the more elaborate mapping
    with `pyclts`. 
    """
    return [_token2clts(segment)[0] for segment in sequence]


def clts(sequence):
    """
    Convert a sequence in supposed IPA to the CLTS feature names.

    Notes
    -----
    The mapping is not guaranteed to work as well as the more elaborate mapping
    with `pyclts`. 
    """
    return [_token2clts(segment)[1] for segment in sequence]


def seallable(
        sequence,
        medials={
            'j', 'w', 'jw', 'wj', 'i̯', 'u̯', 'i̯u̯', 'u̯i̯', 'iu', 'ui', 'y', 'ɥ', 'l',
            'lj', 'lʲ', 'r', 'rj', 'rʲ', 'ʐ', 'ʑ', 'ʂ', 'ʂ'},
        vowels=VOWELS,
        tones=TONES,
        diacritics=DIACRITICS,
        stress=STRESS,
        cldf=True,
        unknown=REPLACEMENT,
        ):
    """
    Check if a syllable conforms to the basic SEA syllable.
    """
    if not sequence:
        raise ValueError('empty sequence passed to function')
    if len(sequence) > 5:
        return len(sequence) * [unknown]

    cv = soundclass(sequence, model='cv', diacritics=diacritics, stress=stress, cldf=cldf)

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
            ini = None
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

