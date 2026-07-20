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

    def test_confd_rendering_key_only_list_uses_key_as_argument(self):
        interface = ET.fromstring(
            "<interface><name>VSI_ONT-01_VEIP_HSI</name></interface>"
        )
        lines = []
        render_confd(interface, "", 0, lines)
        self.assertEqual(lines, ["interface VSI_ONT-01_VEIP_HSI", "!"])

    def test_confd_rendering_preserves_onu_template_root(self):
        onu = ET.fromstring(
            '<onu xmlns="urn:bbf:params:xml:ns:yang:bbf-fiber-onu-emulated-mount">'
            '<name>GENERIC-NOKIA</name>'
            '<usage>node-template-usage</usage>'
            '<root>'
            '<voip-configuration-characteristics '
            'xmlns="urn:bbf:yang:bbf-voip-configuration-mounted">'
            '<configuration-method>omci</configuration-method>'
            '</voip-configuration-characteristics>'
            '<hardware xmlns="urn:ietf:params:xml:ns:yang:ietf-hardware-mounted">'
            '<component><name>CHASSIS</name><admin-state>unlocked</admin-state>'
            '</component></hardware>'
            '</root></onu>'
        )
        lines = []
        render_confd(onu, "", 0, lines)
        rendered = "\n".join(lines)
        self.assertIn("onu GENERIC-NOKIA", rendered)
        self.assertIn("root", rendered)
        self.assertIn(
            "voip-configuration-characteristics configuration-method omci",
            rendered,
        )
        self.assertIn("hardware component CHASSIS", rendered)

    def test_overlay_replaces_leaf(self):
        base = ET.fromstring("<system><hostname>old</hostname></system>")
        edit = ET.fromstring("<system><hostname>new</hostname></system>")
        merge_overlay(base, edit)
        self.assertEqual(base.findtext("hostname"), "new")


if __name__ == "__main__":
    unittest.main()
