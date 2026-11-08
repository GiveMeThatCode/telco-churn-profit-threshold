# PROTOCOL: Telco churn profit-optimal threshold

Written 7 Nov 2026. Last revised 8 Nov 2026, before any holdout was used.

Rule: nothing below changes after the holdout is opened. If something must change, a dated amendment is added at the bottom saying what and why.

## 1. DATA AND SPLIT

- Data: original IBM Telco sample as distributed on Kaggle (BlastChar), 7,043 rows x 21 columns, about 26.5% churn. No CLTV, campaign outcome or acceptance data. All profit results are simulations on assumed parameters.
- Run 1 is the primary run. Runs 2 and 3 are OPTIONAL replications: if they are run, all of them are reported whatever they show; if skipped, say so in Limitations (single split). Each run has its own stratified 70/30 split (dev about 4,930 rows, holdout about 2,113 rows), its own stratified 10-fold CV on dev, and its own process seed. Each holdout is used once, for reporting only.
- Run 1: split seed 5416, CV seed 1790, process seed 6989.  Run 2: split 4821, CV 9137, process seed 5513.  Run 3: split 7306, CV 2578, process seed 8420.
- Thresholds, calibration and sweep optima are chosen separately inside each run, only from that run's dev OOF predictions.
- The three holdouts overlap (repeated random splits), so replications are not independent samples. Report the mean and the range across runs.

## 2. MODELS AND CALIBRATION

- RapidMiner (Altair AI Studio) 9.10.008, native models: Logistic Regression, Decision Tree, Random Forest, Gradient Boosted Trees.
- Confidence c is clipped to [0.001, 0.999] before the logit.
- Calibration: Platt scaling (2 parameters) for all four models, fitted on dev OOF predictions. Platt is the primary calibrator for every model.
- Any second calibrator (for DT or GBT) is a sensitivity analysis only, labeled as such, run after the holdout result.
- GBT: learning rate 0.1, reproducible true, 50 trees, depth 5 (run 1 as first run used 0.01 and is replaced). Observed with 0.01: raw confidences 0.160-0.525.
- Positive class set to Yes in every Performance operator. The OOF "prediction" column is not used for any result or baseline.
- RF and GBT use the process seed (use_local_random_seed false). Platt A and B are fitted per run and per model.

## 3. PROFIT FUNCTION

- Expected gain per flagged customer = p*a*V - c.
- c is paid for every flagged customer (accepting or not). This is an assumption.
- Analytic threshold: tau = c / (a*V), flag when p > tau.
- Constant-V rule uses V = mean dev MonthlyCharges (recomputed from each run's own dev set) x H.
- Customer-specific rule: V_i = MonthlyCharges_i x H, tau_i = c / (a*V_i).
- Flag rule: p > t on both the empirical and analytic sides.

## 4. PARAMETERS (all assumed; sources to be added after reading the papers)

- Base case: a = 0.3, H = 6 months, c = tau * a * V.
- Worked example only (from the discarded first split, mean 64.784): H = 6 gives V = 388.70, a*V = 116.61. Recompute from the run-1 dev set.
- Grid for a: 0.1, 0.2, 0.3, 0.4, 0.5. Grid for H: 3, 6, 12.
- Tau grid: 0.05, 0.10, 0.15, 0.20, 0.30, 0.40. Main text shows 0.10, 0.20, 0.30; the rest go in the appendix.
- Placeholder origin: default values used by software implementing Verbraken et al. (2013): acceptance 0.3, customer value 200, incentive cost 10, contact cost 1. NOT yet checked against the paper.

## 5. SWEEP AND BAND

- Empirical sweep on dev OOF in p-space, bins of 0.01.
- Near-optimal band: every threshold with profit >= 98% of the maximum. The 2% tolerance is fixed.
- Report band width next to every gap between t* and tau.
- If maximum profit <= 0 for a tau, the best action is "offer nobody".

## 6. HOLDOUT COMPARISON (seven rules)

offer nobody; offer everybody; threshold 0.5 applied to calibrated p; F1-optimal threshold (chosen on dev OOF); analytic constant threshold; empirical optimum (from dev OOF); customer-specific V_i rule.
- Paired profit differences between rules.
- Interval for holdout profit by bootstrap (1,000 resamples of the holdout), in RapidMiner if feasible, otherwise in Excel, stated in Methods.

## 7. KNOWN LIMITS TO STATE IN THE PAPER

- Assumed a, V, H and c; no campaign outcome data, so all profits are simulated.
- Sample dataset (external validity).
- Single primary split (run 1); runs 2 and 3, if run, overlap with it and are not independent samples.
- Platt fitted in-sample on dev OOF; calibration is only truly tested on the holdout.
- Platt is known from dev to fit DT poorly (few distinct scores); DT results are reported as a calibration failure.
- c is paid for every flagged customer; richer cost structures (incentive paid only on acceptance) are not modeled.
- With constant V the optimum depends only on tau by algebra, so the real test is the V_i rule, which has no empirical counterpart.
- The bootstrap captures holdout sampling noise only, not model or split variance.
- RapidMiner limits (native models only, no tuning); GBT uses fixed settings (50 trees, depth 5, learning rate 0.1) and RF/GBT use the process seed.
- Near-optimal band is wide at low tau, so agreement between t* and tau there is weak evidence.

## 8. ADDITIONAL RULES (added 8 Nov 2026, before any holdout use)

- a. Holdout scoring uses realized churn, not model probability: gain_i = y_i*a*V_i - c for each flagged customer, 0 otherwise, with V_i = MonthlyCharges_i x H for EVERY rule. Only the flagging rule differs between rules. a is the expected acceptance rate (no random acceptance is simulated).
- b. Primary comparison (one only): base case a = 0.3, H = 6, tau = 0.10, V_i rule versus constant analytic rule, per model, with a paired bootstrap 95% interval (same resamples for both rules). All other tau, a, H cells and the t*-versus-tau comparison are secondary and labeled exploratory.
- c. Platt stays the primary calibrator for all four models. For DT only, a sensitivity analysis with histogram binning (bins under 100 rows merged, fitted on dev OOF) is fixed here in advance and reported as sensitivity only.
- d. Final models are refit on the full dev set; Platt A and B come from the dev OOF predictions; holdout predictions come from the refit models.
- e. No empirical counterpart exists for the V_i rule; this is stated as a limitation.

## Amendments and clarifications (after the holdout was opened)

Sections 1 to 8 above are unchanged. The entries below record what was done after the first holdout was exported.

- **A1** (8 Nov 2026, after the run 1 holdout files were exported and before any run 1 profit result was computed): runs 2 and 3, which section 1 lists as optional, were carried out. All three runs are reported whatever they show.
- **A2** (8 Nov 2026, after the run 1 holdout profit results were computed; no rule changed): the holdout bootstrap and all profit tables are computed in Python (`holdout_analysis.py`, 1,000 resamples, seed 20261108) instead of RapidMiner or Excel (section 6). Runs 2 and 3 are analyzed the same way.
- **A3** (8 Nov 2026, after the run 3 holdout analysis; no rule changed): the DT histogram-binning sensitivity of rule 8c was run for all three runs (`dt_binning.py`). Bins are formed from distinct development out-of-fold scores and merged left to right until each has at least 100 rows, with a small final bin merged into the previous one. The bin churn rate is the calibrated p, and holdout scores map to the bin containing their raw score. It is reported as a sensitivity analysis only.
- **A4** (8 Nov 2026, after all three holdout analyses; no rule changed): holdout results are computed for tau = 0.10, 0.20 and 0.30 only (the main-text values of section 4); tau = 0.05, 0.15 and 0.40 are not computed on the holdout. The development near-optimal band (section 5) is reported for all six tau values. The grids for a (0.1 to 0.5) and H (3, 6, 12) of section 4 are not run: with c = tau * a * V-bar, both the analytic and the V_i threshold are independent of a and H, and holdout profit only rescales by a * H (checked numerically for a in 0.1, 0.3, 0.5 and H in 3, 6, 12).
- **A5** (8 Nov 2026; no rule changed): the parameter values of section 4 were checked against the literature. Acceptance 0.3, customer value 200, incentive cost 10 and contact cost 1 appear in Verbraken et al. (2013, p. 967) and Verbeke et al. (2012, p. 215); Neslin et al. (2006, p. 207) uses acceptance 10%, 30% and 50%. H = 6 months is the horizon used by Mozer et al. (2000, accepted manuscript). In this study all parameter values remain assumptions.
