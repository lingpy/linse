from linse.subsequence import affixes, prefixes, suffixes, subsequences


def test_misc():

    assert affixes("abc") == ["abc", "ab", "bc", "a", "c"]
    assert suffixes("abc") == ["abc", "bc", "c"]
    assert prefixes("abc") == ["abc", "ab", "a"]

    assert subsequences("abc") == ["abc", "ab", "bc", "a", "b", "c"]


