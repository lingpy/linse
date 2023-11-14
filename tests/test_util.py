from linse.util import *


def test_data_path():
    assert data_path('nothing').stem == 'nothing'


def test_get_CLTS():
    clts = get_CLTS()
    for a, b in [('a', 'a'), ('th', 'tʰ')]:
        assert clts[a][0] == b


def test_NORMALIZE():
    norm = get_NORMALIZE()
    for a, b in [(':', 'ː'), ('ʸ', 'ʲ')]:
        assert norm[a] == b
