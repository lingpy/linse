from collections import defaultdict
from linse.segment import ipa
from linse.models import *

class Form(object):

    def __init__(self, text, **kw):
        self.text = text
        kw['text'] = text
        self.kw = kw

    def __str__(self):
        return str(self.text)


class DraftProfile(object):

    def __init__(self, *forms, preceding=None, following=None, segmenter=None,
            **kw):
        """
        Initialize a draft profile from a list of forms.
        """
        # initiate the segmenter
        if not segmenter:
            keywords = dict(
                    semi_diacritics='shʃʂɕɦʐʑʒw',
                    merge_vowels=True,
                    merge_geminates=True)
            keywords.update(kw)
            self.segmentize = lambda x: ipa(x['text'], **keywords)
        else:
            self.segmentize = lambda x: segmenter(x['text'], **kw)
        # preceding and following
        self.preceding, self.following = preceding or '', following or ''
        # counter
        self.graphemes = defaultdict(list)
        self.exceptions = defaultdict(list)
        self.counter = 1
        # add forms passed upon initialization
        self.add_forms(*forms)

    def add_forms(self, *forms):
        """
        Add new forms to the profile.
        """
        for i, form in enumerate(forms):
            meta = form.kw if hasattr(form, 'kw') else {'ID': i+self.counter, 'text': form}
            try:
                segs = self.segmentize(meta)
                segs[0] = self.preceding+segs[0]
                segs[-1] += self.following
                for segment in segs:
                    if segment:
                        self.graphemes[segment].append(meta)
            except Exception as e:
                self.exceptions[str(form), str(e)].append(meta)
        # increase counter by i
        self.counter += i


