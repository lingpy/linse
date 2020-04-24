import pytest

from linse.annotate import *


@pytest.mark.parametrize(
    'seq,model,res',
    [
        ('th o ?/x a', 'cv', 'CVCV'),
        ('tʰ ɔ x ˈth ə r A ˈI ʲ', 'dolgo', 'TVKTVR' + REPLACEMENT + REPLACEMENT + REPLACEMENT),
    ]
)
def test_soundclass(seq, model, res):
    assert ''.join(soundclass(seq.split(), model)) == res


#assert_raises(ValueError, tokens2class, ['A'], 'dolgo')
#assert_raises(ValueError, tokens2class, 'bla', 'sca')


@pytest.mark.parametrize(
    'seq,res',
    [
        ('', ''),
        ('tʰ ɔ x t ə r', 'AXMBYN'),
        ('th o x ¹ t e', 'AXLTBZ'),
        ('', ''),
    ]
)
def test_prosody(seq, res):
    assert ''.join(prosody(seq.split())) == res


def test_prosodic_weights():
    seq = 'tʰ ɔ x t ə r'.split(' ')
    assert prosodic_weight(seq)[0] == 2
    assert prosodic_weight(seq)[-1] == 0.8


def test_codepoints():
    assert codepoints(['ˈtʲʰ']) == ['U+02C8 U+0074 U+02B2 U+02B0']
