from lazymath import *
import pytest


def test_equal():
    lazy = Lazy(5)
    assert lazy == 5
    assert lazy == 5.0
    assert lazy != 4
    assert lazy == lazy
    
def test_add():
    assert Lazy(5)+1 == 6
    assert Lazy(1) + 0 == Lazy(1)
    assert Lazy(1/3) + 1  == Lazy(1/3 +1)

