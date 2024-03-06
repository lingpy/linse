import pytest

from linse.typedsequence import *


def test_TypedSequence_init():
    with pytest.raises(ValueError):
        _ = TypedSequence()

    class T(TypedSequence):
        item_type = int

    s = TypedSequence(type=int)
    assert s == T()
    assert T(1) == T(['1'])

    with pytest.raises(TypeError):
        TypedSequence(['1'], type=int, strict=True)

    assert TypedSequence('abc', type=str) == TypedSequence(['abc'], type=str)


def test_TypedSequence_str():
    s = TypedSequence(type=int)
    assert str(s) == ''
    assert s == []
    assert str(TypedSequence([1, 2, 3], type=int)) == '1 2 3'
    t = TypedSequence([1, 2, 3], type=int, separator='-')
    assert str(t) == '1-2-3'
    assert t == TypedSequence.from_string(str(t), type=t.item_type, separator=t.item_separator)


def test_TypedSequence_hash():
    s = TypedSequence([1, 2, 3], type=int)
    d = {s: 5}
    assert d[s] == 5, 'Cannot use TypedSequence as dict key'
    # Hash includes the separator:
    assert len({s, TypedSequence([1, 2, 3], type=int)}) == 1
    assert len({s, TypedSequence([1, 2, 3], type=int, separator='x')}) == 2
    # unless there's just one item in the sequence:
    assert len(
        {TypedSequence([1], type=int), TypedSequence([1], type=int, separator='x')}
    ) == 1


def test_TypedSequence_setitem():
    s = TypedSequence(type=int)
    s.insert(0, '3')
    assert s == [3]

    with pytest.raises(TypeError):
        s[0] = []

    s[0] = '5'
    assert s == [5]

    with pytest.raises(ValueError):
        s.append('')


def test_TypedSequence_getitem():
    s = TypedSequence('1 2 3'.split(), type=int)
    assert s[1] == 2
    assert isinstance(s[:2], TypedSequence)
    assert s[1:] == TypedSequence('2 3'.split(), type=int)


def test_TypedSequence_and_list():
    a1 = TypedSequence('1 2 3'.split(), type=int)
    a2 = [1, 2, 3]
    a3 = [1, 3]
    assert a1 == a2
    assert a1 != a3
    del a1[1]
    assert a1 == a3
    assert isinstance(a1 + [4, 5], TypedSequence)
    assert isinstance([4, 5] + a1, TypedSequence)
    assert TypedSequence(str(a1).split(), type=int) == a1

    with pytest.raises(TypeError):
        TypedSequence('1 2 3'.split(), type=int, strict=True)

    a = TypedSequence(type=int, strict=True)
    with pytest.raises(TypeError):
        a.append('a')

    with pytest.raises(ValueError):
        _ = a + ['a']

    with pytest.raises(ValueError):
        a.extend(['a'])

    # check for slicing
    assert isinstance(TypedSequence("1 2 3".split(), type=int)[:], TypedSequence)
    assert TypedSequence("1 2 3".split(), type=int)[:2] == TypedSequence("1 2".split(), type=int)


def test_ints():
    string2 = '1 2 3 1 2 3'
    i = ints(string2.split())
    assert i[0] == 1
    assert str(i) == string2


def test_floats():
    string2 = '1 2 3 1 2 3'
    i = ints(string2.split())
    f = floats(string2.split())
    assert float(i[0]) == f[0]
    assert ' '.join([str(fl).split('.')[0] for fl in f]) == string2
    assert str(f).split()[0].startswith('1.')

    with pytest.raises(TypeError):
        _ = i + f

    i += [n for n in f]
    assert len(i) == 12


def test_Morpheme():
    string1 = '1 2 3'
    s = Morpheme(string1.split())
    assert str(s) == string1
    assert s.to_text() == '123'

    assert Morpheme(s) == s

    with pytest.raises(TypeError):
        _ = Morpheme('1 2 3 + 1 2 3'.split())

    # check for types
    s = Morpheme('1 2 3'.split())
    assert s == ['1', '2', '3']
    assert str(s + s) == '1 2 3 1 2 3'
    i = ints('1 2 3'.split())
    assert str(i + [1, 2, 3]) == '1 2 3 1 2 3'

    # append
    app = Morpheme('1 2 3'.split())
    app.append('4')
    assert str(app) == '1 2 3 4'
    
    assert Morpheme("a b c".split())[:2] == Morpheme("a b".split())
    assert isinstance(Morpheme("a b c".split())[:1], Morpheme)
    

    app = ints('1 2 3'.split())
    app.extend('4 5'.split())
    assert str(app) == '1 2 3 4 5'

    with pytest.raises(TypeError):
        Morpheme('1 2'.split()).append('2 3'.split())

    app = Morpheme('1 2 3'.split())
    with pytest.raises(TypeError):
        app[1] = 2
    app[1] = '2'
    assert app[1] == '2'


def test_Word():
    s = Word.from_string("a b c + d e f")
    assert str(s[0]) == "a b c"
    assert s.to_text() == 'abcdef'
    assert str(s + s) == str(s) + " + " + str(s)
    with pytest.raises(TypeError):
        s.append(str(s))
    s.extend(Word.from_string(str(s)))
    s[0] = Morpheme("b c d".split())
    assert str(s[0]) == "b c d"

    word = Word.from_string("a + b + c")
    
    # make sure word can be hashed
    word_in_dict = {word: word}

    # make sure we can access word by its str() attribute
    assert word_in_dict[Word.from_string("a + b + c")] == word

    # append and extend
    # append adds one item to the list extend adds a new morpheme
    w1, w2 = Word.from_string("a + b"), Word.from_string("a + b")
    w1.append(Morpheme("c"))
    w2.extend(["c"])
    assert w1 == w2

    # append, extend, append
    w = Word("")
    w.append("a")
    w.extend("a")
    w.append("a")
    w.extend("a")
    assert str(w) == "a + a + a + a"

    assert Word.from_string("a b + b")[:1] == Word.from_string("a b")
    assert Word.from_string("a b c")[0][0] == "a"

    # major tests for word properties
    w = Word("")
    assert not w
    w.insert(0, Morpheme("a"))
    w[0].append("b")
    w.extend([Morpheme.from_string("a b")])
    assert w == Word.from_string("a b + a b")
    
    w.extend([])
    assert w == Word.from_string("a b + a b")
    assert w[0] == Morpheme.from_string("a b")

    w = Word("")
    w += w
    assert w == Word("")

    w = Word.from_string("a b")
    w += w
    assert w == Word.from_string("a b + a b")
