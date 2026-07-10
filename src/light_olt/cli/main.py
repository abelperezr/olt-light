"""Interactive session stack and executable entrypoint.

Entry point `light-olt` (console script). Parses argv, selects initial plane
(ihub/shelf/lt, default shelf), optional oneshot command, and runs the REPL
loop with readline completion.

Architecture
------------
- `repl()` manages a stack of CLI instances (one per plane). Forwarding pushes
  a new CLI onto the stack; logout/exit pops.
- `banner()` prints SSH-like login banner with source IP and timestamp.
- Readline completer caches per-(cli, line, cursor) to avoid re-walking schema
  on every TAB.
- `start_cli_watch` / `stop_cli_watch` manage the CommitWatcher per plane.
"""

import os
import re
import signal
import sys
import time

from .common import ECLI_VERSION, PLANES, tokenize
from .completion import COMPL, CURRENT_PROMPT, readline
from .confd_cli import ConfdCLI
from .md_cli import MdCli

def make_cli(ctx, user, lt_n=1):
    return MdCli(user) if ctx == "ihub" else ConfdCLI(ctx, user, lt_n)


def start_cli_watch(cli):
    start = getattr(cli, "start_commit_watcher", None)
    if start:
        start()


def stop_cli_watch(cli):
    stop = getattr(cli, "stop_commit_watcher", None)
    if stop:
        stop()


def banner(cli, user):
    src = (os.environ.get("SSH_CLIENT") or "").split()
    frm = src[0] if src else "console"
    print("%s connected from %s using ssh on %s" % (user, frm, cli.hostname()))
    print()
    print("Last login: %s." % time.strftime("%Y-%m-%dT%H:%M:%S%z"))
    print("Welcome, %s!" % user)


def repl(start_ctx, user, oneshot=None):
    stack = [make_cli(start_ctx, user)]
    watch_commits = oneshot is None and sys.stdin.isatty()

    def out(s):
        if s:
            print(s)

    def feed(cli, line):
        res = cli.handle(line, out)
        if res is None:
            return True
        if res[0] == "forward":
            tgt = res[1]
            new_cli = None
            if tgt == "ihub":
                new_cli = make_cli("ihub", user)
            elif re.fullmatch(r"lt-[1-4]", tgt):
                n = int(tgt.split("-", 1)[1])
                new_cli = make_cli("lt", user, n)
            else:
                out("Error: unknown forward target '%s'" % tgt)
            if new_cli is not None:
                if watch_commits:
                    start_cli_watch(new_cli)
                stack.append(new_cli)
            return True
        if res[0] == "logout":
            old = stack.pop()
            stop_cli_watch(old)
            return len(stack) > 0
        return True

    if oneshot is not None:
        for ln in oneshot.split(";"):
            if not stack or not feed(stack[-1], ln.strip()):
                break
        return 0

    if sys.stdin.isatty():
        banner(stack[0], user)
        if watch_commits:
            start_cli_watch(stack[0])

    if readline:
        completion_cache = {"key": None, "names": [], "desc": {}}

        def completer(text, state):
            try:
                cli = stack[-1]
                linebuf = readline.get_line_buffer()
                key = (id(cli), linebuf, readline.get_begidx(), text)
                if state == 0 or completion_cache["key"] != key:
                    buf = linebuf[: readline.get_begidx()]
                    toks = tokenize(buf)
                    items = cli.completion_options(toks, text)
                    completion_cache["key"] = key
                    completion_cache["names"] = [n for n, _ in items]
                    completion_cache["desc"] = dict(items)
                    COMPL.desc = completion_cache["desc"]
                    title = getattr(cli, "completion_title", None)
                    COMPL.title = (title(toks) if title
                                   else "Possible completions:")
                names = completion_cache["names"]
                return (names[state] + " ") if state < len(names) else None
            except Exception:
                return None
        readline.set_completer(completer)
        readline.set_completer_delims(" \t")
        readline.set_completion_display_matches_hook(COMPL.show)
        readline.parse_and_bind("tab: complete")
        readline.parse_and_bind('"?": possible-completions')

    while stack:
        cli = stack[-1]
        p = cli.prompt()
        CURRENT_PROMPT[0] = p.splitlines()[-1]
        try:
            line = input(p)
        except EOFError:
            print()
            old = stack.pop()
            stop_cli_watch(old)
            continue
        except KeyboardInterrupt:
            print()
            if isinstance(cli, ConfdCLI) and cli.config_mode:
                cli.config_mode = False
                cli.frames = []
            continue
        try:
            if not feed(cli, line):
                break
        except Exception as e:
            print("internal error: %s" % e)
    return 0


def main():
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except (AttributeError, ValueError):
        pass
    args = sys.argv[1:]
    user = os.environ.get("USER") or os.environ.get("LOGNAME") or "admin"
    ctx, oneshot = "shelf", None
    while args:
        a = args.pop(0)
        if a in PLANES:
            ctx = a
        elif a == "-c" and args:
            oneshot = args.pop(0)
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        elif a in ("-V", "--version"):
            print("ecli %s" % ECLI_VERSION)
            return 0
    return repl(ctx, user, oneshot)


if __name__ == "__main__":
    sys.exit(main())
