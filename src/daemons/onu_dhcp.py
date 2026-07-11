#!/usr/bin/env python3
"""
onu_dhcp — emulated IPoE subscribers via ONT (DHCPv4 DORA / DHCPv6 SARR).

Purpose
-------
ONTs in the emulator are YANG data structures in the LT plane; this daemon
gives them "subscriber life": for each provisioned l2-user (Altiplano
IBRIDGE_USER_PORT intent) it creates a virtual host on the uplink and runs a
real DHCP client toward the BNG (SROS), so the router authenticates them
(ESM/RADIUS) and they appear in `show service active-subscribers`.

Discovery (polled from LT running, idempotent)
----------------------------------------------
- ietf-interfaces: interfaces type bbfift:vlan-sub-interface (<user>-VSI)
  with frame-processing-profile-ref and subif-lower-layer (the ONT UNI).
- bbf-frame-processing-profile: o-vlan = match-criteria tag index 0.
- nokia-conf from IHUB: v-VPLS with vlan == o-vlan -> (uplink eth, wire tag)
  (same semantics as ihub_net; fallback: ONU_DHCP_UPLINK + o-vlan).

Per-subscriber plumbing
-----------------------
- macvlan 'suXXXXXXXX' over ethN.<wire-vlan> with deterministic MAC
  (configurable OUI, default 00:d0:f6 as in the lab) -> kernel answers
  ARP/ND/ICMP: BNG can ping the subscriber.
- DHCPv4: raw DISCOVER/OFFER/REQUEST/ACK (AF_PACKET) with option 61,
  hostname, and option 82 (circuit-id ISAM-style + remote-id = UNI), as if
  the OLT relayed it. Renewal re-sends REQUEST.
- DHCPv6: SOLICIT/ADVERTISE/REQUEST/REPLY (IA_NA, DUID-LL) via UDP 546/547
  over the macvlan link-local.

Configuration
-------------
- PORTMAP / /etc/olt/portmap.conf        same map as ihub_net
- ONU_DHCP_UPLINK=eth1                   fallback if no v-VPLS
- ONU_DHCP_MAC_OUI=00:d0:f6              OUI for synthetic MACs
- ONU_DHCP_V4=1 / ONU_DHCP_V6=1          enable per family
- ONU_DHCP_OPT82=1                       insert option 82
- ONU_DHCP_EXCLUDE=(?i)(network|nni|uplink|^ntw_)  VSI regex to ignore
- ONU_DHCP_POLL=20                       seconds between reconciliations
- /etc/olt/onu_dhcp.conf                 overrides: "<vsi> mac=.. vlan=N off"
"""
import hashlib
import os
import re
import socket
import struct
import subprocess
import sys
import threading
import time
import xml.etree.ElementTree as ET

POLL = int(os.environ.get("ONU_DHCP_POLL", "20"))
DRY = "--dry-run" in sys.argv
ONCE = "--once" in sys.argv
V4_ON = os.environ.get("ONU_DHCP_V4", "1") != "0"
V6_ON = os.environ.get("ONU_DHCP_V6", "1") != "0"
OPT82 = os.environ.get("ONU_DHCP_OPT82", "1") != "0"
MAC_OUI = os.environ.get("ONU_DHCP_MAC_OUI", "00:d0:f6")
FALLBACK_UPLINK = os.environ.get("ONU_DHCP_UPLINK", "eth1")
EXCLUDE_RE = re.compile(os.environ.get("ONU_DHCP_EXCLUDE",
                                       r"(?i)(network|nni|uplink|^ntw_)"))
LT_ENV = dict(os.environ, SYSREPO_REPOSITORY_PATH="/repo/lt",
              SYSREPO_SHM_PREFIX="lt_")
IHUB_ENV = dict(os.environ, SYSREPO_REPOSITORY_PATH="/repo/ihub",
                SYSREPO_SHM_PREFIX="ihub_")


def lt_envs():
    """Return environments for the primary LT and any runtime LT clones."""
    out = [("lt", LT_ENV)]
    for n in (2, 3, 4):
        repo = "/repo/lt%d" % n
        if os.path.isdir(repo):
            out.append(("lt%d" % n,
                        dict(os.environ, SYSREPO_REPOSITORY_PATH=repo,
                             SYSREPO_SHM_PREFIX="lt%d_" % n)))
    return out
DEFAULT_MAP = {"1/2/1": "eth1", "1/1/1": "eth2", "1/1/2": "eth3",
               "1/1/3": "eth4", "1/1/4": "eth5"}
ETH_P_IP = 0x0800


def log(msg):
    print("[onu-dhcp] %s" % msg, flush=True)


def sh(cmd):
    if DRY:
        log("DRY: " + " ".join(cmd))
        return 0
    return subprocess.run(cmd, capture_output=True).returncode


def t(el):
    return el.tag.split("}", 1)[1] if el.tag.startswith("{") else el.tag


def kids(el, name):
    return [c for c in el if t(c) == name]


def kid(el, name):
    for c in el:
        if t(c) == name:
            return c
    return None


def text(el, name, default=None):
    c = kid(el, name)
    return (c.text or "").strip() if c is not None and c.text else default


def deep(el, *names):
    for n in names:
        if el is None:
            return None
        el = kid(el, n)
    return el


def sr_export(env, module):
    r = subprocess.run(["sysrepocfg", "-X", "-d", "running", "-m", module,
                        "-f", "xml"], env=env, capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    try:
        return ET.fromstring("<top>%s</top>" % r.stdout)
    except ET.ParseError:
        return None


def portmap():
    m = {}
    env = os.environ.get("PORTMAP", "")
    if env:
        for pair in re.split(r"[,\s]+", env.strip()):
            if "=" in pair:
                p, i = pair.split("=", 1)
                m[p.strip()] = i.strip()
        return m
    try:
        for line in open("/etc/olt/portmap.conf"):
            line = line.split("#")[0].strip()
            if line and len(line.split()) == 2:
                p, i = line.split()
                m[p] = i
    except OSError:
        pass
    return m or dict(DEFAULT_MAP)


def overrides():
    """/etc/olt/onu_dhcp.conf: '<vsi> mac=xx:.. vlan=N off'"""
    ov = {}
    try:
        for line in open("/etc/olt/onu_dhcp.conf"):
            line = line.split("#")[0].strip()
            if not line:
                continue
            parts = line.split()
            entry = {}
            for kv in parts[1:]:
                if kv == "off":
                    entry["off"] = True
                elif "=" in kv:
                    k, v = kv.split("=", 1)
                    entry[k] = v
            ov[parts[0]] = entry
    except OSError:
        pass
    return ov


# ---------------------------------------------------------------------------
# Subscriber discovery.
# ---------------------------------------------------------------------------
def fpp_outer_vlans(env):
    """Map frame-processing profile names to their outer VLAN."""
    root = sr_export(env, "bbf-frame-processing-profile")
    out = {}
    if root is None:
        return out
    for fpps in kids(root, "frame-processing-profiles"):
        for fpp in kids(fpps, "frame-processing-profile"):
            name = text(fpp, "name")
            mc = kid(fpp, "match-criteria")
            if not name or mc is None:
                continue
            for tag in kids(mc, "tag"):
                if text(tag, "index") == "0":
                    vid = text(tag, "vlan-id")
                    if vid and vid.isdigit():
                        out[name] = vid
                    break
    return out


def interface_outer_vlan(itf):
    """Return the service VLAN configured directly on a subinterface.

    Altiplano commonly instantiates profiles with a parameterized VLAN ID and
    stores the resolved value under tag-0/tag-1 on the subscriber interface.
    The interface value takes precedence so any provisioned VLAN can trigger
    DORA.
    """
    for tag_name in ("tag-0", "tag-1", "tag"):
        for tag in kids(itf, tag_name):
            vid = text(tag, "vlan-id")
            if vid and vid.isdigit():
                return vid
    return None


def ihub_vvpls_wire(pmap):
    """Map service VLANs to IHUB base interfaces and optional wire VLANs."""
    root = sr_export(IHUB_ENV, "nokia-conf")
    out = {}
    if root is None:
        return out
    for conf in kids(root, "configure"):
        service = kid(conf, "service")
        if service is None:
            continue
        for vp in kids(service, "vpls"):
            vvlan = text(vp, "vlan")
            if not vvlan:
                continue
            for sap in kids(vp, "sap"):
                sap_id = text(sap, "sap-id") or (sap.text or "").strip()
                if not sap_id:
                    continue
                pid, _, svlan = sap_id.partition(":")
                if pid in pmap:
                    out[vvlan] = (pmap[pid], svlan or None)
                    break
    return out


def discover(pmap, ov):
    """[{key, vsi, uni, mac, wire_iface}] de l2-users en TODOS los planos LT."""
    wire = ihub_vvpls_wire(pmap)
    subs = []
    for plane, env in lt_envs():
        root = sr_export(env, "ietf-interfaces")
        if root is None:
            continue
        vlans = fpp_outer_vlans(env)
        for ifs in kids(root, "interfaces"):
            for itf in kids(ifs, "interface"):
                typ = text(itf, "type", "")
                if not typ.endswith("vlan-sub-interface"):
                    continue
                name = text(itf, "name")
                if not name or EXCLUDE_RE.search(name):
                    continue
                o = ov.get(name, {})
                if o.get("off"):
                    continue
                if text(itf, "enabled", "true") == "false":
                    continue
                fpref = text(itf, "frame-processing-profile-ref")
                ovlan = (o.get("vlan") or interface_outer_vlan(itf)
                         or (vlans.get(fpref) if fpref else None))
                if not ovlan:
                    continue
                uni = text(deep(itf, "subif-lower-layer"), "interface", name)
                base, wvlan = wire.get(ovlan, (FALLBACK_UPLINK, ovlan))
                wvlan = wvlan or ovlan
                mac = o.get("mac") or synth_mac("%s/%s" % (plane, name))
                subs.append({"key": "%s/%s" % (plane, name), "vsi": name,
                             "uni": uni, "mac": mac, "ovlan": ovlan,
                             "base": base, "wvlan": wvlan})
    return subs


def synth_mac(name):
    h = hashlib.md5(name.encode()).digest()
    return "%s:%02x:%02x:%02x" % (MAC_OUI, h[0], h[1], h[2])


def mv_name(key):
    return "su" + hashlib.md5(key.encode()).hexdigest()[:8]


# ---------------------------------------------------------------------------
# Per-subscriber network plumbing.
# ---------------------------------------------------------------------------
def ensure_plumbing(sub):
    """Create the wire VLAN and subscriber macvlan when needed."""
    base, wvlan = sub["base"], sub["wvlan"]
    parent = "%s.%s" % (base, wvlan)
    links = subprocess.run(["ip", "-o", "link"], capture_output=True,
                           text=True).stdout
    if ("%s@" % base) not in links and (" %s:" % base) not in links:
        return False                      # No containerlab link is attached.
    if (" %s@" % parent) not in links and (" %s:" % parent) not in links:
        sh(["ip", "link", "set", base, "up"])
        sh(["ip", "link", "add", "link", base, "name", parent,
            "type", "vlan", "id", str(wvlan)])
    sh(["ip", "link", "set", parent, "up"])
    mv = mv_name(sub["key"])
    if (" %s@" % mv) not in links and (" %s:" % mv) not in links:
        if sh(["ip", "link", "add", mv, "link", parent, "type", "macvlan",
               "mode", "bridge"]) != 0:
            return False
        log("%s: macvlan %s on %s, MAC %s" %
            (sub["key"], mv, parent, sub["mac"]))
    sh(["ip", "link", "set", mv, "address", sub["mac"]])
    sh(["ip", "link", "set", mv, "up"])
    sub["iface"] = mv
    return True


def teardown(key):
    sh(["ip", "link", "del", mv_name(key)])


# ---------------------------------------------------------------------------
# DHCPv4 DORA over AF_PACKET.
# ---------------------------------------------------------------------------
def csum(data):
    if len(data) % 2:
        data += b"\x00"
    s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    return (~s) & 0xffff


def mac_bytes(mac):
    return bytes(int(x, 16) for x in mac.split(":"))


def build_dhcp4(sub, xid, msgtype, requested=None, server=None):
    mac = mac_bytes(sub["mac"])
    opts = b"\x35\x01" + bytes([msgtype])                     # 53 msg type
    opts += b"\x3d\x07\x01" + mac                             # 61 client-id
    host = re.sub(r"[^A-Za-z0-9-]", "-", sub["uni"])[:32].encode()
    opts += bytes([12, len(host)]) + host                     # 12 hostname
    if requested:
        opts += b"\x32\x04" + socket.inet_aton(requested)     # 50
    if server:
        opts += b"\x36\x04" + socket.inet_aton(server)        # 54
    opts += b"\x37\x04\x01\x03\x06\x0f"                       # 55 param list
    if OPT82:
        circ = ("%s xpon %s:%s" % (socket.gethostname(),
                                   sub["uni"], sub["ovlan"])).encode()[:60]
        rem = sub["uni"].encode()[:60]
        sub82 = bytes([1, len(circ)]) + circ + bytes([2, len(rem)]) + rem
        opts += bytes([82, len(sub82)]) + sub82
    opts += b"\xff"
    bootp = struct.pack("!BBBBIHH4s4s4s4s16s64s128s",
                        1, 1, 6, 0, xid, 0, 0x8000,
                        b"\x00" * 4, b"\x00" * 4, b"\x00" * 4, b"\x00" * 4,
                        mac + b"\x00" * 10, b"\x00" * 64, b"\x00" * 128)
    payload = bootp + b"\x63\x82\x53\x63" + opts
    udp = struct.pack("!HHHH", 68, 67, 8 + len(payload), 0) + payload
    ph = (socket.inet_aton("0.0.0.0") + socket.inet_aton("255.255.255.255")
          + struct.pack("!BBH", 0, 17, len(udp)))
    udp = udp[:6] + struct.pack("!H", csum(ph + udp)) + udp[8:]
    ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(udp), 0, 0, 64, 17,
                     0, socket.inet_aton("0.0.0.0"),
                     socket.inet_aton("255.255.255.255"))
    ip = ip[:10] + struct.pack("!H", csum(ip)) + ip[12:]
    eth = b"\xff" * 6 + mac + struct.pack("!H", ETH_P_IP)
    return eth + ip + udp


def parse_dhcp4(pkt, mac, xid):
    """-> (msgtype, yiaddr, {opt: bytes}) o None"""
    if len(pkt) < 282 or pkt[12:14] != struct.pack("!H", ETH_P_IP):
        return None
    ihl = (pkt[14] & 0x0f) * 4
    if pkt[23] != 17:
        return None
    udp = pkt[14 + ihl:]
    if struct.unpack("!H", udp[2:4])[0] != 68:
        return None
    bootp = udp[8:]
    if struct.unpack("!I", bootp[4:8])[0] != xid:
        return None
    if bootp[28:34] != mac_bytes(mac):
        return None
    yiaddr = socket.inet_ntoa(bootp[16:20])
    opts, o = {}, bootp[240:]
    i = 0
    while i < len(o):
        code = o[i]
        if code == 255 or code == 0:
            if code == 0:
                i += 1
                continue
            break
        ln = o[i + 1]
        opts[code] = o[i + 2:i + 2 + ln]
        i += 2 + ln
    mt = opts.get(53, b"\x00")[0]
    return (mt, yiaddr, opts)


def dora(sub, stop):
    """Run a complete DORA exchange and return the lease, if any."""
    try:
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,
                          socket.htons(ETH_P_IP))
        s.bind((sub["iface"], 0))
        s.settimeout(3)
    except OSError as e:
        log("%s: raw socket: %s" % (sub["key"], e))
        return None
    xid = struct.unpack("!I", os.urandom(4))[0]
    try:
        for attempt in range(4):
            if stop.is_set():
                return None
            s.send(build_dhcp4(sub, xid, 1))                  # DISCOVER
            offer = _wait4(s, sub, xid, 2)
            if offer is None:
                continue
            yiaddr, server = offer
            s.send(build_dhcp4(sub, xid, 3, yiaddr, server))  # REQUEST
            ack = _wait4(s, sub, xid, 5, want_opts=True)
            if ack is None:
                continue
            addr, opts = ack
            mask = opts.get(1)
            plen = bin(struct.unpack("!I", mask)[0]).count("1") if mask else 24
            lease = struct.unpack("!I", opts.get(51, b"\x00\x00\x0e\x10"))[0]
            router = socket.inet_ntoa(opts[3][:4]) if 3 in opts else None
            return {"ip": addr, "plen": plen, "lease": lease,
                    "server": server, "router": router}
        return None
    finally:
        s.close()


def _wait4(s, sub, xid, want, want_opts=False):
    end = time.time() + 4
    while time.time() < end:
        try:
            pkt = s.recv(2048)
        except socket.timeout:
            return None
        r = parse_dhcp4(pkt, sub["mac"], xid)
        if not r or r[0] != want:
            continue
        mt, yiaddr, opts = r
        server = socket.inet_ntoa(opts[54][:4]) if 54 in opts else None
        if want_opts:
            return (yiaddr, opts)
        return (yiaddr, server)
    return None


# ---------------------------------------------------------------------------
# DHCPv6 SARR over link-local UDP.
# ---------------------------------------------------------------------------
def link_local(iface, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        r = subprocess.run(["ip", "-6", "-o", "addr", "show", "dev", iface,
                            "scope", "link"], capture_output=True, text=True)
        m = re.search(r"inet6 (fe80::[0-9a-f:]+)/", r.stdout)
        if m:
            return m.group(1)
        time.sleep(0.5)
    return None


def _v6opt(code, data):
    return struct.pack("!HH", code, len(data)) + data


def sarr(sub, stop):
    ll = link_local(sub["iface"])
    if not ll:
        return None
    mac = mac_bytes(sub["mac"])
    duid = struct.pack("!HH", 3, 1) + mac                     # DUID-LL
    iaid = struct.unpack("!I", hashlib.md5(
        sub["key"].encode()).digest()[:4])[0]
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ll, 546, 0, socket.if_nametoindex(sub["iface"])))
        s.settimeout(3)
    except OSError as e:
        log("%s: v6 socket: %s" % (sub["key"], e))
        return None
    dst = ("ff02::1:2", 547, 0, socket.if_nametoindex(sub["iface"]))

    def build(mtype, sid=None, ia_body=b""):
        tid = os.urandom(3)
        msg = bytes([mtype]) + tid
        msg += _v6opt(1, duid)                                # client-id
        if sid:
            msg += _v6opt(2, sid)                             # server-id
        msg += _v6opt(3, struct.pack("!III", iaid, 0, 0) + ia_body)  # IA_NA
        msg += _v6opt(8, b"\x00\x00")                         # elapsed
        msg += _v6opt(6, struct.pack("!HH", 23, 24))          # ORO dns
        return tid, msg

    def rx(tid, want):
        end = time.time() + 4
        while time.time() < end:
            try:
                data, _ = s.recvfrom(2048)
            except socket.timeout:
                return None
            if len(data) < 4 or data[0] != want or data[1:4] != tid:
                continue
            opts, i = {}, 4
            while i + 4 <= len(data):
                c, ln = struct.unpack("!HH", data[i:i + 4])
                opts.setdefault(c, []).append(data[i + 4:i + 4 + ln])
                i += 4 + ln
            return opts
        return None

    try:
        for attempt in range(4):
            if stop.is_set():
                return None
            tid, msg = build(1)                               # SOLICIT
            s.sendto(msg, dst)
            adv = rx(tid, 2)                                  # ADVERTISE
            if not adv or 2 not in adv or 3 not in adv:
                continue
            sid = adv[2][0]
            tid, msg = build(3, sid, adv[3][0][12:])          # REQUEST
            s.sendto(msg, dst)
            rep = rx(tid, 7)                                  # REPLY
            if not rep or 3 not in rep:
                continue
            ia = rep[3][0]
            j = 12
            while j + 4 <= len(ia):                           # IAADDR (5)
                c, ln = struct.unpack("!HH", ia[j:j + 4])
                if c == 5 and ln >= 24:
                    addr = socket.inet_ntop(socket.AF_INET6,
                                            ia[j + 4:j + 20])
                    valid = struct.unpack("!I", ia[j + 24:j + 28])[0]
                    return {"ip6": addr, "valid": valid}
                j += 4 + ln
        return None
    finally:
        s.close()


# ---------------------------------------------------------------------------
# Subscriber lifecycle.
# ---------------------------------------------------------------------------
def subscriber_thread(sub, stop):
    key, iface = sub["key"], sub["iface"]
    log("%s: mac=%s wire=%s.%s uni=%s" %
        (key, sub["mac"], sub["base"], sub["wvlan"], sub["uni"]))
    l4 = l6 = None
    t4 = t6 = 0.0
    while not stop.is_set():
        now = time.time()
        if V4_ON and now >= t4:
            lease = dora(sub, stop)
            if lease:
                if not l4 or l4["ip"] != lease["ip"]:
                    if l4:
                        sh(["ip", "addr", "del",
                            "%s/%d" % (l4["ip"], l4["plen"]), "dev", iface])
                    sh(["ip", "addr", "add",
                        "%s/%d" % (lease["ip"], lease["plen"]), "dev", iface])
                    log("%s: DHCPv4 ACK %s/%d (server %s, lease %ss)" %
                        (key, lease["ip"], lease["plen"],
                         lease["server"], lease["lease"]))
                l4 = lease
                t4 = now + max(lease["lease"] // 2, 60)
            else:
                if l4:
                    log("%s: DHCPv4 renewal failed; retrying" % key)
                t4 = now + 30
        if V6_ON and now >= t6:
            lease6 = sarr(sub, stop)
            if lease6:
                if not l6 or l6["ip6"] != lease6["ip6"]:
                    if l6:
                        sh(["ip", "-6", "addr", "del", l6["ip6"] + "/128",
                            "dev", iface])
                    sh(["ip", "-6", "addr", "add", lease6["ip6"] + "/128",
                        "dev", iface])
                    log("%s: DHCPv6 REPLY %s (valid %ss)" %
                        (key, lease6["ip6"], lease6["valid"]))
                l6 = lease6
                t6 = now + max(lease6["valid"] // 2, 120)
            else:
                t6 = now + 45
        stop.wait(2)
    teardown(key)
    log("%s: subscriber removed" % key)


def main():
    pmap = portmap()
    log("uplink map: " + " ".join("%s=%s" % kv for kv in sorted(pmap.items())))
    active = {}   # key -> (thread, stop_event)
    while True:
        try:
            subs = discover(pmap, overrides())
            seen = set()
            for sub in subs:
                seen.add(sub["key"])
                if sub["key"] in active:
                    continue
                if not ensure_plumbing(sub):
                    continue
                stop = threading.Event()
                th = threading.Thread(target=subscriber_thread,
                                      args=(sub, stop), daemon=True)
                th.start()
                active[sub["key"]] = (th, stop)
            for key in list(active):
                if key not in seen:
                    active[key][1].set()
                    del active[key]
        except Exception as e:
            log("error: %s" % e)
        if ONCE:
            break
        time.sleep(POLL)
    return 0


if __name__ == "__main__":
    sys.exit(main())
