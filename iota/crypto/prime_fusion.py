"""
PrimeFusion 10-byte trailer helpers
(see ‘PrimeFusion Ledger’ white-note, 2025)  # :contentReference[oaicite:0]{index=0}
"""
from __future__ import annotations
import hmac, hashlib, struct
from typing import Tuple

_MAGIC = 0xCF
_CRC_POLY = 0x1D  # 0x07 reflected – classic CRC-8

__all__ = ["PrimeFusionCodec"]

class PrimeFusionCodec:
    """Stateless helpers to pack / unpack the PrimeFusion trailer."""

    @staticmethod
    def _crc8(buf: bytes) -> int:
        crc = 0
        for b in buf:
            crc ^= b
            for _ in range(8):
                crc = ((crc << 1) ^ _CRC_POLY) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
        return crc

    # ————————————————————————————————————————————————————————— encode ———
    @classmethod
    def encode(
        cls,
        epoch_s: int,
        p_root_id: int,
        tip_ids: Tuple[int, int],
        session_key: bytes,
        header_and_payload: bytes,
    ) -> bytes:
        """
        Produce the 10-byte trailer.

        * `epoch_s`        : seconds mod 256.
        * `p_root_id`      : 16-bit short-ID of previous root.
        * `tip_ids`        : two 12-bit short-IDs (tuple order matters).
        * `session_key`    : 16/32 B AES-CMAC, reused for 1 s.
        * `header_and_payload` : bytes over which MAC8 is calculated.
        """
        if not (0 <= epoch_s < 256 and 0 <= p_root_id < 65536):
            raise ValueError("epoch or p_root_id out of range")

        a, b = tip_ids
        packed_tips = ((a & 0xFFF) << 12) | (b & 0xFFF)
        tip_bytes = packed_tips.to_bytes(3, "big")

        trailer = bytearray(9)               # magic-…-MAC8   (CRC8 added later)
        struct.pack_into(">BBH3s", trailer, 0,
                         _MAGIC,
                         epoch_s,
                         p_root_id,
                         tip_bytes)

        mac = hmac.new(session_key,
                       header_and_payload,
                       hashlib.sha256).digest()[:1]  # 8 bit trunc. (“MAC8”)
        trailer[7:8] = mac  # index 7 because we already consumed 7 bytes

        crc = cls._crc8(trailer)             # over first 9 B
        trailer.append(crc)
        return bytes(trailer)                # → 10 B

    # ————————————————————————————————————————————————————————— decode ———
    @classmethod
    def decode(cls, trailer: bytes, session_key: bytes,
               header_and_payload: bytes) -> dict:
        """Validate trailer, return parsed fields, raise `ValueError` on failure."""
        if len(trailer) != 10:
            raise ValueError("Trailer must be exactly 10 bytes")
        if trailer[0] != _MAGIC:
            raise ValueError("Bad magic 0x%02X" % trailer[0])

        epoch_s, p_root_id = struct.unpack_from(">BH", trailer, 1)
        packed_tips = int.from_bytes(trailer[4:7], "big")
        tip_ids = ((packed_tips >> 12) & 0xFFF, packed_tips & 0xFFF)
        mac8 = trailer[7]
        crc8 = trailer[9]

        if cls._crc8(trailer[:-1]) != crc8:
            raise ValueError("CRC-8 mismatch")

        ref_mac8 = hmac.new(session_key,
                            header_and_payload,
                            hashlib.sha256).digest()[0]
        if mac8 != ref_mac8:
            raise ValueError("MAC8 mismatch")

        return dict(epoch=epoch_s,
                    p_root_id=p_root_id,
                    tip_ids=tip_ids)

