"""Selected V3 model, offline standard-library implementation.
Run from any working directory: python model/forecast.py --validate
No automatic download, trading, or human approval claims.
"""
import argparse,bisect,csv,datetime as dt,hashlib,json,math,platform,statistics as st
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def load():
    def read(name,col):
        with (ROOT/'data'/name).open() as f:return {dt.date.fromisoformat(r['observation_date']):float(r[col]) for r in csv.DictReader(f) if r[col] not in ('','.','NA')}
    return read('daily,_close.csv','SP500'),read('daily.csv','DGS10')

def calculate(prices,rates,origin,horizon=6,window=252,shrink=.5,alpha=20):
    # Truncate before constructing factors or training labels.
    p={d:v for d,v in prices.items() if d<=origin};y={d:v for d,v in rates.items() if d<origin};dates=sorted(p);rd=sorted(y);xs={};timing={}
    if not dates or dates[-1]!=origin:raise ValueError('Baseline must be a saved completed close')
    for i in range(20,len(dates)):
        k=bisect.bisect_left(rd,dates[i])
        if k<6:continue
        a,b=rd[k-1],rd[k-6]
        if (dates[i]-a).days>7:continue
        xs[i]=y[a]-y[b];timing[i]=(a,b)
    i=len(dates)-1
    if i not in xs:raise ValueError('Insufficient usable rate observations')
    ids=[j for j in xs if j+horizon<i][-window:]
    if len(ids)!=window:raise ValueError('Insufficient matured training labels')
    x=[xs[j] for j in ids];returns=[math.log(p[dates[j+horizon]]/p[dates[j]]) for j in ids]
    mean=st.mean(x);sd=st.stdev(x) or 1;z=[(v-mean)/sd for v in x]
    # Exact 2x2 normal-equation solution, unpenalized intercept.
    n=len(z);sz=sum(z);sy=sum(returns);szz=sum(v*v for v in z)+alpha;szy=sum(a*b for a,b in zip(z,returns));det=n*szz-sz*sz
    intercept=(sy*szz-szy*sz)/det;slope=(n*szy-sz*sy)/det
    expected=intercept+slope*(xs[i]-mean)/sd;base=p[origin];raw=base*math.exp(expected);forecast=base+shrink*(raw-base)
    raw_slope=slope/sd;raw_intercept=intercept-raw_slope*mean
    assert abs(forecast-(base+shrink*(base*math.exp(raw_intercept+raw_slope*xs[i])-base)))<1e-8
    assert dates[ids[-1]+horizon]<origin
    return {'market':'S&P 500 price index','unit':'index points','origin':str(origin),'horizon_sessions':horizon,'baseline':base,'forecast':round(forecast,2),'forecast_full_precision':forecast,'factor_yield_change_percentage_points':xs[i],'yield_latest':str(timing[i][0]),'yield_lookback':str(timing[i][1]),'intercept':intercept,'standardized_slope':slope,'training_mean':mean,'training_sd':sd,'raw_factor_slope':raw_slope,'raw_factor_intercept':raw_intercept,'expected_log_return_before_shrink':expected,'raw_forecast':raw,'window':window,'alpha':alpha,'shrink':shrink,'last_training_target':str(dates[ids[-1]+horizon]),'n_train':n}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--origin');parser.add_argument('--target');parser.add_argument('--validate',action='store_true');parser.add_argument('--output',default='results/demo_forecast.json');args=parser.parse_args();p,y=load();out=ROOT/args.output
    if args.validate:
        origins=json.loads((ROOT/'model/validation_origins.json').read_text());rows=[]
        for pair in origins:
            origin=dt.date.fromisoformat(pair['origin']);target=dt.date.fromisoformat(pair['target']);r=calculate(p,y,origin);actual=p[target]
            r.update(target=str(target),actual=actual,APE_percent=100*abs(r['forecast_full_precision']-actual)/actual,unchanged_APE_percent=100*abs(p[origin]-actual)/actual);rows.append(r)
        later=[r for r in rows if r['origin']>='2023-01-01'];summary={'n':len(later),'MAPE_percent':st.mean(r['APE_percent'] for r in later),'unchanged_MAPE_percent':st.mean(r['unchanged_APE_percent'] for r in later),'max_APE_percent':max(r['APE_percent'] for r in later),'rows':rows,'python_version':platform.python_version()};out=ROOT/'results/reproduced_validation.json';out.write_text(json.dumps(summary,indent=2));print(json.dumps({k:v for k,v in summary.items() if k!='rows'},indent=2));return
    origin=dt.date.fromisoformat(args.origin) if args.origin else max(p);horizon=6
    if args.target:
        target=dt.date.fromisoformat(args.target)
        if target<=origin:raise ValueError('Target must follow origin')
        if target<=max(p):
            if target not in p:raise ValueError('Target is not an observed stock trading date')
            sessions=[d for d in sorted(p) if origin<d<=target]
        else:
            # This limited interval was verified against the NYSE 2026 holiday calendar.
            if not dt.date(2026,10,21)<=origin<target<=dt.date(2026,11,20):raise ValueError('Verify the exchange calendar before extending this future date interval')
            sessions=[];d=origin+dt.timedelta(days=1)
            while d<=target:
                if d.weekday()<5:sessions.append(d)
                d+=dt.timedelta(days=1)
        horizon=len(sessions)
        if horizon!=6:raise ValueError('Selected model and comparable validation require six sessions; refresh closer to submission or separately validate a different horizon')
    result=calculate(p,y,origin,horizon);result.update(run_utc=dt.datetime.now(dt.timezone.utc).isoformat(),python_version=platform.python_version(),status='DEMONSTRATION_ONLY_NOT_BINDING_FORECAST',target=args.target,input_sha256={name:hashlib.sha256((ROOT/'data'/name).read_bytes()).hexdigest() for name in ['daily,_close.csv','daily.csv']})
    out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
