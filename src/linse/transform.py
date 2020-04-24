from linse.annotate import soundclass
from linse.typedsequence import ints

def resegment(tokens, sep='+'):
    """
    Resegmentation of a sequence based on a segmentation character.

    :param tokens: the input sequence
    :param separator: a character or a list of characters

    :returns: a list of tokens, which conform to the *type*
    """
    out = [[]]
    for token in tokens:
        if token in sep:
            out += [[]]
        else:
            out[-1] += [token]
    return [part for part in out if part]


def syllabify(tokens, sep='+', vowels=2):
    """
    Find syllable breakpoints for a set of tokens, based on their prosody.

    :param tokens: input sequence
    :param sep: separator
    :param vowels: indicate after how many vowels in a row it should split
    """
    out = []
    prosodies = ints(soundclass(tokens, 'art'))
    tuples = [('#', 0)]+list(zip(tokens, prosodies))+[('$', 0)]
    vowel = 0
    for i, (tok, pro) in enumerate(tuples[1:-1], start=1):
        ptok, ppro = tuples[i-1]
        ftok, fpro = tuples[i+1]
        if pro == 7:
            vowel += 1
        if fpro != 8:
            if ppro >= pro < fpro and vowel:
                out += [sep]
                vowel = 0
            elif vowel > vowels and pro == 7:
                out += [sep]
        out += [tok]
    return out
        
    
