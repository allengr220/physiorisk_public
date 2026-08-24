# Sprint 1 TotalRisk findings

## Scope/status

The mathematical diagnosis and leakage-safe training-only calibration are complete. The exact native raw-LP sensitivity remains unavailable because the historical scored files contain the two axes and standardized PhysioRisk, but not the native raw LP or exact unrounded two-axis coefficients.

1. **Was the submitted TotalRisk mathematically mis-scaled?**

   Yes. `DemoRisk` is a native Cox linear predictor, while submitted `PhysioRisk` is the raw physiological Cox LP transformed to unit training SD. Adding them with unit coefficients does not preserve the fitted joint Cox log-hazard scale. In raw-LP terms, the submitted physiology coefficient is implicitly `1 / sigma_train(PhysioRisk_raw)`, not 1. The construction remains a valid ranking score, but its claimed Cox-LP interpretation is not justified.

2. **What coefficients does the training-only calibration estimate?**

   The unpenalized training-only Cox calibration estimates `beta_Demo = 1.058658` (SE 0.016472; 95% CI 1.026373–1.090943) and `beta_Physio = 0.356351` (SE 0.012796; 95% CI 0.331273–0.381430). Training partial log likelihood is `-20327.879117`. Lifelines batch mode converged successfully in six iterations.

3. **How different is beta_Physio from the implicit original value of 1?**

   It is `0.643649` below 1, a 64.4% reduction from the submitted implicit unit weight. Its 95% CI excludes 1.

4. **How different is beta_Demo from 1?**

   It is `0.058658` above 1, a 5.9% increase. Its 95% CI also excludes 1.

5. **How much does correction change temporal C-index?**

   The historical value is 0.839760 and the calibrated value is 0.843153, an absolute increase of 0.003393. This is a frozen-model evaluation, not a basis for model selection.

6. **How much does correction change HR/SD?**

   With convergence-controlled fits, the original value is 1.877466 (95% CI 1.815234–1.941831); the calibrated value is 3.259002 (95% CI 3.035997–3.498387), an absolute increase of 1.381536. Notebook 07 standardizes every test predictor to its actual test-cohort sample SD before univariable Cox evaluation and asserts SD=1.

7. **Does the corrected model retain the substantive claim that physiological risk adds information beyond DemoRisk?**

   Yes, within this internal temporal-validation analysis. The training-only physiology coefficient is positive with 95% CI 0.331273–0.381430, and the frozen calibrated score has temporal C-index 0.843153 versus 0.826876 for DemoRisk. This supports incremental information but is not external validation or a test-driven model choice.

8. **Are there unexpected discrepancies suggesting a deeper reconstruction problem?**

   Yes. The scored parquets are now available and reproduce the historical composite exactly, but the exact two-axis producer, model object, unrounded coefficients, penalty, raw-LP mean/SD, and residualization parameters remain missing. The rounded 0.433/0.235 formula does not reproduce stored standardized PhysioRisk exactly. In addition, the manuscript PhysioRisk HR/SD of 2.77 is from a non-converged Cox fit whose warning was globally suppressed; a convergence-controlled fit gives approximately 1.39. Both results are preserved as separate rows in the revision comparison table. The public notebook set also contains an older three-axis pipeline with a different age-spline implementation and penalties; it is not the Table 2 producer.

## Interpretation guardrails

No sensitivity construction has been ranked using temporal-test performance. The native raw-LP sum is prespecified in `notebooks/07_totalrisk_reconstruction.ipynb`. The DemoRisk-offset sensitivity is recorded as not fitted because lifelines does not expose a Cox offset parameter directly; implementing a custom partial likelihood solely to force that sensitivity was not considered “straightforward.”
