# vix_exp_hypoth
**Description** \
This paper tests expectations hypothesis for realized variance by way of an options trading strategy.

**Instructions** \
To run the code in this project, you will need a [WRDS](https://wrds-www.wharton.upenn.edu) research account with subscriptions to the following datasets:
[OptionMetrics - Forward Price](https://wrds-www.wharton.upenn.edu/pages/get-data/optionmetrics/ivy-db-us/options/forward-price/)
[OptionMetrics - Option Prices](https://wrds-www.wharton.upenn.edu/pages/get-data/optionmetrics/ivy-db-us/options/option-prices/)
[Compustat Daily Updates - Index Daily Prices](https://wrds-www.wharton.upenn.edu/pages/get-data/compustat-capital-iq-standard-poors/compustat/north-america-daily/index-prices-daily/)

To run this code on your local machine, you will need to create .pgpass file in your home directory and this will be read by `wrds_creds.py` when trying to connect to WRDS' databases. You can read [this](https://www.postgresql.org/docs/current/libpq-pgpass.html) for more information about creating a .pgpass file. [wrds.py](https://github.com/wharton/wrds/blob/main/wrds/sql.py) also will help you create a .pgpass file if you do not have one initially.


**Data** \
Option Data: Individual option price data comes from [OptionMetrics](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/optionmetrics/).

Treasury Rates: Interest rate data used comes courtesy of the U.S. Department of Treasury's [Daily Treasury Par Yield Curve Rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=202608).

Settlement: Index Options are settled according to settlement index values provided by the [CBOE](https://www.cboe.com/index_settlement_values/). For example, S&P500 index options are settled according to the "S&P 500 (SET)".

Forward/Spot Prices: Forward levels are provided in the OptionMetrics dataset. Spot prices are availible in Compustat daily index files.