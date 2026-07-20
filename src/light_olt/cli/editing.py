"""Candidate edit construction and sysrepo commit handling.

EditSession accumulates a candidate configuration as a forest of XML trees
(one per top-level module). Each edit action from resolve() (create/set/remove)
mutates the in-memory tree. On commit(), trees are serialized with
xmlns:nc and identityref prefixes, then applied via Plane.apply_edit()
(sysrepocfg --edit) to running and startup.

Identityref handling
--------------------
YANG identityref leaves (class, type) require prefix:namespace in XML.
IDENTITY_NS maps local name -> namespace. EditSession allocates sequential
prefixes (id1, id2, ...) per namespace and writes xmlns:idN declarations on
the root element. Values without ":" are expanded at serialize time.

Concurrency
-----------
EditSession is per-CLI-instance (not shared). Plane.apply_edit runs
sysrepocfg with sudo as needed; errors are parsed for `[ERR]` lines and
returned to the CLI for display. On success, caches are invalidated and
session cleared.
"""

import xml.etree.ElementTree as ET

from .common import (
    IDENTITY_LEAVES, IDENTITY_NS, MOUNTED_IDENTITY_NS, NC_NS,
)

def _q(ns, name):
    return "{%s}%s" % (ns, name) if ns else name


COMMIT_TOP_PRIORITY = {
    "hardware": 10,
    "onus": 20,
    "tm-profiles": 30,
    "subscriber-profiles": 30,
    "frame-processing-profiles": 30,
    "l2-dhcpv4-relay-profiles": 30,
    "dhcpv6-ldra-profiles": 30,
    "pppoe-profiles": 30,
    "icmpv6-profiles": 30,
    "interfaces": 50,
    "xpongemtcont": 60,
    "forwarding": 70,
    "multicast": 80,
}


class EditSession:
    def __init__(self, plane):
        self.plane = plane
        self.roots = {}      # (module, top) -> ET.Element
        self.idns = {}       # namespace -> idN prefix for identityrefs
        self.dirty = False

    def _ensure(self, segs):
        top = segs[0]
        key = (top.module, top.name)
        root = self.roots.get(key)
        if root is None:
            root = ET.Element(_q(self.plane.ns_of(top.module), top.name))
            self.roots[key] = root
            if top.keys:
                self._keys(root, top)
        cur = root
        for seg in segs[1:]:
            cur = self._child(cur, seg)
        return cur

    def _keys(self, el, seg):
        ns = self.plane.ns_of(seg.module)
        children = (seg.node or {}).get("c", {})
        for k, v in (seg.keys or {}).items():
            if el.find(_q(ns, k)) is None:
                key_node = children.get(k, {})
                key_module = key_node.get("m") or seg.module
                key_ns = self.plane.ns_of(key_module)
                ET.SubElement(el, _q(key_ns, k)).text = self._identity_value(
                    key_module, k, key_node, v,
                )

    def _child(self, parent, seg):
        ns = self.plane.ns_of(seg.module)
        tag = _q(ns, seg.name)
        if seg.keys:
            for el in parent.findall(tag):
                if all(el.findtext(_q(ns, k)) == v
                       for k, v in seg.keys.items()):
                    return el
            el = ET.SubElement(parent, tag)
            self._keys(el, seg)
            return el
        el = parent.find(tag)
        if el is None:
            el = ET.SubElement(parent, tag)
        return el

    def _idpfx(self, ns):
        if ns not in self.idns:
            self.idns[ns] = "id%d" % (len(self.idns) + 1)
        return self.idns[ns]

    def _identity_value(self, module, name, node, value):
        """Return a namespace-qualified lexical identityref value."""
        if ":" in value:
            return value
        identity_ns = MOUNTED_IDENTITY_NS.get((module, name, value))
        if identity_ns is None and name in IDENTITY_LEAVES:
            identity_ns = IDENTITY_NS.get(value)
        if (identity_ns is None
                and (node.get("t") or "").lower().startswith("identityref")):
            identity_ns = self.plane.ns_of(module)
        if identity_ns:
            return "%s:%s" % (self._idpfx(identity_ns), value)
        return value

    def add(self, action):
        kind = action[0]
        if kind == "create":
            self._ensure(action[1])
        elif kind == "set":
            _, segs, leaf, val = action
            parent = self._ensure(segs)
            ns = self.plane.ns_of(leaf.module)
            tag = _q(ns, leaf.name)
            vals = val if isinstance(val, list) else [val]
            if isinstance(val, list):
                for old in parent.findall(tag):
                    parent.remove(old)
            texts = []
            for v in vals:
                texts.append(self._identity_value(
                    leaf.module, leaf.name, leaf.node, v,
                ))
            if isinstance(val, list):
                for tx in texts:
                    ET.SubElement(parent, tag).text = tx
            else:
                el = parent.find(tag)
                if el is None:
                    el = ET.SubElement(parent, tag)
                el.text = texts[0]
        elif kind == "remove":
            el = self._ensure(action[1])
            el.set("nc:operation", "remove")
        self.dirty = True

    def serialize(self):
        out = []
        ordered = sorted(
            self.roots.items(),
            key=lambda item: COMMIT_TOP_PRIORITY.get(item[0][1], 40),
        )
        for (mod, _), root in ordered:
            root.set("xmlns:nc", NC_NS)
            for ns, pfx in self.idns.items():
                root.set("xmlns:" + pfx, ns)
            out.append((mod, ET.tostring(root, encoding="unicode")))
        return out

    def commit(self):
        errs = []
        self.plane.begin_local_commit()
        try:
            failed = False
            for mod, xml in self.serialize():
                for ds in ("running", "startup"):
                    r = self.plane.apply_edit(xml, mod, ds)
                    if r.returncode != 0:
                        output_lines = [
                            line.strip()
                            for line in (r.stderr + r.stdout).splitlines()
                            if line.strip()
                        ]
                        error_lines = [line for line in output_lines
                                       if "[ERR]" in line]
                        if error_lines:
                            msg = " | ".join(
                                line.split("[ERR]", 1)[1].strip()
                                for line in error_lines[-3:]
                            )
                        elif output_lines:
                            msg = " | ".join(output_lines[-3:])
                        else:
                            msg = (
                                "edit failed (sysrepocfg rc=%d, datastore=%s)"
                                % (r.returncode, ds))
                        errs.append((mod, msg))
                        failed = True
                        break
                if failed:
                    break
        finally:
            self.plane.end_local_commit()
        if not errs:
            self.roots.clear()
            self.idns.clear()
            self.dirty = False
        return errs
