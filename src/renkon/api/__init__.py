# pyright: reportUnusedImport=false
"""
Exposes the (dev)user-facing Renkon API. Think scipy.stats.api or statsmodels.api,
that is, an API which is ergonomic for use in a notebook/interactive session (less OO).

This is the only module that needs to be imported by the user. Submodules don't
need to be imported for namespacing to work, e.g. sample need not be imported::

    import renkon as rk

    df.filter(rk.sample.const(k=10).mask)

In this case, `rk.sample` works as an alias for `rk.core.sample`.
"""

__all__ = ["stats"]

from renkon.api import stats
from renkon.util.polars import RenkonPolarsUtils  # noqa: F401
