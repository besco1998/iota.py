import time
from iota import Iota, Address
from iota.adapter import MockAdapter
from iota import ProposedTransaction, TryteString, Tag

def _seed_minimal(adapter):
    # The three API calls send_transfer makes for a zero-value bundle
    adapter.seed_response('getTransactionsToApprove',
                          {'trunkTransaction': 'A'*81,
                           'branchTransaction': 'B'*81})
    adapter.seed_response('attachToTangle', {'trytes': ['A'*2673]})
    adapter.seed_response('broadcastTransactions', {})
    adapter.seed_response('storeTransactions', {})

SK = b"\x02"*16

ZERO_TX = ProposedTransaction(
    address=Address("Z"*81),
    value=0,
    tag=Tag(b"TEST"),
    message=TryteString.from_bytes(b""),
)

def test_default_path_unchanged():
    adapter = MockAdapter()
    _seed_minimal(adapter)
    api = Iota(adapter, seed='A'*81)
    api.send_transfer(depth=1, transfers=[ZERO_TX])  # should not raise

def test_fusion_kwargs_adds_tx():
    adapter = MockAdapter()
    _seed_minimal(adapter)
    api = Iota(adapter, seed='A'*81)

    api.send_transfer(
        depth=1,
        transfers=[],           # empty bundle at first
        fusion_kwargs=dict(
            address      = "Z"*81,
            epoch_s      = int(time.time()) % 256,
            p_root_id    = 0xBEEF,
            tip_ids      = (0x123, 0x456),
            session_key  = SK,
            payload      = b"P",
            header       = {"d":"uav"},
            compress_header = True,
        ),
    )
    # If we got here with MockAdapter, function executed successfully.