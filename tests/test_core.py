import unittest

from bag_multiset import Bag


class TestBag(unittest.TestCase):

    def test_init_with_iterable(self):
        b = Bag(["a", "a", "b"])
        self.assertEqual(b.count("a"), 2)
        self.assertEqual(b.count("b"), 1)
        self.assertEqual(b.count("c"), 0)
        self.assertEqual(len(b), 3)

    def test_init_with_string(self):
        b = Bag("aab")
        self.assertEqual(b.count("a"), 2)
        self.assertEqual(b.count("b"), 1)

    def test_init_with_positional_extras(self):
        b = Bag("a", "b", "a")
        self.assertEqual(b.count("a"), 2)
        self.assertEqual(b.count("b"), 1)

    def test_init_none_default(self):
        b = Bag()
        self.assertEqual(len(b), 0)
        self.assertEqual(b.count("a"), 0)

    def test_insert_default_one(self):
        b = Bag()
        b.insert("x")
        self.assertEqual(b.count("x"), 1)
        b.insert("x")
        self.assertEqual(b.count("x"), 2)

    def test_insert_multiple(self):
        b = Bag()
        b.insert("x", 5)
        self.assertEqual(b.count("x"), 5)

    def test_insert_zero_is_noop(self):
        b = Bag(["a"])
        b.insert("a", 0)
        self.assertEqual(b.count("a"), 1)
        b.insert("z", 0)
        self.assertNotIn("z", b)

    def test_insert_negative_raises(self):
        b = Bag()
        with self.assertRaises(ValueError):
            b.insert("x", -1)

    def test_insert_non_int_raises(self):
        b = Bag()
        with self.assertRaises(ValueError):
            b.insert("x", 2.0)
        with self.assertRaises(ValueError):
            b.insert("x", "2")

    def test_insert_bool_rejected(self):
        b = Bag()
        with self.assertRaises(ValueError):
            b.insert("x", True)

    def test_remove_default_one(self):
        b = Bag(["a", "a"])
        b.remove("a")
        self.assertEqual(b.count("a"), 1)
        b.remove("a")
        self.assertEqual(b.count("a"), 0)
        self.assertNotIn("a", b)

    def test_remove_multiple(self):
        b = Bag(["a", "a", "a", "a"])
        b.remove("a", 3)
        self.assertEqual(b.count("a"), 1)

    def test_remove_to_zero_prunes_key(self):
        b = Bag(["a", "a"])
        b.remove("a", 2)
        self.assertEqual(b.count("a"), 0)
        self.assertNotIn("a", b)
        self.assertEqual(len(b), 0)

    def test_remove_absent_raises_keyerror(self):
        b = Bag(["a"])
        with self.assertRaises(KeyError):
            b.remove("z")

    def test_remove_more_than_present_raises_keyerror(self):
        b = Bag(["a"])
        with self.assertRaises(KeyError):
            b.remove("a", 2)
        self.assertEqual(b.count("a"), 1)

    def test_remove_after_prune_raises_keyerror(self):
        b = Bag(["a"])
        b.remove("a")
        with self.assertRaises(KeyError):
            b.remove("a")

    def test_remove_zero_is_noop(self):
        b = Bag(["a"])
        b.remove("a", 0)
        self.assertEqual(b.count("a"), 1)
        b.remove("z", 0)
        self.assertNotIn("z", b)

    def test_remove_negative_raises(self):
        b = Bag(["a"])
        with self.assertRaises(ValueError):
            b.remove("a", -1)

    def test_remove_non_int_raises(self):
        b = Bag(["a", "a", "a"])
        with self.assertRaises(ValueError):
            b.remove("a", 1.5)
        with self.assertRaises(ValueError):
            b.remove("a", "1")

    def test_remove_bool_rejected(self):
        b = Bag(["a", "a"])
        with self.assertRaises(ValueError):
            b.remove("a", True)

    def test_count_absent_is_zero(self):
        b = Bag(["a"])
        self.assertEqual(b.count("missing"), 0)

    def test_contains(self):
        b = Bag(["a", "a", "b"])
        self.assertIn("a", b)
        self.assertIn("b", b)
        self.assertNotIn("c", b)

    def test_len_total_multiplicity(self):
        b = Bag(["a", "a", "b"])
        self.assertEqual(len(b), 3)
        b.insert("c", 4)
        self.assertEqual(len(b), 7)
        b.remove("a", 2)
        self.assertEqual(len(b), 5)

    def test_iter_yields_with_multiplicity(self):
        b = Bag(["a", "a", "b", "c", "c", "c"])
        got = sorted(list(b))
        self.assertEqual(got, ["a", "a", "b", "c", "c", "c"])

    def test_iter_empty_yields_nothing(self):
        b = Bag()
        self.assertEqual(list(b), [])

    def test_elements_pairs(self):
        b = Bag(["a", "a", "b"])
        got = sorted(b.elements(), key=lambda kv: kv[0])
        self.assertEqual(got, [("a", 2), ("b", 1)])

    def test_elements_after_prune_omits_zero(self):
        b = Bag(["a", "a"])
        b.remove("a", 2)
        self.assertEqual(list(b.elements()), [])

    def test_equality_same_counts(self):
        self.assertEqual(Bag(["a", "a", "b"]), Bag(["a", "a", "b"]))
        self.assertEqual(Bag(["a", "a", "b"]), Bag(["b", "a", "a"]))

    def test_equality_after_prune(self):
        # Removing all copies prunes the key, so two bags that both have zero
        # of an element must compare equal regardless of history.
        x = Bag(["a", "a", "b"])
        x.remove("a", 2)
        y = Bag(["b"])
        self.assertEqual(x, y)

    def test_inequality_different_counts(self):
        self.assertNotEqual(Bag(["a", "a"]), Bag(["a"]))
        self.assertNotEqual(Bag(["a", "b"]), Bag(["a", "c"]))

    def test_equality_vs_non_bag(self):
        self.assertNotEqual(Bag(["a", "b"]), {"a", "b"})
        self.assertNotEqual(Bag(["a"]), 42)

    def test_repr_round_trips_through_init(self):
        b = Bag(["a", "a", "b"])
        r = repr(b)
        self.assertEqual(r, "Bag(['a', 'a', 'b'])")
        rebuilt = eval(r)
        self.assertEqual(b, rebuilt)

    def test_repr_empty(self):
        self.assertEqual(repr(Bag()), "Bag([])")

    def test_unhashable_element_rejected(self):
        with self.assertRaises(TypeError):
            Bag([[1, 2]])

    def test_mixed_types_supported(self):
        b = Bag([1, "a", 1, "a", "a"])
        self.assertEqual(b.count(1), 2)
        self.assertEqual(b.count("a"), 3)

    def test_remove_preserves_unaffected_elements(self):
        b = Bag(["a", "a", "b", "b", "b"])
        b.remove("a", 2)
        self.assertEqual(b.count("b"), 3)
        self.assertEqual(b.count("a"), 0)
        self.assertNotIn("a", b)


if __name__ == "__main__":
    unittest.main()
