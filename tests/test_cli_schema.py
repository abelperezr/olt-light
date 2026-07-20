import unittest
import xml.etree.ElementTree as ET

from light_olt.cli.backend import fallback_tree
from light_olt.cli.schema import (
    PathSeg,
    ResolveError,
    lookup,
    resolve,
    schema_value_options,
)


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
                    "c": {
                        "enabled": {"k": "f", "t": "boolean"},
                        "channel-partition": {
                            "k": "c",
                            "c": {
                                "authentication-method": {
                                    "k": "f", "m": "bbf-xpon",
                                    "t": "enumeration",
                                },
                                "multicast-aes-indicator": {
                                    "k": "f", "t": "boolean",
                                },
                            },
                        },
                        "channel-termination": {
                            "k": "c", "m": "bbf-xpon",
                            "c": {
                                "channel-termination-type": {
                                    "k": "f", "m": "bbf-xpon",
                                    "t": "identityref",
                                },
                                "location": {
                                    "k": "f", "m": "bbf-xpon",
                                    "t": "identityref",
                                },
                            },
                        },
                        "multicast-cac": {
                            "k": "c",
                            "c": {
                                "max-group-number": {
                                    "k": "f", "m": "nokia-mcast-cac",
                                    "t": "bbf-mgmd:usage-limit",
                                },
                                "multicast-rate-limit-exceed-action": {
                                    "k": "f",
                                    "m": "nokia-mcast-cac",
                                    "t": "bbf-mgmd:rate-limit-action-enum",
                                },
                            },
                        },
                        "tm-root": {
                            "k": "c", "loose": 1,
                            "c": {"queue": {"k": "l", "keys": ["id"]}},
                        },
                    },
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

    def test_channel_partition_scheduler_hierarchy_is_resolvable(self):
        plane = type("Plane", (), {"index": fallback_tree("lt")})()
        commands = (
            "interfaces interface CPART tm-root scheduler-node ONT-01 "
            "scheduling-level 1 child-scheduler-nodes ONT-01_VEIP "
            "priority 0 weight 1",
            "interfaces interface CPART tm-root scheduler-node ONT-01_VEIP "
            "contains-queues true",
            "interfaces interface CPART tm-root scheduler-node ONT-01_VEIP "
            "queue local-queue-id 0 priority 0 weight 1",
            "interfaces interface CPART tm-root child-scheduler-nodes "
            "ONT-01 priority 0",
        )

        for command in commands:
            actions, _ = resolve(plane, [], command.split())
            self.assertTrue(actions, command)

        with self.assertRaises(ResolveError) as ctx:
            resolve(
                plane, [],
                "interfaces interface CPART tm-root scheduler-node "
                "ONT-01_VEIP queue".split(),
            )
        self.assertEqual(ctx.exception.options, ["local-queue-id"])

        with self.assertRaises(ResolveError) as abbreviated:
            resolve(
                plane, [],
                "interfaces interface CPART tm-root scheduler-node "
                "ONT-01_VEIP queue loc".split(),
            )
        self.assertEqual(str(abbreviated.exception), "incomplete command")

    def test_venet_and_template_parameter_paths_are_resolvable(self):
        plane = type("Plane", (), {"index": fallback_tree("lt")})()
        commands = (
            "interfaces interface VENET type olt-v-enet",
            "interfaces interface VENET egress-tm-objects root-if-name "
            "CPART scheduler-node-name ONT-01_VEIP",
            "interfaces interface VENET olt-v-enet lower-layer-interface "
            "ONT-01 protocol-identifier-helper slot-id 14 port-id 1",
            "onus onu ONT-01 template-parameters interfaces interface "
            "template-ref ANI",
            "onus onu ONT-01 template-parameters hardware-config hardware "
            "template-ref CHASSIS admin-state unlocked",
        )

        for command in commands:
            actions, _ = resolve(plane, [], command.split())
            self.assertTrue(actions, command)

        self.assertIn(
            "unlocked",
            schema_value_options(
                plane, [],
                "onus onu ONT-01 template-parameters hardware-config "
                "hardware template-ref CHASSIS admin-state".split(),
            ),
        )

    def test_frame_processing_reference_fallback_is_resolvable(self):
        plane = type("Plane", (), {"index": fallback_tree("lt")})()
        actions, _ = resolve(
            plane, [],
            "interfaces interface NTW_VSI_HSI "
            "frame-processing-profile-ref CC-SINGLE-VLAN-PROFILE "
            "tag-0 vlan-id 100".split(),
        )
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0][2].module,
                         "bbf-frame-processing-profile")

    def test_classifier_legacy_branch_is_resolvable_and_completable(self):
        plane = type("Plane", (), {"index": fallback_tree("lt")})()
        commands = (
            "classifiers classifier-entry pbit0_to_TC0 "
            "filter-operation match-all-filter",
            "classifiers classifier-entry pbit0_to_TC0 match-criteria "
            "pbit-marking-list 0 pbit-value 0",
            "classifiers classifier-entry pbit0_to_TC0 "
            "classifier-action-entry-cfg scheduling-traffic-class "
            "scheduling-traffic-class 0",
        )
        for command in commands:
            actions, _ = resolve(plane, [], command.split())
            self.assertTrue(actions, command)

        entry = (plane.index["classifiers"]["c"]["classifier-entry"])
        self.assertEqual(
            entry["c"]["match-criteria"]["c"]["pbit-marking-list"]["m"],
            "bbf-qos-policing",
        )
        self.assertIn(
            "match-all-filter",
            schema_value_options(
                plane, [],
                "classifiers classifier-entry pbit0_to_TC0 "
                "filter-operation".split(),
            ),
        )

    def test_leaf_list_completion_inside_brackets(self):
        plane = type("Plane", (), {"index": {
            "mac-can-not-move-to": {
                "k": "F", "m": "bbf-l2-forwarding",
                "t": "bbf-if-usg:interface-usage",
            },
        }})()
        self.assertIn(
            "subtended-node-port",
            schema_value_options(
                plane, [], ["mac-can-not-move-to", "["]
            ),
        )
        self.assertNotIn(
            "user-port",
            schema_value_options(
                plane, [], ["mac-can-not-move-to", "[", "user-port"]
            ),
        )

    def test_protocol_profile_leaf_lists_offer_open_and_close_brackets(self):
        cases = (
            ("bbf-l2-dhcpv4-relay", "suboptions", "circuit-id"),
            ("bbf-ldra", "option", "interface-id"),
            ("bbf-pppoe-intermediate-agent", "subtag", "remote-id"),
            ("bbf-xpon-acc-d6r", "xpon-access-loop-characteristics",
             "onu-peak-data-rate-downstream"),
        )
        for module, name, expected in cases:
            plane = type("Plane", (), {"index": {
                name: {"k": "F", "m": module, "t": "identityref"},
            }})()
            initial = schema_value_options(plane, [], [name])
            opened = schema_value_options(
                plane, [], [name, "[", expected])
            self.assertIn("[", initial)
            self.assertIn(expected, initial)
            self.assertIn("]", opened)

    def test_empty_interface_description_is_accepted(self):
        plane = type("Plane", (), {"index": fallback_tree("lt")})()
        actions, _ = resolve(
            plane, [], "interfaces interface VSI description".split())
        self.assertEqual(actions[0][3], "")

    def test_alloc_id_completion_returns_next_free_gpon_value(self):
        running = ET.fromstring(
            '<xpongemtcont><tconts><tcont><name>a</name>'
            '<alloc-id>256</alloc-id></tcont></tconts></xpongemtcont>')
        plane = type("Plane", (), {
            "index": {"xpongemtcont": {"k": "c", "c": {
                "tconts": {"k": "c", "c": {
                    "tcont": {"k": "l", "keys": ["name"], "c": {
                        "name": {"k": "f"},
                        "alloc-id": {"k": "f", "m": "bbf-xpongemtcont"},
                    }},
                }},
            }}},
            "export_xml_roots": lambda *_args: [running],
        })()
        values = schema_value_options(
            plane, [],
            "xpongemtcont tconts tcont TCONT alloc-id".split())
        self.assertEqual(values, ("257",))

    def test_boolean_rejects_abbreviated_value(self):
        with self.assertRaises(ResolveError) as ctx:
            resolve(
                FakePlane(), [],
                ["interfaces", "interface", "xpon0", "channel-partition",
                 "multicast-aes-indicator", "fa"],
            )
        self.assertEqual(ctx.exception.options, ["false", "true"])

    def test_curated_enum_completion_and_validation(self):
        base = PathSeg(
            "interface", "ietf-interfaces", {"name": "xpon0"},
            FakePlane.index["interfaces"]["c"]["interface"],
        )
        self.assertIn(
            "as-per-v-ani-expected",
            schema_value_options(
                FakePlane(), [base],
                ["channel-partition", "authentication-method"],
            ),
        )
        with self.assertRaises(ResolveError):
            resolve(
                FakePlane(), [base],
                ["channel-partition", "authentication-method", "as-per"],
            )

    def test_usage_limit_accepts_no_limit_or_integer_only(self):
        prefix = ["interfaces", "interface", "xpon0", "multicast-cac",
                  "max-group-number"]
        resolve(FakePlane(), [], prefix + ["no-limit"])
        resolve(FakePlane(), [], prefix + ["128"])
        with self.assertRaises(ResolveError):
            resolve(FakePlane(), [], prefix + ["no"])

    def test_known_loose_node_rejects_unknown_context(self):
        with self.assertRaises(ResolveError):
            resolve(
                FakePlane(), [],
                ["interfaces", "interface", "xpon0", "tm-root", "COMM"],
            )

    def test_channel_termination_identity_values(self):
        prefix = ["interfaces", "interface", "ct0", "channel-termination"]
        resolve(FakePlane(), [], prefix + ["channel-termination-type", "gpon"])
        resolve(FakePlane(), [], prefix + ["location", "inside-olt"])
        with self.assertRaises(ResolveError):
            resolve(FakePlane(), [], prefix + ["location", "inside"])


if __name__ == "__main__":
    unittest.main()
