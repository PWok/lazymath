from abc import ABC, abstractmethod
from math import prod
from typing import Callable


__all__ = [
    "LazyAbstract",
    "LazyVal",
    "LazySum",
    "LazyProd",
    "LazyFuncFactory",
    "LazyNeg",
]


# TODO: Mixiny żeby isinstance(LazyVal(3), number) zwracało true. Specjalna klasa LazyNum?

class NotEvaluatedType:
    """Base class of the NotEvaluated singleton.
    (well, if you explicitly make another instance it won't be a singleton)"""

    def __repr__(self) -> str:
        return "NotEvaluated"

    def __neg__(self):
        return self


NotEvaluated = NotEvaluatedType()


class LazyAbstract(ABC):
    """Abstract Base Class for Lazy classes.
    
    Classes derived from this can raise Exceptions. For example even though this implements __int__
    calling something like `int(LazyVal([1,2,3]))` will raise the same* exception as int([1,2,3])
        (* the traceback will actually differ -- it will include the LazyAbstract.__int__ method)
    """

    __slots__ = ("_value",)

    def __init__(self) -> None:
        self._value = NotEvaluated  # type: ignore

    def eval(self):
        """Return the value this Lazy expresion evaluates to. If it's not cached calculate it."""
        if isinstance(self._value, NotEvaluatedType):
            self._value = self.calculate()
        return self._value

    @abstractmethod
    def calculate(self):
        """Calculate and return the returned value of Lazy expression. Do not use cache."""
        raise NotImplementedError

    # __repr__ is used for debugging and informal representation
    # we dont want to evaluate the value if we dont need to
    # This abstract implementation should (hopefully) never be used
    def __repr__(self):
        return f"<{type(self).__name__}: value = {self._value}>"

    # __str__ is used for converting to str type - we have to evaluate
    def __str__(self):
        return str(self.eval())

    # A lot of the following will have the same format:
    # If we want to call a mathod on Lazy object we evaluate it
    # And call the same method on the calculated value
    def __bytes__(self):
        # May raise error if the value we evaluate to does not implement __bytes__
        return bytes(self.eval())  # type: ignore

    def __lt__(self, other):
        if isinstance(other, LazyAbstract):
            return self.eval() < other.eval()
        return self.eval() < other

    def __le__(self, other):
        if isinstance(other, LazyAbstract):
            return self.eval() <= other.eval()
        return self.eval() <= other

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, LazyAbstract):
            return self.eval() == other.eval()
        return self.eval() == other

    def __ne__(self, other):
        if self is other:
            return False
        if isinstance(other, LazyAbstract):
            return self.eval() != other.eval()
        return self.eval() != other

    def __gt__(self, other):
        if isinstance(other, LazyAbstract):
            return self.eval() > other.eval()
        return self.eval() > other

    def __ge__(self, other):
        if isinstance(other, LazyAbstract):
            return self.eval() >= other.eval()
        return self.eval() >= other

    # TODO: theres a lot of thinking needed to get this right and i dont feel like doing it rn
    def __hash__(self):
        raise NotImplementedError

    def __bool__(self):
        return bool(self.eval())

    def __add__(self, other):
        if not isinstance(other, LazyAbstract):
            return LazySum(self, other)
        # leave other types for __radd__ (especially LazySums specialized __radd__)
        return NotImplemented

    def __radd__(self, other):
        return LazySum(other, self)

    def __sub__(self, other):
        if not isinstance(other, LazyAbstract):
            return LazySum(self, LazyNeg(other))
        return NotImplemented

    def __rsub__(self, other):
        return LazySum(other, LazyNeg(self))

    def __mul__(self, other):
        if not isinstance(other, LazyAbstract):
            return LazyProd(self, other)
        return NotImplemented

    def __rmul__(self, other):
        return LazyProd(other, self)

    # XXX: Do I want to make matmul?
    def __matmul__(self, other):
        raise NotImplementedError

    def __rmatmul__(self, other):
        raise NotImplementedError

    # TODO skipped a few here, come back later

    def __neg__(self):
        return -self.eval()  # type: ignore

    # TODO skipped a few here, come back later

    def __int__(self):
        return int(self.eval())
    def __float__(self):
        return float(self.eval())
    def __complex__(self):
        return complex(self.eval())
    def __index__(self):
        return int(self)
    def __round__(self, ndigits=None):
        return round(float(self), ndigits)
    def __trunc__(self):
        return float(self).__trunc__()
    def __floor__(self):
        return float(self).__floor__()
    def __ceil__(self):
        return float(self).__ceil__()


class LazyVal(LazyAbstract):
    __slots__ = ()

    # TODO: Possible optimization -- when an instance of a Lazy class is passed as value
    # the constructor could *not* construct a new Lazy object and just pass on the value
    # Probably requires a metaclass?
    # FIXME May add metaclass anyway because executing code like `Lazy._value = 4` breaks things

    def __init__(self, value):
        super().__init__()
        self._value = value

    def calculate(self):
        return self._value

    def __repr__(self):
        return f"LazyVal({self._value})"


# Sum and Prod accept any number of arguments (they are not binary operators)
# Because there *were* plans for optimization that *may* not come to fruition...
class LazySum(LazyAbstract):
    __slots__ = ("_terms",)

    def __init__(self, *args) -> None:
        super().__init__()
        self._terms = tuple(
            map(lambda x: x if isinstance(x, LazyAbstract) else LazyVal(x), args)
        )

    def calculate(self):
        return sum(map(lambda x: x.eval(), self._terms))

    def __add__(self, other):
        if isinstance(other, LazySum):
            return LazySum(*self._terms, *other._terms)
        if isinstance(other, LazyAbstract):
            return LazySum(*self._terms, other)
        return LazySum(*self._terms, LazyVal(other))

    def __repr__(self):
        return f"LazySum{str(self._terms)}"


class LazyProd(LazyAbstract):
    __slots__ = ("_terms",)

    def __init__(self, *args) -> None:
        super().__init__()
        self._terms = tuple(
            map(lambda x: x if isinstance(x, LazyAbstract) else LazyVal(x), args)
        )

    def calculate(self):
        return prod(map(lambda x: x.eval(), self._terms))

    def __mul__(self, other):
        if isinstance(other, LazyProd):
            return LazyProd(*self._terms, *other._terms)
        if isinstance(other, LazyAbstract):
            return LazyProd(*self._terms, other)
        return LazyProd(*self._terms, LazyVal(other))

    def __repr__(self):
        return f"LazyProd{str(self._terms)}"


class LazyNeg(LazyAbstract):
    __slots__ = ("_arg",)

    def __init__(self, arg) -> None:
        super().__init__()
        self._arg = arg

    def calculate(self):
        return -self._arg

    def __repr__(self):
        return f"LazyNeg({str(self._arg)})"


def LazyFuncFactory(func: Callable):
    """LazyFuncFactory -- a decorator for mamking functions Lazy

    Parameters
    ----------
    func : Callable
        Function (or any Callable really) to make lazy

    Returns
    -------
    LazyFunc (or similar)
        A concrete subclass of LazyAbstract. Evaluates to
    """

    # TODO: Add lru_cache
    class LazyFunc(LazyAbstract):
        """A Lazy function made using LazyFuncFactory. You shouldn't be able to see this..."""

        __slots__ = ("_args", "_kwargs")

        def __init__(self, *args, **kwargs) -> None:
            super().__init__()
            self._args = args
            self._kwargs = kwargs

        def calculate(self):
            calculated_args = map(_calculate, self._args)
            calculated_kwargs = {k: _calculate(v) for k, v in self._kwargs.items()}
            return func(*calculated_args, **calculated_kwargs)

        def __repr__(self):
            return f"LazyFunc({func.__qualname__})(args={self._args}, kwargs={self._kwargs})"

    try:
        LazyFunc.__name__ = f"LazyFunc({func.__name__})"
        LazyFunc.__qualname__ = LazyFunc.__name__

        doc = f"""Lazy implementation of `{func.__qualname__}` via LazyFuncFactory decorator

                ----------
                # Original {func.__qualname__} docstring:
                {func.__doc__}"""
        LazyFunc.__doc__ = doc

        setattr(
            LazyFunc, "__wrapped__", func
        )  # MyPy and Pylint both scream at this BUT IT WORKS!
    except (AttributeError, LookupError):
        pass

    return LazyFunc


def _calculate(value):
    if isinstance(value, LazyAbstract):
        return value.eval()
    return value
