"""
The regular expression used in the sampa2unicode-converter  is taken from an
algorithm for the conversion of XSAMPA to IPA (Unicode) by Peter
Kleiweg <http://www.let.rug.nl/~kleiweg/L04/devel/python/xsampa.html>.
@author: Peter Kleiweg
@date: 2007/07/19
"""
import re
import pathlib

from clldutils.misc import lazyproperty

__all__ = ['SAMPA']


class Sampa(dict):
    def __init__(self):
        dict.__init__(self)
        for line in pathlib.Path(
                __file__).parent.joinpath('data', 'sampa.csv').open(encoding='utf-8-sig'):
            line = line.strip()
            if line and not line.startswith('#'):
                key, val = line.split('\t', maxsplit=1)
                if key in self and self[key] != val:
                    raise ValueError("Keys encode too many values.")
                self[key] = val

        for k in self:
            self[k] = eval('"""' + self[k] + '"""')
        self[' '] = ' '

    @lazyproperty
    def segent_pattern(self):
        segs = '|'.join(re.escape(s) for s in sorted(self.keys(), key=lambda k: -len(k)))
        return re.compile('(' + segs + ')|(.)')


SAMPA = Sampa()
