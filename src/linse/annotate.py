"""
Annotating a sequence means creating a list of annotations for a sequence.
"""
from linse.models import *  # noqa: F401, F403
from linse.typedsequence import ints, floats

__all__ = ['soundclass', 'REPLACEMENT', 'prosody', 'prosodic_weight', 'codepoints']

REPLACEMENT = '\ufffd'


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
            return '0'
        except KeyError:
            # check for stressed syllables
            if len(token) > 0:
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
            else:
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

    See also
    --------
    ipa2tokens
    class2tokens
    token2class

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


def prosody(sequence, format=True, stress=STRESS, diacritics=DIACRITICS, cldf=False):
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
    assert 9 not in sonority[1:-1]

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

    assert len(psequence) == len(sequence)
    conv = PROSODY_FORMATS.get(format, {})
    return [conv.get(x, x) for x in psequence]


def prosodic_weight(sequence, _transform=None, stress=STRESS, diacritics=DIACRITICS):
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
    psequence = prosody(sequence, stress=stress, diacritics=diacritics)

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


def codepoints(sequence):
    def codepoint(c):
        return 'U+' + hex(ord(c))[2:].upper().zfill(4)

    return [' '.join(codepoint(c) for c in s) for s in sequence]


def sea_structure(sequence):
    return [None for s in sequence]
