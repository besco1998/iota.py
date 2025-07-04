from typing import Dict

# Define a few magic constants.
DEFAULT_PORT: int = 14265
"""
Default port to use when configuring an adapter, if the port is not
specified.
"""

TRITS_PER_TRYTE: int = 3
"""
Number of trits in a tryte.
Changing this will probably break everything, but there's a chance it
could create a sexy new altcoin instead.
In that way, it's kind of like toxic waste in a superhero story.
"""

STANDARD_UNITS: Dict[str, int] = {
    # Valid IOTA unit suffixes. Example value '-273.15 Ki'
    'i': 1,
    'Ki': 1000,
    'Mi': 1000000,
    'Gi': 1000000000,
    'Ti': 1000000000000,
    'Pi': 1000000000000000
}

# Activate codecs.
from .codecs import *

# Make some imports accessible from the top level of the package.
# Note that order is important, to prevent circular imports.
from .types import *
from .transaction import *
from .adapter import *
from .api_async import *
from .api import *
from .trits import *

# Expose Seed on the top level package
from .crypto.types import Seed

# :see: http://stackoverflow.com/a/2073599/
from pkg_resources import require
__version__ = require('PyOTA')[0].version
del require
# Adding Support for Prime-Fusion
from .crypto.prime_fusion import PrimeFusionCodec       # noqa: F401
from .builders.beacon import BeaconBuilder              # noqa: F401
from .fusion_send import build_fusion_tx                # noqa: F401
# Adding Support for CBOR Header
from .codec.cbor_header import encode as encode_cbor_header, decode as decode_cbor_header
# ---- Prime-Fusion patch: add fusion_kwargs to send_transfer ----
from .fusion_patch import Iota as _patched  # noqa: F401