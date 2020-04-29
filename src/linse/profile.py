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
        return str(self.text)


def get_profile(
        *forms, 
        preceding=None,
        following=None,
        segmenter=None,
        **kw
        ):
    """
    Retrieve a list of graphemes from a list of forms.
    """
    if not segmenter:
        keywords = dict(
                semi_diacritics='shʃʂɕɦʐʑʒw',
                merge_vowels=True,
                merge_geminates=True)
        keywords.update(kw)
        segmentize = lambda x: ipa(x['text'], **keywords)
    else:
        segmentize = lambda x: segmenter(x['text'], **kw)
            
    preceding, following = preceding or '', following or ''
    graphemes = defaultdict(list)
    for i, form in enumerate(forms):
        meta = form.kw if hasattr(form, 'kw') else {'ID': i+1, 'text': form}
        try:
            segs = segmentize(meta)
            segs[0] = preceding+segs[0]
            segs[-1] += following
            for segment in segs:
                if segment:
                    graphemes[segment, 0].append(meta)

        except Exception as e:
            graphemes[str(form), str(e)].append(meta)

    return graphemes


