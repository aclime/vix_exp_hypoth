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
                         formula_checks,
                         )

    from helpers_Ftest import (compute_option_portfolios_Ftest,
                               formula_checks_Ftest)
    #forming portfolios
    """
    lb_year=1998
    ub_year=2023
    ticker='SPX'
    num_periods_wanted=3
    monthly_portfolios, option_portfolios_df=compute_option_portfolios(num_periods_wanted,lb_year,ub_year,ticker)
    monthly_portfolios.to_csv('expectations_hypothesis_testing/outputs/monthly_portfolios.csv')
    option_portfolios_df.to_csv('expectations_hypothesis_testing/outputs/option_portfolios.csv')

    expectation_hypothesis_regressions(monthly_portfolios,None)
    """
    #Formula Testing
    """
    monthly_portfolios=pd.read_csv('expectations_hypothesis_testing/outputs/monthly_portfolios.csv')
    option_portfolios=pd.read_csv('expectations_hypothesis_testing/outputs/option_portfolios.csv')
    formula_checks(monthly_portfolios,option_portfolios)
    """
    #check_quote_uniqueness(ticker,lb_year,ub_year)

    #making forward rates using F=S exp(rT)
    #"""
    lb_year=1998
    ub_year=2023
    ticker='SPX'
    num_periods_wanted=3
    monthly_portfolios, option_portfolios_df=compute_option_portfolios_Ftest(num_periods_wanted,lb_year,ub_year,ticker)
    monthly_portfolios.to_csv('expectations_hypothesis_testing/outputs/monthly_portfolios_Ftest.csv')
    option_portfolios_df.to_csv('expectations_hypothesis_testing/outputs/option_portfolios_Ftest.csv')
    #"""

    #"""
    monthly_portfolios=pd.read_csv('expectations_hypothesis_testing/outputs/monthly_portfolios_Ftest.csv')
    option_portfolios=pd.read_csv('expectations_hypothesis_testing/outputs/option_portfolios_Ftest.csv')
    formula_checks_Ftest(monthly_portfolios,option_portfolios)
    #"""

    

