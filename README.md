# Airline Revenue Management Toolkit

An interactive Streamlit toolkit covering four revenue management problems: seat protection, overbooking, forecast monitoring and optimiser parameter testing. It is built on synthetic data to show the methods and the judgement around them.

**Live app:** https://airline-rm-toolkit-hx6qhavyqb3avitxnqvlw9.streamlit.app/

> Status: all demand data is synthetic. Next step is to estimate demand and fares from real US route data (BTS T-100 and DB1B).

## What it does

| Page | Question it answers | Key idea |
|---|---|---|
| **Seat protection (EMSR-b)** | How much revenue does protecting seats for high fares add, and what happens when the forecast is wrong? | EMSR-b nested booking limits vs first-come-first-served, Monte Carlo over 20,000 flights. Protection levels are computed from the forecast and revenue is simulated against actual demand. |
| **Overbooking** | How many seats should be sold above capacity given no-shows? | Binomial show-up model that balances empty seats against denied-boarding cost. |
| **Forecast monitor** | Is the forecast biased anywhere, even when the overall error looks fine? | WAPE and signed bias by market and booking window, with alerts above a threshold. |
| **Parameter A/B test** | How long must a change to optimiser settings be tested before the result is trustworthy? | Sample size and power for a test and control group of flights. |

## Main takeaway

Seat protection adds material revenue when the forecast is right. At the default settings EMSR-b earns about 14% more than first-come-first-served. That advantage shrinks as the forecast over-states demand, and at 30% over-forecast it turns negative. Forecast calibration matters as much as the optimisation algorithm, which is why the toolkit includes a bias monitor and a test-design page.

## Run it locally

    conda create -n rm-project python=3.11 -y
    conda activate rm-project
    pip install -r requirements.txt
    streamlit run app.py

A command-line version of the seat protection simulation is also available in `emsrb_demo.py` if present in the repo:

    python emsrb_demo.py

## Project structure

    app.py                    # entry point and navigation
    requirements.txt          # dependencies (needed for Streamlit Cloud)
    views/
      seat_protection.py      # EMSR-b vs FCFS
      overbooking.py          # overbooking limit optimisation
      forecast_monitor.py     # forecast accuracy and bias by segment
      parameter_test.py       # A/B test design for optimiser changes

## Method notes

- **EMSR-b:** classes are ranked by fare. For each class j, classes 1 to j are aggregated with summed mean and variance and a demand-weighted average fare. The protection level is set so that the probability of selling the last protected seat equals the next-lower fare divided by that average fare. The booking limit for class j+1 is capacity minus the protection level.
- **Simulation:** demand per class is normal, rounded and floored at zero. Low-fare demand arrives first, which is the worst case for revenue. Both strategies use the same random draws so the comparison is not distorted by sampling noise.
- **Overbooking:** passengers show independently, so shows are Binomial(booking limit, show rate). Revenue is fare times passengers flown minus denied-boarding cost times passengers denied.
- **Forecast monitor:** WAPE is the sum of absolute errors over the sum of actuals. Bias is the sum of signed errors over the sum of actuals. A bias is injected into one segment so the monitor has something to find.
- **A/B test:** two-sample comparison of mean revenue per flight using the normal approximation, n = 2 x ((z_alpha/2 + z_power) x sd / effect)^2 per group.

## Limitations

- Synthetic data. Small differences between runs are Monte Carlo noise.
- Single flight leg only: no network (origin-destination) optimisation, cancellations or recapture.
- Demand is assumed normal and independent across classes.
- The overbooking page uses one show-up rate. Real systems vary it by market, fare class and booking window.
- The A/B test page assumes flights in the test and control groups are comparable and independent.

## Roadmap

- Estimate demand per fare class from real route data. T-100 gives monthly passengers, seats and departures by route, and DB1B gives fares. T-100 passengers are capped by seats, so demand will need unconstraining.
- Back-test forecast bias on the real route data.
- Extend to a two-leg network example.

## Author

Pallavi Krishna - [Portfolio](https://www.pallavikrishnadata.com) | [LinkedIn](https://www.linkedin.com/in/pallavikrish/)
