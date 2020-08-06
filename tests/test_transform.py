import pytest

from linse.transform import *


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
