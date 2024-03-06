import re
import functools

__all__ = ['TypedSequence', 'Morpheme', 'Word', 'ints', 'floats']


class TypedSequence(list):
    """
    A list of objects of the same type.
    """
    item_type = None
    item_separator = None

    def __init__(self,
                 iterable=None,
                 type=None,
                 separator=None,
                 strict=False):
        """
        If `strict` is `False` - the default - items to be added to the sequence will be cast to \
        the required type, if this is implemented in the type's initializer. E.g. `int` can be \
        initialized with a suitable `str`.

        :param iterable: Iterable of items
        :param type: Type class for the items of the sequence
        :param strict: Flag signaling whether to strictly type check items in the sequence. If \
        `True`, no implicit type casting will be done when adding items to the sequence. If \
        `False`, implicit type casting - as far as supported by `type` will be done.
        """
        if type:
            self.item_type = type
        if self.item_type is None:
            raise ValueError('TypedSequence must have an item type.')
        if separator:
            self.item_separator = separator
        self.strict = strict
        super().__init__(self._iter_items(iterable or []))

    def _cast(self, item):
        if isinstance(item, self.item_type):
            return item
        if self.strict:
            raise TypeError('Items in TypedSequence must be of type {}'.format(self.item_type))
        return self.item_type(item)

    def _iter_items(self, iterable):
        if isinstance(iterable, self.item_type):
            # We want `str` to **not** be interpreted as list of characters!
            iterable = [iterable]
        for item in iterable:
            yield self._cast(item)

    def _from_items(self, iterable):
        if isinstance(iterable, TypedSequence):
            if self.item_type != iterable.item_type:
                raise TypeError()
            return iterable
        return self.__class__(iterable, type=self.item_type, separator=self.item_separator)

    def __str__(self):
        return (self.item_separator or ' ').join([str(item) for item in self])

    @classmethod
    def from_string(cls, s, type=None, separator=None, strict=False):
        return cls(
            s.split(sep=separator or cls.item_separator),
            type=type or cls.item_type,
            separator=separator or cls.item_separator,
            strict=strict)

    def __hash__(self):
        return hash(str(self))

    def __add__(self, other):
        return self._from_items(list(self) + list(self._from_items(other)))

    def __radd__(self, other):
        return self._from_items(list(self._from_items(other)) + list(self))

    def __iadd__(self, other):
        self.extend(other)
        return self

    def append(self, item):
        return super().append(self._cast(item))

    def extend(self, other):
        return super().extend(self._from_items(other))

    def insert(self, __index, __object):
        return super().insert(__index, self._cast(__object))

    def __setitem__(self, index, item):
        super().__setitem__(index, self._cast(item))

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self._from_items(list(self)[key])
        return list(self)[key]


class Segment(str):
    """
    A segment is a non-empty string which does not contain punctuation.
    """
    def __new__(cls, s):
        if not isinstance(s, str) or re.search(r'\s+', s) or '+' in s or not s:
            raise TypeError('Segments must be non-empty strings without whitespace or "+".')
        return str.__new__(cls, s)


class Morpheme(TypedSequence):  # noqa: N801
    """
    A morpheme is a sequence of segments.

    .. code-block:: python

        >>> m = Morpheme('abu')
        >>> str(m)
        'a b u'
        >>> m.to_text()
        'abu'
        >>> m[0]
        'a'
        >>> m2 = Morpheme.from_string(str(m))
        >>> m2 == m
        True
        >>> m.append('r')
        >>> m
        ['a', 'b', 'u', 'r']
   """
    item_type = Segment
    item_separator = ' '

    @classmethod
    def from_string(cls, s):
        if re.search(r'\s+', s):
            # We assume that s is a whitespace-separated list of segments:
            s = s.split()
        else:
            #
            # FIXME: do segmentation here!
            #
            s = list(s)
        return cls(s)

    def to_text(self):
        return ''.join(self)


class Word(TypedSequence):
    """
    A word is a sequence of morphemes.

    Words can be represented as strings in two ways:
    - as "string" of ' + '-separated morphemes, e.g. 'a m u q’ + d a + č',
    - as "text", e.g. 'amuq’dač'.
    """
    item_type = Morpheme
    item_separator = ' + '

    @classmethod
    def from_string(cls, s: str, **kw):
        kw['type'] = Morpheme
        # We assume s is a list of morphemes separated by +:
        return cls(iterable=[
            Morpheme.from_string(m.strip()) for m in s.split(cls.item_separator.strip())], **kw)

    def to_text(self):
        return ''.join(m.to_text() for m in self)


class Phrase(TypedSequence):
    item_type = Word
    item_separator = ' _ '

    @classmethod
    def from_string(cls, s: str, **kw):  # pragma: no cover
        kw['type'] = Word
        # We assume s is a list of morphemes separated by +:
        return cls(iterable=[
            Word.from_string(m.strip()) for m in s.split(cls.item_separator.strip())], **kw)

    @classmethod
    def from_text(cls, text):
        raise NotImplementedError()  # pragma: no cover


ints = functools.partial(TypedSequence, type=int)
floats = functools.partial(TypedSequence, type=float)
