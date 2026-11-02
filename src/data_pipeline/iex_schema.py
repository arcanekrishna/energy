"""
IEX market schema definitions and validation.

Defines the canonical constants, time-block mappings, grid operating
regimes, and the ``MarketRecord`` dataclass used throughout the
Indian Power Market Intelligence pipeline.

Key design notes
----------------
* **96 blocks** of 15 minutes each per day (IEX convention).
* **48 RTM sessions**, each covering 2 consecutive blocks.
* CERC price bounds: Rs 0 – Rs 10,000 / MWh.
* All block numbers are 1-indexed (block 1 = 00:00–00:15 IST).
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Global constants
# ---------------------------------------------------------------------------

BLOCKS_PER_DAY: int = 96
"""Number of 15-minute time blocks per day on IEX."""

SESSIONS_PER_DAY: int = 48
"""Number of RTM sessions per day (each session clears 2 blocks)."""

CERC_PRICE_CAP: float = 10_000.0
"""CERC-mandated maximum clearing price in Rs / MWh."""

CERC_PRICE_FLOOR: float = 0.0
"""CERC-mandated minimum clearing price in Rs / MWh."""

BLOCK_DURATION_MIN: int = 15
"""Duration of each block in minutes."""

DAM_GATE_CLOSURE_HOUR: int = 14
"""Approximate hour (IST, 24-h) when DAM gate closes on D-1."""

RTM_GATE_LEAD_MIN: int = 60
"""Minutes before delivery that the RTM gate closes."""


# ---------------------------------------------------------------------------
# Grid operating regimes
# ---------------------------------------------------------------------------

class GridRegime(str, Enum):
    """
    Named grid operating regimes keyed to IEX 15-min block ranges.

    Each member maps to a ``(start_block, end_block)`` tuple (inclusive,
    1-indexed).  The EVENING_RAMP regime is where DAM→RTM stress
    typically concentrates due to the solar generation ramp-down.
    """

    NIGHT = "night"
    MORNING_RAMP = "morning_ramp"
    SOLAR_PEAK = "solar_peak"
    EVENING_RAMP = "evening_ramp"
    LATE_EVENING = "late_evening"


#: Block ranges (inclusive, 1-indexed) for each regime.
REGIME_BLOCK_RANGES: dict[GridRegime, Tuple[int, int]] = {
    GridRegime.NIGHT: (1, 24),           # 00:00 – 06:00
    GridRegime.MORNING_RAMP: (25, 40),   # 06:00 – 10:00
    GridRegime.SOLAR_PEAK: (41, 64),     # 10:00 – 16:00
    GridRegime.EVENING_RAMP: (65, 84),   # 16:00 – 21:00
    GridRegime.LATE_EVENING: (85, 96),   # 21:00 – 24:00
}

#: Subset of evening blocks where solar-ramp stress is most acute.
EVENING_STRESS_BLOCKS: Tuple[int, int] = (68, 82)  # 17:00 – 20:30


# ---------------------------------------------------------------------------
# Time / block / session mapping helpers
# ---------------------------------------------------------------------------

def block_to_time(block_no: int) -> Tuple[dt.time, dt.time]:
    """Return the (start_time, end_time) for a 1-indexed block number.

    Parameters
    ----------
    block_no : int
        Block number in [1, 96].

    Returns
    -------
    tuple[datetime.time, datetime.time]
        Start and end IST times of the block.

    Raises
    ------
    ValueError
        If *block_no* is outside [1, 96].

    Examples
    --------
    >>> block_to_time(1)
    (datetime.time(0, 0), datetime.time(0, 15))
    >>> block_to_time(96)
    (datetime.time(23, 45), datetime.time(0, 0))
    """
    if not 1 <= block_no <= BLOCKS_PER_DAY:
        raise ValueError(
            f"block_no must be in [1, {BLOCKS_PER_DAY}], got {block_no}"
        )
    start_min = (block_no - 1) * BLOCK_DURATION_MIN
    end_min = block_no * BLOCK_DURATION_MIN

    start = dt.time(start_min // 60, start_min % 60)
    end = dt.time(end_min // 60 % 24, end_min % 60)
    return start, end


def block_to_hour(block_no: int) -> float:
    """Return the fractional hour corresponding to the *start* of a block.

    Parameters
    ----------
    block_no : int
        Block number in [1, 96].

    Returns
    -------
    float
        E.g. block 1 → 0.0, block 5 → 1.0, block 68 → 16.75.
    """
    if not 1 <= block_no <= BLOCKS_PER_DAY:
        raise ValueError(
            f"block_no must be in [1, {BLOCKS_PER_DAY}], got {block_no}"
        )
    return (block_no - 1) * BLOCK_DURATION_MIN / 60.0


def session_to_blocks(session_id: int) -> Tuple[int, int]:
    """Return the two block numbers covered by an RTM session.

    RTM session *k* (1-indexed) covers blocks ``(2k-1, 2k)``.

    Parameters
    ----------
    session_id : int
        Session number in [1, 48].

    Returns
    -------
    tuple[int, int]
        (first_block, second_block).

    Raises
    ------
    ValueError
        If *session_id* is outside [1, 48].
    """
    if not 1 <= session_id <= SESSIONS_PER_DAY:
        raise ValueError(
            f"session_id must be in [1, {SESSIONS_PER_DAY}], got {session_id}"
        )
    first_block = 2 * session_id - 1
    return first_block, first_block + 1


def block_to_session(block_no: int) -> int:
    """Return the RTM session that covers a given block.

    Parameters
    ----------
    block_no : int
        Block number in [1, 96].

    Returns
    -------
    int
        Session number in [1, 48].
    """
    if not 1 <= block_no <= BLOCKS_PER_DAY:
        raise ValueError(
            f"block_no must be in [1, {BLOCKS_PER_DAY}], got {block_no}"
        )
    return (block_no + 1) // 2


def dam_gate_closure(delivery_date: dt.date) -> dt.datetime:
    """Return the approximate DAM gate closure datetime (IST) for *delivery_date*.

    DAM auction for Day D is conducted on Day D-1 and the gate
    closes at approximately 14:00 IST.

    Parameters
    ----------
    delivery_date : datetime.date
        The delivery date (Day D).

    Returns
    -------
    datetime.datetime
        Gate closure timestamp on D-1.
    """
    d_minus_1 = delivery_date - dt.timedelta(days=1)
    return dt.datetime.combine(d_minus_1, dt.time(DAM_GATE_CLOSURE_HOUR, 0))


def rtm_gate_closure(delivery_date: dt.date, session_id: int) -> dt.datetime:
    """Return the RTM gate closure datetime (IST) for a session.

    RTM gate closes 60 minutes before delivery of the first block in
    the session.

    Parameters
    ----------
    delivery_date : datetime.date
        The delivery date.
    session_id : int
        RTM session number in [1, 48].

    Returns
    -------
    datetime.datetime
        Gate closure timestamp.
    """
    first_block, _ = session_to_blocks(session_id)
    start_time, _ = block_to_time(first_block)
    delivery_start = dt.datetime.combine(delivery_date, start_time)
    return delivery_start - dt.timedelta(minutes=RTM_GATE_LEAD_MIN)


def regime_for_block(block_no: int) -> GridRegime:
    """Return the :class:`GridRegime` that contains *block_no*.

    Parameters
    ----------
    block_no : int
        Block number in [1, 96].

    Returns
    -------
    GridRegime

    Raises
    ------
    ValueError
        If *block_no* is outside [1, 96].
    """
    if not 1 <= block_no <= BLOCKS_PER_DAY:
        raise ValueError(
            f"block_no must be in [1, {BLOCKS_PER_DAY}], got {block_no}"
        )
    for regime, (lo, hi) in REGIME_BLOCK_RANGES.items():
        if lo <= block_no <= hi:
            return regime
    # Should never reach here if REGIME_BLOCK_RANGES is exhaustive.
    raise RuntimeError(f"No regime found for block {block_no}")  # pragma: no cover


# ---------------------------------------------------------------------------
# MarketRecord dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class MarketRecord:
    """A single 15-minute market observation (DAM or RTM).

    Attributes
    ----------
    date : datetime.date
        Delivery date.
    block_no : int
        Block number in [1, 96].
    hour : float
        Fractional hour for the start of the block (derived).
    session_id : int
        RTM session covering this block (1-48).
    purchase_bid_mw : float
        Total purchase (buy) bid volume in MW.
    sell_bid_mw : float
        Total sell (supply) bid volume in MW.
    mcv_mw : float
        Market Clearing Volume in MW.
    mcp : float
        Market Clearing Price in Rs / MWh.
    """

    date: dt.date
    block_no: int
    hour: float
    session_id: int
    purchase_bid_mw: float
    sell_bid_mw: float
    mcv_mw: float
    mcp: float

    def __post_init__(self) -> None:
        """Validate field constraints on construction."""
        errors = _validate_fields(
            block_no=self.block_no,
            mcp=self.mcp,
            purchase_bid_mw=self.purchase_bid_mw,
            sell_bid_mw=self.sell_bid_mw,
            mcv_mw=self.mcv_mw,
        )
        if errors:
            raise ValueError(
                "MarketRecord validation failed:\n  • " + "\n  • ".join(errors)
            )


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_fields(
    *,
    block_no: int,
    mcp: float,
    purchase_bid_mw: float,
    sell_bid_mw: float,
    mcv_mw: float,
) -> List[str]:
    """Return a list of human-readable validation error strings (empty = OK)."""
    errors: List[str] = []
    if not 1 <= block_no <= BLOCKS_PER_DAY:
        errors.append(f"block_no={block_no} outside [1, {BLOCKS_PER_DAY}]")
    if not CERC_PRICE_FLOOR <= mcp <= CERC_PRICE_CAP:
        errors.append(
            f"mcp={mcp} outside CERC bounds [{CERC_PRICE_FLOOR}, {CERC_PRICE_CAP}]"
        )
    if purchase_bid_mw < 0:
        errors.append(f"purchase_bid_mw={purchase_bid_mw} is negative")
    if sell_bid_mw < 0:
        errors.append(f"sell_bid_mw={sell_bid_mw} is negative")
    if mcv_mw < 0:
        errors.append(f"mcv_mw={mcv_mw} is negative")
    return errors


def validate_record(record: MarketRecord) -> List[str]:
    """Validate a :class:`MarketRecord` and return a list of issues.

    Parameters
    ----------
    record : MarketRecord
        The record to validate.

    Returns
    -------
    list[str]
        Empty list if valid; otherwise human-readable error messages.
    """
    return _validate_fields(
        block_no=record.block_no,
        mcp=record.mcp,
        purchase_bid_mw=record.purchase_bid_mw,
        sell_bid_mw=record.sell_bid_mw,
        mcv_mw=record.mcv_mw,
    )


def validate_dataframe(
    df: pd.DataFrame,
    price_col: str = "mcp",
    block_col: str = "block_no",
    volume_cols: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Validate an entire DataFrame of market records.

    Returns a boolean DataFrame of the same shape indicating which
    cells fail validation, plus prints a summary.

    Parameters
    ----------
    df : pd.DataFrame
        Market data with at least *price_col* and *block_col*.
    price_col : str
        Column containing clearing price.
    block_col : str
        Column containing block numbers.
    volume_cols : list[str] | None
        Columns that must be non-negative.  Defaults to
        ``["purchase_bid_mw", "sell_bid_mw", "mcv_mw"]``.

    Returns
    -------
    pd.DataFrame
        Boolean mask where ``True`` = failing cell.
    """
    if volume_cols is None:
        volume_cols = ["purchase_bid_mw", "sell_bid_mw", "mcv_mw"]

    mask = pd.DataFrame(False, index=df.index, columns=df.columns)

    if price_col in df.columns:
        bad_price = (df[price_col] < CERC_PRICE_FLOOR) | (
            df[price_col] > CERC_PRICE_CAP
        )
        mask[price_col] = bad_price

    if block_col in df.columns:
        bad_block = (df[block_col] < 1) | (df[block_col] > BLOCKS_PER_DAY)
        mask[block_col] = bad_block

    for vc in volume_cols:
        if vc in df.columns:
            mask[vc] = df[vc] < 0

    n_bad = int(mask.any(axis=1).sum())
    if n_bad:
        import warnings

        warnings.warn(
            f"validate_dataframe: {n_bad} / {len(df)} rows have at least "
            f"one invalid field.",
            stacklevel=2,
        )
    return mask


# ---------------------------------------------------------------------------
# Vectorized block ↔ time helpers for DataFrames
# ---------------------------------------------------------------------------

def blocks_to_hours(blocks: np.ndarray | pd.Series) -> np.ndarray:
    """Vectorised conversion of block numbers to fractional hours.

    Parameters
    ----------
    blocks : array-like of int
        Block numbers (1-indexed).

    Returns
    -------
    np.ndarray
        Fractional hours (float64).
    """
    arr = np.asarray(blocks, dtype=np.float64)
    return (arr - 1.0) * BLOCK_DURATION_MIN / 60.0


def blocks_to_sessions(blocks: np.ndarray | pd.Series) -> np.ndarray:
    """Vectorised conversion of block numbers to RTM session IDs.

    Parameters
    ----------
    blocks : array-like of int
        Block numbers (1-indexed, 1–96).

    Returns
    -------
    np.ndarray of int
        Session IDs (1–48).
    """
    arr = np.asarray(blocks, dtype=np.int64)
    return ((arr + 1) // 2).astype(np.int64)
