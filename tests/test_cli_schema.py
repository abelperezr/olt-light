import unittest

from light_olt.cli.schema import PathSeg, ResolveError, lookup, resolve


class FakePlane:
    index = {
        "system": {
            "k": "c",
            "m": "ietf-system",
            "c": {"hostname": {"k": "f", "m": "ietf-system"}},
        },
        "interfaces": {
            "k": "c",
            "m": "ietf-interfaces",
            "c": {
                "interface": {
                    "k": "l",
                    "m": "ietf-interfaces",
                    "keys": ["name"],
                    "c": {"enabled": {"k": "f", "t": "boolean"}},
                }
            },
        },
    }


class SchemaTests(unittest.TestCase):
    def test_unique_abbreviation(self):
        name, _ = lookup({"c": FakePlane.index}, "sys")
        self.assertEqual(name, "system")

    def test_resolve_list_and_leaf(self):
        actions, mode = resolve(
            FakePlane(), [], ["interfaces", "interface", "xpon0", "enabled"]
        )
        self.assertEqual(actions[0][0], "set")
        self.assertEqual(actions[0][3], "true")
        self.assertEqual(mode[-1].keys, {"name": "xpon0"})

    def test_unknown_element(self):
        with self.assertRaises(ResolveError):
            resolve(FakePlane(), [], ["missing"])

    def test_path_segment_fields(self):
        node = {"k": "l"}
        segment = PathSeg("interface", "ietf-interfaces", {"name": "x"}, node)
        self.assertEqual(segment.name, "interface")
        self.assertEqual(segment.node, node)


if __name__ == "__main__":
    unittest.main()
