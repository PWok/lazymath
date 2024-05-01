import time
import sys


sys.path.append(".")
from lazymath.lazyclasses import *


def super_slow_function(x):
    time.sleep(3)
    return x * 2


def choosing_function(choice, if_true, if_false):
    return if_true if choice else if_false

start = time.time()
print(choosing_function(False, super_slow_function(5), -1))
end = time.time()
print(f"Elapsed time: {end-start}")


lazy_slow_function = LazyFuncFactory(super_slow_function)
start = time.time()
print(choosing_function(False, lazy_slow_function(5), -1))
end = time.time()
print(f"Elapsed time: {end-start}")