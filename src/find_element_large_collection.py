from typing import List, Set
from timeit import timeit

lst: List[int] = list(range(100_000))
st: Set[int] = set(range(100_000))

print(timeit("99_999 in lst", number=1000, globals=globals()))
print(timeit("99_999 in st", number=1000, globals=globals()))

# lst = 0.57754 sec
# st = 0.00002 sec

# Sets are way faster
# Why ?
# 1. Sets are structured as hash tables -> much better
# lookup, insertion and deletion operations

# 2. Sets are usually (O1) time
# complexity so should scale almost linear if collection grows
# Lists use 0n so search time grows as size increases

# 3. List preserve order and can have duplicates so slower. Sets are unordered and unique

# So if no dups and order are unimportant - use a set.
