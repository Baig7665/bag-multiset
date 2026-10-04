# Bag Multiset

A small, dependency-free Python multiset that tracks how many times each
element appears. Supports `insert`, `remove`, and `count`, plus the usual
dunder methods (`len`, `in`, `iter`, `==`, `repr`).

## Usage

```python
from bag_multiset import Bag

b = Bag(["a", "a", "b"])
b.insert("a")        # now "a" has count 3
b.remove("b")        # "b" gone entirely
print(b.count("a"))  # 3
print(list(b))       # ['a', 'a', 'a'] in arbitrary order
print(len(b))        # 3
```

## Why this exists

`collections.Counter` reads a multiset if you squint, but its API is oriented
around counting occurrences of an input iterable and then reading statistics
back. When the workload is explicitly insert / remove / count with mutation
over time, `Counter` makes the intent murky: `del c[x]` vs `c[x] = 0` vs
`c.subtract` have different pruning behaviour, and `subtract` can produce
negative counts that surprise later readers. This library provides one
clear mutation model with no negative counts.

## The awkward edge

Removing an element down to zero copies prunes its key immediately. After that,
`count` returns `0` and `in` returns `False`, which is the desired behaviour.
The consequence is that `remove` cannot distinguish "element was never there"
from "element was there but removed to zero" — both raise `KeyError`. We chose
this over keeping zero-count tombstones, which would leak internals to anyone
iterating the bag or comparing two bags for equality. `insert(element, 0)`
and `remove(element, 0)` are no-ops rather than errors; they let callers skip
their own guards when counts are computed dynamically. `n` must be a plain
`int` — `bool` is rejected even though it subclasses `int`, because a
`True` count of 1 is almost always a caller mistake.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

