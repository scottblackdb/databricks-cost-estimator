"""Lakebase-backed configuration loader for the cost estimator.

The Streamlit app runs as a Databricks App with a Lakebase Postgres resource
attached under the key `postgres` (see app.yaml). The platform auto-injects
the connection details as standard libpq env vars at runtime:

    PGHOST
    PGPORT
    PGDATABASE
    PGUSER
    PGSSLMODE

The Lakebase endpoint path is read from `ENDPOINT_NAME` and looks like
`projects/<project>/branches/<branch>/endpoints/<endpoint>`. The app uses
the Databricks SDK to mint a short-lived OAuth token for that endpoint and
uses it as the Postgres password.

Workload modules import this module instead of defining inline option dicts
and magic numbers. Results are cached with `st.cache_data` so the database
is hit at most once per (loader, args) every five minutes.
"""

from __future__ import annotations

import os
from contextlib import closing
from typing import Optional

import psycopg2
import streamlit as st


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def _env(*names: str, default: Optional[str] = None) -> Optional[str]:
    """Return the first non-empty environment variable from `names`."""
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return default


def _password() -> str:
    """Resolve the Postgres password.

    Prefers an explicit `PGPASSWORD` / `POSTGRES_PASSWORD` (useful for local
    dev). Otherwise asks the Databricks SDK to mint a short-lived OAuth
    token for the Lakebase endpoint — that's the standard pattern for
    Databricks Apps.
    """
    explicit = _env("PGPASSWORD", "POSTGRES_PASSWORD")
    if explicit:
        return explicit

    from databricks.sdk import WorkspaceClient

    endpoint = _env(
        "ENDPOINT_NAME",
        "POSTGRES_INSTANCE",
        "POSTGRES_ENDPOINT_NAME",
        "LAKEBASE_ENDPOINT_NAME",
        "PGAPPNAME",
    )
    if not endpoint:
        raise RuntimeError(
            "Could not locate the Lakebase endpoint name in the environment "
            "(checked ENDPOINT_NAME, POSTGRES_INSTANCE, POSTGRES_ENDPOINT_NAME, "
            "LAKEBASE_ENDPOINT_NAME, PGAPPNAME). Set one of these to your "
            "Lakebase endpoint path "
            "(e.g. 'projects/<project>/branches/<branch>/endpoints/primary'), "
            "or set PGPASSWORD / POSTGRES_PASSWORD directly."
        )

    cred = WorkspaceClient().postgres.generate_database_credential(endpoint=endpoint)
    return cred.token


def _connect():
    return psycopg2.connect(
        host=_env("PGHOST", "POSTGRES_HOST", "POSTGRES_PGHOST"),
        port=int(_env("PGPORT", "POSTGRES_PORT", "POSTGRES_PGPORT", default="5432")),
        dbname=_env("PGDATABASE", "POSTGRES_DATABASE_NAME", "POSTGRES_DATABASE", "POSTGRES_PGDATABASE"),
        user=_env("PGUSER", "POSTGRES_USER", "POSTGRES_PGUSER"),
        password=_password(),
        sslmode=_env("PGSSLMODE", "POSTGRES_SSLMODE", default="require"),
    )


def _query(sql: str, params: tuple):
    # `closing()` ensures the connection is actually closed — psycopg2's
    # `with conn:` only manages the transaction, not the connection lifetime.
    with closing(_connect()) as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


# ---------------------------------------------------------------------------
# Public loaders. Each is cached so the workload modules can call them on
# every Streamlit rerender without hammering Postgres.
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300, show_spinner=False)
def load_options(workload: str, option_group: str) -> dict[str, float]:
    """Return label -> multiplier for a workload's selectbox, in display order."""
    rows = _query(
        """
        SELECT label, multiplier
        FROM cost_estimator.workload_options
        WHERE workload = %s AND option_group = %s
        ORDER BY sort_order
        """,
        (workload, option_group),
    )
    if not rows:
        raise KeyError(f"No options found for workload={workload!r} group={option_group!r}")
    return {label: float(mult) for label, mult in rows}


@st.cache_data(ttl=300, show_spinner=False)
def load_constants(workload: str) -> dict[str, float]:
    """Return all scalar constants for a workload as {name: value}."""
    rows = _query(
        """
        SELECT name, value
        FROM cost_estimator.workload_constants
        WHERE workload = %s
        """,
        (workload,),
    )
    if not rows:
        raise KeyError(f"No constants found for workload={workload!r}")
    return {name: float(value) for name, value in rows}


@st.cache_data(ttl=300, show_spinner=False)
def load_rates() -> dict[str, float]:
    """Return all global rates as {name: value}."""
    rows = _query("SELECT name, value FROM cost_estimator.rates", ())
    return {name: float(value) for name, value in rows}


# ---------------------------------------------------------------------------
# Admin loaders + writers — used by the Configure page. These are NOT cached
# because the editor needs to see the current state of Postgres on each open.
# ---------------------------------------------------------------------------

def load_all_rates() -> list[dict]:
    rows = _query(
        "SELECT name, value, COALESCE(description, '') AS description "
        "FROM cost_estimator.rates ORDER BY name",
        (),
    )
    return [{"name": n, "value": float(v), "description": d} for n, v, d in rows]


def load_all_constants() -> list[dict]:
    rows = _query(
        "SELECT workload, name, value, COALESCE(description, '') AS description "
        "FROM cost_estimator.workload_constants "
        "ORDER BY workload, name",
        (),
    )
    return [
        {"workload": w, "name": n, "value": float(v), "description": d}
        for w, n, v, d in rows
    ]


def load_all_options() -> list[dict]:
    rows = _query(
        "SELECT workload, option_group, label, multiplier, sort_order "
        "FROM cost_estimator.workload_options "
        "ORDER BY workload, option_group, sort_order",
        (),
    )
    return [
        {
            "workload": w,
            "option_group": g,
            "label": l,
            "multiplier": float(m),
            "sort_order": int(s),
        }
        for w, g, l, m, s in rows
    ]


def save_rate_values(updates: list[tuple[str, float]]) -> None:
    """Apply rate edits. `updates` is a list of (name, new_value)."""
    if not updates:
        return
    with closing(_connect()) as conn, conn.cursor() as cur:
        cur.executemany(
            "UPDATE cost_estimator.rates SET value = %s WHERE name = %s",
            [(v, n) for n, v in updates],
        )
        conn.commit()


def save_constant_values(updates: list[tuple[str, str, float]]) -> None:
    """Apply workload-constant edits. `updates` is (workload, name, new_value)."""
    if not updates:
        return
    with closing(_connect()) as conn, conn.cursor() as cur:
        cur.executemany(
            "UPDATE cost_estimator.workload_constants "
            "SET value = %s WHERE workload = %s AND name = %s",
            [(v, w, n) for w, n, v in updates],
        )
        conn.commit()


def save_option_values(updates: list[tuple[str, str, str, float, int]]) -> None:
    """Apply workload-option edits.

    `updates` is (workload, option_group, label, new_multiplier, new_sort_order).
    """
    if not updates:
        return
    with closing(_connect()) as conn, conn.cursor() as cur:
        cur.executemany(
            "UPDATE cost_estimator.workload_options "
            "SET multiplier = %s, sort_order = %s "
            "WHERE workload = %s AND option_group = %s AND label = %s",
            [(m, s, w, g, l) for w, g, l, m, s in updates],
        )
        conn.commit()
