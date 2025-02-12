from itertools import batched

# Using batched to paginate


class Pager:
    def __init__(self, results, page_size=25):
        self.pages = batched(results, page_size)
        # Initialise empty navigation caches.
        self.prev_pages = []
        self.next_pages = []

    def next_page(self):
        """Gets the next page of results or None."""
        # Get the next page, possibly from the navigation cache.
        next_page = self.next_pages.pop() if self.next_pages else next(self.pages, None)
        if next_page is not None:
            self.prev_pages.append(next_page)

        return next_page

    def prev_page(self):
        """Gets the previous page of results or None."""
        # The last page in prev_pages was the last one sent, so we need
        # to move it to `next_pages`.
        if len(self.prev_pages) >= 2:
            self.next_pages.append(self.prev_pages.pop())
            return self.prev_pages[-1]

        return None
