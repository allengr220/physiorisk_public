# PhysioRisk to RSE-NHANES handoff — 2026-10-16

This handoff separates reusable NHANES infrastructure from PhysioRisk scientific assumptions. The RSE architecture and state files remain the authority for RSE.

## Safe to inherit

RSE-NHANES may inherit, subject to its own validation:

- The audited NHANES download and input inventory.
- Cycle identification and cycle-year representation.
- `SEQN` normalization, uniqueness checks, and mortality linkage rules.
- Unit-harmonization infrastructure, including the testable cross-cycle creatinine and glucose contracts.
- Cycle-specific laboratory exceptions and source-variable provenance metadata.
- Input/output manifests, checksums, and provenance conventions.
- Missingness summaries and complete-case accounting utilities.
- Reproducibility assertions for source-cycle counts, linkage, completeness, and temporal partitioning.
- Cohort-building utilities when their scientific inclusion rules fit the RSE question.

## Do not inherit as RSE assumptions

RSE-NHANES must not automatically inherit:

- The two-axis PhysioRisk representation.
- HematologicStress or RenalHepaticTurnover as privileged latent states.
- PhysioRisk residualization as the definition of biological state.
- PhysioRisk Cox coefficients.
- CalibratedTotalRisk coefficients.
- PhenoAge NCP as ground truth.
- Mortality prediction as the definition of rejuvenation or biological state.
- The PhysioRisk temporal split as automatically optimal for RSE.
- The complete-case restriction as automatically appropriate for RSE.

These may serve as comparators or empirical probes when pre-specified for a particular RSE analysis.

## What NHANES can test for RSE

### Potentially testable

- Partial-observation and state-estimation ideas.
- Multimodal clinical state representations.
- Information added by modalities beyond a restricted observation set.
- Uncertainty under missing observations.
- Markov-sufficiency proxies where their assumptions are defensible.
- Associations between latent-state proxies and outcomes.
- Age-conditioned and age-independent physiological signals.
- Missing-state diagnostics.
- Distribution shift across survey eras and subgroups.

### Not directly testable from ordinary cross-sectional NHANES

- True within-person biological trajectories.
- Controlled intervention dynamics.
- `z_(t+1) = f(z_t, e_t, u_t)`.
- Trajectory-level intervention safety.
- Rejuvenation path safety.
- Controllability.
- Causal response to reprogramming.

## RSE-NHANES starting principle

RSE-NHANES must ask: **“What components of the RSE architecture can NHANES empirically constrain?”**

It must not ask: **“How can PhysioRisk be expanded into RSE?”**

## First recommended RSE-NHANES task

Begin with a modality and availability inventory across the supported NHANES cycles. Define one restricted observation set and incrementally richer observed-variable sets, then ask whether the additional observations improve predeclared state-sufficiency proxies while characterizing missingness and survey-era/subgroup shifts. Preserve source-unit metadata and do not choose an RSE model architecture in this first task.

## Bootstrap prompt for a new RSE-NHANES thread

```text
You are starting RSE-NHANES work. Read these repository documents first:

1. PHYSIORISK_TO_RSE_NHANES_HANDOFF_2026-10-16.md
2. NHANES_DATA_CONTRACT_2026-10-16.md
3. PHYSIORISK_AUDIT_CLOSURE_2026-10-16.md

Treat them as audited NHANES infrastructure and provenance context only. They are not the authority for RSE scientific assumptions, model structure, state definition, or success criteria. Locate and use the current canonical RSE architecture and state files as the authority for what RSE is.

Do not import the PhysioRisk two-axis representation, residualization, Cox coefficients, CalibratedTotalRisk coefficients, PhenoAge NCP, mortality-prediction framing, complete-case restriction, or temporal split as RSE assumptions. They may be used only as explicitly justified comparators or empirical probes.

Start with a data inventory: identify usable NHANES modalities and their cycle coverage, units, missingness, source provenance, and linkage constraints. Then formulate a minimal experiment asking whether additional observed variables improve defensible state-sufficiency proxies beyond a restricted observation set. Do not select an RSE architecture yet. Distinguish what cross-sectional NHANES can constrain from trajectory, intervention, controllability, and causal questions that it cannot directly test.
```
