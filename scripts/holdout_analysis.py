import pandas as pd, numpy as np, sys
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
RUN=sys.argv[1] if len(sys.argv)>1 else 'r1'
DATA=sys.argv[2] if len(sys.argv)>2 else 'exports'
DEV=DATA+'/R%s/calib_fit_{m}_%s_per_customer.csv'%(RUN[1],RUN)
HOLD=DATA+'/R%s/final_holdout_{m}_%s_per_customer.csv'%(RUN[1],RUN)
a=0.3; H=6; TAUS=[0.10,0.20,0.30]; MAIN=0.10; B=1000
ts=np.round(np.arange(0,1.0,0.01),2)
rng=np.random.default_rng(20261108)
def logit(c): c=np.clip(c,0.001,0.999); return np.log(c/(1-c))
res=[];boot_rows=[]
for m in ['lr','dt','rf','gbt']:
    d=pd.read_csv(DEV.format(m=m)); h=pd.read_csv(HOLD.format(m=m))
    fit=LogisticRegression(C=1e9,max_iter=1000).fit(logit(d.c).values.reshape(-1,1),d.y)
    A,Bc=fit.coef_[0][0],fit.intercept_[0]
    pf=lambda c:1/(1+np.exp(-(A*logit(c)+Bc)))
    pd_=pf(d.c.values); ph=pf(h.c.values); yd=d.y.values; yh=h.y.values
    Vbar=d.MonthlyCharges.mean()*H; aV=a*Vbar
    Vi=h.MonthlyCharges.values*H
    # F1-optimal threshold on dev
    def f1(t):
        fl=pd_>t; tp=(fl&(yd==1)).sum(); fp=(fl&(yd==0)).sum(); fn=((~fl)&(yd==1)).sum()
        return 2*tp/(2*tp+fp+fn) if tp>0 else 0
    tf1=ts[np.argmax([f1(t) for t in ts])]
    auc=roc_auc_score(yh,h.c.values)
    for tau in TAUS:
        c=tau*aV
        N=np.array([(pd_>t).sum() for t in ts]); N1=np.array([yd[pd_>t].sum() for t in ts])
        prof=N1-tau*N; tstar=ts[prof.argmax()] if prof.max()>0 else None
        flags={'offer nobody':np.zeros(len(h),bool),'offer everybody':np.ones(len(h),bool),
               'threshold 0.5 (calibrated p)':ph>0.5,'F1-optimal (dev, t=%.2f)'%tf1:ph>tf1,
               'analytic constant (p>tau)':ph>tau,
               'empirical optimum (dev, t*=%s)'%('nobody' if tstar is None else '%.2f'%tstar):(ph>tstar) if tstar is not None else np.zeros(len(h),bool),
               'V_i rule (p>c/(a*V_i))':ph>c/(a*Vi)}
        gain=lambda fl: (fl*(yh*a*Vi-c))
        G={k:gain(v) for k,v in flags.items()}
        idx=rng.integers(0,len(h),(B,len(h))) if True else None
        for k,g in G.items():
            tot=g.sum(); bs=g[idx].sum(1)
            res.append(dict(model=m.upper(),tau=tau,rule=k,flagged=int(flags[k].sum()),profit=round(tot,1),per_cust=round(tot/len(h),3),lo=round(np.percentile(bs,2.5),1),hi=round(np.percentile(bs,97.5),1)))
        # paired diffs
        for name,x,y_ in [('V_i minus analytic constant','V_i rule (p>c/(a*V_i))','analytic constant (p>tau)'),
                          ('analytic constant minus empirical','analytic constant (p>tau)',[k for k in G if k.startswith('empirical')][0]),
                          ('analytic constant minus 0.5 rule','analytic constant (p>tau)','threshold 0.5 (calibrated p)'),
                          ('analytic constant minus offer everybody','analytic constant (p>tau)','offer everybody')]:
            dg=G[x]-G[y_]; bs=dg[idx].sum(1)
            boot_rows.append(dict(model=m.upper(),tau=tau,comparison=name,diff=round(dg.sum(),1),lo=round(np.percentile(bs,2.5),1),hi=round(np.percentile(bs,97.5),1),excludes_0=bool(np.percentile(bs,2.5)>0 or np.percentile(bs,97.5)<0)))
    res.append(dict(model=m.upper(),tau=None,rule='INFO',flagged=0,profit=0,per_cust=0,lo=round(auc,3),hi=round(A,3)))
R=pd.DataFrame(res); P=pd.DataFrame(boot_rows)
R.to_csv(f'holdout_rules_{RUN}.csv',index=False); P.to_csv(f'holdout_paired_{RUN}.csv',index=False)
pd.set_option('display.width',250)
print(R[R.rule=='INFO'][['model','lo','hi']].rename(columns={'lo':'holdout AUC(raw c)','hi':'Platt A'}).to_string(index=False))
print(); print('MAIN tau=0.10, profit in $ over 2113 holdout customers (95% bootstrap interval)')
x=R[(R.tau==MAIN)]
for m in ['LR','DT','RF','GBT']:
    print(m); print(x[x.model==m][['rule','flagged','profit','lo','hi']].to_string(index=False))
print(); print(P[P.tau==MAIN].to_string(index=False))
print(); print('secondary V_i minus analytic'); print(P[(P.comparison=='V_i minus analytic constant')].to_string(index=False))
