class Iterator:

    @staticmethod
    def previous_current_next(iterable):
        """
        Make an iterator that yields an (previous, current, next) tuple per element.
        Args:
            iterable:

        Returns:
            None if the value does not make sense (i.e. previous before first and next after last).
        """
        iterable = iter(iterable)
        prv = None
        cur = iterable.__next__()
        try:
            while True:
                nxt = iterable.__next__()
                if abs(cur - nxt) > 1:
                    data = None
                else:
                    data = nxt
                if prv is not None:
                    if abs(prv - cur) > 1:
                        prv = None

                yield prv, cur, data
                prv = cur
                cur = nxt
        except StopIteration:
            if prv is not None:
                if abs(prv - cur) > 1:
                    prv = None
            yield prv, cur, None

