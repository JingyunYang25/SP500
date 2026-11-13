# S&P 500 V3 forecast reconstruction

The model gives **7,603.30 index points** for the official 20 November 2026 close at 16:00 New York / 21:00 UTC.

The assignment information cutoff was 13 November at 12:00 UTC. The inputs were assembled and the model run at 2026-11-13T15:17:59.899976+00:00, after the cutoff. This is a reconstruction using observations dated before the cutoff. The archive does not establish a contemporaneous freeze or formal approval. Source links and input hashes are in the forecast record. Exact historical publication times were not independently verified for all rows.

## Inputs and calculation

The archived October FRED series were extended through 11 November for the equity index and 10 November for DGS10 from the FRED tables. The 12 November cash close of 7,592.40 was taken from AP and cross-checked against Yahoo Finance. The six subsequent equity sessions are 13, 16, 17, 18, 19 and 20 November. DGS10 on 10 November was 4.98%, versus 4.95% on 3 November. The factor was +0.03 percentage points. The raw level was 7,614.197104. Retaining half the movement from 7,592.40 yields 7,603.30.

## Reproduction

Extract the ZIP and run from its root with Python 3.9.6 (standard library only).

```sh
python3 model/forecast.py --origin 2026-11-12 --target 2026-11-20 --output results/reproduction.json
```

Check the forecast and input hashes against final_forecast_record.json. The rerun timestamp will reflect the actual execution time. The original calculation output is in agent/calculation_run.txt. No network, account or AI subscription is required.
