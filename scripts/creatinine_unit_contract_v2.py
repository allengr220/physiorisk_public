#!/usr/bin/env python3
"""Explicit NHANES creatinine source and unit contract for PhysioRisk v2.

The canonical output variable is ``LBXSCR`` in mg/dL.  This module changes
creatinine only; it does not apply the separate 1999--2000 assay correction.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


CREATININE_SI_DIVISOR = 88.4
# NHANES reports the paired conventional and SI fields at different decimal
# precision.  This bound covers their combined display-rounding intervals.
NHANES_ROUNDING_TOLERANCE_MG_DL = 0.011


@dataclass(frozen=True)
class CreatinineContract:
    cycle: str
    chemistry_source_file: str
    selected_source_variable: str
    source_unit: str
    canonical_variable: str = "LBXSCR"
    canonical_unit: str = "mg/dL"
    conversion_applied: str = "none"
    conversion_factor: float = 1.0
    conversion_formula: str = "LBXSCR = LBXSCR"
    fallback_source_variable: str = ""
    fallback_source_unit: str = ""
    fallback_conversion_factor: float | None = None
    fallback_conversion_formula: str = ""
    reconciliation_formula: str = "LBDSCRSI / 88.4 vs selected conventional-unit field"
    reconciliation_absolute_tolerance_mg_dL: float = NHANES_ROUNDING_TOLERANCE_MG_DL


CREATININE_CONTRACTS = {
    row.cycle: row
    for row in [
        CreatinineContract("1999-2000", "LAB18.XPT", "LBXSCR", "mg/dL"),
        CreatinineContract(
            "2001-2002",
            "L40_B.XPT",
            "LBDSCR",
            "mg/dL",
            conversion_formula="LBXSCR = LBDSCR",
            fallback_source_variable="LBDSCRSI",
            fallback_source_unit="µmol/L",
            fallback_conversion_factor=1.0 / CREATININE_SI_DIVISOR,
            fallback_conversion_formula="LBXSCR = LBDSCRSI / 88.4",
        ),
        CreatinineContract("2003-2004", "L40_C.XPT", "LBXSCR", "mg/dL"),
        CreatinineContract("2005-2006", "BIOPRO_D.XPT", "LBXSCR", "mg/dL"),
        CreatinineContract("2007-2008", "BIOPRO_E.XPT", "LBXSCR", "mg/dL"),
        CreatinineContract("2009-2010", "BIOPRO_F.XPT", "LBXSCR", "mg/dL"),
        CreatinineContract("2011-2012", "BIOPRO_G.XPT", "LBXSCR", "mg/dL"),
        CreatinineContract("2013-2014", "BIOPRO_H.XPT", "LBXSCR", "mg/dL"),
        CreatinineContract("2015-2016", "BIOPRO_I.XPT", "LBXSCR", "mg/dL"),
    ]
}


def contract_dataframe() -> pd.DataFrame:
    """Return the source contract in cycle order."""

    return pd.DataFrame(asdict(row) for row in CREATININE_CONTRACTS.values())


def _reconcile_with_si(
    chemistry: pd.DataFrame,
    conventional_variable: str,
    cycle: str,
) -> tuple[int, float]:
    """Check paired conventional/SI fields at NHANES rounding precision."""

    if conventional_variable not in chemistry or "LBDSCRSI" not in chemistry:
        return 0, float("nan")

    paired = chemistry[[conventional_variable, "LBDSCRSI"]].dropna()
    if paired.empty:
        return 0, float("nan")

    differences = (
        pd.to_numeric(paired[conventional_variable], errors="coerce")
        - pd.to_numeric(paired["LBDSCRSI"], errors="coerce") / CREATININE_SI_DIVISOR
    ).abs()
    max_difference = float(differences.max())
    if max_difference > NHANES_ROUNDING_TOLERANCE_MG_DL:
        raise AssertionError(
            f"{cycle} creatinine fields disagree: max absolute difference "
            f"{max_difference:.12g} mg/dL exceeds "
            f"{NHANES_ROUNDING_TOLERANCE_MG_DL:.12g}"
        )
    return int(len(paired)), max_difference


def harmonize_creatinine(
    chemistry: pd.DataFrame,
    cycle: str,
    chemistry_source_file: str,
) -> pd.DataFrame:
    """Select and harmonize creatinine under the cycle-specific contract.

    The 2001--2002 preferred route is direct ``LBDSCR`` in mg/dL.  Only when
    that field is unavailable in the execution context may ``LBDSCRSI`` be
    converted by division by 88.4.  When both exist, they are reconciled before
    the preferred conventional-unit field is selected.
    """

    if cycle not in CREATININE_CONTRACTS:
        raise KeyError(f"No creatinine unit contract for cycle {cycle!r}")
    contract = CREATININE_CONTRACTS[cycle]
    if chemistry_source_file.upper() != contract.chemistry_source_file.upper():
        raise AssertionError(
            f"{cycle} chemistry file {chemistry_source_file!r} does not match "
            f"contract {contract.chemistry_source_file!r}"
        )
    if "SEQN" not in chemistry:
        raise KeyError(f"{cycle} chemistry file has no SEQN")

    paired_n, max_difference = _reconcile_with_si(
        chemistry, contract.selected_source_variable, cycle
    )

    selected = contract.selected_source_variable
    preferred_available = selected in chemistry and chemistry[selected].notna().any()
    if preferred_available:
        values = pd.to_numeric(chemistry[selected], errors="coerce")
        route = selected
        formula = f"LBXSCR = {selected}"
    elif (
        cycle == "2001-2002"
        and contract.fallback_source_variable in chemistry
        and chemistry[contract.fallback_source_variable].notna().any()
    ):
        selected = contract.fallback_source_variable
        values = (
            pd.to_numeric(chemistry[selected], errors="coerce")
            / CREATININE_SI_DIVISOR
        )
        route = selected
        formula = contract.fallback_conversion_formula
    else:
        raise KeyError(
            f"{cycle} lacks approved creatinine source "
            f"{contract.selected_source_variable!r}"
        )

    out = pd.DataFrame(
        {
            "SEQN": pd.to_numeric(chemistry["SEQN"], errors="coerce").astype("Int64"),
            "LBXSCR": values,
        }
    )
    out.attrs.update(
        {
            "cycle": cycle,
            "chemistry_source_file": chemistry_source_file,
            "selected_source_variable": route,
            "canonical_unit": "mg/dL",
            "conversion_formula": formula,
            "paired_reconciliation_n": paired_n,
            "paired_max_abs_difference_mg_dL": max_difference,
        }
    )
    if not np.isfinite(out["LBXSCR"].dropna()).all():
        raise AssertionError(f"{cycle} harmonized creatinine contains non-finite values")
    return out
