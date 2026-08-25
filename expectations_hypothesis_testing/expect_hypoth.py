import io
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from io import StringIO
from datetime import timedelta
import pytz
import datetime

import pandas_market_calendars as mcal
import yfinance as yf

if __name__ == "__main__":

    from helpers import (compute_option_portfolios,
                        check_quote_uniqueness,
                         expectation_hypothesis_regressions,
                         )

    lb_year=2020
    ub_year=2023
    ticker='SPX'
    num_periods_wanted=3
    monthly_portfolios, option_portfolios_df=compute_option_portfolios(num_periods_wanted,lb_year,ub_year,ticker)

    expectation_hypothesis_regressions(monthly_portfolios,None)
    #check_quote_uniqueness(ticker,lb_year,ub_year)
    

