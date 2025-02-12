from utils import pager

pager = pager.Pager(range(10), page_size=4)
print(pager.prev_page())  # None
print(pager.next_page())  # (0, 1, 2, 3)
print(pager.prev_page())  # None
print(pager.next_page())  # (4, 5, 6, 7)
