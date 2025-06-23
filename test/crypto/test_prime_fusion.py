import pytest
from iota.crypto.prime_fusion import PrimeFusionCodec as PF

SK   = b'\x01' * 16
DATA = b'ABC'

def test_roundtrip_ok():
    tr = PF.encode(epoch_s=11, p_root_id=0xCAFE,
                   tip_ids=(0x123, 0x456),
                   session_key=SK, header_and_payload=DATA)
    out = PF.decode(tr, session_key=SK, header_and_payload=DATA)
    assert out["epoch"] == 11
    assert out["tip_ids"] == (0x123, 0x456)

@pytest.mark.parametrize("idx", range(10))
def test_corruption_fails(idx):
    tr = bytearray(PF.encode(epoch_s=1, p_root_id=2,
                             tip_ids=(3, 4), session_key=SK,
                             header_and_payload=DATA))
    tr[idx] ^= 0xFF
    with pytest.raises(ValueError):
        PF.decode(bytes(tr), session_key=SK, header_and_payload=DATA)