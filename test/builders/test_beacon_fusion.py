from iota.builders.beacon import BeaconBuilder
from iota.crypto.prime_fusion import PrimeFusionCodec as PF

SK = b'\x99' * 16

def _builder(fusion: bool):
    return BeaconBuilder(
        payload=b'DATA',
        tags=('demo',),
        fusion=fusion,
        fusion_kwargs=dict(
            epoch_s=200,
            p_root_id=0xBEEF,
            tip_ids=(0xAAA, 0xBBB),
            session_key=SK,
        ),
    )

def test_default_no_trailer():
    tx = _builder(False).build()
    assert tx.raw_bytes == b'DATA'

def test_fusion_appends_valid_trailer():
    tx = _builder(True).build()
    trailer = tx.raw_bytes[-10:]
    PF.decode(trailer, session_key=SK, header_and_payload=b'DATA')