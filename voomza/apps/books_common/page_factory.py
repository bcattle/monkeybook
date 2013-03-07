
class BaseBookPageFactory(object):
    """
    This is an abstract class,
    should be implemented by each book
    """
    def __init__(self, book_cls, hash=None, user=None):
        assert hash or user

        # Needs to be defined in the child class
        assert self._pages

        # Set the user and yearbook on each Page instance
        if hash:
            book = book_cls.objects.get(hash=hash)
            user = book.rankings.user
        else:
            book = book_cls.objects.filter(rankings__user=user)[0]
        for page in self._pages:
            page.user = user
            page.book = book

    @property
    def pages(self):
        return self._pages

    def get_page(self, page_num):
        for page in self._pages:
            if page.page == page_num:
                return page
        return None
