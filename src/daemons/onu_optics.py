#!/usr/bin/env python3
"""
onu_optics.py — publishes operational optical diagnostics per ONU for the
OLT emulator.

Why this exists
---------------
The Pazel `/optics` endpoint (services/lightspan/optics_service.py) queries
via NETCONF GET the subtree:

  onus/onu/root/hardware-state/component[class=transceiver-link]
      /transceiver-link/diagnostics/{tx-bias, rx-power, tx-power,
       laser-temperature, rx-power-dbm, tx-power-dbm}

On a real OLT those values are published by the management plane as operational
state (config=false). In the emulator they don't exist, so `/optics` returned
empty. This daemon synthesizes them with random-but-deterministic, time-stable-
with-jitter values per authenticated ONU, and pushes to the operational
datastore using the same `oper_push` binary used by autofind.

Authentication gate
-------------------
Reuses the IPFIX exporter inventory: only authenticated ONUs (admin-unlocked /
online) receive diagnostics, so a newly created but not yet activated ONU
doesn't show power levels (consistent with the exporter gate). If
IPFIX_EMU_REQUIRE_AUTH=0, applies to all configured ONUs.

Scales (must match optics_service._scale):
  rx-power-dbm / tx-power-dbm : dBm * 10        (int, e.g. -2007 => -20.07 dBm)
  tx-bias                     : 2 uA  -> mA*1000 divides /1000 in client,
                                  but model uses 'units 2 uA'. Client does
                                  raw/1000 => we store micro-amperes.
  rx-power / tx-power         : 0.1 mW -> client divides /10 (mW)
  laser-temperature           : 1/256 C; client divides /100. To display ~C,
                                  we store C*100.

Usage:
  onu_optics.py [--once]
Variables:
  ONU_OPTICS_REFRESH_SECS   (default 30)  regeneration interval
  ONU_OPTICS_OUT            (default /run/np2/onu_optics_oper.xml)
  IPFIX_EMU_RANDOM_SEED     shared seed with exporter
  IPFIX_EMU_REQUIRE_AUTH    auth gate (default 1)
"""
from __future__ import annotations

import math
import os
import random
import subprocess
import sys
import time
from pathlib import Path

# Reuse the IPFIX exporter's resolved, authentication-gated inventory instead
# of maintaining another sysrepo parser here.
from ipfix_exporter import (
    InventoryCache,
    Onu,
    env_bool,
    env_int,
    log as _log,
)

NS_BBF_ONU = "urn:bbf:params:xml:ns:yang:bbf-fiber-onu-emulated-mount"
NS_HW_MOUNTED = "urn:ietf:params:xml:ns:yang:ietf-hardware-mounted"
NS_HW_TYPES = "urn:bbf:yang:bbf-hardware-types"
NS_HW_XCVR = "urn:bbf:yang:bbf-hardware-transceivers-mounted"
NS_NOKIA_DBM = (
    "http://www.nokia.com/Fixed-Networks/BBA/yang/"
    "nokia-hardware-transceivers-dbm-mounted"
)

OUT_PATH = os.environ.get("ONU_OPTICS_OUT", "/run/np2/onu_optics_oper.xml")
OPER_PUSH = os.environ.get("ONU_OPTICS_OPER_PUSH", "/usr/local/bin/oper_push")


def log(msg: str) -> None:
    _log(f"[optics] {msg}")


def _stable_rng(onu: Onu) -> random.Random:
    """Build a deterministic per-ONU RNG that survives restarts."""
    base_seed = env_int("IPFIX_EMU_RANDOM_SEED", 20260614)
    key = (onu.serial or onu.name).encode("utf-8", "ignore")
    h = 0
    for b in key:
        h = (h * 131 + b) & 0xFFFFFFFF
    return random.Random(base_seed ^ h)


def _diag_values(onu: Onu, tick: int) -> dict[str, int]:
    """Generate stable diagnostic baselines with small time-based jitter.

    Realistic GPON/XGS-PON ranges:
      rx-power : -28 .. -8  dBm (typical optical plant)
      tx-power : +0.5 .. +5 dBm
      tx-bias  : 5 .. 25 mA
      laser-temp: 35 .. 55 C
    """
    rng = _stable_rng(onu)
    rx_base = rng.uniform(-26.0, -10.0)
    tx_base = rng.uniform(1.0, 4.5)
    bias_base = rng.uniform(7.0, 22.0)
    temp_base = rng.uniform(38.0, 52.0)

    # Gentle jitter preserves the stable correlation with the serial number.
    phase = (hash(onu.name) & 0xFF) / 40.0
    rx = rx_base + 0.6 * math.sin(tick / 5.0 + phase)
    tx = tx_base + 0.25 * math.sin(tick / 6.0 + phase)
    bias = bias_base + 0.8 * math.sin(tick / 4.0 + phase)
    temp = temp_base + 1.5 * math.sin(tick / 9.0 + phase)

    # Convert to the raw units expected by the client-side scaling code.
    # rx/tx-power-dbm : dBm*10 (optics_service divide /10)
    # rx/tx-power     : 0.1 mW; the client divides by 10, so store mW*10.
    #                   mW = 10^(dBm/10).
    rx_mw = 10 ** (rx / 10.0)
    tx_mw = 10 ** (tx / 10.0)
    return {
        "rx_power_dbm": int(round(rx * 10)),
        "tx_power_dbm": int(round(tx * 10)),
        "rx_power": int(round(rx_mw * 10)),       # Client /10 => mW.
        "tx_power": int(round(tx_mw * 10)),
        "tx_bias": int(round(bias * 1000)),        # Client /1000 => mA.
        "laser_temperature": int(round(temp * 100)),  # Client /100 => C.
    }


def _component_xml(onu: Onu, tick: int) -> str:
    d = _diag_values(onu, tick)
    comp_name = f"{onu.name}/XVPS/1"
    return (
        '      <component>\n'
        f'        <name>{comp_name}</name>\n'
        f'        <class xmlns:bbf-hw-types="{NS_HW_TYPES}">'
        'bbf-hw-types:transceiver-link</class>\n'
        f'        <transceiver-link xmlns="{NS_HW_XCVR}">\n'
        '          <diagnostics>\n'
        f'            <tx-bias>{d["tx_bias"]}</tx-bias>\n'
        f'            <tx-power>{d["tx_power"]}</tx-power>\n'
        f'            <rx-power>{d["rx_power"]}</rx-power>\n'
        f'            <laser-temperature>{d["laser_temperature"]}</laser-temperature>\n'
        f'            <tx-power-dbm xmlns="{NS_NOKIA_DBM}">{d["tx_power_dbm"]}</tx-power-dbm>\n'
        f'            <rx-power-dbm xmlns="{NS_NOKIA_DBM}">{d["rx_power_dbm"]}</rx-power-dbm>\n'
        '          </diagnostics>\n'
        '        </transceiver-link>\n'
        '      </component>\n'
    )


def _onu_xml(onu: Onu, tick: int) -> str:
    return (
        '  <onu>\n'
        f'    <name>{onu.name}</name>\n'
        '    <root>\n'
        f'      <hardware-state xmlns="{NS_HW_MOUNTED}">\n'
        f'{_component_xml(onu, tick)}'
        '      </hardware-state>\n'
        '    </root>\n'
        '  </onu>\n'
    )


def build_xml(onus: tuple[Onu, ...], tick: int) -> str:
    body = "".join(_onu_xml(o, tick) for o in onus)
    return f'<onus xmlns="{NS_BBF_ONU}">\n{body}</onus>\n'


def write_and_push(xml: str) -> int:
    Path(OUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(OUT_PATH).write_text(xml)
    if not os.path.exists(OPER_PUSH):
        log(f"oper_push not found at {OPER_PUSH}; wrote XML to {OUT_PATH}")
        return 0
    env = os.environ.copy()
    env.setdefault("SYSREPO_REPOSITORY_PATH", "/repo/lt")
    env.setdefault("SYSREPO_SHM_PREFIX", "lt_")
    # oper_push stays resident and watches mtime. Relaunch it after each refresh
    # so the operational data follows both the jitter and authenticated ONU
    # inventory. The caller terminates the previous resident process.
    proc = subprocess.Popen(
        [OPER_PUSH, OUT_PATH], env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    return proc.pid


def main() -> int:
    if not env_bool("ONU_OPTICS_ENABLED", True):
        log("ONU_OPTICS_ENABLED=0; optics daemon disabled")
        return 0

    once = "--once" in sys.argv
    refresh = env_int("ONU_OPTICS_REFRESH_SECS", 30)
    seed_path = os.environ.get("IPFIX_EMU_ONTS_OPER", "/seeds/onts_oper.xml")
    max_onus = env_int("IPFIX_EMU_MAX_ONUS", 0)
    max_pons = env_int("IPFIX_EMU_MAX_PONS", 0)

    cache = InventoryCache(seed_path, max_onus, max_pons, refresh)
    tick = 0
    last_pid: int | None = None

    while True:
        inv = cache.get()
        xml = build_xml(inv.onus, tick)
        # End the previous push session so stale data disappears before the
        # refreshed set is applied.
        if last_pid:
            try:
                os.kill(last_pid, 15)
            except ProcessLookupError:
                pass
        last_pid = write_and_push(xml)
        log(f"published optical diagnostics for {len(inv.onus)} ONUs (tick={tick})")
        tick += 1
        if once:
            return 0
        time.sleep(max(5, refresh))


if __name__ == "__main__":
    sys.exit(main())
