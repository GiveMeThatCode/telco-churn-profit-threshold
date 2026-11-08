import pandas as pd, numpy as np
pd.set_option('display.width',250)
R={r:pd.read_csv(f'holdout_rules_{r}.csv') for r in ['r1','r2','r3']}
P={r:pd.read_csv(f'holdout_paired_{r}.csv') for r in ['r1','r2','r3']}
def ms(v): return f'{np.mean(v):,.0f} ({np.min(v):,.0f} to {np.max(v):,.0f})'
def key(s):
    return 'empirical optimum (dev)' if s.startswith('empirical') else ('F1-optimal (dev)' if s.startswith('F1') else s)
rows={}
for m in ['LR','DT','RF','GBT']:
    for r in R:
        x=R[r][(R[r].tau==0.10)&(R[r].model==m)]
        for _,q in x.iterrows(): rows.setdefault((key(q.rule),m),[]).append(q.profit)
print('MEAN (min to max) holdout profit, tau 0.10')
t=pd.Series({k:ms(v) for k,v in rows.items()}).unstack()
print(t.reindex(columns=['LR','DT','RF','GBT']).to_string())
print('\nPAIRED diffs: mean (min to max) | excludes 0 in r1,r2,r3')
for tau in [0.10,0.20,0.30]:
  for c in P['r1'].comparison.unique():
    if tau!=0.10 and c!='V_i minus analytic constant': continue
    for m in ['LR','DT','RF','GBT']:
        v=[];e=[]
        for r in P:
            x=P[r][(P[r].tau==tau)&(P[r].comparison==c)&(P[r].model==m)].iloc[0]; v.append(x['diff']); e.append('Y' if x.excludes_0 else 'n')
        print(f'tau {tau} | {c:40s} | {m:3s} | {ms(v):30s} | {"".join(e)} | pos {sum(d>0 for d in v)}/3')
print('\nHoldout AUC (raw c) / Platt A')
for r in R:
    i=R[r][R[r].rule=='INFO']; print(r, {a.model:(a.lo,a.hi) for a in i.itertuples()})
