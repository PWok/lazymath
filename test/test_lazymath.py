from lazymath import *
import pytest


def test_equal():
    lazy = LazyVal(5)
    assert lazy == 5
    assert lazy == 5.0
    assert lazy != 4
    assert lazy == lazy
    
def test_add():
    assert LazyVal(5)+1 == 6
    assert LazyVal(1) + 0 == LazyVal(1)
    assert LazyVal(1/3) + 1  == LazyVal(1/3 +1)
    assert 1+LazyVal(-1)  == 0

def test_sub():
    assert LazyVal(5)-1 == 4
    assert LazyVal(1) - 0 == LazyVal(1)
    assert LazyVal(1/3) - 1  == LazyVal(1/3 -1)
    assert 1 - LazyVal(-1)  == 2
