import unittest

from light_olt.cli.confd_cli import ConfdCLI
from light_olt.cli.md_cli import MdCli


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


if __name__ == "__main__":
    unittest.main()
