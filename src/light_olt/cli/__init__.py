"""Interactive eCLI support for the IHUB, SHELF, and LT planes.

SHELF and LT use :class:`ConfdCLI`, while IHUB uses :class:`MdCli`. Both
frontends share schema navigation, candidate editing, rendering, completion,
and the sysrepo-backed :class:`Plane` abstraction. A CLI session can move from
SHELF to another plane without dropping its SSH connection.

The base image generates ``/etc/olt/cli_index_<plane>.json.gz``. At runtime,
the backend fills gaps in mounted schemas with a curated fallback tree. This
keeps list-key completion and navigation useful even when the generated index
contains only part of a mounted subtree.
"""

from .common import ECLI_VERSION

__all__ = ["ECLI_VERSION"]
