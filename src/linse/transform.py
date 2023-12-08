"""
Transformations convert a sequence of tokens to new data structure.
"""
import typing
import unicodedata
from collections import defaultdict

from linse.models import STRESS, DIACRITICS
from linse.typedsequence import ints
from linse.annotate import soundclass, prosody
from linse.util import iter_dicts_from_csv, write_csv


__all__ = ['syllables', 'morphemes', 'flatten', 'syllable_inventories',
           "segment", "convert", "SegmentGrouper"]


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
            elif ppro in vowels and pro not in vowels and fpro > pro:
                yield syllable
                syllable, vowel_count = [], 0

        syllable.append(char)
    if syllable:
        yield syllable


def syllables(sequence,
              model='art',
              gap_symbol="-",
              slash=True,
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
        seq, model=model, slash=slash))
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
              slash=True):
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
        return syllables(sequence, slash=slash)

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
            D[form[doculect]] = defaultdict(lambda: defaultdict(list))
        for morpheme in morphemes(form[segments]):
            for syl in syllables(morpheme):
                cv = prosody(syl, format=format)
                template = ''.join(cv)
                for i, (s, c) in enumerate(zip(syl, cv)):
                    tpl = template[:i] + '**' + template[i] + '**' + template[i + 1:]
                    D[form[doculect]][s][tpl] += [form[ID]]
    return D


def _unorm(normalization, string):
    """
    Apply unicode normalization to a string.

    Note
    ----
    In contrast to the normal method, errors are caught and the input is
    returned, e.g., when passing an integer.
    """
    if isinstance(string, str):
        return unicodedata.normalize(normalization, string)
    return string


def segment(word: str, segments: typing.Container) -> typing.List[str]:
    """
    Segment a sequence with the help of list of subsequences.
    """
    if len(word) == 0:
        return [word]
    queue = [[[], word, word[:0]]]
    while queue:
        segmented, current, rest = queue.pop(0)
        if current in segments and not rest:
            return segmented + [current]
        elif len(current) == 1 and current not in segments:
            if rest:
                queue += [[segmented + [current], rest, word[:0]]]
            else:
                return segmented + [current]
        elif current not in segments:
            queue += [[segmented, current[: len(current) - 1], current[-1:] + rest]]
        else:
            queue += [[segmented + [current], rest, word[:0]]]


def convert(segments: typing.Iterable[str],
            converter,
            column,
            missing="«{0}»") -> typing.List[str]:
    """
    Convert a segmented sequence with the help of a conversion table.
    """
    return [
        converter.get(s, {column: missing.format(s)}).get(
            column, missing.format("column--{0}-not-found".format(column))
        )
        for s in segments
    ]


def retrieve_converter(
        words: typing.Iterable[typing.Iterable[str]],
        mapping: typing.Optional[
            typing.Callable[[typing.Iterable[str]], typing.Iterable[str]]] = None,
        grapheme_column="Sequence",
        frequency_column="Frequency",
) -> typing.Dict[str, typing.Dict[str, typing.Union[str, int]]]:
    """
    Retrieve a conversion table for segmented words.

    Parameters
    ----------
    words: list of iterables
    mapping: function that determines how individual segments are
             retrieved from each word, if None, we assume that the
             individual words are iterables
    """
    converter = defaultdict(lambda: {grapheme_column: "", frequency_column: 0})
    for word in words:
        for token in mapping(word) if mapping else word:
            converter[token][grapheme_column] = token
            converter[token][frequency_column] += 1
    return converter


class SegmentGrouper:
    """
    Sequence grouping with a conversion table.
    """
    def __init__(
        self,
        converter: typing.Sequence[typing.Dict[str, str]],
        normalization: str = "NFD",
        missing: str = "«{0}»",
        null: str = "NULL",
        grapheme_column: str = "Sequence",
    ):
        self.converter = {}
        self.columns = [grapheme_column] + [
            c for c in sorted(converter[0].keys()) if c != grapheme_column
        ]
        for row in converter:
            self.converter[_unorm(normalization, row[grapheme_column])] = {
                k: _unorm(normalization, row.get(k)) for k in self.columns
            }
        self.norm = lambda x: _unorm(normalization, x)
        self.missing = missing
        self.null = null
        self.grapheme = grapheme_column

    def __getitem__(self, idx):
        """
        Access rows of the conversion table by (normalized) grapheme.
        """
        return self.converter[idx]

    def __call__(self, sequence, column=None):
        column = column or self.grapheme
        if column not in self.columns:
            raise ValueError("The column {0} is not available.".format(column))
        return [
            elm
            for elm in convert(
                segment(self.norm(sequence), self.converter),
                self.converter,
                column or self.grapheme,
                self.missing,
            )
            if elm != self.null
        ]

    @classmethod
    def from_file(
        cls,
        file,
        normalization="NFD",
        delimiter="\t",
        missing="«{0}»",
        null="NULL",
        grapheme_column="Sequence",
    ):
        return cls(
            list(iter_dicts_from_csv(file, delimiter=delimiter)),
            normalization=normalization,
            missing=missing,
            null=null,
            grapheme_column=grapheme_column,
        )

    @classmethod
    def from_table(
        cls,
        table,
        normalization="NFD",
        missing="«{0}»",
        null="NULL",
        grapheme_column="Sequence",
    ):
        return cls(
            [dict(zip(table[0], row)) for row in table[1:]],
            normalization=normalization,
            missing=missing,
            null=null,
            grapheme_column=grapheme_column,
        )

    @classmethod
    def from_words(
        cls,
        words,
        normalization="NFD",
        missing="«{0}»",
        mapping=None,
        null="NULL",
        grapheme_column="Sequence",
    ):
        return cls(
            list(retrieve_converter(words, mapping=mapping).values()),
            normalization=normalization,
            missing=missing,
            null=null,
            grapheme_column=grapheme_column,
        )

    def to_table(self):
        table = [self.columns]
        for row in self.converter.values():
            table += [[row[c] for c in self.columns]]
        return table

    def write(self, path, delimiter="\t"):
        write_csv(path, self.to_table(), delimiter=delimiter)
