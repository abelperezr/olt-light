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

from .common import IDENTITY_LEAVES, IDENTITY_NS, NC_NS

def _q(ns, name):
    return "{%s}%s" % (ns, name) if ns else name


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
        for k, v in (seg.keys or {}).items():
            if el.find(_q(ns, k)) is None:
                ET.SubElement(el, _q(ns, k)).text = v

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
                if (leaf.name in IDENTITY_LEAVES and ":" not in v
                        and v in IDENTITY_NS):
                    v = "%s:%s" % (self._idpfx(IDENTITY_NS[v]), v)
                texts.append(v)
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
        for (mod, _), root in self.roots.items():
            root.set("xmlns:nc", NC_NS)
            for ns, pfx in self.idns.items():
                root.set("xmlns:" + pfx, ns)
            out.append((mod, ET.tostring(root, encoding="unicode")))
        return out

    def commit(self):
        errs = []
        self.plane.suppress_commit_notice()
        for mod, xml in self.serialize():
            for ds in ("running", "startup"):
                r = self.plane.apply_edit(xml, mod, ds)
                if r.returncode != 0:
                    lines = [l for l in (r.stderr + r.stdout).splitlines()
                             if "[ERR]" in l]
                    msg = (lines[0].split("[ERR]", 1)[1].strip()
                           if lines else "edit failed")
                    errs.append((mod, msg))
                    break
        if not errs:
            self.roots.clear()
            self.idns.clear()
            self.dirty = False
        return errs
