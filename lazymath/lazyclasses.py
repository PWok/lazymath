from abc import ABC, abstractmethod
from math import prod
from numbers import Number


class _Lazy(ABC):
    def __add__(self, other):
        if isinstance(other, LazySum):
            return LazySum(self, *other.terms)
        if isinstance(other, _Lazy):
            return LazySum(self, other)
        return LazySum(self, Lazy(other))

    def __radd__(self, other):
        return self+other

    def __mul__(self, other):
        if isinstance(other, LazyProd):
            return LazyProd(self, *other.terms)
        if isinstance(other, _Lazy):
            return LazyProd(self, other)
        return LazyProd(self, Lazy(other))

    def __rmul__(self, other):
        return self*other

    
    def __eq__(self, other):
        return self.evaluate() == other

    @abstractmethod
    def evaluate(self, simplify=True): ...


class Lazy(_Lazy):
    def __init__(self, value: Number):
        self.value = value

    def evaluate(self, simplify=True):
        return self.value


class LazySum(_Lazy):
    def __init__(self, *args) -> None:
        self.terms = list(args)

    def simplify(self):
        pass

    def evaluate(self, simplify=True):
        if simplify:
            self.simplify()
        return sum(map(lambda x: x.evaluate(), self.terms))

    def __add__(self, other):
        if isinstance(other, LazySum):
            return LazySum(*self.terms, *other.terms)
        if isinstance(other, _Lazy):
            return LazySum(*self.terms, other)
        return LazySum(*self.terms, Lazy(other))

class LazyProd(_Lazy):
    def __init__(self, *args) -> None:
        self.terms = list(args)

    def evaluate(self, simplify=True):
        if simplify:
            self.simplify()
        return prod(map(lambda x: x.evaluate(), self.terms))
    
    def __mul__(self, other):
        if isinstance(other, LazyProd):
            return LazyProd(*self.terms, *other.terms)
        if isinstance(other, _Lazy):
            return LazyProd(*self.terms, other)
        return LazyProd(*self.terms, Lazy(other))
