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


CURATED_VALUE_OPTIONS = {
    ("bbf-xpon", "authentication-method"): (
        "serial-number", "registration-id", "as-per-v-ani-expected", "loid",
    ),
    ("bbf-xpon", "channel-pair-type"): (
        "fiftyg-twdm", "fiftyg-tdm", "twentyfivegs", "ngpon2-twdm",
        "ngpon2-ptp", "xgs", "xgpon", "gpon",
    ),
    ("nokia-mcast-cac", "max-group-number"): ("no-limit",),
    ("nokia-mcast-cac", "max-multicast-rate-limit"): ("no-limit",),
    ("nokia-mcast-cac", "multicast-rate-limit-exceed-action"):
        ("drop", "best-effort"),
}

UINT_OR_NO_LIMIT_LEAVES = {
    "max-group-number", "max-multicast-rate-limit",
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
    return CURATED_VALUE_OPTIONS.get((node.get("m"), name))


def _validate_leaf_value(name, node, value, pos):
    options = leaf_value_options(name, node)
    if options is None or value in options:
        return
    if name in UINT_OR_NO_LIMIT_LEAVES and re.fullmatch(r"[0-9]+", value):
        return
    raise ResolveError(pos, "invalid value", list(options))


def schema_value_options(plane, base, tokens):
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
            i += 1 + len(child.get("keys", []))
            if i > len(tokens):
                return None
            node = child
            continue
        if kind == "c":
            node = child
            i += 1
            continue
        if kind in ("f", "F") and i == len(tokens) - 1:
            return leaf_value_options(real, child)
        return None
    return None


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
                    if (ch.get("t") or "").lower().startswith("boolean"):
                        val = "true"   # A valueless boolean means enabled.
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


def schema_list_instances_for(plane, base, body):
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
            supplied = n - (i + 1)
            supplied_vals = body[i + 1:i + 1 + min(supplied, len(keys))]
            if supplied < len(keys):
                top = path_names[0] if path_names else real
                return plane.list_instances(module, top, path_names, keys,
                                            path_keys, supplied_vals)
            key_pos = len(path_names) - 1
            path_keys[key_pos] = {
                key: body[i + 1 + off] for off, key in enumerate(keys)
            }
            i += 1 + len(keys)
            node = ch
            continue
        node = ch
        i += 1
    return None
