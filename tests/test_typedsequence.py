import pytest

from linse.typedsequence import *


def test_TypedSequence():
    a1 = TypedSequence(int, '1 2 3')
    a2 = [1, 2, 3]
    a3 = [1, 3]
    assert list(a1) == a2
    assert a1 != a3
    del a1[1]
    assert list(a1) == a3
    assert isinstance(a1 + [4, 5], TypedSequence)
    assert not isinstance([4, 5] + a1, TypedSequence)
    assert TypedSequence(int, str(a1)) == a1

    with pytest.raises(ValueError):
        TypedSequence(int, '1 2 3'.split(), strict=True)

    a = TypedSequence(int, [], strict=True)
    with pytest.raises(ValueError):
        a.append('a')

    with pytest.raises(ValueError):
        _ = a + ['a']

    with pytest.raises(ValueError):
        a.extend(['a'])

    assert repr(a1) == "'1 3'"


def test_ints():
    string2 = '1 2 3 1 2 3'
    i = ints(string2)
    assert i[0] == 1
    assert str(i) == string2


def test_floats():
    string2 = '1 2 3 1 2 3'
    i = ints(string2)
    f = floats(string2)
    assert float(i[0]) == f[0]
    assert ' '.join([str(fl).split('.')[0] for fl in f]) == string2
    assert str(f).split()[0].startswith('1.')


def test_string():
    string1 = '1 2 3 + 1 2 3'
    s = Morpheme(string1)
    assert str(s) == string1


def test_misc():
    # check for types
    s = Morpheme('1 2 3')
    assert str(s + s) == '1 2 3 1 2 3'
    i = ints('1 2 3')
    assert str(i + [1, 2, 3]) == '1 2 3 1 2 3'

    # append
    app = Morpheme('1 2 3')
    app.append('4')
    assert str(app) == '1 2 3 4'

    app = ints('1 2 3')
    app.extend('4 5')
    assert str(app) == '1 2 3 4 5'

    with pytest.raises(ValueError):
        Morpheme('1 2').append('2 3')

    app = Morpheme('1 2 3')
    app[1] = 2
    assert app[1] == '2'

    s = Word("a b c + d e f")
    assert str(s.morphemes[0]) == "a b c"

    assert str(s + s) == str(s) + " + " + str(s)
    with pytest.raises(ValueError):
        s.append(str(s))
    s.extend(str(s))
    s.replace(0, "b c d")
    assert str(s.morphemes[0]) == "b c d"

    word = Word("a + b + c")
    
    # make sure word can be hashed
    word_in_dict = {word: word.morphemes}

    # make sure we can access word by its str() attribute
    assert word_in_dict[Word("a + b + c")] == word.morphemes

    # append and extend
    # append adds one item to the list extend adds a new morpheme
    w1, w2 = Word("a + b"), Word("a + b")
    w1.append("c")
    w2.extend("c")
    assert w1 != w2
    assert w1.morphemes != w2.morphemes
    assert str(w1) == "a + b c"
    assert str(w2) == "a + b + c"
    
    


