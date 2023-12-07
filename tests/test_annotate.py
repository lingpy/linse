import pytest

from linse.annotate import *
import linse.annotate


@pytest.mark.parametrize(
    'seq,model,res',
    [
        ('th o ?/x a', 'cv', 'CVCV'),
        ("b ˀⁿgʷ a", "sca", "PKA"),
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
        ('b a ⁵', 'AXT'),
        ('m a t a o', 'AXBYZ'),
        ('a u t', 'XYN'),
        ('m s s', 'ALN'),
        ('m k a', 'ACZ'),
        ('k m n a', 'ACBX'),
        ('p n p', 'AXN'),
        ('p a k n k a', 'AXBYBZ'),
    ]
)
def test_prosody(seq, res):
    assert ''.join(prosody(seq.split())) == res


def test_prosodic_weights():
    seq = 'tʰ ɔ x t ə r'.split(' ')
    assert prosodic_weight(seq)[0] == 2
    assert prosodic_weight(seq)[-1] == 0.8
    assert prosodic_weight("b a ⁵".split(), _transform={"A": 0, "X": 1, "T": 2})[0] == 0
    assert prosodic_weight("b a ⁵".split())[0] == 1.6


def test_codepoints():
    assert codepoints(['ˈtʲʰ']) == ['U+02C8 U+0074 U+02B2 U+02B0']


def test_normalize():
    assert normalize(['a:', 't', 'e', 'm'])[0] == 'aː'


def test_bipa():
    assert bipa(['th', 'o', 'x', 't', 'e:', 'r']) == [
            'tʰ', 'o', 'x', 't', 'eː', 'r']


def test_clts():
    assert clts(['m', 'u', 't', 'i']) == ['voiced bilabial nasal consonant',
            'rounded close back vowel', 'voiceless alveolar stop consonant',
            'unrounded close front vowel']

    assert clts(["0"]) == ["?"]


def test__token2soundclass():
    assert linse.annotate._token2soundclass('', 'sca') == REPLACEMENT
    assert linse.annotate._token2soundclass('A', 'sca') == REPLACEMENT
    assert linse.annotate._token2soundclass('ʰaa', 'sca') == 'A'
    assert linse.annotate._token2soundclass('ʰ', 'sca') == REPLACEMENT
    assert linse.annotate._token2soundclass('ʰA', 'sca') == REPLACEMENT
    assert linse.annotate._token2soundclass('ˈA', 'sca') == REPLACEMENT
    assert linse.annotate._token2soundclass('ˈaː', 'sca') == 'A'
    assert linse.annotate._token2soundclass('ʰA/a', 'sca') == 'A'
    assert linse.annotate._token2soundclass('a/', 'sca') == REPLACEMENT




def test_soundclass_err():
    with pytest.raises(ValueError):
        soundclass('bla', 'sca')
    with pytest.raises(ValueError):
        soundclass(['A', 'O'], 'sca')


@pytest.mark.parametrize(
    'seq,res',
    [
        (['m', 'a', 't', '⁵'], ['i', 'n', 'c', 't']),
        (['m', 'J', 'a', 't', '⁵'], ['i', '?', 'n', 'c', 't']),
        (['m', 'j', 'a', 't', '⁵'], ['i', 'm', 'n', 'c', 't']),
        (['m', 'ju', 'a', 't', '⁵'], ['i', '?', 'n', 'c', 't']),
        (['m', 't', '⁵'], ['i', '?', 't']),
        (['m', 'j', ], ['?', '?']),
        (['a', '⁵'], ['n', 't']),
        (['m', 'j', 'a', '³'], ['i', 'm', 'n', 't']),
        (['a'], ['n']),
        (['a', 'a', 'a', 'a', 'a', 'a'], ['?', '?', '?', '?', '?', '?']),
        (['a', 'ŋ', '⁵'], ['n', 'c', 't']),
        (['m', 'a', '⁴'], ['i', 'n', 't']),
        (['m', 'j', 'a', '⁵'], ['i', 'm', 'n', 't']),
        (['m', 'n', 'a', 'u'], ['i', 'm', 'n', '?']),
        (['m', 'j', 't', '⁴'], ['i', 'm', '?', 't']),
    ]
)
def test_seallable(seq, res):
    assert seallable(seq, res)
    with pytest.raises(ValueError):
        seallable([])
