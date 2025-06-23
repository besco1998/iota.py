import time
from iota import Address, Tag, Iota
from iota.adapter import MockAdapter
from iota.fusion_send import build_fusion_tx
from iota.crypto.prime_fusion import PrimeFusionCodec as PF

SK = b'\xAA'*16

def test_build_and_decode():
    api = Iota(MockAdapter(), seed='A'*81)

    tx = build_fusion_tx(
        payload=b'PAY',
        destination=Address('Z'*81),
        tag=Tag(b'DEMO'),
        fusion_kwargs=dict(
            epoch_s=42,
            p_root_id=0xBEEF,
            tip_ids=(0x123, 0x456),
            session_key=SK,
        ),
        timestamp=1_600_000_000,
    )

    # Ensure ProposedTransaction looks sane
    chk = str(tx.address.with_valid_checksum())
    # 90-tryte address = 81 body + 9 checksum
    assert len(chk) == 90
    assert chk.startswith('Z' * 81)            # body remains unchanged
    assert tx.value == 0
    assert tx.tag   == Tag(b'DEMO')

    # Pull back the embedded trailer and verify
    raw = tx.message.as_bytes()              # back to bytes (may contain pad 0x00)

    # Trim any 0-padding that came from Tryte rounding.
    raw = raw.rstrip(b'\x00')

    # The Prime-Fusion trailer always starts with 0xCF.
    start = raw.rfind(b'\xCF')
    assert start != -1, "Trailer magic not found"

    trailer = raw[start : start + 10]
    header_and_payload = raw[:start]

    PF.decode(trailer, session_key=SK, header_and_payload=header_and_payload)

def test_tx_object_is_valid():
    """Ensure build_fusion_tx delivers a stand-alone ProposedTransaction."""
    tx = build_fusion_tx(
        payload=b'P',
        destination=Address('Z' * 81),
        fusion_kwargs=dict(
            epoch_s=0, p_root_id=0, tip_ids=(0, 0), session_key=SK,
        ),
    )

    # Basic sanity checks (no network needed)
    assert tx.value == 0
    assert isinstance(tx.address, Address)
    assert len(tx.message.as_bytes()) >= len(b'P') + 10   # payload + trailer