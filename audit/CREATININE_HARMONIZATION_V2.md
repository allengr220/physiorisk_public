# Creatinine Harmonization V2 Checkpoint

## Repair

The canonical NHANES loader treated creatinine aliases as unit-equivalent. For
the 2001–2002 cycle, it selected `LBDSCRSI` in µmol/L and renamed it to
`LBXSCR` without conversion. This made the affected values approximately 88.4
times larger than the intended canonical unit.

The corrected 2001–2002 route selects `LBDSCR` directly from `L40_B.XPT` in
mg/dL. If `LBDSCR` is unavailable in an execution context, the approved
fallback is `LBDSCRSI / 88.4`. The canonical `LBXSCR` unit is mg/dL for every
PhysioRisk cycle.

The separate 1999–2000 creatinine assay-standardization issue was not changed.

## Reconciliation

- Benchmark cohort: 19,829 participants; participant IDs identical to v1.
- Development cohort: 13,090 participants and 2,520 deaths; participant IDs
  identical to v1.
- Validation cohort: 6,739 participants and 416 deaths; participant IDs
  identical to v1.
- Exactly 2,217 development participants changed, all from 2001–2002.
- Validation participant IDs did not change.
- Creatinine values in all other cycles were unchanged.
- All other benchmark fields were unchanged.
- All 6,891 paired 2001–2002 `LBDSCR`/`LBDSCRSI` records reconciled; maximum
  absolute disagreement after SI conversion was approximately
  `1.78e-15 mg/dL`.

| Diagnostic | Historical v1 | Corrected v2 input |
|---|---:|---:|
| Creatinine residual SD | 33.1785677880 | 0.3600779213 |
| Correlation with 2001-cycle indicator | 0.8806619715 | 0.0420942933 |
| Cycle-indicator R² | 0.7755655080 | 0.0017719295 |
| 2001–2002 median | 79.56 | 0.90 mg/dL |

All independent numerical audit targets reconciled.

## Artifacts and scope

- Executable audit: `scripts/audit_creatinine_harmonization_v2.py`
- Machine-readable unit contract: `audit/creatinine_unit_contract_v2.csv`
- Executable unit-contract implementation:
  `scripts/creatinine_unit_contract_v2.py`

No PhysioRisk or CalibratedTotalRisk model has been refit. Historical submitted
artifacts were not overwritten or modified.

Checkpoint branch: `fix/creatinine-unit-harmonization-v2`

Pre-repair HEAD: `82de89d2015141cc4f9e038e94f56a98362b5a85`
