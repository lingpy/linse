import functools
import itertools

__all__ = ['TypedSequence', 'Morpheme', 'Word', 'ints', 'floats']


class TypedSequence(list):
    """
    A list of objects of the same type.
    """
    def __init__(self, type_, iterable, strict=False):
        """
        :param type_: Type class for the items of the sequence
        :param iterable: Iterable of items
        :param strict: Boolean forcing type check if `True` and type cast if
            `False`
        """
        self._type = type_
        self._strict = strict
        items = []
        for x in (iterable.split() if isinstance(iterable, str) else iterable):
            items.append(self.__class__.read(x, self._type, self._strict))
        list.__init__(self, items)

    @staticmethod
    def read(item, type_, strict):
        if not isinstance(item, type_):
            if strict:
                raise ValueError(item)
            item = type_(item)
        return item

    @staticmethod
    def write(item):
        return str(item)

    def __str__(self):
        return ' '.join([self.__class__.write(x) for x in self])

    def __repr__(self):
        return repr(str(self))

    def __hash__(self):
        return hash(str(self))

    def __add__(self, other):
        return TypedSequence(self._type, itertools.chain(self, other), strict=self._strict)

    def append(self, item):
        list.append(self, self.__class__.read(item, self._type, self._strict))

    def extend(self, other):
        list.extend(self, TypedSequence(self._type, other, strict=self._strict))

    def __setitem__(self, index, item):
        list.__setitem__(self, index, self.__class__.read(item, self._type, self._strict))

    def __getitem__(self, key):
        if isinstance(key, slice):
            return TypedSequence(self._type, list(self)[key],
                                 strict=self._strict)
        return list(self)[key]


class Morpheme(TypedSequence):  # noqa: N801
    def __init__(self, iterable, strict=False):
        TypedSequence.__init__(self, str, iterable, strict=strict)

    @staticmethod
    def read(item, type_, strict):
        item = TypedSequence.read(item, type_, strict)
        if len(item.split()) > 1:
            raise ValueError(item)
        return item

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Morpheme(list(self)[key], strict=self._strict)
        return list(self)[key]


class Word(Morpheme):

    def __init__(self, iterable, sep=" + "):
        Morpheme.__init__(self, iterable, strict=False)
        self.morphemes = [
            Morpheme(x) for x in (
                ' '.join(iterable).split(sep)
                if not isinstance(iterable, str)
                else iterable.split(sep))]
        self.sep = sep

    def __add__(self, other):
        if self and other:
            self.morphemes.append(Morpheme(other))
            return Word(str(self) + self.sep + str(other))
        else:
            return Word(str(self) or str(other))

    def __iadd__(self, other):
        return self.__add__(other)

    def append(self, other):
        self.morphemes[-1].append(Morpheme(str(other)))
        return super(Word, self).append(other)

    def extend(self, other):
        if not self and not Word(str(other)):
            return
        if not self:
            self.morphemes = Word(str(other)).morphemes
            return super(Word, self).__init__(str(other))
        if not other:
            return
        if self and other:
            self.morphemes.extend(Word(str(other)).morphemes)
            return super(Word, self).__init__(str(self) + self.sep +
                                              str(other))

    def replace(self, i, item):
        self.morphemes[i] = Morpheme(item)
        new_word = self.sep.join([str(x) for x in self.morphemes])
        self.__init__(new_word, sep=self.sep)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Word(list(self)[key], sep=self.sep)
        return list(self)[key]



ints = functools.partial(TypedSequence, int)
floats = functools.partial(TypedSequence, float)
