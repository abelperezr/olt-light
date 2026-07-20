"""Schema navigation, abbreviated lookup, and CLI path resolution.

Core types
----------
- PathSeg : single step in a YANG path (name, module, keys dict, schema node).
- ResolveError(pos, msg, options) : raised when token cannot be resolved;
  pos = token index, options = valid completions at that position.

Functions
---------
- lookup(node, token) -> (real_name, child_node)
  Exact match or unique prefix (ConfD/SR Linux abbreviation). Raises
  ResolveError(-1, "ambiguous", [options]) on multiple matches.
  If node has "loose":1 (schema-mount root), accepts any token as container.

- resolve(plane, ctx_segs, tokens) -> (actions, mode)
  Walks tokens from context, producing edit actions (create/set/remove) and
  the resulting config mode (deepest list/container traversed). Implements
  ConfD rule: mode = deepest list entered, or final node if container/list
  and line ends there. Handles `no`/`delete` prefix for removal.

- schema_list_instances_for(plane, base, body) -> list[(key, desc)] | None
  Called by completers when the current token position expects a list key.
  Walks schema from base following body tokens; if the next schema node is a
  list and not all keys are supplied yet, queries Plane.list_instances() for
  *existing* keys in running datastore (filtered by ancestor keys). Returns
  None if not at a list key position.
"""

import re


def _local_name(tag):
    return tag.split("}", 1)[1] if tag.startswith("{") else tag


def xml_child_text(el, name):
    for child in list(el):
        if _local_name(child.tag) == name:
            value = (child.text or "").strip()
            return value.split(":", 1)[-1] if ":" in value else value
    return None


def xml_path_elements(roots, path_names, path_keys=None):
    """Small local XML walker; kept here to avoid a rendering/schema cycle."""
    if not path_names:
        return []
    path_keys = path_keys or {}

    def matches(el, pos):
        return all(xml_child_text(el, key) == value
                   for key, value in path_keys.get(pos, {}).items())

    cur = [root for root in roots
           if _local_name(root.tag) == path_names[0] and matches(root, 0)]
    for pos, name in enumerate(path_names[1:], 1):
        cur = [child for parent in cur for child in list(parent)
               if _local_name(child.tag) == name and matches(child, pos)]
    return cur


CURATED_VALUE_OPTIONS = {
    ("bbf-xpon", "authentication-method"): (
        "serial-number", "registration-id", "as-per-v-ani-expected", "loid",
    ),
    ("bbf-xpon", "channel-pair-type"): (
        "fiftyg-twdm", "fiftyg-tdm", "twentyfivegs", "ngpon2-twdm",
        "ngpon2-ptp", "xgs", "xgpon", "gpon",
    ),
    ("bbf-xpon", "channel-termination-type"): (
        "fiftyg-twdm", "fiftyg-tdm", "twentyfivegs", "ngpon2-twdm",
        "ngpon2-ptp", "xgs", "xgpon", "gpon",
    ),
    ("bbf-xpon", "location"): ("inside-olt", "outside-olt"),
    ("nokia-mcast-cac", "max-group-number"): ("no-limit",),
    ("nokia-mcast-cac", "max-multicast-rate-limit"): ("no-limit",),
    ("nokia-mcast-cac", "multicast-rate-limit-exceed-action"):
        ("drop", "best-effort"),
}

COMPLETION_VALUE_OPTIONS = {
    ("bbf-qos-classifiers", "filter-operation"): (
        "match-all-filter", "match-any-filter",
    ),
    ("bbf-qos-classifiers", "action-type"): (
        "scheduling-traffic-class", "pbit-marking", "dei-marking", "pass",
    ),
    ("ietf-interfaces", "type"): (
        "channel-group", "channel-partition", "channel-pair",
        "channel-termination", "v-ani", "ani", "olt-v-enet",
        "onu-v-enet", "vlan-sub-interface", "ethernetCsmacd",
    ),
    ("bbf-if-usg", "interface-usage"): (
        "user-port", "network-port", "subtended-node-port", "inherit",
    ),
    ("bbf-l2-forwarding", "receiving-interface-usage"): (
        "user-port", "network-port", "subtended-node-port", "inherit",
    ),
    ("bbf-l2-forwarding", "mac-can-not-move-to"): (
        "user-port", "network-port", "subtended-node-port", "inherit",
    ),
    ("bbf-l2-forwarding", "in-interface-usage"): (
        "user-port", "network-port", "subtended-node-port", "inherit",
    ),
    ("bbf-l2-forwarding", "out-interface-usage"): (
        "user-port", "network-port", "subtended-node-port", "inherit",
    ),
    ("bbf-l2-forwarding", "interface-usages"): (
        "user-port", "network-port", "subtended-node-port", "inherit",
    ),
    ("bbf-frame-processing-profile", "tag-type"): (
        "c-vlan", "s-vlan", "tag-type-from-match",
    ),
    ("bbf-frame-processing-profile", "vlan-id"): (
        "parameter-vlan-id", "priority-tagged", "vlan-id-from-match",
    ),
    ("bbf-frame-processing-profile", "pbit"): ("any",),
    ("bbf-frame-processing-profile", "dei"): ("any",),
    ("nokia-arpsec", "downstream-arp-broadcast"): (
        "apply-layer2-forwarding", "secured-forwarding",
        "secured-with-fallback-to-layer2",
    ),
    ("nokia-ndsec", "downstream-ns-multicast"): (
        "apply-layer2-forwarding", "secured-forwarding",
        "secured-with-fallback-to-layer2",
    ),
    ("onus-from-template", "admin-state"): (
        "unknown", "locked", "shutting-down", "unlocked",
    ),
    ("nokia-onus-from-template", "admin-state"): (
        "unknown", "locked", "shutting-down", "unlocked",
    ),
    ("bbf-l2-dhcpv4-relay", "suboptions"): (
        "circuit-id", "remote-id", "access-loop-characteristics",
    ),
    ("bbf-l2-dhcpv4-relay", "default-circuit-id-syntax"): (
        "Access_Node_ID:Chassis:Port:OnuID:v-ani:olt-v-enet",
    ),
    ("bbf-l2-dhcpv4-relay", "default-remote-id-syntax"): (
        "Access_Node_ID:Chassis:Port:OnuID:v-ani:olt-v-enet",
    ),
    ("bbf-ldra", "option"): (
        "interface-id", "remote-id", "vendor-specific-information",
    ),
    ("bbf-ldra", "default-interface-id-syntax"): (
        "Access_Node_ID:Chassis:Port:OnuID:v-ani:olt-v-enet",
    ),
    ("bbf-ldra", "default-remote-id-syntax"): ("pon-id",),
    ("bbf-xpon-acc-d6r", "xpon-access-loop-characteristics"): (
        "xpon-tree-maximum-data-rate-upstream",
        "onu-maximum-data-rate-upstream",
        "xpon-tree-maximum-data-rate-downstream",
        "onu-peak-data-rate-downstream",
    ),
    ("bbf-xpon-access-line-characteristics-dhcpv6",
     "xpon-access-loop-characteristics"): (
        "xpon-tree-maximum-data-rate-upstream",
        "onu-maximum-data-rate-upstream",
        "xpon-tree-maximum-data-rate-downstream",
        "onu-peak-data-rate-downstream",
    ),
    ("bbf-pppoe-intermediate-agent", "subtag"): (
        "circuit-id", "remote-id", "access-loop-characteristics",
    ),
    ("bbf-pppoe-intermediate-agent", "default-circuit-id-syntax"): (
        "Access_Node_ID:Chassis:Port:OnuID:v-ani:olt-v-enet",
    ),
    ("bbf-pppoe-intermediate-agent", "default-remote-id-syntax"): (
        "Access_Node_ID:Chassis:Port:OnuID:v-ani:olt-v-enet",
    ),
}

REFERENCE_TARGETS = {
    ("bbf-frame-processing-profile", "frame-processing-profile-ref"):
        ("bbf-frame-processing-profile", "frame-processing-profiles",
         ("frame-processing-profiles", "frame-processing-profile"), ("name",)),
    ("bbf-l2-forwarding", "flooding-policies-profile"):
        ("bbf-l2-forwarding", "forwarding",
         ("forwarding", "flooding-policies-profiles",
          "flooding-policies-profile"), ("name",)),
    ("bbf-l2-forwarding", "forwarding-database"):
        ("bbf-l2-forwarding", "forwarding",
         ("forwarding", "forwarding-databases", "forwarding-database"),
         ("name",)),
    ("bbf-l2-forwarding", "split-horizon-profile"):
        ("bbf-l2-forwarding", "forwarding",
         ("forwarding", "split-horizon-profiles", "split-horizon-profile"),
         ("name",)),
    ("bbf-l2-forwarding", "mac-learning-control-profile"):
        ("bbf-l2-forwarding", "forwarding",
         ("forwarding", "mac-learning-control-profiles",
          "mac-learning-control-profile"), ("name",)),
}

CURATED_LIST_KEY_OPTIONS = {
    ("bbf-l2-forwarding", "flooding-policy"): ("dn_drop", "up_drop"),
}

UINT_OR_NO_LIMIT_LEAVES = {
    "max-group-number", "max-multicast-rate-limit",
}

VALUELESS_STRING_LEAVES = {
    ("ietf-interfaces", "description"),
}

class PathSeg:
    __slots__ = ("name", "module", "keys", "node")

    def __init__(self, name, module, keys, node):
        self.name, self.module, self.keys, self.node = name, module, keys, node


class ResolveError(Exception):
    def __init__(self, pos, msg, options=None):
        super().__init__(msg)
        self.pos = pos
        self.options = options or []


def _children(node):
    return node.get("c", {}) if node else {}


def lookup(node, token):
    """Look up an exact child name or an unambiguous abbreviated prefix."""
    ch = _children(node)
    if token in ch:
        return token, ch[token]
    pref = [n for n in ch if n.startswith(token)]
    if len(pref) == 1:
        return pref[0], ch[pref[0]]
    if len(pref) > 1:
        raise ResolveError(-1, "ambiguous", sorted(pref))
    # ``loose`` is a fallback for genuinely missing mounted schemas. Once
    # yanglint supplied real children, accepting arbitrary names creates fake
    # configuration contexts such as ``tm-root COMM``.
    if node.get("loose") and not ch:
        return token, {"k": "c", "m": node.get("m"), "c": {}, "loose": 1}
    return None, None


def leaf_value_options(name, node):
    """Return CLI values known for a leaf, or ``None`` for free-form input."""
    indexed = node.get("v")
    if indexed:
        return tuple(indexed)
    if (node.get("t") or "").lower().startswith("boolean"):
        return ("false", "true")
    key = (node.get("m"), name)
    return CURATED_VALUE_OPTIONS.get(key) or COMPLETION_VALUE_OPTIONS.get(key)


def schema_leaf_value_options(plane, name, node, candidate_roots=None):
    """Static values plus live values for well-known profile leafrefs."""
    options = list(leaf_value_options(name, node) or ())
    if (node.get("m"), name) == ("bbf-xpongemtcont", "alloc-id"):
        used = set()
        roots = list(candidate_roots or ())
        if hasattr(plane, "export_xml_roots"):
            roots += list(plane.export_xml_roots(
                "running", "bbf-xpongemtcont") or ())
        for root in roots:
            for el in root.iter():
                if _local_name(el.tag) == "alloc-id":
                    try:
                        used.add(int((el.text or "").strip()))
                    except ValueError:
                        pass
        options.append(str(next(
            (value for value in range(256, 1024) if value not in used),
            256)))
    target = REFERENCE_TARGETS.get((node.get("m"), name))
    if target and hasattr(plane, "list_instances"):
        module, top, path, keys = target
        for value, _ in plane.list_instances(
                module, top, list(path), list(keys), {}, []):
            if value not in options:
                options.append(value)
        for el in xml_path_elements(list(candidate_roots or ()), list(path)):
            value = xml_child_text(el, keys[0])
            if value and value not in options:
                options.append(value)
    return tuple(options) if options else None


def _validate_leaf_value(name, node, value, pos):
    if (node.get("m"), name) in COMPLETION_VALUE_OPTIONS:
        return
    options = leaf_value_options(name, node)
    if options is None or value in options:
        return
    if name in UINT_OR_NO_LIMIT_LEAVES and re.fullmatch(r"[0-9]+", value):
        return
    raise ResolveError(pos, "invalid value", list(options))


def schema_value_options(plane, base, tokens, candidate_roots=None):
    """Return value completions when ``tokens`` ends at a leaf name."""
    node = base[-1].node if base else {"c": plane.index, "k": "c"}
    i = 0
    while i < len(tokens):
        try:
            real, child = lookup(node, tokens[i])
        except ResolveError:
            return None
        if child is None:
            return None
        kind = child.get("k", "c")
        if kind == "l":
            for key in child.get("keys", []):
                i += 1
                if i >= len(tokens):
                    return None
                if child.get("cli-explicit-keys"):
                    if not key.startswith(tokens[i]):
                        return None
                    i += 1
                    if i >= len(tokens):
                        return None
            i += 1
            node = child
            continue
        if kind == "c":
            node = child
            i += 1
            continue
        if kind in ("f", "F") and i == len(tokens) - 1:
            options = schema_leaf_value_options(
                plane, real, child, candidate_roots)
            if kind == "F" and options is not None:
                return ("[",) + tuple(options)
            return options
        if kind == "F":
            options = schema_leaf_value_options(
                plane, real, child, candidate_roots)
            if options is None:
                return None
            rest = tokens[i + 1:]
            if rest and rest[0] == "[":
                rest = rest[1:]
            if "]" in rest:
                return None
            used = set(rest)
            remaining = tuple(value for value in options if value not in used)
            return remaining + (("]",) if rest else ())
        return None
    return None


def schema_node_after_tokens(plane, base, tokens):
    """Return the schema parent left after complete leaf assignments."""
    node = base[-1].node if base else {"c": plane.index, "k": "c"}
    i = 0
    while i < len(tokens):
        try:
            _, child = lookup(node, tokens[i])
        except ResolveError:
            return None
        if child is None:
            return None
        kind = child.get("k", "c")
        if kind == "l":
            i += 1
            for key in child.get("keys", []):
                if i >= len(tokens):
                    return None
                if child.get("cli-explicit-keys"):
                    if not key.startswith(tokens[i]):
                        return None
                    i += 1
                    if i >= len(tokens):
                        return None
                i += 1
            node = child
            continue
        if kind == "c":
            node = child
            i += 1
            continue
        if kind in ("f", "F"):
            i += 1
            if i >= len(tokens):
                return None
            if kind == "F" and tokens[i] == "[":
                i += 1
                while i < len(tokens) and tokens[i] != "]":
                    i += 1
                if i >= len(tokens):
                    return None
                i += 1
            else:
                leaf_type = (child.get("t") or "").lower()
                next_is_sibling = False
                if leaf_type.startswith(("boolean", "empty")):
                    try:
                        _, sibling = lookup(node, tokens[i])
                        next_is_sibling = sibling is not None
                    except ResolveError:
                        pass
                if not next_is_sibling:
                    i += 1
            continue
        return None
    return node


def resolve(plane, ctx_segs, tokens):
    """Resolve tokens into edit actions and the resulting CLI mode.

    ConfD leaves the session in the deepest list it traversed, or on the final
    container/list when the command ends on that node.
    """
    node = ctx_segs[-1].node if ctx_segs else {"c": plane.index, "k": "c"}
    segs = list(ctx_segs)
    actions = []
    deepest_list = len(ctx_segs)
    remove = False
    i = 0
    if tokens and tokens[0] in ("no", "delete"):
        remove = True
        tokens = tokens[1:]
    ends_on_node = False
    while i < len(tokens):
        t = tokens[i]
        try:
            real, ch = lookup(node, t)
        except ResolveError as e:
            e.pos = i
            raise
        if ch is None:
            raise ResolveError(i, "element does not exist")
        kind = ch.get("k", "c")
        mod = ch.get("m") or (segs[-1].module if segs else None)
        if kind == "l":
            kv = {}
            for k in ch.get("keys", []):
                i += 1
                if i >= len(tokens):
                    options = [k] if ch.get("cli-explicit-keys") else []
                    raise ResolveError(i - 1, "incomplete command", options)
                if ch.get("cli-explicit-keys"):
                    if not k.startswith(tokens[i]):
                        raise ResolveError(i, "element does not exist", [k])
                    i += 1
                    if i >= len(tokens):
                        raise ResolveError(i - 1, "incomplete command")
                kv[k] = tokens[i]
            segs.append(PathSeg(real, mod, kv, ch))
            node = ch
            deepest_list = len(segs)
            ends_on_node = True
        elif kind == "c":
            segs.append(PathSeg(real, mod, None, ch))
            node = ch
            ends_on_node = True
        elif kind in ("f", "F"):
            leafseg = PathSeg(real, mod, None, ch)
            ends_on_node = False
            if remove:
                actions.append(("remove", list(segs) + [leafseg]))
                return actions, ctx_segs
            i += 1
            if kind == "F" or (i < len(tokens) and tokens[i] == "["):
                vals = []
                if i < len(tokens) and tokens[i] == "[":
                    i += 1
                    while i < len(tokens) and tokens[i] != "]":
                        vals.append(tokens[i])
                        i += 1
                elif i < len(tokens):
                    vals.append(tokens[i])
                actions.append(("set", list(segs), leafseg, vals))
            else:
                if i < len(tokens):
                    val = tokens[i]
                    _validate_leaf_value(real, ch, val, i)
                else:
                    leaf_type = (ch.get("t") or "").lower()
                    if leaf_type.startswith("boolean"):
                        val = "true"   # A valueless boolean means enabled.
                        i -= 1
                    elif leaf_type.startswith("empty"):
                        val = ""
                        i -= 1
                    elif (ch.get("m"), real) in VALUELESS_STRING_LEAVES:
                        val = ""
                        i -= 1
                    else:
                        options = leaf_value_options(real, ch) or ()
                        raise ResolveError(i - 1, "incomplete command",
                                           list(options))
                actions.append(("set", list(segs), leafseg, val))
        i += 1
    if remove and len(segs) > len(ctx_segs):
        actions.append(("remove", list(segs)))
        return actions, ctx_segs
    if not actions and len(segs) > len(ctx_segs):
        actions.append(("create", list(segs)))
    if ends_on_node and len(segs) > len(ctx_segs):
        mode = segs
    elif deepest_list > len(ctx_segs):
        mode = segs[:deepest_list]
    else:
        mode = ctx_segs
    return actions, mode


def schema_list_instances_for(plane, base, body, candidate_roots=None):
    """Return existing list keys when a YANG path ends at a list.

    ``base`` is the current absolute context and ``body`` contains tokens typed
    from that context. ``None`` means the cursor is not at a list-key position;
    a list, including an empty one, means that list-key completion applies.
    """
    if not body:
        return None
    node = base[-1].node if base else {"c": plane.index}
    module = base[-1].module if base else None
    path_names = [s.name for s in base]
    path_keys = {
        pos: dict(seg.keys)
        for pos, seg in enumerate(base)
        if seg.keys
    }
    i = 0
    n = len(body)
    while i < n:
        tok = body[i]
        try:
            real, ch = lookup(node, tok)
        except ResolveError:
            return None
        if ch is None:
            return None
        kind = ch.get("k", "c")
        module = ch.get("m") or module
        path_names.append(real)
        if kind == "l":
            keys = ch.get("keys", [])
            cursor = i + 1
            supplied_vals = []
            explicit = ch.get("cli-explicit-keys")
            for key in keys:
                if cursor >= n:
                    if explicit:
                        return [(key, plane.desc(key))]
                    top = path_names[0] if path_names else real
                    found = plane.list_instances(
                        module, top, path_names, keys, path_keys,
                        supplied_vals)
                    for el in xml_path_elements(
                            list(candidate_roots or ()), path_names,
                            path_keys):
                        value = xml_child_text(el, key)
                        if value:
                            found.append((value, ""))
                    key_node = _children(ch).get(key, {})
                    schema_values = schema_leaf_value_options(
                        plane, key, key_node) or ()
                    curated = CURATED_LIST_KEY_OPTIONS.get((module, real), ())
                    return sorted(set(found)
                                  | {(v, "") for v in schema_values}
                                  | {(v, "") for v in curated})
                if explicit:
                    if not key.startswith(body[cursor]):
                        return [(key, plane.desc(key))]
                    cursor += 1
                    if cursor >= n:
                        top = path_names[0] if path_names else real
                        return plane.list_instances(
                            module, top, path_names, keys, path_keys,
                            supplied_vals)
                supplied_vals.append(body[cursor])
                cursor += 1
            if len(supplied_vals) < len(keys):
                top = path_names[0] if path_names else real
                return plane.list_instances(module, top, path_names, keys,
                                            path_keys, supplied_vals)
            key_pos = len(path_names) - 1
            path_keys[key_pos] = {
                key: supplied_vals[off] for off, key in enumerate(keys)
            }
            i = cursor
            node = ch
            continue
        node = ch
        i += 1
    return None
