"""
Tiny wrapper around `cbor2` that:
• converts frequent string keys ⇢ small ints (static dictionary),
• encodes with canonical CBOR (deterministic),
• round-trips back to the original dict.

If `cbor2` is missing, `encode()` raises ImportError so callers can
fall back to JSON.
"""
from __future__ import annotations
from typing import Dict, Any, Mapping

try:
    import cbor2
except ModuleNotFoundError as exc:            # pragma: no cover
    cbor2 = None                              # noqa: N816
    _CBOR_MISSING = exc
else:
    # create a placeholder so callers can always `raise _CBOR_MISSING`
    _CBOR_MISSING = ModuleNotFoundError("optional dependency 'cbor2' not installed")

# ---- static key dictionary ------------------------------------------------
_KDICT: Dict[str, int] = {
    "epoch"  : 0,
    "device" : 1,
    "lat"    : 2,
    "lon"    : 3,
    "alt"    : 4,
    "sensor" : 5,
    # add more if you like
}

def _map_keys(d: Mapping[str, Any], encode: bool) -> Dict[Any, Any]:
    if encode:
        return {_KDICT.get(k, k): v for k, v in d.items()}
    # decode path
    rev = {v: k for k, v in _KDICT.items()}
    return {rev.get(k, k): v for k, v in d.items()}

# ---- public API -----------------------------------------------------------
def encode(header: Mapping[str, Any]) -> bytes:
    if cbor2 is None:
        raise _CBOR_MISSING       # caller decides what to do
    mapped = _map_keys(header, encode=True)
    return cbor2.dumps(mapped, canonical=True)

def decode(blob: bytes) -> Dict[str, Any]:
    if cbor2 is None:
        raise _CBOR_MISSING
    mapped = cbor2.loads(blob)
    return _map_keys(mapped, encode=False)