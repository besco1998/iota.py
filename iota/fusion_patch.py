from iota import Iota
from typing import Any, List
from .fusion_tx import build_from_kwargs
from typing import Any, List, Optional
if not hasattr(Iota, "_fusion_patch_applied"):

    orig_send_transfer = Iota.send_transfer

    def send_transfer(self, depth: int, transfers: Optional[List[Any]] = None, *a,
                      fusion_kwargs: Optional[dict] = None, **kw):
        # If user passes fusion_kwargs *and* did NOT build the beacon
        # themselves, build + append one transfer for them.
        if transfers is None:
            transfers = []
        if fusion_kwargs:
            transfers = list(transfers)   # copy (may be empty)
            transfers.append(build_from_kwargs(fusion_kwargs))
        return orig_send_transfer(self, depth=depth, transfers=transfers,
                                  *a, **kw)

    Iota.send_transfer = send_transfer                   # type: ignore[assignment]
    Iota._fusion_patch_applied = True