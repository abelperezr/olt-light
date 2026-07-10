"""ConfD-like operational and configuration CLI for SHELF and LT planes.

This is the main CLI class emulating the SROS / Lightspan ConfD CLI
behavior: operational mode (`#`), configuration mode (`(config)#`), context
stack navigation, list key completion from running datastore, `forward cli
to <target>` for plane hopping, and commit watcher for NETCONF commit
notifications.

Key behaviors replicated from real OLT:
- Abbreviated command matching (unique prefix).
- List key completion shows *only existing instances* from running (not
  schema placeholders), matching ConfD/SRL behavior.
- `show full-configuration` in a config submode scopes to current context.
- `do <oper-command>` from config mode.
- Commit watcher prints async "System message..." when running datastore
  changes via NETCONF (suppressed for 5s after local commit).
- Forward targets derived from SHELF hardware inventory (Board-LTn
  components), not hardcoded.

Schema navigation uses the merged index from backend.Plane.index (generated
+ curated fallback). resolve() walks the schema returning actions
(create/set/remove) and the deepest list/container as the new config mode.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET

from .backend import CONFD_PREAMBLE, CommitWatcher, Plane
from .common import (
    BUILTIN_CONFIG, BUILTIN_OPER, apply_filter, run_ping, split_pipe, tokenize,
)
from .editing import EditSession
from .rendering import (
    merge_overlay, render_confd, segs_exist_in_running, strip_ns,
    xml_child_text, xml_roots,
)
from .schema import (
    PathSeg, ResolveError, _children, lookup, resolve,
    schema_list_instances_for,
)

class ConfdCLI:
    def __init__(self, plane_name, user, lt_n=1):
        if plane_name == "lt" and lt_n > 1 \
                and os.path.isdir("/repo/lt%d" % lt_n):
            plane_name = "lt%d" % lt_n     # plano LT clonado (OLT_LT_PLANES)
        self.plane = Plane(plane_name)
        self.user = user
        self.lt_n = lt_n
        self.config_mode = False
        self.frames = []   # pila de modos; cada frame = ruta absoluta [PathSeg]
        self.session = EditSession(self.plane)
        self._commit_watcher = None
        self._hostname_cache = None

    def start_commit_watcher(self):
        if self._commit_watcher is None:
            self._commit_watcher = CommitWatcher(self.plane, self.user)
            self._commit_watcher.start()

    def stop_commit_watcher(self):
        if self._commit_watcher is not None:
            self._commit_watcher.stop()
            self._commit_watcher = None

    def ctx(self):
        return self.frames[-1] if self.frames else []

    def hostname(self):
        sig = self.plane.running_signature()
        if self._hostname_cache is not None and self._hostname_cache[0] == sig:
            return self._hostname_cache[1]
        xml = self.plane.export_xml("running", "ietf-system")
        if xml:
            try:
                hn = ET.fromstring(xml).findtext(
                    "{urn:ietf:params:xml:ns:yang:ietf-system}hostname")
                if hn:
                    name = hn.strip()
                    self._hostname_cache = (sig, name)
                    return name
            except ET.ParseError:
                pass
        if self.plane.name == "lt":
            name = "LT%d-GPON" % self.lt_n
        else:
            name = "isam-reborn"
        self._hostname_cache = (sig, name)
        return name

    def prompt(self):
        hn = self.hostname()
        if not self.config_mode:
            return "%s# " % hn
        if self.frames:
            last = self.frames[-1][-1]
            key = "-".join((last.keys or {}).values())
            return "%s(config-%s%s)# " % (hn, last.name,
                                          ("-" + key) if key else "")
        return "%s(config)# " % hn

    # ---------- ayuda ------------------------------------------------------
    def _list_instances_for(self, base, body):
        return schema_list_instances_for(self.plane, base, body)

    def _schema_completion(self, base, body):
        inst = self._list_instances_for(base, body)
        if inst is not None:
            return {n: d for n, d in inst}, True
        node = base[-1].node if base else {"c": self.plane.index}
        if body:
            try:
                _, mode = resolve(self.plane, base, body)
                node = mode[-1].node if mode else node
            except ResolveError:
                return {}, False
        return {n: self.plane.desc(n) for n in _children(node)}, False

    def _schema_path_error(self, body):
        if not body:
            return None
        try:
            resolve(self.plane, [], body)
            return None
        except ResolveError as e:
            return e

    def _show_completion(self, body):
        show_cmds = {
            "full-configuration": "Show complete running configuration",
            "configuration": "Show running configuration",
            "hardware-state": self.plane.desc("hardware-state")
                              or "Data nodes for the operational state of components.",
            "interfaces-state": "Operational interface state",
        }
        if not body:
            opts = dict(show_cmds)
            for n in self.plane.index:
                opts.setdefault(n, self.plane.desc(n))
            return opts
        first = body[0]
        if "full-configuration".startswith(first) or "configuration".startswith(first):
            if len(body) == 1:
                return {n: self.plane.desc(n) for n in self.plane.index}
            opts, _ = self._schema_completion([], body[1:])
            return opts
        if "hardware-state".startswith(first):
            return {"component": "Hardware component"}
        opts, _ = self._schema_completion([], body)
        return opts

    def oper_builtins(self):
        """Comandos operacionales disponibles en el contexto actual."""
        builtins = dict(BUILTIN_OPER)
        if self.plane.name != "shelf":
            builtins.pop("forward", None)
        return builtins

    def forward_targets(self):
        """Destinos existentes, derivados del inventario del SHELF.

        Altiplano crea un componente Board-LTn al insertar cada tarjeta. Ese
        inventario es la fuente de verdad tanto para el TAB como para validar
        un ``forward`` escrito a mano. El IHUB no es una Board y se ofrece
        siempre como destino fijo del SHELF.
        """
        if self.plane.name != "shelf":
            return []
        slots = set()
        for datastore in ("operational", "running"):
            xml = self.plane.export_xml(datastore, "ietf-hardware")
            for root in xml_roots(xml):
                for component in root.iter():
                    if strip_ns(component.tag) != "component":
                        continue
                    name = xml_child_text(component, "name") or ""
                    match = re.fullmatch(r"Board-LT([1-4])", name,
                                         re.IGNORECASE)
                    if match:
                        slots.add(int(match.group(1)))
            # operational normalmente ya es la vista combinada. Solo leer
            # running por separado cuando esa vista no contiene tarjetas.
            if slots:
                break
        return ["ihub"] + ["lt-%d" % n for n in sorted(slots)]

    def completion_options(self, toks, partial):
        """[(nombre, desc)] para el token parcial actual"""
        opts = {}
        if not self.config_mode:
            if not toks:
                for n, d in self.oper_builtins().items():
                    opts[n] = d
                for n in self.plane.index:
                    opts.setdefault(n, self.plane.desc(n))
            elif self.plane.name == "shelf" and toks[:1] == ["forward"]:
                if toks == ["forward"]:
                    opts = {"cli": "Forward CLI sessions"}
                elif toks == ["forward", "cli"]:
                    opts = {"to": ""}
                elif toks == ["forward", "cli", "to"]:
                    opts = {target: "" for target in self.forward_targets()}
            elif toks[:1] == ["show"]:
                opts = self._show_completion(toks[1:])
            elif toks:
                try:
                    root, _ = lookup({"c": self.plane.index}, toks[0])
                except ResolveError:
                    root = None
                if root:
                    opts, _ = self._schema_completion([], toks)
        else:
            base = self.ctx()
            node = base[-1].node if base else {"c": self.plane.index}
            body = toks[1:] if toks[:1] == ["no"] else toks
            if toks[:1] == ["show"]:
                opts = self._show_completion(toks[1:])
                if partial:
                    opts = {n: d for n, d in opts.items()
                            if n.startswith(partial)}
                return sorted(opts.items())
            if toks[:1] == ["do"] and toks[1:2] == ["show"]:
                opts = self._show_completion(toks[2:])
                if partial:
                    opts = {n: d for n, d in opts.items()
                            if n.startswith(partial)}
                return sorted(opts.items())
            # Caminamos el schema por nombres registrando la ruta de nodos y
            # cuantas keys lleva consumidas la ultima lista. Esto es
            # independiente de resolve() (que es greedy con las keys y aborta
            # con 'incomplete command' justo en el caso que nos interesa).
            inst = self._list_instances_for(base, body)
            if inst is not None:
                # Esperando la key de una lista: la OLT real muestra SOLO las
                # instancias existentes (mas el placeholder del nombre de key),
                # sin los builtins de config.
                for kname, kdesc in inst:
                    opts.setdefault(kname, kdesc)
                if partial:
                    opts = {n: d for n, d in opts.items()
                            if n.startswith(partial)}
                return sorted(opts.items())
            schema_started = False
            if body:
                for start_node in (node, {"c": self.plane.index}):
                    try:
                        _, ch = lookup(start_node, body[0])
                    except ResolveError:
                        ch = None
                    if ch is not None:
                        schema_started = True
                        break
            for n, d in BUILTIN_CONFIG.items():
                opts[n] = d
            if body:
                try:
                    _, mode = resolve(self.plane, base, body)
                    node = mode[-1].node if mode else node
                except ResolveError:
                    if schema_started:
                        return []
                    node = {"c": {}}
            for n, nd in _children(node).items():
                opts.setdefault(n, self.plane.desc(n))
        if partial:
            opts = {n: d for n, d in opts.items() if n.startswith(partial)}
        return sorted(opts.items())

    def print_completions(self, items, out):
        if not items:
            out("Possible completions:\n  <cr>")
            return
        w = max(len(n) for n, _ in items) + 3
        lines = ["Possible completions:"]
        for n, d in items:
            lines.append(("  %-*s%s" % (w, n, d)).rstrip())
        out("\n".join(lines))

    # ---------- dispatch ---------------------------------------------------
    def handle(self, line, out):
        line = line.rstrip()
        if not line.strip():
            return None
        if line.rstrip().endswith("?"):
            base = line.rstrip()[:-1]
            toks = tokenize(base)
            partial = "" if (not base or base.endswith(" ")) else toks.pop()
            self.print_completions(self.completion_options(toks, partial), out)
            return None
        cmd, pipe = split_pipe(line)
        toks = tokenize(cmd)
        if not toks:
            return None
        if self.config_mode:
            return self.handle_config(toks, pipe, out, line)
        return self.handle_oper(toks, pipe, out, line)

    def expand_builtin(self, tok, table):
        if tok in table:
            return tok
        hits = [n for n in table if n.startswith(tok)]
        return hits[0] if len(hits) == 1 else None

    def handle_oper(self, toks, pipe, out, raw):
        names = self.oper_builtins()
        for n in self.plane.index:
            names.setdefault(n, "")
        c = self.expand_builtin(toks[0], names)
        if c is None:
            hits = sorted(n for n in names if n.startswith(toks[0]))
            if hits:
                self.print_completions(
                    [(h, names.get(h) or self.plane.desc(h)) for h in hits],
                    out)
            else:
                self.syntax_error(raw, toks, 0, out)
            return None
        if c == "config":
            self.config_mode = True
            self.frames = []
            out("Entering configuration mode terminal")
            return None
        if c == "ping":
            return run_ping(toks[1:], out)
        if c == "show":
            show_body = toks[1:]
            if show_body:
                first = show_body[0]
                path = None
                offset = 1
                if ("full-configuration".startswith(first)
                        or "configuration".startswith(first)):
                    path = show_body[1:]
                    offset = 2
                elif first in self.plane.index:
                    path = show_body
                if path and len(path) > 1:
                    err = self._schema_path_error(path)
                    if err is not None:
                        err.pos += offset
                        self.syntax_error(raw, toks, err.pos, out)
                        return None
            return self.do_show(toks[1:], pipe, out, raw)
        if c == "forward":
            if toks[1:3] == ["cli", "to"] and len(toks) == 4:
                target = toks[3].lower()
                match = re.fullmatch(r"lt-?([1-4])", target)
                if match:
                    target = "lt-%d" % int(match.group(1))
                if target in self.forward_targets():
                    return ("forward", target)
                out("Error: unavailable forward target '%s'" % toks[3])
                return None
            out("Usage: forward cli to <ihub|lt-N>")
            return None
        if c in ("logout", "exit", "quit"):
            return ("logout",)
        if c == "pwd":
            out("At top level")
            return None
        if c == "id":
            out("user = %s, gid=20, euid=0, egid=0, groups=admin"
                % self.user)
            return None
        if c == "who":
            out("Session  User     Context  From          Proto    Date     Mode\n"
                "*1       %-8s cli      console       ssh      -        operational"
                % self.user)
            return None
        if c == "help":
            self.print_completions(sorted(self.oper_builtins().items()), out)
            return None
        if c in self.plane.index:
            # nodo YANG en modo operacional -> muestra su subarbol
            if len(toks) > 1:
                err = self._schema_path_error(toks)
                if err is not None:
                    self.syntax_error(raw, toks, err.pos, out)
                    return None
            return self.do_show(toks, pipe, out, raw)
        return None

    def handle_config(self, toks, pipe, out, raw):
        c = self.expand_builtin(toks[0], BUILTIN_CONFIG) or toks[0]
        if c == "commit":
            errs = self.session.commit()
            if errs:
                for mod, e in errs:
                    out("Aborted: %s" % e)
            else:
                out("Commit complete.")
            return None
        if c == "exit":
            if self.frames:
                self.frames.pop()
            else:
                self.leave_config(out)
            return None
        if c == "exit-all":
            self.frames = []
            return None
        if c == "top":
            self.frames = []
            if len(toks) > 1:
                return self.handle_config(toks[1:], pipe, out, raw)
            return None
        if c == "end":
            self.leave_config(out)
            return None
        if c == "abort":
            self.session = EditSession(self.plane)
            self.config_mode = False
            self.frames = []
            return None
        if c == "pwd":
            if not self.frames:
                out("At top level")
            else:
                path = []
                for s in self.frames[-1]:
                    path.append(s.name)
                    path += list((s.keys or {}).values())
                out("Current mode path: " + " ".join(path))
            return None
        if c == "do":
            return self.handle_oper(toks[1:], pipe, out, raw)
        if c == "show":
            sub = toks[1:2]
            if sub and "full-configuration".startswith(sub[0]):
                return self.show_full(toks[2:], pipe, out)
            if sub and "configuration".startswith(sub[0]):
                return self.show_full(toks[2:], pipe, out)
            return self.do_show(toks[1:], pipe, out, raw)
        if c == "help":
            self.print_completions(sorted(BUILTIN_CONFIG.items()), out)
            return None
        # comando de configuracion: intenta en el modo actual y, si el
        # PRIMER token no existe ahi, sube por los modos ancestros hasta
        # la raiz (comportamiento del eCLI real)
        bases = [list(f) for f in reversed(self.frames)] + [[]]
        actions = mode = None
        used = len(bases) - 1
        last_err = None
        for bi, base in enumerate(bases):
            try:
                actions, mode = resolve(self.plane, base, toks)
                used = bi
                break
            except ResolveError as e:
                last_err = e
                if e.pos == 0 and not e.options and bi < len(bases) - 1:
                    continue
                if e.options:
                    self.print_completions(
                        [(o, self.plane.desc(o)) for o in e.options], out)
                else:
                    self.syntax_error(raw, toks, e.pos, out)
                return None
        if actions is None:
            self.syntax_error(raw, toks, last_err.pos if last_err else 0, out)
            return None
        for a in actions:
            # navegar a un contexto existente no ensucia la sesion
            if a[0] == "create" and segs_exist_in_running(self.plane, a[1]):
                continue
            self.session.add(a)
        # recorta la pila al frame usado y apila el nuevo modo si profundizo
        keep = len(self.frames) - used
        self.frames = self.frames[:max(keep, 0)]
        base_len = len(bases[used])
        if len(mode) > base_len:
            self.frames.append(list(mode))
        return None

    def leave_config(self, out):
        if self.session.dirty:
            if sys.stdin.isatty():
                while True:
                    answer = input(
                        "Uncommitted changes found, commit them? [yes/no/CANCEL] "
                    ).strip()
                    if not answer:
                        answer = "yes"
                    answer_l = answer.lower()
                    if answer_l in ("yes", "y"):
                        break
                    if answer_l in ("no", "n"):
                        self.session = EditSession(self.plane)
                        self.config_mode = False
                        self.frames = []
                        return True
                    if answer_l in ("cancel", "c"):
                        return False
                    out("Please answer yes, no, or CANCEL.")
            else:
                out("Uncommitted changes found, commit them? [yes/no/CANCEL] yes")
            errs = self.session.commit()
            if errs:
                for mod, e in errs:
                    out("Aborted: %s" % e)
                self.session = EditSession(self.plane)
            else:
                out("Commit complete.")
        self.config_mode = False
        self.frames = []
        return True

    # ---------- show -------------------------------------------------------
    def do_show(self, toks, pipe, out, raw=""):
        if toks and "full-configuration".startswith(toks[0]):
            return self.show_full(toks[1:], pipe, out)
        if toks and ("hardware-state".startswith(toks[0])
                     or toks[0] == "hardware"):
            return self.show_hw(pipe, out)
        if toks and toks[0] == "interfaces-state":
            return self.show_interfaces_state(toks[1:], pipe, out)
        return self.show_full(toks, pipe, out)

    def show_interfaces_state(self, filter_toks, pipe, out):
        roots = self.plane.export_xml_roots(
            "operational", "ietf-interfaces", clone=False)
        top = next((r for r in roots if strip_ns(r.tag) == "interfaces-state"), None)
        if top is None:
            out("")
            return None

        node = top
        toks = list(filter_toks)
        while toks and node is not None:
            name = toks.pop(0)
            if name == "interface" and toks:
                if_name = toks.pop(0)
                node = next(
                    (
                        child for child in node
                        if strip_ns(child.tag) == "interface"
                        and xml_child_text(child, "name") == if_name
                    ),
                    None,
                )
                continue
            node = next(
                (child for child in node if strip_ns(child.tag) == name),
                None,
            )

        lines = []
        if node is not None:
            render_confd(node, "", 0, lines)
        text = "\n".join(lines)
        out(apply_filter(text, pipe))
        return None

    def show_full(self, filter_toks, pipe, out):
        root_name = filter_toks[0] if filter_toks else None
        root_node = self.plane.root_node(root_name) if root_name else None
        # En un submodo de config (p.ej. config-onu-ONT-001) y sin filtro
        # explicito, 'show full-configuration' se acota al contexto actual,
        # como la OLT real: muestra solo el subarbol del frame vigente.
        ctx = self.ctx()
        if root_node is None and not filter_toks and ctx:
            top_seg = ctx[0]
            root_name = top_seg.name
            module = top_seg.module
            roots = self.plane.export_xml_roots(
                "running", module, clone=bool(self.session.roots))
            for (_, _), eroot in self.session.roots.items():
                if strip_ns(eroot.tag) != root_name:
                    continue
                hit = next((b for b in roots if b.tag == eroot.tag), None)
                if hit is None:
                    roots.append(ET.fromstring(ET.tostring(eroot)))
                else:
                    merge_overlay(hit, eroot)
            # localizar el subarbol exacto del contexto (siguiendo keys)
            lines = []
            for top in roots:
                if strip_ns(top.tag) != root_name:
                    continue
                sub = self._descend_to_ctx(top, ctx)
                if sub is not None:
                    render_confd(sub, "", 0, lines)
            out(apply_filter("\n".join(lines), pipe))
            return None
        if root_node:
            lines = []
            module = root_node.get("m")
            schema_ctx = None
            if len(filter_toks) > 1:
                try:
                    _, schema_ctx = resolve(self.plane, [], filter_toks)
                except ResolveError:
                    schema_ctx = None
            roots = self.plane.export_xml_roots(
                "running", module, clone=bool(self.session.roots))
            for (_, _), eroot in self.session.roots.items():
                if strip_ns(eroot.tag) != root_name:
                    continue
                hit = next((b for b in roots if b.tag == eroot.tag), None)
                if hit is None:
                    roots.append(ET.fromstring(ET.tostring(eroot)))
                else:
                    merge_overlay(hit, eroot)
            for top in roots:
                if strip_ns(top.tag) == root_name:
                    if schema_ctx and len(schema_ctx) > 1:
                        sub = self._descend_to_ctx(top, schema_ctx)
                        if sub is not None:
                            render_confd(sub, "", 0, lines)
                    else:
                        render_confd(top, "", 0, lines)
            text = "\n".join(lines)
            if len(filter_toks) > 1 and not schema_ctx:
                pat = " ".join(filter_toks[1:])
                text = "\n".join(l for l in text.splitlines() if pat in l)
            out(apply_filter(text, pipe))
            return None

        lines = CONFD_PREAMBLE.format(port=self.plane.port).splitlines()
        roots = self.plane.export_xml_roots(
            "running", clone=bool(self.session.roots))
        for (_, _), eroot in self.session.roots.items():
            hit = next((b for b in roots if b.tag == eroot.tag), None)
            if hit is None:
                roots.append(ET.fromstring(ET.tostring(eroot)))
            else:
                merge_overlay(hit, eroot)
        for top in roots:
            render_confd(top, "", 0, lines)
        text = "\n".join(lines)
        if filter_toks:
            pat = " ".join(filter_toks)
            text = "\n".join(l for l in text.splitlines() if pat in l)
        out(apply_filter(text, pipe))
        return None

    def _descend_to_ctx(self, top_el, ctx):
        """Desde el elemento raiz <top>, baja siguiendo los segmentos del
        contexto (ctx[1:]; ctx[0] es el propio top) hasta el subarbol del
        submodo actual. Para listas, casa por el valor de la(s) key(s).
        Devuelve el elemento o None si no existe en el datastore."""
        cur = top_el
        for seg in ctx[1:]:
            found = None
            for child in cur:
                if strip_ns(child.tag) != seg.name:
                    continue
                if seg.keys:
                    ok = True
                    for k, v in seg.keys.items():
                        kv = xml_child_text(child, k)
                        if kv != v:
                            ok = False
                            break
                    if not ok:
                        continue
                found = child
                break
            if found is None:
                return None
            cur = found
        return cur

    def show_hw(self, pipe, out):
        xml = (self.plane.export_xml("operational", "ietf-hardware")
               or self.plane.export_xml("running", "ietf-hardware"))
        rows = []
        if xml:
            try:
                ns = "{urn:ietf:params:xml:ns:yang:ietf-hardware}"
                for comp in ET.fromstring(xml).iter(ns + "component"):
                    nm = comp.findtext(ns + "name") or ""
                    extra = (comp.findtext(ns + "model-name")
                             or comp.findtext(ns + "description") or "")
                    rows.append((nm, extra))
            except ET.ParseError:
                pass
        rows.sort()
        w = max([len(r[0]) for r in rows] + [10]) + 3
        lines = ["Possible completions:"]
        for nm, ex in rows:
            lines.append(("  %-*s%s" % (w, nm, ex)).rstrip())
        lines.append("  %-*s%s" % (w, "|", "Output modifiers"))
        lines.append("  <cr>")
        out(apply_filter("\n".join(lines), pipe))
        return None

    def syntax_error(self, raw, toks, pos, out):
        tok = toks[min(pos, len(toks) - 1)]
        col = raw.find(tok)
        col = col if col >= 0 else len(raw)
        out("-" * (len(self.prompt()) + col) + "^")
        out("syntax error: element does not exist")
