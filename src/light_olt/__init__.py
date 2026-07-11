"""Public behavior layer for the Light OLT emulator.

The base image owns the NETCONF stack, YANG schemas, sysrepo repositories,
seeds, and startup supervision. This package supplies the part users are
expected to change: the interactive eCLI. The neighboring daemon scripts add
customizable ONU DHCP, optical diagnostics, and synthetic IPFIX behavior.

The eCLI connects to the independent IHUB, SHELF, and LT sysrepo repositories.
It combines the schema index generated while the base image is built with a
small fallback tree for mounted schemas, then applies configuration changes
through ``sysrepocfg``. The executable installed at ``/usr/local/bin/ecli``
imports this package from ``/opt/light-olt``.

Runtime behavior can be tuned with ``ECLI_COMMIT_POLL_SECONDS``,
``ONU_DHCP_POLL``, ``IPFIX_EMU_INTERVAL_SECS``, and
``ONU_OPTICS_REFRESH_SECS``. The base image supplies the per-plane
``SYSREPO_REPOSITORY_PATH`` and ``SYSREPO_SHM_PREFIX`` values.
"""

__all__ = ["cli"]
