import subprocess, sys, json, os
from pathlib import Path

BIN = Path(sys.executable).with_suffix('')  # python launcher
SCRIPT = "-m"                                # run module
MOD = "iota.cli.fusion_send"

def test_cli_mockadapter(tmp_path):
    payload = tmp_path / "p.bin"
    payload.write_bytes(b"PAY")

    cmd = [
        BIN, SCRIPT, MOD,
        "--addr", "Z"*81,
        "--payload", str(payload),
        "--p-root", "0",
        "--tips", "1", "2",
        "--epoch", "0",
        "--cbor",
        "--dry-run",
        # mock node & seed default
    ]
    out = subprocess.check_output(cmd, text=True)
    assert out.startswith("Trytes:")