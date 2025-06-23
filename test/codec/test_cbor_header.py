import json
import pytest
from iota.codec import cbor_header as CH

HDR = {"epoch": 99, "device": "uav-001", "sensor": [21.3, 48.1]}

def test_roundtrip():
    blob = CH.encode(HDR)
    out  = CH.decode(blob)
    assert out == HDR

def test_smaller_than_json():
    cbor_len  = len(CH.encode(HDR))
    json_len  = len(json.dumps(HDR, separators=(",", ":")).encode())
    assert cbor_len < json_len

def test_missing_dependency(monkeypatch):
    """Encode should raise if cbor2 is unavailable at runtime."""
    # Simulate missing library.
    monkeypatch.setattr(CH, "cbor2", None, raising=False)
    monkeypatch.setattr(CH, "_CBOR_MISSING",
                        ModuleNotFoundError("cbor2 gone"), raising=False)

    with pytest.raises(ModuleNotFoundError):
        CH.encode(HDR)