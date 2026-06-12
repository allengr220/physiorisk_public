# PhysioRisk model lock

This document records the frozen modeling specification for the submitted PhysioRisk manuscript.

## Dataset

- Data source: NHANES 1999–2016
- Outcome source: NHANES-linked mortality follow-up
- Outcome: all-cause mortality
- Time variable: `PERMTH_INT`
- Event variable: `MORTSTAT`

## Demographic risk component

DemoRisk is defined as an age- and sex-based Cox proportional hazards model.

Frozen baseline specification:

```python
BASELINE_FORMULA = "cr(RIDAGEYR, df=4) + C(RIAGENDR)"
PENALIZER = 0.01
L1_RATIO = 0.0
DURATION_COL = "PERMTH_INT"
EVENT_COL = "MORTSTAT"
