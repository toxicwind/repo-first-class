"""repo-first-class: make any GitHub repo first-class.

One job: ``owner/repo`` -> canonical checkout -> polished tree ->
committed -> pushed -> remote SHA verified.

The :mod:`repo_first_class.checkout` module holds the checkout-state
verification logic; :mod:`repo_first_class.cli` exposes it as the
``repo-first-class`` command.
"""

from .checkout import (
    CheckoutState,
    Verdict,
    canonical_dest,
    ensure_checkout,
    git_dirty,
    git_head,
    parse_ensure_output,
    verify_state,
)

__all__ = [
    "CheckoutState",
    "Verdict",
    "canonical_dest",
    "ensure_checkout",
    "git_dirty",
    "git_head",
    "parse_ensure_output",
    "verify_state",
]

__version__ = "0.1.0"
