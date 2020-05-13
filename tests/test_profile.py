import pytest

from linse.profile import Form, DraftProfile 
from clldutils.path import TemporaryDirectory
from pathlib import Path

@pytest.mark.parametrize(
    'seqs,kw,res,errs',
    [
        (
          ['khanti'], 
          {}, 
          {'kh': 1, 'a': 1, 'n': 1, 't': 1, 'i': 1},
          {},
        ),
        (
          ['khanti'], 
          {'preceding': '^', 'following': '$'}, 
          {'^kh': 1, 'a': 1, 'n': 1, 't': 1, 'i$': 1},
          {},
        ),

        (
          ['khantiitta'], 
          {'merge_geminates': True}, 
          {'kh': 1, 'ii': 1, 'tt': 1, 'a': 2, 'n': 1, 't': 1},
          {},
        ),
        (
          ['kha pt a'],
          {},
          {},
          {('kha pt a', 'Invalid multi-word string: kha pt a'): 1},
          ),
        (
            ['maggi', None],
            {},
            {'m': 1, 'a': 1, 'gg': 1, 'i': 1},
            {('None', 'Invalid type for word: None'): 1}            
            ),
        (
          ['khantiitta'], 
          {'merge_geminates': False, 'merge_vowels': False, 'semi_diacritics': ''}, 
          {'k': 1, 'h': 1, 'i': 2, 't': 3, 'a': 2, 'n': 1},
          {}, 
        ),
        (
            [''],
            {},
            {},
            {('', 'Invalid empty string: ""'): 1},
            ),
        (
            ['abcde', 'fghij', 'klmn'],
            {"segmenter": list},
            {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'h': 1,
                'i': 1, 'j': 1, 'k': 1, 'l': 1, 'm': 1, 'n': 1},
            {},
            ),
        (
          ['jeden', 'morgen', 'waŋ', 'wingTsun', 'wàtúvhaks', 'hhhatun'],
          {},
          {
            "j": 1,
            "e": 3,
            "d": 1,
            "n": 5,
            "m": 1,
            "o": 1,
            "r": 1,
            "g": 2,
            "w": 3,
            "a": 3,
            "ŋ": 1,
            "i": 1,
            "Ts": 1,
            "u": 2,
            "à": 1,
            "t": 2,
            "ú": 1,
            "vh": 1,
            "ks": 1,
            "hhh": 1,
           },
          {},
          ),
    ]
)
def test_get_profile(seqs, kw, res, errs):
    for k, v in DraftProfile(*seqs, **kw).graphemes.items():
        assert len(v) == res[k]
    for k, v in DraftProfile(*[Form(s) for s in seqs], **kw).graphemes.items():
        assert len(v) == res[k]

    for (k, error), v in DraftProfile(*seqs, **kw).exceptions.items():
        assert len(v) == errs[k, error]
        
    
def test_DraftProfile():
    path = Path(__file__).parent.joinpath('data', 'forms.csv').as_posix()
    profile1 = DraftProfile.from_cldf(path, following='^', preceding='$')
    profile2 = DraftProfile.from_cldf(path, language='Luobenzhuo')
    profile3 = DraftProfile.from_cldf(path.replace('forms.csv',
        'forms_with_exceptions.csv'))
    assert len(profile3.exceptions) == 1
    assert profile3.get_exceptions()[1][0] == 'f e h l e r'

    assert len(profile2.graphemes) == 36
    with TemporaryDirectory('./') as tmp:
        profile1.write_profile(Path(tmp).joinpath('orthography.tsv'), 
                'Grapheme', 'BIPA', 'Frequency')
        profile3.write_exceptions(Path(tmp).joinpath('lexemes.tsv'))
    table = profile2.get_profile(
            'Grapheme', 'CLTS', 'SCA', 'BIPA', 'Unicode', 'Examples',
            'Frequency', 'Languages')
    with pytest.raises(ValueError):
        DraftProfile('muti').get_profile('This')

