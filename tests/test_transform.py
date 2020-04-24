import pytest
from linse import transform


@pytest.mark.parametrize(
    'seq,res',
    [
        ('t a ŋ ⁵ + ts ai t', ['t a ŋ ⁵', 'ts ai t']),
        ('k u n + d e', ['k u n', 'd e']),
        ('+ k i n + d e r +', ['k i n', 'd e r'])
    ]
)
def test_resegment(seq, res):
    assert transform.resegment(
            seq.split()) == [p.split() for p in res]



@pytest.mark.parametrize(
    'seq,res,vowels',
    [
        ('f a ŋ ⁵ m e i', 'f a ŋ ⁵ + m e i', 2),
        ('m a n t a', 'm a n + t a', 2),
        ('m a o a', 'm a + o + a', 1),
        ('h e r b s t g e w i t t e r', 'h e r + b s t g e + w i t + t e r', 2)
    ]
)
def test_syllabify(seq, res, vowels):
    assert ' '.join(transform.syllabify(seq.split(), vowels=vowels)) == res
