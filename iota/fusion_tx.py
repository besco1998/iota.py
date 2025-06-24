"""
Helper that converts `fusion_kwargs` (dict) into a ready‐made
`ProposedTransaction`.  Meant to be called by `Iota.send_transfer`.
"""
from __future__ import annotations
from typing import Mapping, Any
from iota import Address, Tag, ProposedTransaction, TryteString
from .builders.beacon import BeaconBuilder

def build_from_kwargs(k: Mapping[str, Any]) -> ProposedTransaction:
    k = dict(k)                       # work on a copy
    # --- pull out fields meant for ProposedTransaction itself
    address = k.pop("address")
    tag     = k.pop("tag", "FUSION")
    value   = k.pop("value", 0)

    # --- optional header/payload helpers
    payload = k.pop("payload", b"")
    header  = k.pop("header",  {})
    compress_header = bool(k.pop("compress_header", False))

    beacon = (BeaconBuilder(
                payload          = payload,
                header           = header,
                compress_header  = compress_header,
                fusion           = True,
                fusion_kwargs    = k,              # epoch_s, p_root_id, ...
              ).build())

    return ProposedTransaction(
        address = Address(address),
        value   = value,
        tag     = Tag(tag),
        message = beacon.as_tryte_string(),
    )