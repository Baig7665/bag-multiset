"""Bag multiset implementation tracking element multiplicities."""

from __future__ import annotations

from typing import Hashable, Iterator


class Bag:
    """A multiset counting how many times each hashable element has been inserted.

    Elements with a count of zero are pruned immediately. This keeps iteration and
    equality checks cheap and makes an empty Bag behave like an empty container,
    which is the least surprising choice for callers who switch between sets and
    bags. The cost is that `remove` cannot distinguish "not present" from "removed
    down to zero"; both raise KeyError after the prune. We picked that trade-off
    deliberately over keeping zero-count tombstones, which would surface internals
    to users iterating the bag.
    """

    __slots__ = ("_counts",)

    _counts: dict

    def __init__(self, elements=None, *more):
        """Initialize from an optional iterable of hashable elements.

        Positional extras are treated as additional single elements so that
        `Bag('a', 'b')` and `Bag(['a', 'b'])` are equivalent and unambiguous.
        """
        self._counts = {}
        for src in (elements, *more):
            if src is None:
                continue
            for el in src:
                self._counts[el] = self._counts.get(el, 0) + 1

    def insert(self, element, n=1):
        """Add ``n`` copies of ``element``.

        ``n`` must be a non-negative integer; a negative count would be a
        silently-corrupting alias for remove, which we refuse rather than guess.
        """
        if not isinstance(n, int) or isinstance(n, bool) or n < 0:
            raise ValueError("count must be a non-negative integer")
        if n == 0:
            return
        self._counts[element] = self._counts.get(element, 0) + n

    def remove(self, element, n=1):
        """Remove ``n`` copies of ``element``.

        Raises ``KeyError`` if the element is absent or the count would drop
        below zero. Removing to exactly zero prunes the key, so a subsequent
        ``count`` returns 0 and iteration omits it.
        """
        if not isinstance(n, int) or isinstance(n, bool) or n < 0:
            raise ValueError("count must be a non-negative integer")
        if n == 0:
            return
        current = self._counts.get(element)
        if current is None or current < n:
            raise KeyError(element)
        if current == n:
            del self._counts[element]
        else:
            self._counts[element] = current - n

    def count(self, element):
        """Return the multiplicity of ``element`` (0 if absent)."""
        return self._counts.get(element, 0)

    def __contains__(self, element):
        return element in self._counts

    def __iter__(self):
        # Yield each element as many times as its multiplicity, matching the
        # bag/multiset semantics. Memory is O(elements) via a generator, not
        # O(total multiplicity) as a fully materialised list would be.
        for element, n in self._counts.items():
            for _ in range(n):
                yield element

    def __len__(self):
        return sum(self._counts.values())

    def elements(self):
        """Yield ``(element, count)`` pairs for elements currently present."""
        return iter(self._counts.items())

    def __eq__(self, other):
        if not isinstance(other, Bag):
            return NotImplemented
        return self._counts == other._counts

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __repr__(self):
        inner = ", ".join(repr(el) for el in self)
        return f"Bag([{inner}])"
