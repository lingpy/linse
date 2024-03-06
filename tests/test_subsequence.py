from linse.subsequence import affixes, prefixes, suffixes, substrings


def test_misc():

    assert affixes("abc") == ["abc", "ab", "bc", "a", "c"]
    assert suffixes("abc") == ["abc", "bc", "c"]
    assert prefixes("abc") == ["abc", "ab", "a"]

    assert substrings("abc") == ["abc", "ab", "bc", "a", "b", "c"]


