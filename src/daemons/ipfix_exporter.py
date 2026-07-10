#!/usr/bin/env python3
"""
Synthetic Nokia Lightspan IPFIX exporter for the OLT emulator.

The emulator already accepts the IPFIX YANG configuration in sysrepo. This
daemon turns that management-plane configuration into data-plane behavior:
it reads the LT IPFIX config, connects to the configured tcpExporter
destination, sends the Nokia auth/cache-name templates, then periodically
exports synthetic telemetry records that match the Pazel collector mappings.

Architecture
------------
- Reads ietf-ipfix-psamp from sysrepo (running) to discover enabled caches
  and exportingProcess (host/port/user/pass).
- Sends RFC 7011 IPFIX over TCP: template sets (data + options), auth
  (hostname/user/pass), cache-name options, and periodic data records.
- Record layouts (LAYOUTS dict) are hardcoded to match the Pazel/ClickHouse
  schema: disk-utilisation, mem-utilisation, cpu-usage, xpon-hardware-state,
  xpon-interfaces-state, statistics (capacity, channel-termination, venet, vsi),
  eonu-interfaces-state.
- Inventory (PONs + authenticated ONUs) is built from ietf-interfaces +
  bbf-fiber-onu-emulated-mount, with optional seed fallback
  (/seeds/onts_oper.xml). Only authenticated ONUs (admin-unlocked/online) are
  included, controlled by IPFIX_EMU_REQUIRE_AUTH (default 1).
- Synthetic values use deterministic per-component/ONU counters with
  sinusoidal jitter (seeded by IPFIX_EMU_RANDOM_SEED) so collectors see
  realistic movement without randomness between restarts.

Configuration (environment)
---------------------------
- IPFIX_EMU_ENABLED=1              master switch
- IPFIX_EMU_INTERVAL_SECS=15       export interval
- IPFIX_EMU_RETRY_SECS=5           reconnect retry
- IPFIX_EMU_DOMAIN_ID=4355         observation domain ID
- IPFIX_EMU_MAX_ONUS=0             cap ONUs (0 = all)
- IPFIX_EMU_MAX_PONS=0             cap PONs (0 = all)
- IPFIX_EMU_INVENTORY_REFRESH_SECS=30  inventory re-read
- IPFIX_EMU_ONTS_OPER=/seeds/onts_oper.xml  seed fallback path
- IPFIX_EMU_SEED_FALLBACK=1        use seed if no configured ONUs
- IPFIX_EMU_RANDOM_SEED=20260614   deterministic RNG seed
- IPFIX_EMU_REQUIRE_AUTH=1         gate ONUs by authentication state
- IPFIX_EMU_ONESHOT=0              single export cycle then exit
- IPFIX_EMU_TARGET_HOST / PORT     override exporter destination
- IPFIX_EMU_USERNAME / PASSWORD    default auth credentials
- IPFIX_EMU_HOSTNAME               override system hostname in auth

Supported caches (name -> template ID)
--------------------------------------
disk-utilisation (260), eonu-interfaces-state (262), mem-utilisation (263),
xpon-hardware-state (266), xpon-hardware-state-sensor (267),
xpon-hardware-state-transceiver (270), xpon-hardware-state-transceiver-link (271),
xpon-interfaces-state (272), capacity (275), channel-termination (276),
venet (279), vsi (280), cpu-usage (281).

Output
------
Structured logs with timestamps: connection, template send, per-cache record
counts, cycle summary. Errors log and retry (keeps supervisor alive).
"""

from __future__ import annotations

import math
import os
import random
import socket
import struct
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


NOKIA_PEN = 3729
IPFIX_VERSION = 10
TEMPLATE_SET_ID = 2
OPTIONS_TEMPLATE_SET_ID = 3
AUTH_TEMPLATE_ID = 256
CACHE_NAME_TEMPLATE_ID = 257
IE_META_TEMPLATE_ID = 258
VARLEN = 0xFFFF
MAX_IPFIX_MESSAGE = 65535
SET_OVERHEAD = 4
MESSAGE_OVERHEAD = 16


@dataclass(frozen=True)
class FieldDef:
    ie_id: int
    length: int
    kind: str
    pen: int = NOKIA_PEN


@dataclass(frozen=True)
class Layout:
    name: str
    template_id: int
    fields: tuple[FieldDef, ...]
    row_builder: str


@dataclass(frozen=True)
class ExportProcess:
    name: str
    host: str
    port: int
    username: str
    password: str


@dataclass(frozen=True)
class IpfixConfig:
    enabled: bool
    process: ExportProcess | None
    active_caches: tuple[str, ...]
    unsupported_caches: tuple[str, ...]
    hostname: str

    def signature(self) -> tuple:
        proc = None
        if self.process:
            proc = (
                self.process.name,
                self.process.host,
                self.process.port,
                self.process.username,
                self.process.password,
            )
        return (self.enabled, proc, self.active_caches, self.hostname)


@dataclass(frozen=True)
class Onu:
    name: str
    interface: str
    pon: str
    serial: str = ""


@dataclass(frozen=True)
class Inventory:
    pons: tuple[str, ...]
    onus: tuple[Onu, ...]


def fd(ie_id: int, length: int, kind: str) -> FieldDef:
    return FieldDef(ie_id, length, kind)


def std_fd(ie_id: int, length: int, kind: str) -> FieldDef:
    return FieldDef(ie_id, length, kind, 0)


LAYOUTS: dict[str, Layout] = {
    "disk-utilisation": Layout(
        "disk-utilisation",
        260,
        (
            fd(505, VARLEN, "str"),
            fd(284, VARLEN, "str"),
            fd(142, VARLEN, "str"),
            fd(285, VARLEN, "str"),
            fd(192, 8, "u64"),
            fd(193, 8, "u64"),
        ),
        "disk",
    ),
    "eonu-interfaces-state": Layout(
        "eonu-interfaces-state",
        262,
        (
            fd(505, VARLEN, "str"),
            fd(284, VARLEN, "str"),
            fd(15001, VARLEN, "str"),
            fd(15121, VARLEN, "str"),
            fd(15122, VARLEN, "str"),
            fd(15123, 4, "u32"),
            fd(15124, 4, "u32"),
            fd(15125, VARLEN, "str"),
        ),
        "eonu_interfaces",
    ),
    "mem-utilisation": Layout(
        "mem-utilisation",
        263,
        (
            fd(505, VARLEN, "str"),
            fd(284, VARLEN, "str"),
            fd(142, VARLEN, "str"),
            fd(340, 8, "u64"),
            fd(339, 8, "u64"),
            fd(338, 8, "u64"),
        ),
        "memory",
    ),
    "xpon-hardware-state": Layout(
        "xpon-hardware-state",
        266,
        (
            fd(505, VARLEN, "str"),
            fd(284, VARLEN, "str"),
            fd(142, VARLEN, "str"),
            fd(161, 4, "u32"),
            fd(162, 4, "u32"),
            fd(500, VARLEN, "str"),
        ),
        "hardware_state",
    ),
    "xpon-hardware-state-sensor": Layout(
        "xpon-hardware-state-sensor",
        267,
        (
            fd(505, VARLEN, "str"),
            fd(284, VARLEN, "str"),
            fd(142, VARLEN, "str"),
            fd(163, 4, "u32"),
        ),
        "sensor",
    ),
    "xpon-hardware-state-transceiver": Layout(
        "xpon-hardware-state-transceiver",
        270,
        (
            fd(505, VARLEN, "str"),
            fd(284, VARLEN, "str"),
            fd(142, VARLEN, "str"),
            fd(39, 4, "u32"),
            fd(38, 4, "u32"),
        ),
        "transceiver",
    ),
    "xpon-hardware-state-transceiver-link": Layout(
        "xpon-hardware-state-transceiver-link",
        271,
        (
            fd(505, VARLEN, "str"),
            fd(284, VARLEN, "str"),
            fd(142, VARLEN, "str"),
            fd(60, 4, "u32"),
            fd(194, 2, "u16"),
            fd(195, 2, "i16"),
        ),
        "transceiver_link",
    ),
    "xpon-interfaces-state": Layout(
        "xpon-interfaces-state",
        272,
        (
            fd(505, VARLEN, "str"),
            fd(284, VARLEN, "str"),
            fd(165, VARLEN, "str"),
            fd(167, 4, "u32"),
            fd(168, 4, "u32"),
            fd(169, VARLEN, "str"),
        ),
        "xpon_interfaces",
    ),
    "xpon-interfaces-state-statistics-capacity": Layout(
        "xpon-interfaces-state-statistics-capacity",
        275,
        (
            fd(505, VARLEN, "str"),
            fd(284, VARLEN, "str"),
            fd(165, VARLEN, "str"),
            fd(15133, 8, "u64"),
            fd(15134, 8, "u64"),
        ),
        "capacity",
    ),
    "xpon-interfaces-state-statistics-channel-termination": Layout(
        "xpon-interfaces-state-statistics-channel-termination",
        276,
        (
            fd(505, VARLEN, "str"),
            fd(284, VARLEN, "str"),
            fd(165, VARLEN, "str"),
            fd(176, 8, "u64"),
            fd(183, 8, "u64"),
            fd(180, 4, "u32"),
            fd(187, 4, "u32"),
            fd(514, 8, "u64"),
            fd(515, 8, "u64"),
            fd(82, 8, "u64"),
            fd(83, 8, "u64"),
        ),
        "traffic",
    ),
    "xpon-interfaces-state-statistics-venet": Layout(
        "xpon-interfaces-state-statistics-venet",
        279,
        (
            fd(505, VARLEN, "str"),
            fd(284, VARLEN, "str"),
            fd(165, VARLEN, "str"),
            fd(176, 8, "u64"),
            fd(183, 8, "u64"),
            fd(180, 4, "u32"),
            fd(187, 4, "u32"),
            fd(514, 8, "u64"),
            fd(515, 8, "u64"),
            fd(82, 8, "u64"),
            fd(83, 8, "u64"),
        ),
        "traffic",
    ),
    "xpon-interfaces-state-statistics-vsi": Layout(
        "xpon-interfaces-state-statistics-vsi",
        280,
        (
            fd(505, VARLEN, "str"),
            fd(284, VARLEN, "str"),
            fd(165, VARLEN, "str"),
            fd(176, 8, "u64"),
            fd(183, 8, "u64"),
            fd(180, 4, "u32"),
            fd(187, 4, "u32"),
            fd(514, 8, "u64"),
            fd(515, 8, "u64"),
            fd(82, 8, "u64"),
            fd(83, 8, "u64"),
        ),
        "traffic",
    ),
    "cpu-usage": Layout(
        "cpu-usage",
        281,
        (
            fd(505, VARLEN, "str"),
            fd(284, VARLEN, "str"),
            fd(142, VARLEN, "str"),
            fd(331, 1, "u8"),
            fd(332, 1, "u8"),
            fd(333, 1, "u8"),
        ),
        "cpu",
    ),
}


def log(message: str) -> None:
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(f"{stamp} {message}", flush=True)


def env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        log(f"invalid integer for {name}={raw!r}; using {default}")
        return default


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(elem: ET.Element | None) -> str:
    if elem is None or elem.text is None:
        return ""
    return elem.text.strip()


def direct_child(elem: ET.Element, name: str) -> ET.Element | None:
    for child in list(elem):
        if local_name(child.tag) == name:
            return child
    return None


def direct_text(elem: ET.Element, name: str) -> str:
    return text_of(direct_child(elem, name))


def descendant_text(elem: ET.Element, name: str) -> str:
    for child in elem.iter():
        if child is elem:
            continue
        if local_name(child.tag) == name:
            return text_of(child)
    return ""


def all_descendant_texts(elem: ET.Element, name: str) -> list[str]:
    return [text_of(child) for child in elem.iter() if child is not elem and local_name(child.tag) == name]


def is_direct_list_item(elem: ET.Element, name: str) -> bool:
    return local_name(elem.tag) == name


def run_sysrepocfg(module: str, timeout: int = 25) -> bytes | None:
    env = os.environ.copy()
    env.setdefault("SYSREPO_REPOSITORY_PATH", "/repo/lt")
    env.setdefault("SYSREPO_SHM_PREFIX", "lt_")
    try:
        return subprocess.check_output(
            ["sysrepocfg", "-X", "-d", "running", "-m", module],
            env=env,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
        log(f"could not read sysrepo module {module}: {exc}")
        return None


def read_system_hostname() -> str:
    override = os.environ.get("IPFIX_EMU_HOSTNAME")
    if override:
        return override.strip()

    data = run_sysrepocfg("ietf-system", timeout=10)
    if data:
        try:
            root = ET.fromstring(data)
            hostname = descendant_text(root, "hostname")
            if hostname:
                return hostname
        except ET.ParseError:
            pass

    try:
        host = socket.gethostname().strip()
        if host:
            return host
    except OSError:
        pass
    return "isam-reborn"


def parse_export_process(root: ET.Element, wanted: str) -> ExportProcess | None:
    candidates: list[ExportProcess] = []
    for elem in list(root):
        if local_name(elem.tag) != "exportingProcess":
            continue
        name = direct_text(elem, "name")
        if not name:
            continue

        host = descendant_text(elem, "destinationIPAddress")
        port_raw = descendant_text(elem, "destinationPort")
        user = descendant_text(elem, "username") or os.environ.get("IPFIX_EMU_USERNAME", "labtest")
        password = descendant_text(elem, "password") or os.environ.get("IPFIX_EMU_PASSWORD", "fyco123")
        try:
            port = int(port_raw) if port_raw else 30494
        except ValueError:
            port = 30494
        candidates.append(ExportProcess(name, host, port, user, password))

    selected = next((p for p in candidates if p.name == wanted), None)
    if selected is None and candidates:
        selected = candidates[0]
    if selected is None:
        return None

    host_override = os.environ.get("IPFIX_EMU_TARGET_HOST")
    port_override = os.environ.get("IPFIX_EMU_TARGET_PORT")
    host = host_override.strip() if host_override else selected.host
    port = selected.port
    if port_override:
        try:
            port = int(port_override)
        except ValueError:
            log(f"invalid IPFIX_EMU_TARGET_PORT={port_override!r}; using {port}")
    if not host:
        host = "192.168.9.10"
    return ExportProcess(selected.name, host, port, selected.username, selected.password)


def read_ipfix_config() -> IpfixConfig | None:
    data = run_sysrepocfg("ietf-ipfix-psamp")
    if not data:
        return None

    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        log(f"could not parse ietf-ipfix-psamp XML: {exc}")
        return None

    explicit_enable = None
    for child in list(root):
        if local_name(child.tag) == "ipfix-exporting-enable":
            explicit_enable = text_of(child).lower() == "true"
            break

    caches: list[tuple[str, str]] = []
    unsupported: list[str] = []
    wanted_process = ""
    for cache in list(root):
        if local_name(cache.tag) != "cache":
            continue
        name = direct_text(cache, "name")
        if not name:
            continue
        reporting = direct_text(cache, "reporting-enable").lower() == "true"
        if not reporting:
            continue

        process_refs = [
            text_of(child)
            for child in list(cache)
            if local_name(child.tag) == "exportingProcess" and len(list(child)) == 0
        ]
        process_ref = process_refs[0] if process_refs else ""
        if process_ref and not wanted_process:
            wanted_process = process_ref

        if name in LAYOUTS:
            caches.append((name, process_ref))
        else:
            unsupported.append(name)

    enabled = explicit_enable if explicit_enable is not None else bool(caches)
    process = parse_export_process(root, wanted_process) if enabled else None
    host_name = read_system_hostname()
    active = tuple(name for name, _ in caches)
    return IpfixConfig(enabled, process, active, tuple(unsupported), host_name)


def var_bytes(value: str | bytes) -> bytes:
    data = value if isinstance(value, bytes) else str(value).encode("utf-8")
    n = len(data)
    if n < 255:
        return struct.pack("!B", n) + data
    if n > 65535:
        raise ValueError("IPFIX variable-length field too large")
    return b"\xff" + struct.pack("!H", n) + data


def encode_field(field: FieldDef, value: object) -> bytes:
    if field.kind == "str":
        return var_bytes("" if value is None else str(value))
    if field.kind == "u8":
        return struct.pack("!B", int(value) & 0xFF)
    if field.kind == "u16":
        return struct.pack("!H", int(value) & 0xFFFF)
    if field.kind == "i16":
        return struct.pack("!h", int(value))
    if field.kind == "u32":
        return struct.pack("!I", int(value) & 0xFFFFFFFF)
    if field.kind == "u64":
        return struct.pack("!Q", int(value) & 0xFFFFFFFFFFFFFFFF)
    raise ValueError(f"unknown field kind {field.kind}")


def field_spec(ie_id: int, length: int, pen: int = NOKIA_PEN) -> bytes:
    if pen:
        return struct.pack("!HHI", ie_id | 0x8000, length, pen)
    return struct.pack("!HH", ie_id, length)


def template_record(layout: Layout) -> bytes:
    payload = struct.pack("!HH", layout.template_id, len(layout.fields))
    for field in layout.fields:
        payload += field_spec(field.ie_id, field.length, field.pen)
    return payload


def options_template_record(template_id: int, fields: Iterable[FieldDef], scope_count: int) -> bytes:
    fields = tuple(fields)
    payload = struct.pack("!HHH", template_id, len(fields), scope_count)
    for field in fields:
        payload += field_spec(field.ie_id, field.length, field.pen)
    return payload


def pack_set(set_id: int, payload: bytes) -> bytes:
    total = SET_OVERHEAD + len(payload)
    if total > MAX_IPFIX_MESSAGE:
        raise ValueError(f"IPFIX set {set_id} too large: {total}")
    return struct.pack("!HH", set_id, total) + payload


def pack_message(sets: Iterable[bytes], sequence: int, domain_id: int) -> bytes:
    body = b"".join(sets)
    total = MESSAGE_OVERHEAD + len(body)
    if total > MAX_IPFIX_MESSAGE:
        raise ValueError(f"IPFIX message too large: {total}")
    header = struct.pack("!HHIII", IPFIX_VERSION, total, int(time.time()), sequence, domain_id)
    return header + body


def encode_record(layout: Layout, values: Iterable[object]) -> bytes:
    values = tuple(values)
    if len(values) != len(layout.fields):
        raise ValueError(f"{layout.name}: expected {len(layout.fields)} values, got {len(values)}")
    return b"".join(encode_field(field, value) for field, value in zip(layout.fields, values))


def chunk_records(layout: Layout, rows: Iterable[tuple[object, ...]]) -> Iterable[bytes]:
    max_payload = MAX_IPFIX_MESSAGE - MESSAGE_OVERHEAD - SET_OVERHEAD - 256
    payload = bytearray()
    for row in rows:
        record = encode_record(layout, row)
        if payload and len(payload) + len(record) > max_payload:
            yield bytes(payload)
            payload = bytearray()
        if len(record) > max_payload:
            raise ValueError(f"{layout.name}: single record too large")
        payload.extend(record)
    if payload:
        yield bytes(payload)


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def interface_type(elem: ET.Element) -> str:
    return direct_text(elem, "type").split(":", 1)[-1]


def parse_seed_inventory(path: Path) -> Inventory:
    if not path.exists():
        pons = tuple(f"CT_LT1-PON{i}_{i}_GPON" for i in range(1, 3))
        onus = tuple(
            Onu(f"ALCL{i:08X}", "ANI", pons[(i - 1) % len(pons)], f"ALCL{i:08X}")
            for i in range(1, 17)
        )
        return Inventory(pons, onus)

    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        log(f"could not parse {path}: {exc}; using fallback inventory")
        return parse_seed_inventory(Path("/missing-onts-oper.xml"))

    pons: list[str] = []
    onus: list[Onu] = []
    seen_serials: set[str] = set()
    for iface in root.iter():
        if local_name(iface.tag) != "interface":
            continue
        pon = direct_text(iface, "name")
        if not pon:
            continue
        pons.append(pon)
        for serial in all_descendant_texts(iface, "detected-serial-number"):
            serial = serial.strip()
            if not serial or serial in seen_serials:
                continue
            seen_serials.add(serial)
            onus.append(Onu(serial, "ANI", pon, serial))

    if not pons:
        pons = ["CT_LT1-PON1_1_GPON", "CT_LT1-PON2_2_GPON"]
    if not onus:
        onus = [Onu(f"ALCL{i:08X}", "ANI", pons[(i - 1) % len(pons)], f"ALCL{i:08X}") for i in range(1, 17)]
    return Inventory(tuple(dict.fromkeys(pons)), tuple(onus))


def parse_interface_inventory(root: ET.Element) -> tuple[list[str], dict[str, Onu], dict[str, str]]:
    cpair_to_ct: dict[str, str] = {}
    cpart_to_cpair: dict[str, str] = {}
    cpart_to_ct: dict[str, str] = {}
    pons: list[str] = []
    vani_onus: dict[str, Onu] = {}

    interfaces = [elem for elem in list(root) if local_name(elem.tag) == "interface"]
    for iface in interfaces:
        name = direct_text(iface, "name")
        if not name:
            continue
        typ = interface_type(iface)
        if typ == "channel-termination":
            pons.append(name)
            cpair = descendant_text(iface, "channel-pair-ref")
            if cpair:
                cpair_to_ct[cpair] = name
        elif typ == "channel-pair":
            cpart = descendant_text(iface, "channel-partition-ref")
            if cpart:
                cpart_to_cpair[cpart] = name

    for cpart, cpair in cpart_to_cpair.items():
        if cpair in cpair_to_ct:
            cpart_to_ct[cpart] = cpair_to_ct[cpair]

    for iface in interfaces:
        if interface_type(iface) != "v-ani":
            continue
        if_name = direct_text(iface, "name")
        serial = descendant_text(iface, "expected-serial-number").upper()
        onu_name = descendant_text(iface, "onu-name") or if_name or serial
        cpart = descendant_text(iface, "channel-partition")
        pon = cpart_to_ct.get(cpart) or cpart or (pons[0] if pons else "LT1_PON1")
        if not onu_name:
            continue
        key = serial or onu_name
        vani_onus[key] = Onu(onu_name, "ANI", pon, serial)

    return pons, vani_onus, cpart_to_ct


def parse_configured_inventory() -> Inventory:
    pons: list[str] = []
    configured: dict[str, Onu] = {}
    cpart_to_ct: dict[str, str] = {}

    if_data = run_sysrepocfg("ietf-interfaces", timeout=30)
    if if_data:
        try:
            if_root = ET.fromstring(if_data)
            pons, configured, cpart_to_ct = parse_interface_inventory(if_root)
        except ET.ParseError as exc:
            log(f"could not parse ietf-interfaces XML for inventory: {exc}")

    onu_data = run_sysrepocfg("bbf-fiber-onu-emulated-mount", timeout=30)
    if onu_data:
        try:
            root = ET.fromstring(onu_data)
            for onu in list(root):
                if local_name(onu.tag) != "onu":
                    continue
                name = direct_text(onu, "name")
                if not name:
                    continue
                usage = direct_text(onu, "usage").split(":", 1)[-1]
                if usage == "node-template-usage":
                    continue
                if name in configured:
                    continue
                cpart = descendant_text(onu, "channel-partition")
                pon = cpart_to_ct.get(cpart) or cpart or (pons[0] if pons else "LT1_PON1")
                configured[name] = Onu(name, "ANI", pon, "")
        except ET.ParseError as exc:
            log(f"could not parse bbf-fiber-onu-emulated-mount XML for inventory: {exc}")

    return Inventory(tuple(dict.fromkeys(pons)), tuple(configured.values()))


def merge_inventory(configured: Inventory, max_onus: int, max_pons: int) -> Inventory:
    if not configured.onus:
        return Inventory(tuple(), tuple())

    pons = list(dict.fromkeys(configured.pons))
    if max_pons > 0:
        pons = pons[:max_pons]
    allowed_pons = set(pons)

    merged: list[Onu] = []
    seen: set[str] = set()

    def add(onu: Onu) -> None:
        if allowed_pons and onu.pon not in allowed_pons:
            return
        keys = [k for k in (onu.serial.upper(), onu.name, f"{onu.pon}:{onu.name}") if k]
        if any(k in seen for k in keys):
            return
        merged.append(onu)
        seen.update(keys)

    for onu in configured.onus:
        add(onu)

    if max_onus > 0:
        merged = merged[:max_onus]

    return Inventory(tuple(pons), tuple(merged))


class InventoryCache:
    def __init__(self, path: str, max_onus: int, max_pons: int, refresh_secs: int) -> None:
        self.path = Path(path)
        self.max_onus = max_onus
        self.max_pons = max_pons
        self.refresh_secs = refresh_secs
        self._mtime: float | None = None
        self._last_load = 0.0
        self._inventory: Inventory | None = None

    def get(self) -> Inventory:
        now = time.monotonic()
        try:
            mtime = self.path.stat().st_mtime
        except OSError:
            mtime = None
        stale = self.refresh_secs > 0 and now - self._last_load >= self.refresh_secs
        if self._inventory is None or mtime != self._mtime or stale:
            configured = parse_configured_inventory()
            source = "configured"
            if not configured.onus and env_bool("IPFIX_EMU_SEED_FALLBACK", True):
                configured = parse_seed_inventory(self.path)
                source = "seed-fallback"
            self._inventory = merge_inventory(configured, self.max_onus, self.max_pons)
            self._mtime = mtime
            self._last_load = now
            log(
                "inventory loaded: "
                f"{len(self._inventory.pons)} PONs, {len(self._inventory.onus)} ONUs "
                f"(source={source}, raw={len(configured.onus)})"
            )
        return self._inventory


class SyntheticModel:
    def __init__(self, inventory_cache: InventoryCache) -> None:
        self.inventory_cache = inventory_cache
        self.rng = random.Random(env_int("IPFIX_EMU_RANDOM_SEED", 20260614))
        self.tick = 0
        self.counters: dict[str, int] = {}

    def rows_for(self, layout: Layout) -> Iterable[tuple[object, ...]]:
        builder: Callable[[Layout], Iterable[tuple[object, ...]]] = getattr(self, f"rows_{layout.row_builder}")
        return builder(layout)

    def advance(self) -> None:
        self.tick += 1

    def inventory(self) -> Inventory:
        return self.inventory_cache.get()

    def pon_component(self, pon: str) -> str:
        return f"{pon}/XCVR"

    def base_rows_components(self) -> list[str]:
        inv = self.inventory()
        comps = ["NT-A", "LT1"]
        comps.extend(self.pon_component(pon) for pon in inv.pons)
        return comps

    def bump(self, key: str, base: int, span: int) -> int:
        old = self.counters.get(key, base)
        inc = max(1, int(span * (0.60 + self.rng.random() * 0.80)))
        new = old + inc
        self.counters[key] = new
        return new

    def rows_disk(self, layout: Layout) -> Iterable[tuple[object, ...]]:
        ts = iso_now()
        size_root = 16 * 1024**3
        size_db = 64 * 1024**3
        free_root = int(9 * 1024**3 + math.sin(self.tick / 6.0) * 256 * 1024**2)
        free_db = int(41 * 1024**3 + math.cos(self.tick / 7.0) * 512 * 1024**2)
        yield ("", ts, "NT-A", "rootfs", size_root, free_root)
        yield ("", ts, "NT-A", "database", size_db, free_db)

    def rows_memory(self, layout: Layout) -> Iterable[tuple[object, ...]]:
        ts = iso_now()
        total = 8 * 1024**3
        used = int(3.2 * 1024**3 + math.sin(self.tick / 5.0) * 256 * 1024**2)
        free = max(0, total - used)
        yield ("", ts, "NT-A", free, total, used)
        yield ("", ts, "LT1", free // 2, total // 2, used // 2)

    def rows_cpu(self, layout: Layout) -> Iterable[tuple[object, ...]]:
        ts = iso_now()
        for idx, comp in enumerate(("NT-A", "LT1")):
            user = 8 + idx * 3 + int(5 * (1 + math.sin((self.tick + idx) / 4.0)))
            system = 4 + idx * 2 + int(3 * (1 + math.cos((self.tick + idx) / 5.0)))
            idle = max(0, 100 - user - system)
            yield ("", ts, comp, idle, user, system)

    def rows_hardware_state(self, layout: Layout) -> Iterable[tuple[object, ...]]:
        ts = iso_now()
        changed = "2026-06-10T16:45:26Z"
        for comp in self.base_rows_components():
            yield ("", ts, comp, 1, 1, changed)

    def rows_sensor(self, layout: Layout) -> Iterable[tuple[object, ...]]:
        ts = iso_now()
        for idx, pon in enumerate(self.inventory().pons):
            value = 34 + idx % 4 + int(4 * (1 + math.sin((self.tick + idx) / 8.0)))
            yield ("", ts, f"{pon}/TEMP-SENSOR", value)

    def rows_transceiver(self, layout: Layout) -> Iterable[tuple[object, ...]]:
        ts = iso_now()
        for idx, pon in enumerate(self.inventory().pons):
            voltage_mv = 3290 + (idx % 5) * 7 + int(8 * math.sin((self.tick + idx) / 5.0))
            temp_centideg = 4150 + (idx % 6) * 90 + int(120 * math.sin((self.tick + idx) / 6.0))
            yield ("", ts, self.pon_component(pon), voltage_mv, temp_centideg)

    def rows_transceiver_link(self, layout: Layout) -> Iterable[tuple[object, ...]]:
        ts = iso_now()
        for idx, pon in enumerate(self.inventory().pons):
            tx_bias_micro_ma = 6100 + (idx % 4) * 180 + int(120 * math.sin((self.tick + idx) / 3.0))
            tx_power_tenth_dbm = 27 + (idx % 3)
            rx_power_tenth_dbm = -205 + (idx % 8) + int(5 * math.sin((self.tick + idx) / 4.0))
            yield ("", ts, self.pon_component(pon), tx_bias_micro_ma, tx_power_tenth_dbm, rx_power_tenth_dbm)

    def rows_xpon_interfaces(self, layout: Layout) -> Iterable[tuple[object, ...]]:
        ts = iso_now()
        changed = "2026-06-10T16:45:26Z"
        for pon in self.inventory().pons:
            yield ("", ts, pon, 1, 1, changed)

    def rows_capacity(self, layout: Layout) -> Iterable[tuple[object, ...]]:
        ts = iso_now()
        for pon in self.inventory().pons:
            yield ("", ts, pon, 10_000_000_000, 10_000_000_000)

    def rows_traffic(self, layout: Layout) -> Iterable[tuple[object, ...]]:
        ts = iso_now()
        for idx, pon in enumerate(self.inventory().pons):
            in_octets = self.bump(f"{layout.name}:{pon}:in", 10_000_000 + idx * 500_000, 80_000 + idx * 700)
            out_octets = self.bump(f"{layout.name}:{pon}:out", 15_000_000 + idx * 600_000, 110_000 + idx * 900)
            in_pkts = in_octets // 900
            out_pkts = out_octets // 900
            in_discards = (self.tick + idx) // 97
            out_discards = (self.tick + idx) // 113
            yield ("", ts, pon, in_octets, out_octets, in_discards, out_discards, in_pkts, out_pkts, in_pkts // 30, out_pkts // 40)

    def rows_eonu_interfaces(self, layout: Layout) -> Iterable[tuple[object, ...]]:
        ts = iso_now()
        changed = "2026-06-10T16:45:26Z"
        down_every = env_int("IPFIX_EMU_ONU_DOWN_EVERY", 0)
        for idx, onu in enumerate(self.inventory().onus, start=1):
            oper = 2 if down_every > 0 and idx % down_every == 0 else 1
            yield ("", ts, onu.name, onu.interface, "bbf-xponift:ani", 1, oper, changed)


class IpfixExporter:
    def __init__(self) -> None:
        max_onus = env_int("IPFIX_EMU_MAX_ONUS", 0)
        max_pons = env_int("IPFIX_EMU_MAX_PONS", 0)
        refresh_secs = env_int("IPFIX_EMU_INVENTORY_REFRESH_SECS", 30)
        seed_path = os.environ.get("IPFIX_EMU_ONTS_OPER", "/seeds/onts_oper.xml")
        self.inventory_cache = InventoryCache(seed_path, max_onus, max_pons, refresh_secs)
        self.model = SyntheticModel(self.inventory_cache)
        self.domain_id = env_int("IPFIX_EMU_DOMAIN_ID", 4355)
        self.interval = env_int("IPFIX_EMU_INTERVAL_SECS", 15)
        self.retry = env_int("IPFIX_EMU_RETRY_SECS", 5)
        self.sequence = 0
        self._last_unsupported: tuple[str, ...] = ()

    def next_sequence(self, records: int = 1) -> int:
        seq = self.sequence
        self.sequence = (self.sequence + max(records, 1)) & 0xFFFFFFFF
        return seq

    def send_message(self, sock: socket.socket, sets: Iterable[bytes], records: int = 1) -> None:
        msg = pack_message(sets, self.next_sequence(records), self.domain_id)
        sock.sendall(msg)

    def auth_sets(self, config: IpfixConfig) -> list[bytes]:
        proc = config.process
        if proc is None:
            return []
        fields = (
            fd(256, VARLEN, "str"),
            fd(282, VARLEN, "str"),
            fd(283, VARLEN, "str"),
        )
        opt_payload = options_template_record(AUTH_TEMPLATE_ID, fields, scope_count=1)
        data = var_bytes(config.hostname) + var_bytes(proc.username) + var_bytes(proc.password)
        return [pack_set(OPTIONS_TEMPLATE_SET_ID, opt_payload), pack_set(AUTH_TEMPLATE_ID, data)]

    def template_sets(self, active_caches: tuple[str, ...]) -> list[bytes]:
        layouts = [LAYOUTS[name] for name in active_caches]
        template_payload = b"".join(template_record(layout) for layout in layouts)

        # RFC 5610-style metadata: tell the collector that Nokia IE 505 and
        # IE 284 are helper strings, not telemetry. This keeps the real
        # Lightspan layout while avoiding empty synthetic metrics in ClickHouse.
        ie_meta_fields = (
            std_fd(346, 4, "u32"),       # privateEnterpriseNumber
            std_fd(303, 2, "u16"),      # informationElementId
            std_fd(339, 1, "u8"),       # informationElementDataType
            std_fd(341, VARLEN, "str"), # informationElementName
        )
        ie_meta_template = options_template_record(IE_META_TEMPLATE_ID, ie_meta_fields, scope_count=0)
        ie_meta_data = b"".join(
            (
                struct.pack("!IHB", NOKIA_PEN, 505, 13)
                + var_bytes("/nokia:ipfix/unused"),
                struct.pack("!IHB", NOKIA_PEN, 284, 13)
                + var_bytes("/nokia:ipfix/unused-timestamp"),
            )
        )

        cache_name_fields = (
            fd(248, VARLEN, "str"),
            fd(281, 2, "u16"),
        )
        options_payload = options_template_record(CACHE_NAME_TEMPLATE_ID, cache_name_fields, scope_count=1)
        names_payload = b"".join(
            var_bytes(layout.name) + struct.pack("!H", layout.template_id)
            for layout in layouts
        )
        return [
            pack_set(TEMPLATE_SET_ID, template_payload),
            pack_set(OPTIONS_TEMPLATE_SET_ID, ie_meta_template + options_payload),
            pack_set(IE_META_TEMPLATE_ID, ie_meta_data),
            pack_set(CACHE_NAME_TEMPLATE_ID, names_payload),
        ]

    def send_templates(self, sock: socket.socket, config: IpfixConfig) -> None:
        self.send_message(sock, self.auth_sets(config), records=1)
        self.send_message(sock, self.template_sets(config.active_caches), records=len(config.active_caches))
        log(f"sent auth/templates for {len(config.active_caches)} caches as {config.hostname}")

    def send_cycle(self, sock: socket.socket, config: IpfixConfig) -> int:
        total_records = 0
        for name in config.active_caches:
            layout = LAYOUTS[name]
            rows = list(self.model.rows_for(layout))
            if not rows:
                continue
            sent_for_layout = 0
            for payload in chunk_records(layout, rows):
                # Count records approximately from the prepared row list. For large
                # ONT sets the sequence is not important to the collector, but it
                # remains monotonically increasing.
                set_bytes = pack_set(layout.template_id, payload)
                self.send_message(sock, [set_bytes], records=max(1, len(rows)))
                sent_for_layout += 1
            total_records += len(rows)
            log(f"exported {len(rows)} records for cache {name} in {sent_for_layout} set(s)")
        self.model.advance()
        return total_records

    def connect_and_stream(self, config: IpfixConfig, oneshot: bool) -> None:
        assert config.process is not None
        proc = config.process
        log(f"connecting to IPFIX proxy {proc.host}:{proc.port} using process {proc.name}")
        with socket.create_connection((proc.host, proc.port), timeout=10) as sock:
            sock.settimeout(30)
            self.send_templates(sock, config)
            while True:
                records = self.send_cycle(sock, config)
                log(f"cycle complete: {records} synthetic source records")
                if oneshot:
                    return
                time.sleep(max(1, self.interval))

    def run(self, oneshot: bool = False) -> int:
        while True:
            config = read_ipfix_config()
            if config is None:
                if oneshot:
                    return 2
                time.sleep(self.retry)
                continue

            if config.unsupported_caches and config.unsupported_caches != self._last_unsupported:
                self._last_unsupported = config.unsupported_caches
                log("unsupported reporting caches ignored: " + ", ".join(config.unsupported_caches))

            if not config.enabled:
                log("IPFIX exporting is disabled or no reporting caches are active")
                if oneshot:
                    return 3
                time.sleep(self.retry)
                continue
            if config.process is None:
                log("IPFIX exporting has active caches but no exportingProcess destination")
                if oneshot:
                    return 4
                time.sleep(self.retry)
                continue
            if not config.active_caches:
                log("no supported reporting caches are active")
                if oneshot:
                    return 5
                time.sleep(self.retry)
                continue

            try:
                self.connect_and_stream(config, oneshot)
                if oneshot:
                    return 0
            except OSError as exc:
                log(f"IPFIX connection error: {exc}")
                if oneshot:
                    return 6
                time.sleep(self.retry)
            except Exception as exc:  # keep the supervisor alive on malformed config.
                log(f"IPFIX exporter error: {exc}")
                if oneshot:
                    return 7
                time.sleep(self.retry)


def main() -> int:
    if not env_bool("IPFIX_EMU_ENABLED", True):
        log("IPFIX_EMU_ENABLED=0; exporter disabled")
        return 0
    exporter = IpfixExporter()
    return exporter.run(oneshot=env_bool("IPFIX_EMU_ONESHOT", False))


if __name__ == "__main__":
    sys.exit(main())
