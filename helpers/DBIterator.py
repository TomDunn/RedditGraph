class DBIterator():
    """
        An abstraction for working with SQLAlchemy queries
        that would otherwise return very large result sets.
        Depending on the DB, these query sets could large enough
        to use up all available memory on the machine running it.
    """

    def __init__(self, query=None, use_offset="_count", query_limit=30):

        self._offset        = use_offset
        self._query_limit   = query_limit

        if query is not None:
            self.set_query(query)

    def set_query(self, query):

        self._query = query
        self._count = 0

        if self._query._offset is None:
            self._initial_offset = 0
        else:
            self._initial_offset = self._query._offset

        if self._query._limit is None:
            self._limit = self._query.count()
        else:
            self._limit = self._query._limit

        if self._limit < self._query_limit:
            self._query_limit = self._limit

        self._query = self._query.limit(self._query_limit)

    def _get_offset(self, num=None):
        if self._offset == "_count":
            return self._initial_offset + self._count
        return 0

    def results_iter(self):

        while self._count < self._limit:

            offset = self._get_offset()
            if offset > 0:
                self._query = self._query.offset(offset)

            for result in self._query:
                self._count += 1
                yield result
