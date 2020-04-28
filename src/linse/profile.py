from collections import defaultdict
from linse.segment import ipa
from linse.models import *

__all__ = ['simple', 'context', 'structured']

class Form(object):

    def __init__(self, text, **kw):
        self.text = text
        kw['text'] = text
        self.kw = kw

    def __str__(self):
        return self.text


def get_profile(
        *forms, 
        preceding=None,
        following=None,
        diacritics=DIACRITICS,
        vowels=VOWELS,
        tones=TONES,
        combiners="\u0361\u035c",
        breaks="-.",
        nasals='ãũẽĩõ',
        nasal_char="\u0303",
        nogos="_◦+",
        merge_vowels=True,
        merge_geminates=False,
        expand_nasals=False,
        semi_diacritics='shʃʂɕɦʐʑʒw',
        stress="ˈˌ'",
        nasal_placeholder="∼"):
    """
    Retrieve a list of graphemes from a list of forms.
    """
    graphemes = defaultdict(list)
    for i, form in enumerate(forms):
        kw = form.kw if hasattr(form, 'kw') else {'ID': i+1}
        try:
            segs = [preceding] + ipa(str(form),
                    diacritics=diacritics,
                    vowels=vowels,
                    tones=tones,
                    combiners=combiners,
                    breaks=breaks,
                    nasals=nasals,
                    nasal_char=nasal_char,
                    nogos=nogos,
                    merge_vowels=merge_vowels,
                    merge_geminates=merge_geminates,
                    expand_nasals=expand_nasals,
                    semi_diacritics=semi_diacritics,
                    stress=stress,
                    nasal_placeholder=nasal_placeholder) + [following]
        except ValueError:
            segs = []
            graphemes[str(form), 0].append(kw)
        for segment in segs:
            if segment:
                graphemes[segment, 1].append(kw)

    return graphemes


