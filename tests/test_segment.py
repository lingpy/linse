import pathlib

import pytest

from linse.segment import *


def pytest_generate_tests(metafunc):
    if metafunc.function.__name__ == 'test_ipa':
        vals = [
            ('t͡sɔyɡə', {}, ['t͡s', 'ɔy', 'ɡ', 'ə']),
            ('a.ut', {}, ["a", "u", "t"]),
            ("\u0361tsa", {}, ["\u0361t", "s", "a"]),
            ("ã", {"expand_nasals": True}, ["ã", "∼"]),
            ('t͡sɔyɡə', {'merge_vowels': False}, ['t͡s', 'ɔ', 'y', 'ɡ', 'ə']),
            ("t\u0361sa\u0303an", {"expand_nasals": True}, ['t͡s', 'ãa', '∼', 'n']),
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
        ("tj~ut", ["tj~", "u", "t"]),
        ("kwh$ark", ["kwh$", "a", "r", "k"]),
        ('kwh"$ark', ['kwh$"', "a", "r", "k"]),
        ('kw*~ark', ['kw~*', 'a', 'r', 'k']) 
    ]
)
def test_asjp(text, seq):
    assert asjp(text) == seq


def test_sampa():
    seq = 'tʰɔxtər'
    assert ''.join(sampa('t_hOxt@r')) == seq
    assert ' '.join(xsampa('t_hOxt@r')) == "tʰ ɔ x t ə r"


def test_valid_word():
    with pytest.raises(ValueError):
        ipa(' test ')
    with pytest.raises(ValueError):
        ipa('')
