"""XML helpers and renderers for ConfD-style and MD-CLI output.

Renderers
---------
- render_confd() : ConfD "J-style" output. Single child inlined on parent
  line; multiple children indented with `!` block terminator. Leaf-lists
  grouped as `[ a b c ]`. Key-ish leaves (name, id, slot-number, etc.)
  appended on list header line. Used by ConfdCLI `show` commands.

- render_md_flat() : nokia-conf "info" style flat braces.
  `head key1 key2 { tail }` with string values quoted. Used by MdCli `info`.

XML utilities
-------------
- strip_ns() : removes `{namespace}` prefix from tag.
- xml_roots() : parses sysrepocfg XML string into list of root Elements.
- clone_roots() : deep copy for merge_overlay() without mutating cached roots.
- xml_child_text() / xml_matches_keys() / xml_path_elements() : navigation
  by local name with optional key filtering (handles namespace changes in
  mounted subtrees where absolute XPath is not portable).

Candidate merge
---------------
- merge_overlay(base, edit) : applies edit XML (with nc:operation) onto
  base tree. Handles create (append), replace (text), remove (unlink),
  and recursive merge for containers. Uses elems_match() to correlate
  list entries by key-ish leaves.
"""

import re
import xml.etree.ElementTree as ET

from .common import NC_NS
from .schema import _children

def strip_ns(tag):
    return tag.split("}", 1)[1] if tag.startswith("{") else tag


def segs_exist_in_running(plane, segs):
    """Return whether a resolved path already exists in running.

    ``resolve()`` emits a create action even when a user is merely entering an
    existing context such as ``router Base``. Ignoring that action keeps the
    candidate clean and avoids showing a false dirty marker in the prompt.
    """
    if not segs:
        return True
    try:
        roots = plane.export_xml_roots("running", segs[0].module, clone=False)
    except Exception:
        return False

    def match(el, seg):
        if strip_ns(el.tag) != seg.name:
            return False
        for k, v in (seg.keys or {}).items():
            if not any(strip_ns(c.tag) == k and (c.text or "").strip() == v
                       for c in el):
                return False
        return True

    level = [r for r in (roots or []) if match(r, segs[0])]
    for seg in segs[1:]:
        level = [c for parent in level for c in parent if match(c, seg)]
        if not level:
            return False
    return bool(level)


def _is_leaf(el):
    return len(list(el)) == 0


def _clean_val(v):
    v = (v or "").strip()
    if ":" in v and re.match(r"^[\w.-]+:[\w.-]+$", v):
        return v.split(":", 1)[1]    # Display identityrefs without prefixes.
    return v


def xml_roots(xml):
    if not xml:
        return []
    try:
        body = re.sub(r"^<\?xml[^>]*\?>", "", xml).strip()
        if not body:
            return []
        wrapper = ET.fromstring("<data>%s</data>" % body)
        return list(wrapper)
    except ET.ParseError:
        return []


def clone_roots(roots):
    return [ET.fromstring(ET.tostring(root, encoding="unicode"))
            for root in roots]


def xml_child_text(el, name):
    for child in list(el):
        if strip_ns(child.tag) == name:
            return _clean_val(child.text)
    return None


def xml_matches_keys(el, keys):
    for key, expected in (keys or {}).items():
        if xml_child_text(el, key) != expected:
            return False
    return True


def xml_path_elements(roots, path_names, path_keys=None):
    """Find elements along a YANG path by local name.

    ``path_keys`` filters resolved ancestor lists. For example,
    ``{1: {"name": "ONT-001"}}`` selects one ONU below ``onus/onu``.
    """
    if not path_names:
        return []
    path_keys = path_keys or {}
    cur = [
        root for root in roots
        if strip_ns(root.tag) == path_names[0]
        and xml_matches_keys(root, path_keys.get(0))
    ]
    for pos, name in enumerate(path_names[1:], 1):
        nxt = []
        for el in cur:
            for child in list(el):
                if (strip_ns(child.tag) == name
                        and xml_matches_keys(child, path_keys.get(pos))):
                    nxt.append(child)
        cur = nxt
    return cur


def mq(v):
    if v == "" or re.search(r"\s", v):
        return '"%s"' % v
    return v


KEYISH = ("name", "id", "slot-number", "mda-slot", "port-id", "service-name",
          "lag-name", "router-name", "interface-name", "sap-id", "user-name",
          "index", "rule-name", "group-name")


def render_confd(el, prefix, depth, out):
    """Render ConfD J-style output with inline chains and ``!`` blocks."""
    name = strip_ns(el.tag)
    kids = list(el)
    if not kids:
        val = _clean_val(el.text)
        out.append("%s%s%s%s" % (" " * depth, prefix, name,
                                 (" " + mq(val)) if val else ""))
        return

    only_key = (len(kids) == 1 and _is_leaf(kids[0])
                and strip_ns(kids[0].tag) in KEYISH)
    if len(kids) == 1 and not only_key:
        render_confd(kids[0], prefix + name + " ", depth, out)
        return
    header = prefix + name
    consumed = []
    first = kids[0]
    if _is_leaf(first) and strip_ns(first.tag) in KEYISH:
        header += " " + mq(_clean_val(first.text))
        consumed.append(first)
    out.append(" " * depth + header)
    # Group repeated leaf-list values as ``[ a b c ]``.
    seen_ll = set()
    for k in kids:
        if k in consumed:
            continue
        nm = strip_ns(k.tag)
        same = [x for x in kids if strip_ns(x.tag) == nm and _is_leaf(x)]
        if _is_leaf(k) and len(same) > 1:
            if nm in seen_ll:
                continue
            seen_ll.add(nm)
            out.append("%s%s [ %s ]" % (" " * (depth + 1), nm,
                       " ".join(_clean_val(x.text) for x in same)))
            continue
        render_confd(k, "", depth + 1, out)
    out.append(" " * depth + "!")


def render_md_flat(el, path, out, inode):
    """Render nokia-conf XML as flat ``head { remainder }`` output.

    ``inode`` is the schema node used to identify lists, keys, and strings.
    """
    name = strip_ns(el.tag)
    kids = list(el)
    if not kids:
        val = _clean_val(el.text)
        if val and _md_is_string(inode):
            val = '"%s"' % val
        _emit_flat(path + [name] + ([val] if val else []), out)
        return
    keyvals, rest = [], list(kids)
    if inode and inode.get("k") == "l":
        ich = _children(inode)
        for k in inode.get("keys", []):
            hit = next((x for x in kids if strip_ns(x.tag) == k), None)
            if hit is not None:
                v = _clean_val(hit.text)
                if _md_is_string(ich.get(k)):
                    v = '"%s"' % v
                keyvals.append(v)
                rest.remove(hit)
    newpath = path + [name] + keyvals
    _emit_flat(newpath, out)
    ich = _children(inode) if inode else {}
    for k in rest:
        render_md_flat(k, newpath, out, ich.get(strip_ns(k.tag)))


def _md_is_string(inode):
    if not inode:
        return False
    t = (inode.get("t") or "").lower()
    if t.startswith(("enumeration", "boolean", "uint", "int", "union")):
        return False
    return ("string" in t or "name" in t or "desc" in t
            or "item" in t)


def _emit_flat(tokens, out):
    if not tokens:
        return
    head = [tokens[0]]
    i = 1
    while i < len(tokens) and (tokens[i].startswith('"')
                               or re.fullmatch(r"[\d/.:x-]+", tokens[i])):
        head.append(tokens[i])
        i += 1
    line = "    %s { %s }" % (" ".join(head), " ".join(tokens[i:]))
    out.append(line.replace("{  }", "{ }"))


def merge_overlay(base, edit):
    for child in list(edit):
        op = child.get("nc:operation") or child.get("{%s}operation" % NC_NS)
        match = None
        for b in base.findall(child.tag):
            if elems_match(b, child):
                match = b
                break
        if op == "remove":
            if match is not None:
                base.remove(match)
            continue
        if match is None:
            clone = ET.fromstring(ET.tostring(child))
            base.append(clone)
        elif _is_leaf(child):
            match.text = child.text
        else:
            merge_overlay(match, child)


def elems_match(a, b):
    if a.tag != b.tag:
        return False
    if _is_leaf(b):
        return True
    for kb in list(b):
        if _is_leaf(kb) and strip_ns(kb.tag) in KEYISH:
            av = a.findtext(kb.tag)
            if av is not None:
                return av == (kb.text or "")
    return True
