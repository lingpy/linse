from linse.util import *


def test_data_path():
    assert data_path('nothing').stem == 'nothing'


def test_get_CLTS():
    bipa, clts = get_CLTS()
    for a, b in [('a', 'a'), ('th', 'tʰ')]:
        assert bipa[a] == b


def test_NORMALIZE():
    norm = get_NORMALIZE()
    for a, b in [(':', 'ː'), ('ʸ', 'ʲ')]:
        assert norm[a] == b
