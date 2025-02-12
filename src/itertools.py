from typing import List
from itertools import batched

for batch in batched("Hello, world!", 3):
    print(batch)

nums: List[int] = [1, 2, 3, 4, 5]

batches = batched(nums, n=3)
print(next(batches))
