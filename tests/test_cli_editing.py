import unittest
import xml.etree.ElementTree as ET
import os
import tempfile

from light_olt.cli.backend import FALLBACK_NS, schema_prefix_aliases
from light_olt.cli.editing import EditSession
from light_olt.cli.schema import PathSeg


class FakePlane:
    def ns_of(self, module):
        return FALLBACK_NS.get(module, "")


class EditingTests(unittest.TestCase):
    def test_commit_orders_profiles_before_interface_consumers(self):
        session = EditSession(FakePlane())
        session.add(("create", [PathSeg(
            "interfaces", "ietf-interfaces", None, {"k": "c"})]))
        session.add(("create", [PathSeg(
            "frame-processing-profiles", "bbf-frame-processing-profile",
            None, {"k": "c"})]))

        self.assertEqual(
            [module for module, _ in session.serialize()],
            ["bbf-frame-processing-profile", "ietf-interfaces"],
        )

    def test_commit_stops_after_first_failed_module(self):
        calls = []

        class Result:
            returncode = 1
            stderr = "validation failed"
            stdout = ""

        class Plane(FakePlane):
            def begin_local_commit(self):
                pass

            def end_local_commit(self):
                pass

            def apply_edit(self, _xml, module, datastore):
                calls.append((module, datastore))
                return Result()

        session = EditSession(Plane())
        session.add(("create", [PathSeg(
            "interfaces", "ietf-interfaces", None, {"k": "c"})]))
        session.add(("create", [PathSeg(
            "frame-processing-profiles", "bbf-frame-processing-profile",
            None, {"k": "c"})]))

        self.assertTrue(session.commit())
        self.assertEqual(calls, [("bbf-frame-processing-profile", "running")])

    def test_schema_prefix_aliases_use_module_namespace(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "example-module.yang")
            with open(path, "w", encoding="utf-8") as yang:
                yang.write(
                    "module example-module {\n"
                    "  namespace \"urn:example\";\n"
                    "  prefix ex;\n"
                    "}\n"
                )
            self.assertEqual(
                schema_prefix_aliases(
                    directory, {"example-module": "urn:example"},
                ),
                {"ex": "urn:example"},
            )

    def test_channel_pair_uses_augment_and_identity_namespaces(self):
        interface = PathSeg(
            "interfaces", "ietf-interfaces", None, {},
        )
        entry = PathSeg(
            "interface", "ietf-interfaces", {"name": "PON1_CPAIR_GPON"}, {},
        )
        multicast = PathSeg(
            "multicast-cac", "nokia-mcast-cac", None, {},
        )
        max_groups = PathSeg(
            "max-group-number", "nokia-mcast-cac", None, {"t": "union"},
        )
        channel_pair = PathSeg("channel-pair", "bbf-xpon", None, {})
        pair_type = PathSeg(
            "channel-pair-type", "bbf-xpon", None, {"t": "identityref"},
        )

        session = EditSession(FakePlane())
        session.add(("set", [interface, entry, multicast], max_groups,
                     "no-limit"))
        session.add(("set", [interface, entry, channel_pair], pair_type,
                     "gpon"))
        _, xml = session.serialize()[0]
        root = ET.fromstring(xml)

        multicast_ns = ("{uri:http://www.nokia.com/Fixed-Networks/BBA/yang/"
                        "nokia-multicast-cac}")
        self.assertIsNotNone(root.find(".//" + multicast_ns + "multicast-cac"))
        pair = root.find(".//{urn:bbf:yang:bbf-xpon}channel-pair-type")
        self.assertIsNotNone(pair)
        self.assertTrue(pair.text.endswith(":gpon"), xml)

    def test_channel_termination_identity_and_port_namespaces(self):
        interfaces = PathSeg("interfaces", "ietf-interfaces", None, {})
        entry = PathSeg(
            "interface", "ietf-interfaces", {"name": "CT_PON1_1_GPON"}, {},
        )
        termination = PathSeg("channel-termination", "bbf-xpon", None, {})
        term_type = PathSeg(
            "channel-termination-type", "bbf-xpon", None,
            {"t": "identityref"},
        )
        location = PathSeg(
            "location", "bbf-xpon", None, {"t": "identityref"},
        )
        port = PathSeg(
            "port-layer-if", "bbf-if-port-ref", None, {"t": "leaf-list"},
        )

        session = EditSession(FakePlane())
        session.add(("set", [interfaces, entry, termination], term_type,
                     "gpon"))
        session.add(("set", [interfaces, entry, termination], location,
                     "inside-olt"))
        session.add(("set", [interfaces, entry], port, ["PON_1_GPON"]))
        _, xml = session.serialize()[0]
        root = ET.fromstring(xml)

        term = root.find(
            ".//{urn:bbf:yang:bbf-xpon}channel-termination-type",
        )
        place = root.find(".//{urn:bbf:yang:bbf-xpon}location")
        port_ref = root.find(
            ".//{urn:bbf:yang:bbf-interface-port-reference}port-layer-if",
        )
        self.assertTrue(term.text.endswith(":gpon"), xml)
        self.assertTrue(place.text.endswith(":inside-olt"), xml)
        self.assertEqual(port_ref.text, "PON_1_GPON")

    def test_onu_usage_uses_template_common_namespace(self):
        session = EditSession(FakePlane())
        value = session._identity_value(
            "bbf-fiber-onu-emulated-mount", "usage",
            {"t": "identityref"}, "node-template-usage",
        )

        prefix, identity = value.split(":", 1)
        self.assertEqual(identity, "node-template-usage")
        self.assertEqual(
            next(ns for ns, pfx in session.idns.items() if pfx == prefix),
            ("http://www.nokia.com/Fixed-Networks/BBA/yang/"
             "nokia-template-common"),
        )

    def test_frame_processing_tag_type_union_is_namespace_qualified(self):
        profile = PathSeg(
            "frame-processing-profile", "bbf-frame-processing-profile",
            {"name": "SINGLE"}, {"k": "l", "keys": ["name"]},
        )
        tag_type = PathSeg(
            "tag-type", "bbf-frame-processing-profile", None,
            {"k": "f", "t": "union"},
        )
        session = EditSession(FakePlane())
        session.add(("set", [profile], tag_type, "c-vlan"))

        _, xml = session.serialize()[0]
        self.assertIn("urn:bbf:yang:bbf-dot1q-types", xml)
        self.assertRegex(xml, r">id\d+:c-vlan<")

    def test_dhcpv6_xpon_characteristic_identity_namespace(self):
        profile = PathSeg(
            "dhcpv6-ldra-profile", "bbf-ldra", {"name": "DHCPv6"},
            {"k": "l", "keys": ["name"]},
        )
        options = PathSeg("options", "bbf-ldra", None, {"k": "c"})
        characteristic = PathSeg(
            "xpon-access-loop-characteristics", "bbf-xpon-acc-d6r", None,
            {"k": "F", "t": "identityref"},
        )
        session = EditSession(FakePlane())
        session.add(("set", [profile, options], characteristic,
                     ["xpon-tree-maximum-data-rate-upstream"]))

        _, xml = session.serialize()[0]
        self.assertIn(
            "urn:bbf:yang:bbf-xpon-access-line-characteristics-type", xml)
        self.assertRegex(
            xml, r">id\d+:xpon-tree-maximum-data-rate-upstream<")


if __name__ == "__main__":
    unittest.main()
