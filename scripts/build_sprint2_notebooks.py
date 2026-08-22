"""Build the two executable Sprint 2 validation notebooks."""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]


def write(name, title, markdown_sections, code_cells):
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {"kernelspec":{"display_name":"Python (physiorisk)","language":"python","name":"python3"},
                      "language_info":{"name":"python","version":"3.11"}}
    cells = [nbf.v4.new_markdown_cell(f"# {title}\n\n" + markdown_sections[0])]
    for code, text in zip(code_cells, markdown_sections[1:]):
        cells.append(nbf.v4.new_code_cell(code))
        if text:
            cells.append(nbf.v4.new_markdown_cell(text))
    nb["cells"] = cells
    nbf.write(nb, ROOT / "notebooks" / name)


common_setup = """from pathlib import Path
import sys
import pandas as pd
ROOT = Path.cwd().resolve().parent if Path.cwd().name == 'notebooks' else Path.cwd().resolve()
sys.path.insert(0, str(ROOT / 'scripts'))
import run_sprint2_validation as s2
print({'bootstrap_seed': s2.SEED, 'bootstrap_replicates': s2.N_BOOT, 'data_dir': str(s2.DATA_DIR)})"""

write("08_validation_v2.ipynb", "Validation v2: frozen CalibratedTotalRisk",
    ["""This notebook evaluates the Sprint 1 primary revised model without model selection or temporal refitting. It verifies the three canonical SHA256 identities before analysis. `CalibratedTotalRisk` uses the locked training-only coefficients `beta_Demo=1.0586578127615558` and `beta_Physio=0.3563514638575306`.

Historical submitted values remain separately labeled. Cox fits use explicit step-size/iteration/precision controls, and convergence warnings are captured locally rather than suppressed. Bootstrap seed: **20260821**.

Uno's IPCW C and cumulative/dynamic AUC use `scikit-survival` 0.28.0, with training data estimating the censoring distribution and temporal data used for evaluation. Fixed-horizon IPCW Brier scores use the temporal censoring distribution as an evaluation metric.""",
     "The exported validation table contains discrimination, uncertainty, HR per actual test-cohort SD, HR confidence intervals, and age correlation. Paired resampling uses identical bootstrap participants for both scores in each contrast.",
     "PH diagnostics are descriptive. A flagged result is recorded, not used to alter the model.",
     "Absolute risk uses the training Cox baseline survival and frozen training coefficients. Temporal outcomes are used only for evaluation. The eight-year horizon is retained with an explicit less-precise-tail qualification.",
     "Calibration plot data are exported as temporal-test risk deciles; plotting can be styled later without rerunning the model.",
     "Scaled Schoenfeld residuals and an extended-Cox score × log(time/60 months) model localize non-proportionality. These are diagnostic only. Horizon-specific IPCW logistic calibration slopes are kept distinct from the global PH-dependent Cox slope."],
    [common_setup,
     "validation = s2.run_validation()\ndisplay(pd.read_csv(ROOT/'tables/validation_v2.csv'))\ndisplay(pd.read_csv(ROOT/'tables/cindex_bootstrap_contrasts.csv'))",
     "display(pd.read_csv(ROOT/'tables/ph_diagnostics.csv'))",
     "display(pd.read_csv(ROOT/'tables/followup_summary.csv'))\ndisplay(pd.read_csv(ROOT/'tables/calibration_fixed_horizons.csv'))",
     "display(pd.read_csv(ROOT/'tables/calibration_plot_data.csv'))",
     "display(pd.read_csv(ROOT/'tables/ph_time_interaction.csv'))\ndisplay(pd.read_csv(ROOT/'tables/censoring_robust_discrimination.csv'))\ndisplay(pd.read_csv(ROOT/'tables/ph_schoenfeld_residuals.csv').head())"])

write("09_cohort_comparator_sensitivity.ipynb", "Cohort flow and comparator sensitivity",
    ["""This notebook reconstructs cohort accounting only as far upstream as retained data permit. The retained benchmark is already adult, mortality-linked, and complete for required biomarkers, so pre-benchmark exclusions cannot be recovered and are labeled accordingly.

PhenoAge NCP is consistently labeled as a **no-CRP proxy**. No frozen PhysioRisk residualization or axis parameters are recreated.""",
     "The source analytic dataset is the earliest retained artifact. Counts do not imply that upstream NHANES eligibility, mortality-linkage, or biomarker exclusions have been fully reconstructed.",
     "Missingness is reported by biomarker and NHANES cycle within the retained benchmark.",
     "Because all retained rows are complete, common complete-case and common training-derived-imputation analyses are identical. The latter is a no-op sensitivity; applying imputation to upstream excluded participants would require unavailable frozen physiology transformations and could constitute redevelopment.",
     "Included/excluded characteristic comparison is limited: no rows are excluded within the retained complete benchmark, so the excluded group is empty."],
    [common_setup,
     "s2.run_cohort_sensitivity()\ndisplay(pd.read_csv(ROOT/'tables/cohort_flow.csv'))",
     "display(pd.read_csv(ROOT/'tables/missingness_by_cycle.csv'))",
     "display(pd.read_csv(ROOT/'tables/comparator_sensitivity.csv'))",
     "display(pd.read_csv(ROOT/'tables/cohort_included_excluded_characteristics.csv'))"])
