import pathlib

import pytest

from linse.segment import *


def pytest_generate_tests(metafunc):
    if metafunc.function.__name__ == 'test_ipa':
        vals = [
            ('t͡sɔyɡə', {}, ['t͡s', 'ɔy', 'ɡ', 'ə']),
            ('t͡sɔyɡə', {'merge_vowels': False}, ['t͡s', 'ɔ', 'y', 'ɡ', 'ə']),
            ('ˈtʲʰoɔːix_tərp͡f¹¹', {}, ['ˈtʲʰ', 'oɔːi', 'x', '_', 't', 'ə', 'r', 'p͡f', '¹¹']),
            ('ʰto͡i', {}, ['ʰt', 'o͡i']),
        ]
        for fname, kw in [
            ('segment_ipa', dict()),
            ('segment_ipa_no_merge_vowels', dict(merge_vowels=False, merge_geminates=False)),
            ('segment_ipa_nasals',
             dict(merge_geminates=True, expand_nasals=True, semi_diacritics='h')),
        ]:
            for line in pathlib.Path(__file__).parent.joinpath('data', fname + '.tsv').open():
                text, _, seq = line.strip().partition('\t')
                vals.append((text, kw, seq.split()))
        metafunc.parametrize("text,kw,seq", vals)


def test_ipa(text, kw, seq):
    assert ipa(text, **kw) == seq


@pytest.mark.parametrize(
    'text,seq',
    [
        ('', []),
    ]
)
def test_asjp(text, seq):
    assert asjp(text) == seq


def test_sampa():
    seq = 'tʰɔxtər'
    assert ''.join(sampa2ipa('t_hOxt@r')) == seq
    assert ' '.join(sampa('t_hOxt@r')) == 't _h O x t @ r'


def test_valid_word():
    with pytest.raises(ValueError):
        ipa(' test ')
    with pytest.raises(ValueError):
        ipa('')
