"""Shared constants, builtin command tables, and helpers for the emulated CLI.

This module centralizes everything that both ConfdCLI (SHELF/LT) and MdCli
(IHUB) need: plane endpoints, identity namespaces, builtin command
descriptions, ping implementation, tokenization, pipe filtering, and the
sudo path resolver used by Plane.run() to execute sysrepocfg as root when
the CLI runs as an unprivileged user.

Constants
---------
- PLANES : mapping plane_name -> (repo_path, shm_prefix, netconf_port)
- IDENTITY_NS / IDENTITY_LEAVES : namespace mapping for YANG identityrefs
  (class, type) used when serializing candidate edits.
- BUILTIN_OPER / BUILTIN_CONFIG : command -> description dicts for the
  builtin commands exposed in each mode. These are the *only* commands the
  emulator accepts; real OLT commands that have no effect here are
  intentionally omitted so the user gets an explicit error instead of
  silent no-op.

Helpers
-------
- run_ping() : executes real kernel ping (IPv4/IPv6) inside the container
  netns. Since ihub_net mirrors IHUB config (port admin-state, router
  "Base"/IES interfaces with IPs) onto Linux interfaces, the ping actually
  traverses the uplink toward SROS containerlab nodes. router-instance is
  accepted and ignored (everything lives in the container netns, equiv to
  "Base").
- tokenize() : shlex-based splitting respecting quotes.
- split_pipe() / apply_filter() : handle `| include/exclude/count/grep`
  post-processing on command output.
"""

import os
import re
import shlex
import subprocess
import sys

NC_NS = "urn:ietf:params:xml:ns:netconf:base:1.0"
ECLI_VERSION = "v5-contexts+dynamic-forward+ihub-global"
PLANES = {
    "ihub":  ("/repo/ihub",  "ihub_", 831),
    "shelf": ("/repo/shelf", "shelf_", 832),
    "lt":    ("/repo/lt",    "lt_", 833),
}
IDX_PATH = "/etc/olt/cli_index_%s.json.gz"
COMMIT_POLL_SECONDS = float(os.environ.get("ECLI_COMMIT_POLL_SECONDS", "1.0"))
SIG_CACHE_SECONDS = float(os.environ.get("ECLI_SIG_CACHE_SECONDS", "0.15"))
XML_CACHE_MAX = int(os.environ.get("ECLI_XML_CACHE_MAX", "24"))

# Resolve sudo once. Plane uses it for sysrepo commands when the eCLI runs as
# an unprivileged login user; an empty value means commands run directly.
def _which(cmd):
    for d in os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep):
        p = os.path.join(d, cmd)
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    return ""
_SUDO = _which("sudo")

# --------------------------------------------------------------------------
# Known identity values mapped to their XML namespaces.
# --------------------------------------------------------------------------
NS_NOKIA_HWI = ("http://www.nokia.com/Fixed-Networks/BBA/yang/"
                "nokia-hardware-identities")
NS_BBF_XPON_TYPES = "urn:bbf:yang:bbf-xpon-types"
IDENTITY_NS = {
    "chassis": "urn:ietf:params:xml:ns:yang:iana-hardware",
    "container": "urn:ietf:params:xml:ns:yang:iana-hardware",
    "module": "urn:ietf:params:xml:ns:yang:iana-hardware",
    "port": "urn:ietf:params:xml:ns:yang:iana-hardware",
    "sensor": "urn:ietf:params:xml:ns:yang:iana-hardware",
    "transceiver": "urn:bbf:yang:bbf-hardware-types",
    "transceiver-link": "urn:bbf:yang:bbf-hardware-types",
    "cage": "urn:bbf:yang:bbf-hardware-types",
    "transceiver-link-gpon": NS_NOKIA_HWI,
    "transceiver-link-xgspon": NS_NOKIA_HWI,
    "lt": NS_NOKIA_HWI,
    "slot-lt": NS_NOKIA_HWI,
    "backplane-port": NS_NOKIA_HWI,
    "channel-group": "urn:bbf:yang:bbf-xpon-if-type",
    "channel-partition": "urn:bbf:yang:bbf-xpon-if-type",
    "channel-pair": "urn:bbf:yang:bbf-xpon-if-type",
    "channel-termination": "urn:bbf:yang:bbf-xpon-if-type",
    "v-ani": "urn:bbf:yang:bbf-xpon-if-type",
    "ani": "urn:bbf:yang:bbf-xpon-if-type",
    "olt-v-enet": "urn:bbf:yang:bbf-xpon-if-type",
    "onu-v-enet": "urn:bbf:yang:bbf-xpon-if-type",
    "vlan-sub-interface": "urn:bbf:yang:bbf-if-type",
    "ethernetCsmacd": "urn:ietf:params:xml:ns:yang:iana-if-type",
    "fiftyg-twdm": NS_BBF_XPON_TYPES,
    "fiftyg-tdm": NS_BBF_XPON_TYPES,
    "twentyfivegs": NS_BBF_XPON_TYPES,
    "ngpon2-twdm": NS_BBF_XPON_TYPES,
    "ngpon2-ptp": NS_BBF_XPON_TYPES,
    "xgs": NS_BBF_XPON_TYPES,
    "xgpon": NS_BBF_XPON_TYPES,
    "gpon": NS_BBF_XPON_TYPES,
}
IDENTITY_LEAVES = {"class", "type", "channel-pair-type"}

# --------------------------------------------------------------------------
# Advertise only commands implemented by the emulator. An explicit error is
# safer than silently accepting a real-device command that has no effect here.
# --------------------------------------------------------------------------
BUILTIN_OPER = {
    "config": "Manipulate software configuration information",
    "exit": "Exit the management session",
    "forward": "Forward CLI sessions",
    "help": "Provide help information",
    "id": "Show user id information",
    "logout": "Logout a user",
    "ping": "Ping an IP address or DNS name",
    "pwd": "Display current mode path",
    "quit": "Exit the management session",
    "show": "Show information about the system",
    "who": "Display currently logged on users",
}
BUILTIN_CONFIG = {
    "commit": "Commit current set of changes",
    "exit": "Exit from current mode",
    "top": "Exit to top level and optionally run command",
    "end": "Terminate configuration session",
    "abort": "Abort configuration session",
    "no": "Negate a command or set its defaults",
    "pwd": "Display current mode path",
    "show": "Show a parameter",
    "do": "Run an operational-mode command",
    "help": "Provide help information",
    "exit-all": "Exit to top level",
}


def run_ping(args, out):
    """Run the container's real ping command.

    Syntax: ping <destination> [count N] [size N] [source-address A]
                      [interface IFC]
                      [router-instance "Base"] [timeout S] [interval S]

    ``ihub_net`` mirrors IHUB port and router-interface configuration onto
    Linux interfaces, so packets leave through the container's actual uplink.
    ``router-instance`` is accepted for CLI compatibility and ignored because
    every interface lives in the same network namespace.
    """
    target = None
    count, size, source, iface, timeout, interval = "5", None, None, None, "2", None
    i = 0
    while i < len(args):
        a = args[i].strip('"')
        nxt = args[i + 1].strip('"') if i + 1 < len(args) else None
        if a == "count" and nxt:
            count = nxt; i += 2
        elif a == "size" and nxt:
            size = nxt; i += 2
        elif a in ("source-address", "source") and nxt:
            source = nxt; i += 2
        elif a == "interface" and nxt:
            iface = nxt; i += 2
        elif a == "timeout" and nxt:
            timeout = nxt; i += 2
        elif a == "interval" and nxt:
            interval = nxt; i += 2
        elif a in ("router-instance", "router", "subscriber") and nxt:
            i += 2                       # Accepted for compatibility; no-op.
        elif target is None:
            target = a; i += 1
        else:
            i += 1
    if not target:
        out("MINOR: CLI Missing destination address")
        return None
    cmd = ["ping", "-c", str(count), "-W", str(timeout)]
    if ":" in target:
        cmd.insert(1, "-6")
    if size:
        cmd += ["-s", str(size)]
    if interval:
        cmd += ["-i", str(interval)]
    if source:
        cmd += ["-I", source]
    elif iface:
        cmd += ["-I", iface]
    cmd.append(target)
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            out(line.rstrip("\n"))
        proc.wait()
    except FileNotFoundError:
        out("MINOR: CLI ping utility not available in this image")
    except KeyboardInterrupt:
        try:
            proc.terminate()
        except Exception:
            pass
    return None


def tokenize(line):
    lex = shlex.shlex(line, posix=True)
    lex.whitespace_split = True
    lex.commenters = ""
    try:
        return list(lex)
    except ValueError:
        return line.split()


def split_pipe(line):
    in_q = None
    for i, ch in enumerate(line):
        if in_q:
            if ch == in_q:
                in_q = None
        elif ch in "\"'":
            in_q = ch
        elif ch == "|":
            return line[:i].rstrip(), line[i + 1:].strip()
    return line, None


def apply_filter(text, pipecmd):
    if not pipecmd:
        return text
    toks = pipecmd.split(None, 1)
    arg = toks[1].strip('"') if len(toks) > 1 else ""
    if toks[0] in ("include", "match", "grep"):
        return "\n".join(l for l in text.splitlines() if arg in l)
    if toks[0] in ("exclude", "match-not"):
        return "\n".join(l for l in text.splitlines() if arg not in l)
    if toks[0] == "count":
        return "Count: %d lines" % len(text.splitlines())
    return text
