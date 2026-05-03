"""Lakebase-backed configuration loader for the cost estimator.

The Streamlit app runs as a Databricks App with a Lakebase Postgres resource
attached under the key `postgres` (see app.yaml). That binding exposes the
connection details as environment variables:

    POSTGRES_HOST
    POSTGRES_PORT
    POSTGRES_DATABASE_NAME
    POSTGRES_USER
    POSTGRES_INSTANCE_NAME    (Lakebase only — used to mint OAuth tokens)
    POSTGRES_PASSWORD         (optional; if absent we mint an OAuth token)

All workload modules import this module instead of defining inline option
dicts and magic numbers. Results are cached with st.cache_data so the
database is hit at most once per (loader, args) every five minutes.
"""

from __future__ import annotations

import os
import uuid
from collections import OrderedDict
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

    Prefers an explicit `POSTGRES_PASSWORD` (useful for local dev). Otherwise
    asks the Databricks SDK to mint a short-lived OAuth token for the
    Lakebase instance — that's the standard pattern for Databricks Apps.
    """
    explicit = _env("POSTGRES_PASSWORD", "PGPASSWORD")
    if explicit:
        return explicit

    from databricks.sdk import WorkspaceClient

    instance = _env("POSTGRES_INSTANCE_NAME", "PGINSTANCE")
    if not instance:
        raise RuntimeError(
            "No POSTGRES_PASSWORD set and POSTGRES_INSTANCE_NAME is missing — "
            "cannot mint a Lakebase OAuth token."
        )

    cred = WorkspaceClient().database.generate_database_credential(
        request_id=str(uuid.uuid4()),
        instance_names=[instance],
    )
    return cred.token


def _connect():
    return psycopg2.connect(
        host=_env("POSTGRES_HOST", "PGHOST"),
        port=int(_env("POSTGRES_PORT", "PGPORT", default="5432")),
        dbname=_env("POSTGRES_DATABASE_NAME", "POSTGRES_DATABASE", "PGDATABASE"),
        user=_env("POSTGRES_USER", "PGUSER"),
        password=_password(),
        sslmode=_env("POSTGRES_SSLMODE", "PGSSLMODE", default="require"),
    )


def _query(sql: str, params: tuple):
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


# ---------------------------------------------------------------------------
# Public loaders. Each is cached so the workload modules can call them on
# every Streamlit rerender without hammering Postgres.
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300, show_spinner=False)
def load_options(workload: str, option_group: str) -> "OrderedDict[str, float]":
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
    return OrderedDict((label, float(mult)) for label, mult in rows)


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
    """Return all global rates as {name: value} (replaces set_rates.py)."""
    rows = _query("SELECT name, value FROM cost_estimator.rates", ())
    return {name: float(value) for name, value in rows}
