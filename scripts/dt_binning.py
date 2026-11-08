import pandas as pd, numpy as np, sys
from sklearn.linear_model import LogisticRegression
DATA=sys.argv[1] if len(sys.argv)>1 else 'exports'
a=0.3;H=6;MIN=100;B=1000;ts=np.round(np.arange(0,1.0,0.01),2)
def logit(c): c=np.clip(c,0.001,0.999); return np.log(c/(1-c))
def make_bins(c,y):
    u=np.sort(np.unique(c)); cnt=np.array([(c==v).sum() for v in u]); pos=np.array([y[c==v].sum() for v in u])
    edges=[];s=0;n=0;k=0  # greedy left-to-right; last small bin merges back
    groups=[];cur=[]
    for i in range(len(u)):
        cur.append(i); n+=cnt[i]
        if n>=MIN: groups.append(cur);cur=[];n=0
    if cur:
        if groups: groups[-1]+=cur
        else: groups.append(cur)
    lo=[u[g[0]] for g in groups]; rate=[pos[g].sum()/cnt[g].sum() for g in groups]; size=[cnt[g].sum() for g in groups]
    return np.array(lo),np.array(rate),np.array(size)
def apply(lo,rate,c): return rate[np.clip(np.searchsorted(lo,c,side='right')-1,0,len(lo)-1)]
rng=np.random.default_rng(20261108)
out=[]
for r in ['r1','r2','r3']:
    d=pd.read_csv(f'{DATA}/R{r[1]}/calib_fit_dt_{r}_per_customer.csv'); h=pd.read_csv(f'{DATA}/R{r[1]}/final_holdout_dt_{r}_per_customer.csv')
    yd=d.y.values;yh=h.y.values
    f=LogisticRegression(C=1e9,max_iter=1000).fit(logit(d.c).values.reshape(-1,1),yd)
    plat=lambda c:1/(1+np.exp(-(f.coef_[0][0]*logit(c)+f.intercept_[0])))
    lo,rate,size=make_bins(d.c.values,yd)
    assert size.min()>=MIN and size.sum()==len(d)
    print(f'{r}: {len(lo)} bins (min size {size.min()}), distinct raw scores {d.c.nunique()}')
    Vi=h.MonthlyCharges.values*H; aV=a*d.MonthlyCharges.mean()*H
    idx=rng.integers(0,len(h),(B,len(h)))
    for name,pf in [('Platt',plat),('Binning',lambda c:apply(lo,rate,c))]:
        pdv=pf(d.c.values);ph=pf(h.c.values)
        brd=((pdv-yd)**2).mean();brh=((ph-yh)**2).mean()
        def f1(t):
            fl=pdv>t;tp=(fl&(yd==1)).sum();fp=(fl&(yd==0)).sum();fn=((~fl)&(yd==1)).sum();return 2*tp/(2*tp+fp+fn) if tp>0 else 0
        tf1=ts[np.argmax([f1(t) for t in ts])]
        for tau in [0.10,0.20,0.30]:
            c=tau*aV
            N=np.array([(pdv>t).sum() for t in ts]);N1=np.array([yd[pdv>t].sum() for t in ts]);pr=N1-tau*N;ts_=ts[pr.argmax()] if pr.max()>0 else None
            fl={'0.5':ph>0.5,'F1':ph>tf1,'analytic':ph>tau,'empirical':(ph>ts_) if ts_ is not None else np.zeros(len(h),bool),'V_i':ph>c/(a*Vi)}
            G={k:v*(yh*a*Vi-c) for k,v in fl.items()}
            def ci(g): s=g[idx].sum(1);return np.percentile(s,2.5),np.percentile(s,97.5)
            vd=G['V_i']-G['analytic'];ae=G['analytic']-G['empirical']
            out.append(dict(run=r,cal=name,tau=tau,brier_dev=round(brd,4),brier_hold=round(brh,4),t_emp=ts_,t_f1=tf1,**{f'profit_{k}':round(v.sum()) for k,v in G.items()},
                n_analytic=int(fl['analytic'].sum()),V_minus_an=round(vd.sum()),V_lo=round(ci(vd)[0]),V_hi=round(ci(vd)[1]),an_minus_emp=round(ae.sum()),ae_lo=round(ci(ae)[0]),ae_hi=round(ci(ae)[1])))
R=pd.DataFrame(out);R.to_csv('dt_binning_sensitivity.csv',index=False)
pd.set_option('display.width',250);pd.set_option('display.max_columns',30)
print(R[R.tau==0.10].drop(columns='tau').to_string(index=False))
print(R[R.tau>0.10][['run','cal','tau','V_minus_an','V_lo','V_hi']].to_string(index=False))
print(R.groupby(['cal','tau'])[['profit_analytic','profit_V_i','V_minus_an','an_minus_emp','brier_hold']].mean().round(0 if False else 3).to_string())
