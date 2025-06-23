#!/usr/bin/env python3
"""
iota-fusion-send  –  push a Prime-Fusion beacon over IOTA from the shell.

Example
-------
iota-fusion-send \
    --addr WSACIMN...999 \
    --payload sensor.bin \
    --epoch auto \
    --p-root 0xCAFE \
    --tips 0x123 0x456
"""
from __future__ import annotations
import argparse, json, sys, time, sysconfig
from pathlib import Path
from secrets import token_bytes
from typing import List

from iota import Iota, Address, Tag, ProposedTransaction
from iota.adapter import MockAdapter   # replaced by real URL if --node given

from iota.builders.beacon import BeaconBuilder
from iota.codec.cbor_header import encode as cbor_encode, _CBOR_MISSING

# ─────────────────────────────────────────── helpers
def _parse_hex_int(s: str) -> int:
    base = 16 if s.lower().startswith("0x") else 10
    return int(s, base)

def _load_payload(path: str | Path) -> bytes:
    p = Path(path)
    if p == Path("-"):
        return sys.stdin.buffer.read()
    return p.read_bytes()

# ─────────────────────────────────────────── CLI
def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="iota-fusion-send",
                                 description="Send Prime-Fusion beacon.")
    g = ap.add_argument
    g("--node", metavar="URL",
      help="Full MQTT/HTTP node URL (default: mock adapter).")
    g("--seed", metavar="SEED", help="81-tryte seed (env var SEED also ok).")
    g("--addr", required=True, help="81-tryte destination address")
    g("--tag",  default="FUSION", help="Tx Tag (≤27 trytes)")

    # header / payload
    g("--payload", required=True,
      help="File with binary payload, or '-' to read stdin")
    g("--json-header", metavar="JSON",
      help="Inline JSON header (e.g. '{\"device\":\"uav-1\"}')")
    g("--header-file", metavar="FILE",
      help="Path to JSON header file (mutually exclusive)")

    # fusion specifics
    g("--epoch", default="auto",
      help="'auto' or integer 0-255")
    g("--p-root", required=True, type=_parse_hex_int,
      help="Previous root-ID (hex or dec)")
    g("--tips", nargs=2, required=True, type=_parse_hex_int,
      help="Two short tip-IDs")
    g("--key", metavar="HEX",
      help="Session key (hex). If omitted, random 16 bytes.")
    g("--cbor", action="store_true",
      help="Compress header with CBOR dictionary")
    g("--dry-run", action="store_true",
      help="Build packet but do NOT contact a node (prints trytes & exits 0)")      
    return ap

def main(argv: List[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)

    # ---------------- IOTA client
    adapter = args.node or MockAdapter()
    api = Iota(adapter, seed=args.seed or "A"*81)

    # ---------------- payload / header
    payload = _load_payload(args.payload)

    header = {}
    if args.json_header and args.header_file:
        sys.exit("Specify only one of --json-header or --header-file")
    if args.json_header:
        header = json.loads(args.json_header)
    elif args.header_file:
        header = json.loads(Path(args.header_file).read_text())

    # ---------------- fusion kwargs
    epoch = int(time.time()) % 256 if args.epoch == "auto" else int(args.epoch)
    fusion_kwargs = dict(
        epoch_s    = epoch,
        p_root_id  = args.p_root,
        tip_ids    = tuple(args.tips),
        session_key= bytes.fromhex(args.key) if args.key else token_bytes(16),
    )

    # ---------------- build beacon
    tx = (BeaconBuilder(
            payload = payload,
            header  = header,
            compress_header = args.cbor,
            fusion  = True,
            fusion_kwargs = fusion_kwargs,
         ).build())

    # ---------------- send or dry-run
    if args.dry_run:
        print("Trytes:", tx.as_tryte_string()[:60], "…")
        return

    res = api.send_transfer(
        depth=1,
        transfers=[
            ProposedTransaction(
                address=Address(args.addr),
                message=tx.as_tryte_string(),
                value=0,
                tag=Tag(args.tag),
            )
        ],
    )
    print("Bundle hash:", res["bundle"].hash)

if __name__ == "__main__":
    try:
        main()
    except _CBOR_MISSING:
        sys.exit("cbor2 not installed; run `pip install cbor2`")
    except Exception as exc:
        sys.exit(f"Error: {exc}")