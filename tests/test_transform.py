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
         [['j', 'a'], ['b', 'u', '-'], ['k', 'o']]),
        ('- a b u - k o',
         {},
         [['-', 'a'], ['b', 'u', '-'], ['k', 'o']]),
        ('m a ⁵ i o', {}, [['m', 'a', '⁵'], ['i', 'o']]),
        ('m a n t a', {}, ['m a n'.split(), 't a'.split()]),
        ('h e r b s t g e w i t t e r',
         {},
         [['h', 'e', 'r'], ['b', 's', 't'], ['g', 'e'], ['w', 'i', 't'], ['t', 'e', 'r']])
    ]
)
def test_syllables(seq, kw, res):

    assert syllables(seq.split(), **kw) == res


@pytest.mark.parametrize(
    'seq,kw,res',
    [
        ('t i a o ¹ b u ² d a o',
         {},
         [['t', 'i', 'a', 'o', '¹'], ['b', 'u', '²'], ['d', 'a', 'o']]),
        ('t i a o ¹ b u ² d a o',
         {'split_on_tones': False},
         [['t', 'i', 'a', 'o', '¹', 'b', 'u', '²', 'd', 'a', 'o']]),
        ('t i a o ¹ + b u ² # d a o',
         {},
         [['t', 'i', 'a', 'o', '¹'], ['b', 'u', '²'], ['d', 'a', 'o']]),
        ('t i a o ¹ b u _ d a o',
         {},
         [['t', 'i', 'a', 'o', '¹', 'b', 'u'], ['d', 'a', 'o']]),
        ('b + + t', {}, [['b'], ['t']]),
    ]
)
def test_morphemes(seq,kw, res):
    assert morphemes(seq.split(), **kw) == res
