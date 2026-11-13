# S&P 500 Forecast Evidence

The V3 model produces **7,603.30 index points** for the official S&P Dow Jones Indices closing level on **20 November 2026 at 16:00 EST (21:00 UTC)**.

The coursework information cutoff was 13 November at 12:00 UTC. This forecast was reconstructed at 15:17:59 UTC using observations dated before the cutoff. Exact historical publication times were not independently verified for every observation.

## Reproduce the forecast offline

Clone the repository or download and extract it using GitHub's **Code → Download ZIP** option. Run these commands from the repository root with Python 3.9.6. The model uses only the standard library.

```sh
cd IFTE0007_SP500_20261113
python3 model/forecast.py --origin 2026-11-12 --target 2026-11-20 --output results/rerun.json
```

The output should show a forecast of **7603.30**. Compare the input hashes and forecast with the saved record. The rerun reports its own execution time.

## Model and inputs

V3 fits a single-factor ridge regression to 252 matured daily observations. The factor is the change in the US ten-year Treasury yield across five valid observation intervals. The model forecasts a six-session log return and retains half the implied change in the index level.

The baseline is the 12 November close of **7,592.40**. DGS10 rose from **4.95%** on 3 November to **4.98%** on 10 November. The fitted raw level is **7,614.197104**. Retaining half the change from the baseline gives **7,603.30** after rounding.

## Files and evidence

- [Python model](IFTE0007_SP500_20261113/model/forecast.py)
- [Saved input data](IFTE0007_SP500_20261113/data)
- [Forecast record, sources and input hashes](IFTE0007_SP500_20261113/final_forecast_record.json)
- [Agent instructions and calculation transcript](IFTE0007_SP500_20261113/agent)
- [Saved calculation output](IFTE0007_SP500_20261113/results/reproduction.json)

## Reproduce the historical comparison

From the coursework folder, run:

```sh
python3 model/forecast.py --validate
```

This writes `results/reproduced_validation.json` with 753 matched forecasts and the three-period MAPE comparison. The intercept-only benchmark uses the same training labels and shrinkage as V3. The forecast rerun writes to `results/rerun.json`. The archived calculation is in `results/reproduction.json`.

[Read the forecast report](report/SP500%20Forecast%20Report.pdf).
