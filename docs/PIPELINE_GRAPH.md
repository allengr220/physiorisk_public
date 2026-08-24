# Pipeline dependency graph

```text
Public NHANES files + linked mortality
                 |
                 v
01 NHANES extended dataset builder
                 |
                 | writes 1999-2016 dataset
                 X  filename/year mismatch: notebook 02 reads 1999-2018
                 |
                 v
02 Benchmark dataset builder (older CRP-complete branch)
                 |
                 X  does not produce benchmark_levine_no_crp_cohort.parquet
                 |
       [external verified no-CRP benchmark]
                 |
                 v
03 Demographic risk model
                 |
                 v
      frozen DemoRisk train/test
                 |
                 v
04 PhysioRisk scoring
                 |
        +--------+---------+
        |                  |
        v                  v
 scored train       scored temporal test
        |                  |
        +--------+---------+
                 |
                 v
05 PhysioRisk model validation --------> submitted Table 2 CSV
                 |                                |
                 +----------------+---------------+
                                  v
                         06 Manuscript figures
                                  |
                                  +--> Figure 1
                                  +--> Figure 2

Optional older branch:
1999-2018 dataset + v1/v2/v3 scored files
                 |
                 v
07 Ablation analysis optional ----------> ablation tables (not committed)

Post-review supplemental branch:
scored train/test + no-CRP benchmark
                 |
       +---------+--------------------------+
       |                                    |
       v                                    v
07_totalrisk_reconstruction       scripts/run_sprint2_validation.py
       |                                    |
       v                          +---------+----------+
reconstruction tables             |                    |
                                  v                    v
                         08 Validation v2     09 Cohort/comparator
                                  |                    |
                                  +----> validation, calibration,
                                         PH/Schoenfeld, bootstrap,
                                         cohort, missingness, and
                                         comparator tables
```

`X` marks a broken canonical handoff. External verified artifacts are recorded with hashes in `ARTIFACT_PROVENANCE.md`; they are not present in a clean clone.
