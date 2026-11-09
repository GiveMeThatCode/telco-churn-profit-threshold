# How the RapidMiner process files work

This folder holds the twelve processes that refit the final model for each run and score the holdout set:

`r1_04_final_holdout_lr.rmp`, `..._dt.rmp`, `..._rf.rmp`, `..._gbt.rmp`, and the same four for runs 2 and 3 (`r2_...`, `r3_...`).

They were built and run in RapidMiner Studio 9.10.008. The twelve processes are identical except for four things: the model operator, the two input tables, the output file name and the random seed.

## What one process does

Read left to right in the process view.

| Step | Operator | What it does |
|---|---|---|
| A1 | Retrieve | Loads the development table of that run, for example `../data/telco_oof_predictions_dt_r1`. |
| A2 | Select Attributes | Drops the old prediction columns `prediction(Churn)`, `confidence(Yes)` and `confidence(No)`, so only the inputs and the label remain. |
| B1 | Model operator | Fits the final model on all 4,930 development customers (LR, DT, RF or GBT, with the settings in Section 2.3 of the paper). |
| C1 | Retrieve | Loads the 30% holdout table of that run (2,113 customers), for example `../data/telco_holdout_30pct_r1`. |
| C1 | Apply Model | Scores the holdout with the fitted model. |
| C1 | Multiply | Sends the scored holdout to two places: the accuracy check (C2) and the export (D1). |
| C2 | Performance (binominal) | Computes accuracy and AUC on the holdout as a sanity check, positive class `Yes`. It is not used for any reported result. |
| D1 | Generate Attributes | Adds `c = min(max(confidence(Yes), 0.001), 0.999)` and `y = 1` if `Churn` is `Yes`, else `0`. |
| D1 | Select Attributes | Keeps four columns: `customerID`, `y`, `c`, `MonthlyCharges`. |
| D1 | Write CSV | Exports the per-customer holdout file that the Python scripts read, for example `final_holdout_dt_r1_per_customer.csv`. |

The Python scripts then do everything else: Platt scaling, the seven rules, profit and the bootstrap.

## The two paths you need to change

A process stores no data. It points to two kinds of place, and both depend on the computer that runs it.

**1. Input tables (the two Retrieve operators, A1 and C1).**
The paths are relative to the process: `../data/telco_oof_predictions_dt_r1` means an entry named `telco_oof_predictions_dt_r1` in a folder `data` that sits one level above the folder holding the process, inside your RapidMiner repository.

Either build that layout, or point each operator to your own tables:
1. Click the operator, then look at the **Parameters** panel.
2. Click the folder icon next to **repository entry** and choose your table.
3. A1 needs the development table of that run, with the label `Churn` and the three prediction columns that A2 removes. C1 needs the holdout table of that run, with the label `Churn` and the columns `customerID` and `MonthlyCharges`.
4. Use the development and holdout tables of the same run. Each run has its own split, so mixing runs breaks the design.

**2. Output folder (the Write CSV operator, D1).**
The output file is `%{export_dir}/final_holdout_dt_r1_per_customer.csv`. `%{export_dir}` is a macro defined once in the process context, so you change it in one place:
1. Open the **Context** panel (View, Show Panel, Context).
2. In the Macros list, edit the value of export_dir. The shared files ship with the value exports; set it to a full path of a folder you own, for example C:/Users/yourname/Documents/exports or /home/yourname/exports.
3. Leave the file name alone, so the scripts can find the file.

**Do not point `export_dir` at a folder that already holds exports.** Write CSV has "append to file" switched off, so running the process overwrites the file with the same name.

## Settings to leave alone

- The **random seed** of the root *Process* operator is the process seed from Table 2 of the paper (run 1: 6989, run 2: 5513, run 3: 8420). RF and GBT use it.
- The model settings (Section 2.3 of the paper). No tuning.
- The positive class `Yes` in the Performance operator.

Press **Run** once. The CSV is the only output that matters. The Performance result is a check.

## What this repository cannot do

- The data tables are not included, because the Kaggle licence is "Data files © Original Authors". You must download the Telco churn dataset yourself.
- The steps that created the development and holdout tables (stratified 70/30 split, stratified 10-fold cross-validation for the out-of-fold predictions, with the seeds in Table 2 of the paper) are not part of these twelve files. These processes are the final step only. Without the same split you will get different customers in each set, so your numbers will differ slightly from the paper.
- The Python scripts in `../scripts/` read the exported files and write the result tables. See the README for how to point them at your export folder.

## Check after a run

- The export has one row per holdout customer (2,113) and four columns: `MonthlyCharges`, `customerID`, `c` and `y` (the order may differ; the scripts read them by name).
- `c` lies between 0.001 and 0.999.
- The AUC shown by the Performance operator is close to the range in Section 4.1 of the paper for that model.
