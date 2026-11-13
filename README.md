# Telco churn: a profit-based decision threshold

Code, process files and result tables for the paper "A profit-based decision threshold for telecom churn retention offers: an analytic rule compared with a tuned threshold and with customer-specific value" (Khương Gia Huy, Nguyễn Văn Hồng Hậu, Nguyễn Hào Nam, Đỗ Hồ Hùng Phong, Trần Đình Sơn, Nguyễn Thế Vũ and Thon-Da Nguyen, University of Economics and Law, 2026).

The study asks whether the rule "contact a customer if the calibrated churn probability exceeds c/(a·V)" earns as much on a holdout as a threshold tuned on development data, and whether letting V vary with the customer's monthly charge helps. All profits are simulated from assumed parameters (a = 0.3, H = 6 months). They are not real campaign results.

## Data

The analysis uses the original IBM Telco customer churn sample on Kaggle: https://www.kaggle.com/datasets/blastchar/telco-customer-churn (7,043 customers, 21 variables; accessed 27 October 2026). The Kaggle page lists the licence as "Data files © Original Authors", so **the raw data and the per-customer prediction files are not included here**. Download the dataset from Kaggle if you need it.

## Contents

| Path | What it is |
|---|---|
| `protocol.md` | The analysis protocol, with a dated list of amendments made after the holdout was opened. |
| `process_files/` | The twelve RapidMiner Studio 9.10.008 processes that refit the final models and score the holdout (`r1_04_final_holdout_lr.rmp` and so on for DT, RF, GBT and runs 1 to 3), with `instructions.md` explaining how they work and which paths to change. |
| `scripts/holdout_analysis.py` | Platt scaling, the seven rules, holdout profit and the paired bootstrap, per run. |
| `scripts/dt_binning.py` | Decision tree sensitivity analysis with histogram binning. |
| `scripts/band.py` | Development near-optimal threshold band and development Brier scores. |
| `scripts/aggregate.py` | Averages the result tables over the three runs. |
| `scripts/plot_reliability.py`| Draws Fig. 2 (reliability of raw development out-of-fold scores) from the twelve `results/calib_fit_*_reliability.csv` files.|
| `results/` | `holdout_rules_r1..r3.csv`, `holdout_paired_r1..r3.csv`, `dt_binning_sensitivity.csv` (DT binning table), `band_output.txt` (output of `band.py`: near-optimal band counts and development Brier scores), and the aggregated reliability and Brier files. |

## Design in brief

- Three repeated stratified 70/30 splits (development 4,930, holdout 2,113), each with its own split, cross-validation and process seeds. Run 1 is the primary run. The holdouts overlap, so the runs are not independent.
- Models: logistic regression, decision tree, random forest and gradient boosted trees, all native RapidMiner operators with no tuning.
- Probabilities: Platt scaling fitted on development out-of-fold predictions only.
- Holdout profit uses realized churn. Intervals are paired bootstrap 95% intervals (1,000 resamples, seed 20261108).

| Run | Split seed | Cross-validation seed | Process seed |
|---|---|---|---|
| 1 | 5416 | 1790 | 6989 |
| 2 | 4821 | 9137 | 5513 |
| 3 | 7306 | 2578 | 8420 |

## Reproducing

The scripts read per-customer prediction files exported from RapidMiner. Those files are not shared (see Data), so the scripts document the analysis but cannot be rerun from this repository alone. Each script expects an `exports/` folder with subfolders `R1`, `R2` and `R3` (or a path passed as an argument), for example `python holdout_analysis.py r1 exports`, `python dt_binning.py exports` and `python band.py exports`. The result tables in `results/` are the exact outputs reported in the paper.

Versions of the final rerun, which reproduced every reported table exactly: Python 3.14.7; NumPy 2.5.4; pandas 3.0.6; scikit-learn 1.9.1; SciPy 1.18.1.

## Citation

Khương Gia Huy, Nguyễn Văn Hồng Hậu, Nguyễn Hào Nam, Đỗ Hồ Hùng Phong, Trần Đình Sơn, Nguyễn Thế Vũ and Thon-Da Nguyen. A profit-based decision threshold for telecom churn retention offers. Repository version: the commit cited in the paper.
