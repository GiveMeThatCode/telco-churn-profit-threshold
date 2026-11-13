"""Fig. 2: reliability of raw development out-of-fold scores.
Reads results/calib_fit_<model>_r<run>_reliability.csv (12 files) and draws observed churn rate against
mean raw score in ten equal-frequency groups, per model and run.

Usage:  python plot_reliability.py [folder_with_csvs] [output.png]
LR, RF and GBT files already hold ten groups of 493 customers. The DT files hold one row per distinct
score (97 to 140 rows), so they are regrouped into ten equal-count groups; a score shared by customers
that fall on both sides of a group boundary is split in proportion (its observed rate is assumed equal
on both sides)."""
import sys, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

FOLDER = sys.argv[1] if len(sys.argv) > 1 else 'results'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'fig2_reliability.png'
MODELS = ['lr', 'dt', 'rf', 'gbt']
RUNS = [1, 2, 3]
K = 10
STYLE = {1: ('tab:blue', 'o'), 2: ('tab:red', 's'), 3: ('tab:green', '^')}

def deciles(d, k=K):
    """d: columns mc (mean score), my (observed churn rate), n (customers); returns k (x, y) points."""
    d = d.sort_values('mc').reset_index(drop=True)
    cs = np.concatenate([[0], d.n.cumsum().values])
    edges = np.linspace(0, cs[-1], k + 1)
    pts = []
    for j in range(k):
        w = np.clip(np.minimum(cs[1:], edges[j + 1]) - np.maximum(cs[:-1], edges[j]), 0, None)
        pts.append(((w * d.mc).sum() / w.sum(), (w * d.my).sum() / w.sum()))
    return np.array(pts)

fig, axes = plt.subplots(1, 4, figsize=(12.9, 3.6), sharey=True)
for ax, m in zip(axes, MODELS):
    for r in RUNS:
        path = os.path.join(FOLDER, f'calib_fit_{m}_r{r}_reliability.csv')
        d = pd.read_csv(path)
        d.columns = ['c', 'mc', 'my', 'n']            # c, average(c), average(y), count(y)
        assert d.n.sum() == 4930, (path, d.n.sum())   # development set size
        p = deciles(d)
        c, mk = STYLE[r]
        ax.plot(p[:, 0], p[:, 1], color=c, marker=mk, markersize=5, linewidth=1.2, label=f'Run {r}')
    ax.plot([0, 1], [0, 1], 'k--', linewidth=1)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_title(m.upper())
    ax.set_xlabel('Mean raw score (decile)')
    ax.grid(alpha=0.3)
axes[0].set_ylabel('Observed churn rate')
axes[0].legend(loc='upper left', frameon=False)
fig.tight_layout()
fig.savefig(OUT, dpi=200)
print('saved', OUT)
