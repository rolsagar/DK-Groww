# DK Groww — RSI + MACD Dashboard

A Streamlit dashboard for RSI + MACD technical analysis, covering a fixed
watchlist of 15 NSE stocks/ETFs, with the option to type in any other
NSE ticker.

## Watchlist included
- GAIL (India) Ltd — `GAIL.NS`
- HDFC Bank Ltd — `HDFCBANK.NS`
- ICICI Bank Ltd — `ICICIBANK.NS`
- Indian Oil Corp Ltd — `IOC.NS`
- InterGlobe Aviation Ltd (IndiGo) — `INDIGO.NS`
- ITC Ltd — `ITC.NS`
- Larsen & Toubro Ltd — `LT.NS`
- Motilal Oswal Nasdaq 100 ETF — `MON100.NS`
- Nippon India ETF Gold BeES — `GOLDBEES.NS`
- Reliance Industries Ltd — `RELIANCE.NS`
- SBI Silver ETF — `SBISILVER.NS`
- Tata Consumer Products Ltd — `TATACONSUM.NS`
- Tata Gold ETF — `TATAGOLD.NS`
- Tata Silver ETF — `TATSILV.NS`
- Trent Ltd — `TRENT.NS`

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL shown in the terminal (usually `http://localhost:8501`).

## Deploy for free (like the original)

1. Push this folder to a GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click "New app", pick the repo, set the main file to `app.py`, and deploy.
4. You'll get a public URL you can rename/share, just like the original dashboard.

## Notes

- Data comes live from Yahoo Finance via `yfinance` — no API key needed.
- To add/remove stocks, edit the `WATCHLIST` dictionary at the top of `app.py`
  (format: `"Display Name": "TICKER.NS"`).
- This tool is for educational/informational purposes only, not investment advice.
