"""Readline completion display state shared by interactive sessions.

Completions class holds the description map and title printed by the
readline display hook (set_completion_display_matches_hook). CURRENT_PROMPT
stores the active prompt so the hook can redraw it after printing matches.

This is a tiny module because readline's hook API requires global-ish state;
the CLI classes populate COMPL.desc / COMPL.title before calling
readline's completion machinery.
"""

import sys

try:
    import readline
except ImportError:  # pragma: no cover - platforms without GNU readline
    readline = None

class Completions:
    """estado compartido entre completer y display hook de readline"""
    def __init__(self):
        self.desc = {}
        self.title = "Possible completions:"

    def show(self, substitution, matches, longest):
        try:
            buf = readline.get_line_buffer()
            print()
            print(self.title)
            w = max([len(m.strip()) for m in matches] + [10]) + 3
            for m in sorted(set(matches)):
                m = m.strip()
                d = self.desc.get(m, "")
                print("  %-*s%s" % (w, m, d) if d else "  " + m)
            sys.stdout.write(CURRENT_PROMPT[0] + buf)
            sys.stdout.flush()
        except Exception:
            pass


CURRENT_PROMPT = [""]
COMPL = Completions()
