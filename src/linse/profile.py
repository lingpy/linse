from collections import defaultdict

from linse.segment import ipa
from linse.annotate import _token2soundclass, _codepoint
from linse.util import iter_dicts_from_csv, write_csv


class Form(object):

    def __init__(self, text, **kw):
        self.text = text
        kw['text'] = text
        self.kw = kw

    def __str__(self):
        return str(self.text)


class DraftProfile(object):

    def __init__(
            self,
            *forms,
            preceding=None,
            following=None,
            segmenter=None,
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
        if forms:
            self.add_forms(*forms)

    @classmethod
    def from_cldf(
            clf,
            filename,
            text='Form',
            preceding=None,
            following=None,
            segmenter=None,
            language=None,
            **kw):
        profile = clf(
            preceding=preceding,
            following=following,
            segmenter=segmenter,
            **kw
        )
        for row in iter_dicts_from_csv(filename):
            if not language or row['Language_ID'] == language:
                profile.add_forms(Form(row[text], **row))
        return profile

    def add_forms(self, *forms):
        """
        Add new forms to the profile.
        """
        i = -1
        for i, form in enumerate(forms):
            meta = form.kw if hasattr(form, 'kw') else {'ID': i + self.counter, 'text': form}
            try:
                segs = self.segmentize(meta)
                segs[0] = self.preceding + segs[0]
                segs[-1] += self.following
                for segment in segs:
                    if segment:
                        self.graphemes[segment].append(meta)
            except Exception as e:
                self.exceptions[str(form), str(e)].append(meta)
        # increase counter by i
        self.counter += i

    def get_profile(self, *columns, transform=None, key=None):
        """
        Return a profile in form of a two-dimensional list.

        Notes
        -----
        Columns which are pre-defined are:
        - Grapheme
        - SCA
        - BIPA
        - CLTS
        - Unicode
        - Examples
        - Frequency
        - Languages
        """
        columns = columns or ['Grapheme']

        def identity(x):
            return x

        key = key or identity
        # not all columns are allowed
        transform = transform or {}
        modify = {
            'Grapheme': lambda x, y: x,
            'SCA': lambda x, y: _token2soundclass(x, 'sca'),
            'IPA': lambda x, y: _token2soundclass(x, "bipa"),
            'CLTS': lambda x, y: _token2soundclass(x, "clts"),
            'Unicode': lambda x, y: ' '.join([_codepoint(c) for c in x]),
            'Examples': lambda x, y: ', '.join(
                sorted(set([item['text'] for item in y]))[:3]
            ),
            'Frequency': lambda x, y: len(y),
            'Languages': lambda x, y: ', '.join(
                sorted(set([item['Language_ID'] for item in y]))
            )
        }
        modify.update(transform)

        if [c for c in columns if c not in modify]:
            raise ValueError('selected columns which are not available')

        table = []
        for char, meta in self.graphemes.items():
            table.append([modify[col](char, meta) for col in columns])
        return [columns] + sorted(table, key=key)

    def write_profile(self, filename, *columns, transform=None, key=None):
        """
        Write profile to file.

        Notes
        -----
        Columns which are pre-defined are:
        - Grapheme
        - SCA
        - BIPA
        - CLTS
        - Unicode
        - Examples
        - Frequency
        - Languages

        """
        columns = columns or ['Grapheme']
        table = self.get_profile(*columns, transform=transform, key=key)
        write_csv(filename, [[str(x) for x in row] for row in table], delimiter='\t')

    def get_exceptions(self):
        """
        Tabulate exceptions.
        """
        table = [['Lexeme', 'Replacement', 'Comment']]
        for (form, exception), metas in self.exceptions.items():
            table.append([form, '?', exception + ' ({0} cases)'.format(len(metas))])
        return table

    def write_exceptions(self, filename):
        write_csv(filename, self.get_exceptions(), delimiter='\t')
