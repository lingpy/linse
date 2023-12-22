from pathlib import Path

import pytest

from linse.transform import *
from linse.transform import retrieve_converter
from linse.transform import _unorm
from linse.typedsequence import ints
from linse.util import iter_dicts_from_csv


@pytest.mark.parametrize(
    'seq,kw,res',
    [
        ('t i a o ¹ b u ² d a o',
         {},
         [['t', 'i', 'a', 'o', '¹'], ['b', 'u', '²'], ['d', 'a', 'o']]),
        ('j a b l o k o',
         {},
         [['j', 'a'], ['b', 'l', 'o'], ['k', 'o']]),
        ('j a b ə l k o',
         {},
         [['j', 'a'], ['b', 'ə', 'l'], ['k', 'o']]),
        ('j a b u - k o',
         {},
         [['j', 'a'], ['b', 'u'], ['-', 'k', 'o']]),
        ('- a b u - k o',
         {},
         [['-', 'a'], ['b', 'u'], ['-', 'k', 'o']]),
        ('m a ⁵ i o', {'max_vowels': 3}, [['m', 'a', '⁵'], ['i', 'o']]),
        ('m a n t a', {}, ['m a n'.split(), 't a'.split()]),
        ("m a u a t o", {}, ["m a u".split(), ["a"], "t o".split()]),
        ('h e r b s t g e w i t t e r',
         {},
         [['h', 'e', 'r'], ['b', 's', 't', 'g', 'e'], ['w', 'i', 't'], ['t', 'e', 'r']])
    ]
)
def test_syllables(seq, kw, res):
    assert syllables(seq.split(), **kw) == res


@pytest.mark.parametrize(
    'seq,kw,res',
    [
        ('t i a o ¹ b u ² d a o',
            {'split_on_tones': True},
            [['t', 'i', 'a', 'o', '¹'], ['b', 'u', '²'], ['d', 'a', 'o']]
            ),
        ('t i a o ¹ b u ² d a o',
            {'split_on_tones': False},
            [['t', 'i', 'a', 'o', '¹', 'b', 'u', '²', 'd', 'a', 'o']]
            ),
        ('t i a o ¹ + b u ² # d a o',
            {},
            [['t', 'i', 'a', 'o', '¹'], ['b', 'u', '²'], ['d', 'a', 'o']]
            ),
        ('t i a o ¹ b u _ d a o',
            {},
            [['t', 'i', 'a', 'o', '¹', 'b', 'u'], ['d', 'a', 'o']]
            ),
        (
            'b + + t', {}, [['b'], ['t']]
                ),
        (
            '+ t a ŋ + n i + + f a +',
            {},
            [['t', 'a', 'ŋ'], ['n', 'i'], ['f', 'a']]
            )
    ]
)
def test_morphemes(seq, kw, res):
    assert morphemes(seq.split(), **kw) == res


@pytest.mark.parametrize(
        'seq, kw, res',
        [
            (
                [['t', 'a', 'g'], ['w', 'e', 'r', 'k']],
                {'separator': '+'},
                ['t', 'a', 'g', '+', 'w', 'e', 'r', 'k']
                ),
            (
                [[], ['t', 'a', 'g'], ['x'], ['w', 'e', 'r', 'k'], []],
                {'separator': 'XXX'},
                ['t', 'a', 'g', 'XXX', 'x', 'XXX', 'w', 'e', 'r', 'k']
                ),

            ]
        )
def test_flatten(seq, kw, res):
    assert flatten(seq, **kw) == res


@pytest.mark.parametrize(
        'forms,kw,res',
        [
            (
                [
                    {
                        'Segments': ['t', 'a', 't', 'a'], 
                        'Language_ID': 'Language',
                        'ID': '1'
                        },
                    ],
                 {
                     'format': 'CcV'
                     },
                 1
                ),
            ]
        )
def test_syllable_inventories(forms, kw, res):
    assert len(syllable_inventories(forms,
        **kw)[forms[0]['Language_ID']][forms[0]['Segments'][0]]) == res


def test__unorm():
    assert len(_unorm("NFD", "á")) == 2
    assert len(_unorm("NFC", "á")) == 1
    assert _unorm("NFD", 1) == 1
    assert _unorm("NFC", None) is None


def test_segment():
    assert segment("matam", {"m", "at", "a", "m"}) == ["m", "at", "a", "m"]
    assert segment("", {"a"}) == [""]
    assert segment("m", {}) == ["m"]

    # test segment with non-string types
    assert segment(
            tuple([1, 2, 3, 4, 5]), 
            {tuple([1, 2]), tuple([3]), tuple([4, 5])}
            ) == [(1, 2), (3,), (4, 5)]

    assert segment(
            ints("1 2 3 4 5".split()),
            {ints("1 2".split()), ints(["3"]), ints("4 5".split())}
            )[0] == ints("1 2".split())

    


def test_convert():
    prf = {
        "am": {"grouped": "a.m", "ungrouped": "a m"},
        "t": {"grouped": "t", "ungrouped": "t"}
            }
    assert convert(segment("tam", prf), prf, "grouped") == ["t", "a.m"]
    assert convert(segment("tam", prf), prf, "ungrouped") == ["t", "a m"]
    assert convert(segment("tak", prf), prf, "grouped") == ["t", "«a»", "«k»"]


def test_SegmentGrouper():
    data = list(iter_dicts_from_csv(Path(__file__).parent / "data" / "data.tsv", delimiter="\t"))
    prf = SegmentGrouper(data, normalization="NFC", missing="?")
    assert prf("tam", "IPA") == ["t", "ã"]

    prf2 = SegmentGrouper.from_file(
        Path(__file__).parent / "data" / "data.tsv", delimiter="\t", missing="?")
    assert prf2("tum") == ["t", "?", "?"]

    prf3 = SegmentGrouper.from_table(
        [["Graphemes", "IPA"]] + [[row["Sequence"], row["IPA"]] for row in data],
        grapheme_column="Graphemes")
    assert prf3("amim") == ["am", "«i»", "«m»"]
    assert prf3.to_table()[0][0] == "Graphemes"

    my_list = [["a", "b"], ["aa", "bb"], ["cc", "cc"]]
    op1 = SegmentGrouper.from_table(my_list, grapheme_column="a")
    op2 = SegmentGrouper.from_table(op1.to_table(), grapheme_column=op1.grapheme)
    assert op1.to_table()[-1][0] == "cc"

    op2.write(Path(__file__).parent / "data" / "test.csv", delimiter=",")
    op3 = SegmentGrouper.from_file(
        Path(__file__).parent / "data" / "test.csv", delimiter=",",
        grapheme_column="a")
    assert len(op3.converter) == 2
    assert op3["aa"]["b"] == "bb"

    op4 = SegmentGrouper.from_words(["mat the ma"], mapping=lambda x: x.split())
    op5 = SegmentGrouper.from_words(["mat the ma".split()])
    assert op4("mat") == op5("mat")

    assert pytest.raises(ValueError, op5, "mat", column="IPPA")


def test_retrieve_converter():
    assert "th" in retrieve_converter(["m a th e m a t i cs"], mapping=lambda x: x.split())
