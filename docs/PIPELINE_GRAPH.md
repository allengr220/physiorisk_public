# Pipeline dependency graph

```text
Public NHANES files + linked mortality
                 |
                 v
01 NHANES extended dataset builder
                 |
                 | nhanes_1999_2016_extended_mortality_model_dataset.parquet
                 v
02 Levine no-CRP benchmark cohort builder
                 |
                 | benchmark_levine_no_crp_cohort.parquet
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
                 |                     +--> row-level PhenoAge NCP/
                 |                          acceleration parquet
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

The direct 01–06 producer graph is complete. Large intermediate artifacts remain in Google Drive/MyDrive rather than Git and are inventoried in `data/ARTIFACT_MANIFEST.tsv`. The optional ablation branch is historical/supporting, not a required manuscript-pipeline stage.
