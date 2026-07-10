import unittest
import xml.etree.ElementTree as ET

from light_olt.cli.rendering import (
    merge_overlay,
    render_confd,
    strip_ns,
    xml_roots,
)


class RenderingTests(unittest.TestCase):
    def test_xml_roots_accepts_multiple_roots(self):
        roots = xml_roots("<system/><interfaces/>")
        self.assertEqual([strip_ns(root.tag) for root in roots], ["system", "interfaces"])

    def test_confd_rendering(self):
        root = ET.fromstring("<system><hostname>OLT-01</hostname><enabled>true</enabled></system>")
        lines = []
        render_confd(root, "", 0, lines)
        self.assertIn("system", lines)
        self.assertIn(" hostname OLT-01", lines)

    def test_overlay_replaces_leaf(self):
        base = ET.fromstring("<system><hostname>old</hostname></system>")
        edit = ET.fromstring("<system><hostname>new</hostname></system>")
        merge_overlay(base, edit)
        self.assertEqual(base.findtext("hostname"), "new")


if __name__ == "__main__":
    unittest.main()
