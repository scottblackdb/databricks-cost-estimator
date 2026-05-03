"""Backward-compatible shim around db_config.load_rates().

Older code (e.g. get_estimate.py) imports this module and reads
`set_rates.rates['storage']` / `set_rates.csp_modifier`. We preserve that
surface area but back it with the Lakebase `cost_estimator.rates` table
instead of hardcoded values.
"""

import db_config


def __getattr__(name):
    if name == "rates":
        return db_config.load_rates()
    if name == "csp_modifier":
        return db_config.load_rates().get("csp_modifier", 0)
    raise AttributeError(name)
