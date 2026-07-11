"""SR OS MD-CLI-inspired interface for the IHUB plane.

Implements a Nokia SR OS style MD-CLI subset for the IHUB (iHub) plane:
- `configure global` enters candidate configuration mode.
- `{ ... }` brace blocks for multi-line config without navigation.
- `info` shows flat `head { tail }` output in current context.
- `commit` / `discard` / `exit` / `back` / `top` / `quit-config`.
- Abbreviated command matching with `?` completions.
- `ping` global command (also available in configure).
- Candidate edits serialized per-module and committed to running+startup
  via sysrepocfg.

Differences from ConfdCLI:
- Single context stack (ctx list of PathSeg) instead of frames.
- Navigation via `exit`/`back`/`top` modifies ctx; no frame push/pop.
- `info` renders nokia-conf as flat braces; ConfdCLI uses `show full-configuration`
  with ConfD-style indentation and `!` block terminators.
- No `forward` command (IHUB is the management plane root).
"""

import xml.etree.ElementTree as ET

from .backend import CommitWatcher, Plane, _loose
from .common import apply_filter, run_ping, split_pipe, tokenize
from .editing import EditSession
from .rendering import merge_overlay, mq, render_md_flat, segs_exist_in_running, strip_ns
from .schema import PathSeg, ResolveError, _children, resolve, schema_list_instances_for

class MdCli:
    def __init__(self, user):
        self.plane = Plane("ihub")
        self.user = user
        self.in_cfg = False
        self.ctx = []
        self.session = EditSession(self.plane)
        self._root = None
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

    def hostname(self):
        sig = self.plane.running_signature()
        if self._hostname_cache is not None and self._hostname_cache[0] == sig:
            return self._hostname_cache[1]
        xml = self.plane.export_xml(
            "running", "nokia-conf", xpath="/nokia-conf:configure/system/name")
        if xml:
            try:
                for el in ET.fromstring(xml).iter():
                    if strip_ns(el.tag) == "name" and (el.text or "").strip():
                        name = el.text.strip()
                        self._hostname_cache = (sig, name)
                        return name
            except ET.ParseError:
                pass
        name = "iHUB-OLT-LAB"
        self._hostname_cache = (sig, name)
        return name

    def cfg_root(self):
        if self._root is None:
            node = self.plane.index.get("configure") or _loose("nokia-conf")
            self._root = [PathSeg("configure", "nokia-conf", None, node)]
        return self._root

    def prompt(self):
        lines = [""]
        if self.in_cfg:
            star = "*" if self.session.dirty else ""
            ctx = " ".join(self.ctx_tokens())
            lines.append("%s[gl:configure%s]" % (star, (" " + ctx) if ctx else ""))
        lines.append("A:%s@%s# " % (self.user, self.hostname()))
        return "\n".join(lines)

    def ctx_tokens(self):
        toks = []
        for s in self.ctx:
            toks.append(s.name)
            toks += [mq(v) for v in (s.keys or {}).values()]
        return toks

    def completion_options(self, toks, partial):
        if not self.in_cfg:
            opts = {"configure": "Enter configuration context",
                    "ping": "Ping an IP address or DNS name",
                    "logout": "Log out of the system",
                    "exit": "Return to the previous context",
                    "quit": ""}
            if toks and "configure".startswith(toks[0]):
                opts = {"global": "- Enter global configuration mode"}
            elif toks:
                opts = {}
        else:
            opts = {"commit": "Commit the candidate configuration",
                    "discard": "Discard the candidate configuration",
                    "info": "Display configuration in the current context",
                    "exit": "Return to the previous context",
                    "back": "Navigate towards the root",
                    "top": "Navigate to the top of the context",
                    "delete": "Delete an element", "quit-config":
                    "Exit configuration mode"}
            base = self.cfg_root() + self.ctx
            node = base[-1].node
            body = toks[1:] if toks[:1] == ["delete"] else toks
            inst = schema_list_instances_for(self.plane, base, body)
            if inst is not None:
                opts = {n: d for n, d in inst}
                if partial:
                    opts = {n: d for n, d in opts.items()
                            if n.startswith(partial)}
                return sorted(opts.items())
            if body:
                try:
                    _, mode = resolve(self.plane, base, body)
                    node = mode[-1].node
                except ResolveError:
                    node = {"c": {}}
            for n in _children(node):
                opts[n] = self.plane.desc(n)
        if partial:
            opts = {n: d for n, d in opts.items() if n.startswith(partial)}
        return sorted(opts.items())

    def completion_title(self, toks):
        if (not self.in_cfg and toks
                and "configure".startswith(toks[0])):
            return "Configuration modes:"
        return "Possible completions:"

    @staticmethod
    def expand_command(token, names):
        if token in names:
            return token
        matches = [name for name in names if name.startswith(token)]
        return matches[0] if len(matches) == 1 else None

    def handle(self, line, out):
        line = line.rstrip()
        if not line.strip():
            return None
        if line.endswith("?"):
            base = line[:-1]
            toks = tokenize(base.replace("{", " ").replace("}", " "))
            partial = "" if (not base or base.endswith(" ")) else toks.pop()
            items = self.completion_options(toks, partial)
            if items:
                w = max(len(n) for n, _ in items) + 3
                lines = [self.completion_title(toks)]
                lines += [" %-*s%s" % (w, n, d) for n, d in items]
                out("\n".join(lines))
            return None
        cmd, pipe = split_pipe(line)
        toks = tokenize(cmd.replace("{", " { ").replace("}", " } "))
        if not toks:
            return None
        c = toks[0]
        if not self.in_cfg:
            oper_commands = ("configure", "ping", "logout", "exit", "quit")
            c = self.expand_command(c, oper_commands)
            if c is None:
                out("MINOR: MGMT_CORE #2201: Unknown element - '%s'" % toks[0])
                return None
            if c == "configure":
                if len(toks) == 1:
                    out("Configuration modes:\n"
                        " global   - Enter global configuration mode")
                    return None
                if (len(toks) == 2 and toks[1]
                        and "global".startswith(toks[1])):
                    self.in_cfg = True
                    self.ctx = []
                    return None
                bad = toks[1] if len(toks) > 1 else toks[0]
                out("MINOR: MGMT_CORE #2201: Unknown element - '%s'" % bad)
                return None
            if c == "ping":
                return run_ping(toks[1:], out)
            if c in ("logout", "exit", "quit"):
                return ("logout",)
        if c == "ping":                 # Available in every CLI context.
            return run_ping(toks[1:], out)
        if c == "exit":
            if toks[1:2] == ["all"]:
                self.ctx = []
            elif self.ctx:
                self.ctx.pop()
            else:
                self.in_cfg = False
            return None
        if c == "back":
            if self.ctx:
                self.ctx.pop()
            return None
        if c == "top":
            self.ctx = []
            return None
        if c == "quit-config":
            self.in_cfg = False
            self.ctx = []
            return None
        if c == "commit":
            errs = self.session.commit()
            for mod, e in errs:
                out("MINOR: MGMT_CORE #2301: %s" % e)
            return None
        if c == "discard":
            self.session = EditSession(self.plane)
            return None
        if c == "info":
            return self.do_info(toks[1:], pipe, out)
        if c == "logout":
            return ("logout",)
        if "{" in toks:
            try:
                h, t = toks.index("{"), toks.index("}")
            except ValueError:
                out("MINOR: MGMT_CORE #2201: Mismatched braces")
                return None
            flat = toks[:h] + toks[h + 1:t]
            nav = False
        else:
            flat = toks
            nav = True
        try:
            actions, mode = resolve(self.plane, self.cfg_root() + self.ctx,
                                    flat)
        except ResolveError as e:
            tok = flat[min(max(e.pos, 0), len(flat) - 1)]
            out("MINOR: MGMT_CORE #2201: Unknown element - '%s'" % tok)
            return None
        for a in actions:
            # Entering an existing context must not mark the candidate dirty.
            if a[0] == "create" and segs_exist_in_running(self.plane, a[1]):
                continue
            self.session.add(a)
        if nav:
            self.ctx = mode[len(self.cfg_root()):]
        return None

    def do_info(self, toks, pipe, out):
        lines = []
        root = None
        roots = self.plane.export_xml_roots(
            "running", "nokia-conf", clone=bool(self.session.roots))
        if roots:
            root = roots[0]
        if root is not None:
            for (_, _), eroot in self.session.roots.items():
                if eroot.tag == root.tag:
                    merge_overlay(root, eroot)
            cur = root
            for seg in self.ctx:
                nxt = None
                for ch in cur:
                    if strip_ns(ch.tag) != seg.name:
                        continue
                    ok = True
                    for k, v in (seg.keys or {}).items():
                        got = next((g.text for g in ch
                                    if strip_ns(g.tag) == k), None)
                        if got is not None and got != v:
                            ok = False
                            break
                    if ok:
                        nxt = ch
                        break
                cur = nxt
                if cur is None:
                    break
            if cur is not None:
                inode = (self.cfg_root() + self.ctx)[-1].node
                ich = _children(inode)
                for ch in cur:
                    render_md_flat(ch, [], lines, ich.get(strip_ns(ch.tag)))
        out(apply_filter("\n".join(lines), pipe))
        return None
