import functools
import itertools

__all__ = ['TypedSequence', 'words', 'ints', 'floats']


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

    def __add__(self, other):
        return TypedSequence(self._type, itertools.chain(self, other), strict=self._strict)

    def append(self, item):
        list.append(self, self.__class__.read(item, self._type, self._strict))

    def extend(self, other):
        list.extend(self, TypedSequence(self._type, other, strict=self._strict))

    def __setitem__(self, index, item):
        list.__setitem__(self, index, self.__class__.read(item, self._type, self._strict))


class words(TypedSequence):  # noqa: N801
    def __init__(self, iterable, strict=False):
        TypedSequence.__init__(self, str, iterable, strict=strict)

    @staticmethod
    def read(item, type_, strict):
        item = TypedSequence.read(item, type_, strict)
        if len(item.split()) > 1:
            raise ValueError(item)
        return item


ints = functools.partial(TypedSequence, int)
floats = functools.partial(TypedSequence, float)
