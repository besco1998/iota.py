"""
Minimal ‘BeaconBuilder’ that can optionally append a
Prime-Fusion trailer.  It does **NOT** replace or modify any
core PyOTA class; it just builds an immutable wrapper object.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Mapping, Any
from ..crypto.prime_fusion import PrimeFusionCodec as PF
import sys
@dataclass(frozen=True, **({"slots": True} if sys.version_info >= (3,10) else {}))
class _BeaconTx:
    raw_bytes: bytes
    tags:       Sequence[str]

    # helper if users want trytes later
    def as_tryte_string(self):
        from iota import TryteString
        return TryteString.from_bytes(self.raw_bytes)

class BeaconBuilder:
    """
    Parameters
    ----------
    payload : bytes         – binary message body.
    tags    : Iterable[str] – optional application tags.
    fusion  : bool          – set True to append Prime-Fusion trailer.
    fusion_kwargs : mapping – required if fusion=True:
          {epoch_s, p_root_id, tip_ids, session_key}
    """
    def __init__(
        self,
        *,
        payload: bytes,
        header: Mapping[str, Any] | None = None,
        tags: Sequence[str] = (),
        fusion: bool = False,
        fusion_kwargs: Mapping[str, Any] | None = None,
        compress_header: bool = False,
    ):
        self._payload        = payload
        self._header  = header or {}
        self._tags           = tags
        self._fusion         = fusion
        self._fusion_kwargs  = dict(fusion_kwargs or {})
        if not fusion:            #  ←  new
            self._fusion_kwargs.clear()
        self._compress_header = compress_header

    # ------------------------------------------------ build --------------
    def build(self) -> _BeaconTx:
        # ---- header serialisation (JSON fallback) -------------------------
        import json
        from iota.codec import cbor_header  # local import to avoid hard dep

        try:
            if self._compress_header and self._header:
                header_bytes = cbor_header.encode(self._header)
            else:
                raise ImportError           # jump to fallback
        except ImportError:
            header_bytes = (
                json.dumps(self._header, separators=(",", ":")).encode()
                if self._header else
                b""
            )
        
        
        raw = self._payload          # header-less “tx” for our demo

        if self._fusion:
            trailer = PF.encode(
                epoch_s     = self._fusion_kwargs.pop("epoch_s"),
                p_root_id   = self._fusion_kwargs.pop("p_root_id"),
                tip_ids     = self._fusion_kwargs.pop("tip_ids"),
                session_key = self._fusion_kwargs.pop("session_key"),
                header_and_payload = header_bytes + raw,
            )
            raw += trailer                      # append immutably

        # guard against typos
        if self._fusion_kwargs:
            raise TypeError(f"Unexpected fusion kw: {list(self._fusion_kwargs)}")

        return _BeaconTx(raw_bytes=raw, tags=self._tags)