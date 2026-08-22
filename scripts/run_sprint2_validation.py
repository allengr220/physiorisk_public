"""Sprint 2 validation analyses for the frozen two-axis PhysioRisk model.

This module is called by notebooks 08 and 09. It verifies the Sprint 1 input
identities before analysis and never fits score coefficients on temporal data.
"""
from __future__ import annotations

import hashlib
import json
import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, CoxTimeVaryingFitter, KaplanMeierFitter
from lifelines.exceptions import ConvergenceWarning
from lifelines.statistics import proportional_hazard_test
from lifelines.utils import concordance_index
from patsy import build_design_matrices, dmatrix
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("PHYSIORISK_DATA_DIR", "/home/ubuntu2204/longevity/data/physiorisk/data"))
TABLE_DIR = ROOT / "tables"
TABLE_DIR.mkdir(exist_ok=True)
TIME, EVENT, AGE = "PERMTH_INT", "MORTSTAT", "RIDAGEYR"
SEED = 20260821
N_BOOT = int(os.environ.get("PHYSIORISK_N_BOOT", "2000"))
BETA_DEMO = 1.0586578127615558
BETA_PHYSIO = 0.3563514638575306
PHENO_COLS = ["LBXSAL", "LBXSCR", "LBXGLU", "LBXMCV", "LBXRDW", "LBXWBCSI", "LBXLYPCT", "LBXSAPSI"]
PHYSIO_COLS = ["LBXWBCSI", "LBXLYPCT", "LBXMCV", "LBXRDW", "LBXSCR", "LBXSAL", "LBXSAPSI"]
FILES = {
    "benchmark": ("benchmark_levine_no_crp_cohort.parquet", "f53d03317a6ea123021e7e36d585f7d92ba6f198821f21b083adfcc4b8e87125"),
    "train": ("physiorisk_2axis_v1_train_scored_from_frozen_baseline_levinenocrp.parquet", "e8f435b5a8b68dbb477f04bad280252f563b9323e9bc9dea4eb7e945c22cbb86"),
    "test": ("physiorisk_2axis_v1_test_scored_from_frozen_baseline_levinenocrp.parquet", "1455e24e8ca3e1f68eb58a779f7a4d48e46b8e54fa435ec00de5cf51256d08ca"),
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_verified():
    frames = {}
    for key, (name, expected) in FILES.items():
        path = DATA_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"Missing canonical input: {path}")
        actual = _sha256(path)
        if actual != expected:
            raise AssertionError(f"SHA256 mismatch for {key}: {actual} != {expected}")
        frames[key] = pd.read_parquet(path)
    benchmark, train, test = frames["benchmark"], frames["train"].copy(), frames["test"].copy()
    assert (len(benchmark), len(train), len(test)) == (19829, 13090, 6739)
    assert (int(benchmark[EVENT].sum()), int(train[EVENT].sum()), int(test[EVENT].sum())) == (2936, 2520, 416)
    assert train.SEQN.is_unique and test.SEQN.is_unique and set(train.SEQN).isdisjoint(test.SEQN)
    return benchmark, train, test


def add_frozen_scores(train: pd.DataFrame, test: pd.DataFrame):
    for df in (train, test):
        df["DemoRisk"] = df["BaselineRisk"]
        df["PhysioRisk"] = df["PhysioRisk_2axis"]
        df["TotalRisk_original"] = df["BaselineRisk"] + df["PhysioRisk_2axis"]
        df["CalibratedTotalRisk"] = BETA_DEMO * df["BaselineRisk"] + BETA_PHYSIO * df["PhysioRisk_2axis"]
        assert np.allclose(df["TotalRisk_original"], df["TotalRisk_2axis"])
    imp = SimpleImputer(strategy="median")
    tr_bio = pd.DataFrame(imp.fit_transform(train[PHENO_COLS]), columns=PHENO_COLS, index=train.index)
    te_bio = pd.DataFrame(imp.transform(test[PHENO_COLS]), columns=PHENO_COLS, index=test.index)
    for df, bio in ((train, tr_bio), (test, te_bio)):
        df["PhenoAge NCP"] = (-19.907 - .0336*bio.LBXSAL + .0095*bio.LBXSCR + .1953*np.log(bio.LBXGLU.clip(lower=1e-6))
            - .0120*bio.LBXLYPCT + .0268*bio.LBXMCV + .3306*bio.LBXRDW + .0019*bio.LBXSAPSI + .0554*bio.LBXWBCSI + .0804*df[AGE])
    xtr = dmatrix(f"cr({AGE}, df=4) + C(RIAGENDR)", train, return_type="dataframe")
    xte = build_design_matrices([xtr.design_info], test, return_type="dataframe")[0]
    reg = LinearRegression().fit(xtr, train["PhenoAge NCP"])
    train["PhenoAge NCP acceleration"] = train["PhenoAge NCP"] - reg.predict(xtr)
    test["PhenoAge NCP acceleration"] = test["PhenoAge NCP"] - reg.predict(xte)
    return imp


def controlled_cox(df: pd.DataFrame, predictor: str):
    d = df[[TIME, EVENT, predictor]].dropna().copy()
    sd = float(d[predictor].std(ddof=1))
    d["predictor_z"] = (d[predictor] - d[predictor].mean()) / sd
    fit = CoxPHFitter(penalizer=0.0)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        fit.fit(d[[TIME, EVENT, "predictor_z"]], TIME, EVENT, batch_mode=True,
                fit_options={"step_size": 0.5, "max_steps": 1000, "precision": 1e-9})
    convergence_warnings = [str(w.message) for w in caught if issubclass(w.category, ConvergenceWarning)]
    s = fit.summary.loc["predictor_z"]
    return d, fit, sd, s, convergence_warnings


def bootstrap_cindices(test: pd.DataFrame, score_map: dict[str, str]):
    rng = np.random.default_rng(SEED)
    n = len(test)
    boot = {label: np.empty(N_BOOT) for label in score_map}
    arrays = {label: test[col].to_numpy() for label, col in score_map.items()}
    times, events = test[TIME].to_numpy(), test[EVENT].to_numpy()
    for b in range(N_BOOT):
        while True:
            ix = rng.integers(0, n, n)
            if events[ix].sum() > 0:
                break
        for label, score in arrays.items():
            boot[label][b] = concordance_index(times[ix], -score[ix], events[ix])
    return boot


def run_validation():
    _, train, test = load_verified()
    add_frozen_scores(train, test)
    score_map = {
        "DemoRisk": "DemoRisk", "PhysioRisk_convergence_corrected": "PhysioRisk",
        "TotalRisk_original": "TotalRisk_original", "CalibratedTotalRisk": "CalibratedTotalRisk",
        "PhenoAge NCP": "PhenoAge NCP", "PhenoAge NCP acceleration": "PhenoAge NCP acceleration",
    }
    boot = bootstrap_cindices(test, score_map)
    rows = []
    for label, col in score_map.items():
        d, _, sd, s, conv = controlled_cox(test, col)
        point = concordance_index(d[TIME], -d[col], d[EVENT])
        rows.append({"model": label, "value_provenance": "recomputed/revised", "cohort": "temporal_test",
            "N": len(d), "deaths": int(d[EVENT].sum()), "C_index": point,
            "C_index_bootstrap_95CI_low": np.quantile(boot[label], .025), "C_index_bootstrap_95CI_high": np.quantile(boot[label], .975),
            "bootstrap_replicates": N_BOOT, "bootstrap_seed": SEED, "actual_test_SD": sd,
            "HR_per_actual_1SD": float(s["exp(coef)"]), "HR_95CI_low": float(s["exp(coef) lower 95%"]),
            "HR_95CI_high": float(s["exp(coef) upper 95%"]), "age_correlation": float(test.loc[d.index, col].corr(test.loc[d.index, AGE])),
            "cox_penalizer": 0.0, "cox_convergence_warning": " | ".join(conv) if conv else "none"})
    validation = pd.DataFrame(rows)
    historical = pd.DataFrame([{"model":"PhysioRisk_submitted", "value_provenance":"submitted/historical",
        "cohort":"temporal_test", "N":6739, "deaths":416, "C_index":0.6541097324576873,
        "HR_per_actual_1SD":2.7716579077104098, "HR_95CI_low":2.655680584394424,
        "HR_95CI_high":2.8927001245992834, "age_correlation":0.10623345250003381,
        "cox_penalizer":0.0, "cox_convergence_warning":"historical fit did not converge; preserved only"}])
    validation = pd.concat([validation.iloc[:1], historical, validation.iloc[1:]], ignore_index=True)
    validation.to_csv(TABLE_DIR / "validation_v2.csv", index=False)

    contrasts = []
    for a, b in [("CalibratedTotalRisk", "DemoRisk"), ("CalibratedTotalRisk", "PhenoAge NCP"),
                 ("PhysioRisk_convergence_corrected", "PhenoAge NCP acceleration")]:
        diffs = boot[a] - boot[b]
        pa = float(validation.loc[validation.model.eq(a), "C_index"].iloc[0])
        pb = float(validation.loc[validation.model.eq(b), "C_index"].iloc[0])
        contrasts.append({"contrast":f"{a} vs {b}", "model_A":a, "model_B":b,
            "value_provenance":"recomputed/revised", "cohort":"temporal_test", "point_C_index_difference_A_minus_B":pa-pb,
            "bootstrap_95CI_low":np.quantile(diffs,.025), "bootstrap_95CI_high":np.quantile(diffs,.975),
            "proportion_bootstrap_difference_above_zero":float(np.mean(diffs>0)), "bootstrap_replicates":N_BOOT, "bootstrap_seed":SEED})
    pd.DataFrame(contrasts).to_csv(TABLE_DIR / "cindex_bootstrap_contrasts.csv", index=False)

    ph_rows = []
    for label, col in [("DemoRisk","DemoRisk"),("PhysioRisk","PhysioRisk"),("CalibratedTotalRisk","CalibratedTotalRisk"),
                       ("HematologicStress","HematologicStress"),("RenalHepaticTurnover","RenalHepaticTurnover")]:
        d, fit, _, _, conv = controlled_cox(test, col)
        result = proportional_hazard_test(fit, d[[TIME,EVENT,"predictor_z"]], time_transform="rank").summary.loc["predictor_z"]
        p = float(result["p"])
        ph_rows.append({"model":label,"value_provenance":"recomputed/revised","cohort":"temporal_test","N":len(d),"deaths":int(d[EVENT].sum()),
            "time_transform":"rank","test_statistic":float(result["test_statistic"]),"p_value":p,
            "material_violation_flag":bool(p<.01),"flag_rule":"p<0.01 (prespecified descriptive flag; no multiplicity adjustment)",
            "cox_convergence_warning":" | ".join(conv) if conv else "none"})
    pd.DataFrame(ph_rows).to_csv(TABLE_DIR / "ph_diagnostics.csv", index=False)

    followup_and_calibration(train, test)
    run_diagnostic_addendum(train, test)
    return validation


def _km_at(kmf: KaplanMeierFitter, t: float) -> float:
    return float(kmf.predict(t))


def _ipcw_brier(time, event, pred, horizon, censor_km):
    time, event, pred = map(np.asarray, (time, event, pred))
    weights = np.zeros(len(time), float)
    event_by_t = (time <= horizon) & (event == 1)
    alive_t = time > horizon
    eps = 1e-10
    for i in np.where(event_by_t)[0]:
        weights[i] = 1.0 / max(_km_at(censor_km, np.nextafter(float(time[i]), -np.inf)), eps)
    weights[alive_t] = 1.0 / max(_km_at(censor_km, horizon), eps)
    outcome = event_by_t.astype(float)
    return float(np.mean(weights * (outcome - pred) ** 2)), int(np.count_nonzero(weights))


def _ipcw_binary_data(time, event, pred, horizon, censor_km):
    """Binary horizon outcome and standard IPCW weights for calibration diagnostics."""
    time, event, pred = map(np.asarray, (time, event, pred))
    keep = ((time <= horizon) & (event == 1)) | (time > horizon)
    y = ((time <= horizon) & (event == 1)).astype(int)[keep]
    w = np.empty(keep.sum(), float)
    kept_time, kept_event = time[keep], event[keep]
    event_by = (kept_time <= horizon) & (kept_event == 1)
    for i in np.where(event_by)[0]:
        w[i] = 1.0 / max(_km_at(censor_km, np.nextafter(float(kept_time[i]), -np.inf)), 1e-10)
    w[~event_by] = 1.0 / max(_km_at(censor_km, horizon), 1e-10)
    return y, pred[keep], w


def followup_and_calibration(train, test):
    durations = test[TIME].astype(float)
    reverse_km = KaplanMeierFitter().fit(durations, event_observed=1-test[EVENT])
    followup_quantiles = reverse_km.percentile([.75,.5,.25]).to_numpy() if False else None
    # Reverse-KM median is the censoring-robust follow-up summary; empirical IQR/max are also shown.
    reverse_median = float(reverse_km.median_survival_time_)
    summary_rows = []
    empirical = durations.quantile([.25,.5,.75])
    for h in (60,96):
        at_risk = int((durations >= h).sum())
        events_by = int(((durations <= h) & test[EVENT].eq(1)).sum())
        summary_rows.append({"cohort":"temporal_test","value_provenance":"recomputed/revised","N":len(test),"deaths_total":int(test[EVENT].sum()),
            "followup_definition":"reverse_KM_median; empirical_IQR_and_max", "reverse_KM_median_months":reverse_median,
            "empirical_median_months":float(empirical.loc[.5]),"empirical_Q1_months":float(empirical.loc[.25]),"empirical_Q3_months":float(empirical.loc[.75]),
            "maximum_months":float(durations.max()),"horizon_months":h,"number_at_risk":at_risk,"deaths_observed_by_horizon":events_by,
            "support_assessment":("supported" if h == 60 else "supported_with_less_precise_tail") if at_risk>=500 and events_by>=100 else "limited"})
    pd.DataFrame(summary_rows).to_csv(TABLE_DIR / "followup_summary.csv", index=False)

    # Refit the already frozen Sprint 1 specification on training solely to recover its baseline survival.
    # Coefficients are asserted equal to the locked values and never replaced by temporal estimates.
    cph = CoxPHFitter(penalizer=0.0).fit(train[[TIME,EVENT,"DemoRisk","PhysioRisk"]], TIME, EVENT, batch_mode=True)
    assert np.allclose(cph.params_.loc[["DemoRisk","PhysioRisk"]], [BETA_DEMO,BETA_PHYSIO], rtol=1e-9, atol=1e-10)
    center = float(cph._norm_mean.loc[["DemoRisk","PhysioRisk"]] @ cph.params_.loc[["DemoRisk","PhysioRisk"]])
    test_lp = test["CalibratedTotalRisk"].to_numpy()
    test_km = KaplanMeierFitter().fit(test[TIME], test[EVENT])
    censor_km_test = KaplanMeierFitter().fit(test[TIME], 1-test[EVENT])
    cal_rows, plot_rows = [], []
    for h in (60,96):
        base_surv = float(cph.baseline_survival_.reindex(cph.baseline_survival_.index.union([h])).sort_index().ffill().loc[h].iloc[0])
        pred = 1 - np.power(base_surv, np.exp(test_lp-center))
        observed = 1-_km_at(test_km,h)
        brier, usable = _ipcw_brier(test[TIME],test[EVENT],pred,h,censor_km_test)
        y_h, pred_h, weights_h = _ipcw_binary_data(test[TIME],test[EVENT],pred,h,censor_km_test)
        logit_pred = np.log(np.clip(pred_h,1e-8,1-1e-8) / np.clip(1-pred_h,1e-8,1-1e-8)).reshape(-1,1)
        fixed_cal = LogisticRegression(C=np.inf, solver="lbfgs", max_iter=1000).fit(logit_pred, y_h, sample_weight=weights_h)
        slope_df = test[[TIME,EVENT]].copy(); slope_df["frozen_lp"] = test_lp
        slope_fit = CoxPHFitter(penalizer=0.0).fit(slope_df,TIME,EVENT,batch_mode=True,
            fit_options={"step_size":.5,"max_steps":1000,"precision":1e-9})
        ss=slope_fit.summary.loc["frozen_lp"]
        cal_rows.append({"model":"CalibratedTotalRisk","value_provenance":"recomputed/revised","cohort":"temporal_test",
            "horizon_months":h,"training_baseline_survival":base_surv,"mean_predicted_mortality_risk":float(pred.mean()),
            "KM_observed_mortality":observed,"calibration_in_large_observed_minus_predicted":observed-float(pred.mean()),
            "observed_to_expected_ratio":observed/float(pred.mean()),"calibration_slope":float(ss["coef"]),
            "calibration_slope_95CI_low":float(ss["coef lower 95%"]),"calibration_slope_95CI_high":float(ss["coef upper 95%"]),
            "global_calibration_slope_method":"temporal Cox coefficient on frozen LP; assumes PH",
            "horizon_specific_calibration_intercept":float(fixed_cal.intercept_[0]),
            "horizon_specific_calibration_slope":float(fixed_cal.coef_[0,0]),
            "horizon_specific_calibration_method":"IPCW-weighted logistic calibration on logit(frozen absolute risk)",
            "IPCW_Brier_score":brier,"IPCW_weight_source":"temporal-test censoring KM (evaluation only)","IPCW_usable_N":usable,
            "no_temporal_recalibration":True})
        bins = pd.qcut(pred, q=10, duplicates="drop")
        for bin_id, idx in pd.Series(np.arange(len(test))).groupby(bins, observed=True):
            ii=idx.to_numpy(); km=KaplanMeierFitter().fit(test[TIME].iloc[ii],test[EVENT].iloc[ii])
            plot_rows.append({"model":"CalibratedTotalRisk","value_provenance":"recomputed/revised","cohort":"temporal_test","horizon_months":h,
                "risk_bin":str(bin_id),"N":len(ii),"deaths_total":int(test[EVENT].iloc[ii].sum()),"mean_predicted_risk":float(pred[ii].mean()),
                "KM_observed_risk":float(1-_km_at(km,h)),"number_at_risk_at_horizon":int((test[TIME].iloc[ii]>=h).sum())})
    pd.DataFrame(cal_rows).to_csv(TABLE_DIR / "calibration_fixed_horizons.csv",index=False)
    pd.DataFrame(plot_rows).to_csv(TABLE_DIR / "calibration_plot_data.csv",index=False)


def _schoenfeld_plot_data(test, label, col):
    d, fit, _, _, _ = controlled_cox(test, col)
    fit_df = d[[TIME, EVENT, "predictor_z"]]
    residual = fit.compute_residuals(fit_df, kind="scaled_schoenfeld")["predictor_z"]
    out = pd.DataFrame({"source_index":residual.index, "event_time_months":test.loc[residual.index,TIME].to_numpy(),
                        "scaled_schoenfeld_residual":residual.to_numpy()}).sort_values("event_time_months")
    out["model"] = label; out["value_provenance"] = "recomputed/revised"; out["cohort"] = "temporal_test"
    out["log_event_time_centered_60m"] = np.log(out.event_time_months / 60.0)
    out["rolling_mean_51_events"] = out.scaled_schoenfeld_residual.rolling(51,center=True,min_periods=15).mean()
    out["followup_region"] = pd.cut(out.event_time_months,[-np.inf,36,72,np.inf],labels=["early_0_36m","middle_37_72m","late_73m_plus"])
    return out


def _expand_time_varying(test, col):
    x = (test[col] - test[col].mean()) / test[col].std(ddof=1)
    event_times = np.sort(test.loc[test[EVENT].eq(1),TIME].unique().astype(float))
    pieces=[]
    for i,(end,event,score) in enumerate(zip(test[TIME].to_numpy(float),test[EVENT].to_numpy(int),x.to_numpy(float))):
        stops=event_times[event_times < end]
        if event == 1 or len(stops)==0 or stops[-1] < end:
            stops=np.append(stops,end)
        starts=np.r_[0.0,stops[:-1]]
        valid=stops>starts
        stops,starts=stops[valid],starts[valid]
        ev=np.zeros(len(stops),int)
        if event==1 and len(ev): ev[-1]=1
        pieces.append(pd.DataFrame({"id":i,"start":starts,"stop":stops,"event":ev,"score_z":score,
            "score_z_x_log_time":score*np.log(np.clip(stops,1e-6,None)/60.0)}))
    return pd.concat(pieces,ignore_index=True)


def _time_interaction(test, label, col):
    tv=_expand_time_varying(test,col)
    fit=CoxTimeVaryingFitter(penalizer=0.0).fit(tv,id_col="id",start_col="start",stop_col="stop",event_col="event",show_progress=False,
        fit_options={"step_size":0.1,"max_steps":1000,"precision":1e-9})
    main=fit.summary.loc["score_z"]; inter=fit.summary.loc["score_z_x_log_time"]
    b0=float(main["coef"]); b1=float(inter["coef"])
    return {"model":label,"value_provenance":"recomputed/revised","cohort":"temporal_test","N":len(test),"deaths":int(test[EVENT].sum()),
        "score_scale":"actual temporal-cohort SD","time_interaction":"score_z * log(time_months/60)","reference_time_months":60,
        "log_HR_per_SD_at_60m":b0,"HR_per_SD_at_12m":float(np.exp(b0+b1*np.log(12/60))),"HR_per_SD_at_60m":float(np.exp(b0)),
        "HR_per_SD_at_96m":float(np.exp(b0+b1*np.log(96/60))),"interaction_coef_per_log_time":b1,
        "interaction_HR_multiplier_per_e_fold_time":float(np.exp(b1)),"interaction_95CI_low":float(inter["coef lower 95%"]),
        "interaction_95CI_high":float(inter["coef upper 95%"]),"interaction_p_value":float(inter["p"]),
        "direction":"effect_weakens_over_time" if b1<0 else "effect_strengthens_over_time","diagnostic_only":True}


def _robust_discrimination(train,test):
    from sksurv.metrics import concordance_index_ipcw, cumulative_dynamic_auc
    from sksurv.util import Surv
    ytr=Surv.from_arrays(train[EVENT].astype(bool),train[TIME].astype(float))
    yte=Surv.from_arrays(test[EVENT].astype(bool),test[TIME].astype(float))
    rows=[]
    for label,col in [("DemoRisk","DemoRisk"),("PhysioRisk","PhysioRisk"),("CalibratedTotalRisk","CalibratedTotalRisk"),
                      ("PhenoAge NCP","PhenoAge NCP"),("PhenoAge NCP acceleration","PhenoAge NCP acceleration")]:
        score=test[col].to_numpy(float)
        aucs,_=cumulative_dynamic_auc(ytr,yte,score,np.array([60.,96.]))
        for h,auc in zip((60,96),aucs):
            uno=concordance_index_ipcw(ytr,yte,score,tau=float(h))[0]
            rows.append({"model":label,"value_provenance":"recomputed/revised","evaluation_cohort":"temporal_test",
                "censoring_distribution_cohort":"training (1999-2010)","training_N_for_censoring":len(train),"test_N":len(test),
                "horizon_months":h,"Uno_C_IPCW_truncated_at_horizon":float(uno),"cumulative_dynamic_AUC_IPCW":float(auc),
                "implementation":"scikit-survival 0.28.0","diagnostic_only":True})
    return pd.DataFrame(rows)


def run_diagnostic_addendum(train=None,test=None):
    if train is None or test is None:
        _,train,test=load_verified(); add_frozen_scores(train,test)
    residuals=[]; interactions=[]
    for label,col in [("DemoRisk","DemoRisk"),("PhysioRisk","PhysioRisk"),("CalibratedTotalRisk","CalibratedTotalRisk")]:
        residuals.append(_schoenfeld_plot_data(test,label,col)); interactions.append(_time_interaction(test,label,col))
    residual_df=pd.concat(residuals,ignore_index=True)
    residual_df.to_csv(TABLE_DIR/"ph_schoenfeld_residuals.csv",index=False)
    regions=(residual_df.groupby(["model","followup_region"],observed=True)
             .agg(events=("scaled_schoenfeld_residual","size"),mean_scaled_residual=("scaled_schoenfeld_residual","mean"),
                  median_scaled_residual=("scaled_schoenfeld_residual","median")).reset_index())
    interaction_df=pd.DataFrame(interactions)
    interaction_df.to_csv(TABLE_DIR/"ph_time_interaction.csv",index=False)
    ph=pd.read_csv(TABLE_DIR/"ph_diagnostics.csv")
    ph=ph.merge(regions.groupby("model").apply(lambda g:"; ".join(f"{r.followup_region}: mean={r.mean_scaled_residual:.3f}" for _,r in g.iterrows()),include_groups=False).rename("scaled_residual_region_summary"),on="model",how="left")
    ph.to_csv(TABLE_DIR/"ph_diagnostics.csv",index=False)
    _robust_discrimination(train,test).to_csv(TABLE_DIR/"censoring_robust_discrimination.csv",index=False)
    return interaction_df


def run_cohort_sensitivity():
    benchmark, train, test = load_verified(); add_frozen_scores(train,test)
    flow = [
        ("source analytic dataset retained",len(benchmark),"reconstructable; earliest retained benchmark"),
        ("adult eligibility",int(benchmark[AGE].ge(18).sum()),"recoverable within retained benchmark; upstream exclusions unknown"),
        ("mortality linkage / usable survival outcome",int(benchmark[[TIME,EVENT]].notna().all(axis=1).sum()),"recoverable within retained benchmark"),
        ("required PhysioRisk biomarkers complete",int(benchmark[PHYSIO_COLS].notna().all(axis=1).sum()),"raw complete-case availability; frozen scored cohort retained all rows"),
        ("PhenoAge NCP biomarkers complete",int(benchmark[PHENO_COLS].notna().all(axis=1).sum()),"no-CRP proxy inputs before training-median imputation"),
        ("benchmark-aligned train cohort",len(train),"cycles 1999-2010"),("benchmark-aligned temporal cohort",len(test),"cycles 2011-2016")]
    pd.DataFrame([{"flow_stage":s,"count":n,"value_provenance":"recomputed/revised","reconstruction_status":note} for s,n,note in flow]).to_csv(TABLE_DIR/"cohort_flow.csv",index=False)
    miss=[]
    for cycle,g in benchmark.groupby("cycle_start_year"):
        for col in sorted(set(PHENO_COLS+PHYSIO_COLS)):
            miss.append({"cycle_start_year":int(cycle),"biomarker":col,"N":len(g),"missing_N":int(g[col].isna().sum()),
                         "missing_percent":100*float(g[col].isna().mean()),"value_provenance":"recomputed/revised","cohort":"retained_benchmark"})
    pd.DataFrame(miss).to_csv(TABLE_DIR/"missingness_by_cycle.csv",index=False)

    complete = test[PHENO_COLS].notna().all(axis=1) & test[PHYSIO_COLS].notna().all(axis=1)
    sens=[]
    for label,col in [("PhysioRisk","PhysioRisk"),("PhenoAge NCP (no-CRP proxy)","PhenoAge NCP")]:
        d=test.loc[complete,[TIME,EVENT,AGE,col]]
        sens.append({"analysis":"common_complete_case","score":label,"value_provenance":"recomputed/revised","cohort":"temporal_test",
            "N":len(d),"deaths":int(d[EVENT].sum()),"C_index":concordance_index(d[TIME],-d[col],d[EVENT]),"age_correlation":float(d[col].corr(d[AGE])),
            "missing_data_rule":"identical participants; all no-CRP comparator and PhysioRisk biomarkers observed","status":"performed"})
    for row in list(sens):
        sens.append({**row, "analysis":"common_training_derived_imputation", "missing_data_rule":
            "no-op in retained benchmark because all required biomarkers are observed; upstream imputation cannot be reconstructed",
            "status":"performed as degenerate no-missing sensitivity; extension to excluded source participants not estimable without frozen residualization parameters"})
    pd.DataFrame(sens).to_csv(TABLE_DIR/"comparator_sensitivity.csv",index=False)

    included=benchmark[PHENO_COLS].notna().all(axis=1)&benchmark[PHYSIO_COLS].notna().all(axis=1)
    chars=[]
    for group,mask in [("common_complete_case",included),("excluded_for_any_required_biomarker_missing",~included)]:
        g=benchmark.loc[mask]
        chars.append({"group":group,"value_provenance":"recomputed/revised","N":len(g),"age_mean":g[AGE].mean(),"age_SD":g[AGE].std(ddof=1),
                      "female_percent":100*g.RIAGENDR.eq(2).mean(),"deaths_N":int(g[EVENT].sum()),"deaths_percent":100*g[EVENT].mean(),
                      "median_followup_months":g[TIME].median()})
    pd.DataFrame(chars).to_csv(TABLE_DIR/"cohort_included_excluded_characteristics.csv",index=False)


if __name__ == "__main__":
    run_validation(); run_cohort_sensitivity()
    print(json.dumps({"bootstrap_seed":SEED,"bootstrap_replicates":N_BOOT,"status":"complete"}))
