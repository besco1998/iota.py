"""
High-level helper: build a Prime-Fusion Beacon *and*
wrap it into a ProposedTransaction ready for `api.send_transfer`.

Example
-------
from iota import Iota, Address, Tag
from iota.fusion_send import build_fusion_tx

api = Iota('https://chrysalis-nodes.iota.org', seed='YOUR9SEED...')
tx  = build_fusion_tx(
        payload=b'SENSOR:21.3',
        destination=Address(b'YOURIOTAADDRESS999...'),
        tag=Tag(b'BEACON'),
        fusion_kwargs=dict(
            epoch_s=123, p_root_id=0xABCD,
            tip_ids=(0x111, 0x222),
            session_key=b'\x01'*16,
        ),
     )
api.send_transfer(depth=3, transfers=[tx])
"""
from __future__ import annotations
from typing   import Mapping, Any
from binascii import hexlify

from iota import ProposedTransaction, Address, Tag, TryteString
from iota.builders.beacon import BeaconBuilder

__all__ = ["build_fusion_tx"]

def build_fusion_tx(
    *,
    payload: bytes,
    destination: Address,
    tag: Tag | bytes = b'FUSION',
    fusion_kwargs: Mapping[str, Any],
    timestamp: int | None = None,
) -> ProposedTransaction:
    """
    Returns a **full ProposedTransaction** whose `message` field embeds a
    Prime-Fusion trailer.

    Parameters
    ----------
    payload       : binary payload to embed.
    destination   : 81-tryte IOTA address.
    tag           : IOTA Tag (≤ 27 trytes).
    fusion_kwargs : dict(epoch_s, p_root_id, tip_ids, session_key)
    timestamp     : Optional epoch seconds; defaults to `int(time.time())`.
    """
    # 1. build raw Beacon bytes
    tx_bytes = (BeaconBuilder(
                    payload=payload,
                    fusion=True,
                    fusion_kwargs=fusion_kwargs,
                ).build().raw_bytes)

    # 2. wrap in IOTA message (Trytes)
    msg_trytes = TryteString.from_bytes(tx_bytes)

    # 3. forge ProposedTransaction
    return ProposedTransaction(
        address   = destination,
        message   = msg_trytes,
        tag       = Tag(tag) if not isinstance(tag, Tag) else tag,
        value     = 0,
        timestamp = timestamp,
    )