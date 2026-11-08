import pandas as pd, numpy as np, sys
from sklearn.linear_model import LogisticRegression
D=sys.argv[1] if len(sys.argv)>1 else 'exports'
def logit(c): c=np.clip(c,0.001,0.999); return np.log(c/(1-c))
ts=np.round(np.arange(0,1.0,0.01),2)
for r in ['r1','r2','r3']:
    n=0;tot=0;miss=[];br=[]
    for m in ['lr','dt','rf','gbt']:
        d=pd.read_csv(f'{D}/R{r[1]}/calib_fit_{m}_{r}_per_customer.csv'); y=d.y.values
        f=LogisticRegression(C=1e9,max_iter=1000).fit(logit(d.c).values.reshape(-1,1),y)
        p=1/(1+np.exp(-(f.coef_[0][0]*logit(d.c.values)+f.intercept_[0])))
        N=np.array([(p>t).sum() for t in ts]); N1=np.array([y[p>t].sum() for t in ts])
        raw=((d.c-y)**2).mean(); pl=((p-y)**2).mean(); br.append(f'{m} {raw:.4f}->{pl:.4f}')
        for tau in [0.05,0.10,0.15,0.20,0.30,0.40]:
            pr=N1-tau*N
            if pr.max()<=0: continue
            b=ts[pr>=0.98*pr.max()]; tt=ts[np.argmin(abs(ts-tau))]; ok=b.min()<=tt<=b.max(); n+=ok; tot+=1
            if not ok: miss.append((m,tau))
    print(r,f'in band {n}/{tot}',miss,'| dev Brier raw->Platt:',', '.join(br))
