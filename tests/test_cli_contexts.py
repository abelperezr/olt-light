import unittest

from light_olt.cli.backend import fallback_tree
from light_olt.cli.confd_cli import ConfdCLI
from light_olt.cli.md_cli import MdCli
from light_olt.cli.schema import PathSeg, resolve


HARDWARE = """
<hardware-state xmlns="urn:ietf:params:xml:ns:yang:ietf-hardware">
  <component><name>Board-LT4</name></component>
  <component><name>Board-LT1</name></component>
  <component><name>Board-LT2</name></component>
  <component><name>Board-Nta</name></component>
</hardware-state>
"""


class FakePlane:
    def __init__(self, name):
        self.name = name
        self.index = {}

    def desc(self, _name):
        return ""

    def export_xml(self, _datastore="running", module=None, xpath=None):
        del xpath
        if self.name == "shelf" and module == "ietf-hardware":
            return HARDWARE
        return None

    def running_signature(self):
        return ()


class ContextTests(unittest.TestCase):
    def test_shelf_forward_targets_follow_board_inventory(self):
        cli = ConfdCLI("shelf", "admin")
        cli.plane = FakePlane("shelf")
        self.assertEqual(cli.forward_targets(), ["ihub", "lt-1", "lt-2", "lt-4"])
        self.assertEqual(
            cli.handle("forward cli to lt-4", lambda _message: None),
            ("forward", "lt-4"),
        )

    def test_lt_does_not_expose_forward(self):
        cli = ConfdCLI("lt", "admin")
        cli.plane = FakePlane("lt")
        self.assertNotIn("forward", cli.oper_builtins())
        self.assertNotIn("forward", dict(cli.completion_options([], "")))

    def test_ihub_accepts_only_global_configuration_mode(self):
        cli = MdCli("admin")
        self.assertEqual(
            cli.completion_options(["configure"], "g"),
            [("global", "- Enter global configuration mode")],
        )
        output = []
        cli.handle("configure candidate", output.append)
        self.assertFalse(cli.in_cfg)
        cli.handle("configure g", output.append)
        self.assertTrue(cli.in_cfg)

    def test_lt_completes_schema_leaf_values(self):
        interface_node = {
            "k": "l", "m": "ietf-interfaces", "keys": ["name"],
            "c": {
                "channel-partition": {
                    "k": "c", "m": "bbf-xpon",
                    "c": {
                        "authentication-method": {
                            "k": "f", "m": "bbf-xpon", "t": "enumeration",
                        },
                    },
                },
                "multicast-cac": {
                    "k": "c", "m": "nokia-mcast-cac",
                    "c": {
                        "multicast-rate-limit-exceed-action": {
                            "k": "f", "m": "nokia-mcast-cac",
                            "t": "bbf-mgmd:rate-limit-action-enum",
                        },
                    },
                },
            },
        }
        cli = ConfdCLI("lt", "admin")
        cli.plane = FakePlane("lt")
        cli.plane.index = {}
        cli.config_mode = True
        cli.frames = [[PathSeg(
            "interface", "ietf-interfaces", {"name": "PON1"}, interface_node,
        )]]

        self.assertEqual(
            cli.completion_options(
                ["channel-partition", "authentication-method"], "as",
            ),
            [("as-per-v-ani-expected", "")],
        )
        self.assertEqual(
            cli.completion_options(
                ["multicast-cac", "multicast-rate-limit-exceed-action"],
                "best",
            ),
            [("best-effort", "")],
        )

    def test_exit_from_classifier_tag_retains_transparent_match_context(self):
        plane = FakePlane("lt")
        plane.index = fallback_tree("lt")
        _, classifier = resolve(
            plane, [], "classifiers classifier-entry copy_tag_pbit0".split())
        _, tag = resolve(
            plane, classifier, "match-criteria tag 0".split())

        cli = ConfdCLI("lt", "admin")
        cli.plane = plane
        cli.config_mode = True
        cli.frames = [classifier, tag]
        cli.handle_config(["exit"], None, lambda _message: None, "exit")

        self.assertEqual(cli.ctx()[-1].name, "match-criteria")
        self.assertIn("config-classifier-entry-copy_tag_pbit0", cli.prompt())
        actions, _ = resolve(plane, cli.ctx(), "dscp-range any".split())
        self.assertEqual(actions[0][2].name, "dscp-range")
        actions, _ = resolve(plane, cli.ctx(), ["any-protocol"])
        self.assertEqual(actions[0][2].name, "any-protocol")


if __name__ == "__main__":
    unittest.main()
