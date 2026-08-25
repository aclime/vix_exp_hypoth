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
                         comparison_against_vix,
                         hedged_returns_analysis,
                         hedged_returns_analysis_multihorizon,
                         shuaiqi_results_comparison
                         )

    lb_year=1998
    ub_year=2023
    ticker='SPX'
    num_periods_wanted=3
    monthly_portfolios, option_portfolios_df=compute_option_portfolios(num_periods_wanted,lb_year,ub_year,ticker)

    comparison_against_vix(monthly_portfolios)
    hedged_returns_analysis(monthly_portfolios)
    hedged_returns_analysis_multihorizon(monthly_portfolios)
    shuaiqi_results_comparison(monthly_portfolios)





    













###########LEGACY CODE###########
"""

    #New logic: find closest date to third friday that all options price on
    approx_period_days=[30,60,90]
    #approx_period_days=[30]
    option_portfolios=[]
    id_counter=1

    sp500_df=get_sp500_file()
    sp500_df.dropna(subset=['Index Value - Total Return'],inplace=True)
    sp500_df=sp500_df[['Date','Index Value - Total Return','Index Price - Close Daily']]
    sp500_df['Index Return']=sp500_df['Index Value - Total Return']/sp500_df['Index Value - Total Return'].shift()-1

    #lb_year,ub_year=2001,2023
    lb_year,ub_year=1998,2023
    #lb_year,ub_year=2006,2020
    #lb_year=2023#1998
    #ub_year=2023
    portfolio_dict={}
    #portfolio_df=pd.DataFrame()
    id_counter=1
    for yr in range(lb_year,ub_year+1):
        print(f'{yr} file')
        df = option_metric_query('SPX',yr,day=None,month=None)
        df2=df.copy()
        lb='1996-01-04'
        ub='2040-12-31'
        #CBOE Holidays and Early Closes
        #   NOTE: need to come back to early closes
        cboe=mcal.get_calendar('CBOE_Index_Options')
        cboe_holidays=cboe.holidays()
        cboe_holidaylist=pd.to_datetime(cboe_holidays.holidays)
        fridays = list( pd.date_range(lb, ub,freq='W-FRI', tz='US/Eastern',normalize=True).values )
        third_fridays = list( pd.date_range(lb, ub,freq='WOM-3FRI', tz='US/Eastern',normalize=True).values )
        fridays=pd.to_datetime(fridays).normalize()
        third_fridays=pd.to_datetime(third_fridays).normalize()
        diffed_fridays=list(set(fridays)-set(third_fridays))
        holiday_dict={}
        third_friday_holidays=list(set(third_fridays) & set(cboe_holidaylist))
        expir_not_third_friday=set(pd.to_datetime(df2.exdate.unique()).normalize())-set(third_fridays)
        for expir in expir_not_third_friday:
            for holiday in third_friday_holidays:
                if (holiday-expir).days==1:
                    holiday_dict[expir]=True

        df2['holiday_exp']=df2['exdate'].map(holiday_dict)
        df2.fillna({'holiday_exp':False},inplace=True)
        #Compute time to expiration
        df3=df2.copy()    
        df3['datetime_close']=df3['date']+pd.Timedelta(hours=16,minutes=15)
        df3['ex_time']=df3['exdate']+pd.Timedelta(hours=9,minutes=30)
        df3['time_to_exp']=df3['ex_time']-df3['datetime_close']
        #Merge forward price
        df_fwd=get_fwd_price('SPX',yr)
        df4=df3.merge(df_fwd,how='left',left_on=['secid','date','exdate'],right_on=['secid','date','expiration'])
        #df4[pd.isnull(df4.forwardprice)]

        df4['midpoint_price']=(df4.best_bid+df4.best_offer)/2
        

        expirs_wanted=[ i[0] for i in df4.groupby([df4.exdate.dt.year,df4.exdate.dt.month])[['exdate']].min().values ]
        #for expir in sorted(df4.exdate.unique()):
        for expir in expirs_wanted:
            print(f'trade_date: {expir}')
            #display(df4[df4.date==expir].exdate.min())
            slice_=df4[df4.date==expir]
            modified_trade_date=expir
            expir_days=sorted( df4[df4.exdate.isin(expirs_wanted)][df4[df4.exdate.isin(expirs_wanted)].exdate>expir].exdate.unique() ) 

            expirs_found=[]
            for d in approx_period_days:
                #print(f'{d} days')
                #for e in expir_days:
                if bool([(i-expir).days for i in expir_days]):
                    closest_dte=min( [(i-expir).days for i in expir_days], key=lambda x:abs(x-d))
                    idx=[(i-expir).days for i in expir_days].index(closest_dte)
                    #print( expir_days[idx] )
                    expirs_found.append(expir_days[idx])

                #print( [(i-expir).days for i in expir_days] )
                #print( min( [(i-expir).days for i in expir_days], key=lambda x:abs(x-d)) )
                #print([(i-expir).days for i in expir_days])
                #print('~~~~~~~~~')

            #Find modified_trade_date
            print(expirs_found) 
            trade_date_cands=[]
            for e in expirs_found:
                #print(e)
                sub_slice_=df4[df4.exdate==e]
                #print( min(sub_slice_.date.unique(), key=lambda x: abs(expir - x)) )
                trade_date_cands.append( min(sub_slice_.date.unique(), key=lambda x: abs(expir - x)) )
                #print('~~~~~~~~~')
            if bool(trade_date_cands):
                #print(trade_date_cands)
                #print(max(trade_date_cands))
                modified_trade_date=max(trade_date_cands)
                print(f'mod trade date: {modified_trade_date}')
                #slice_=df4[df4.date>=modified_trade_date] #this line could be causing the problem
                slice_=df4[df4.date==modified_trade_date]
                #display(slice_)
                #continue

                portfolio_dict[id_counter]={'Trade Date':expir}
                portfolio_dict[id_counter]['modified_trade_date']=modified_trade_date

                slice_temp=df4[df4.date>=modified_trade_date]
                #if not slice_[slice_.date>modified_trade_date].empty: #this was for when the year in the date was beyond the yr
                if not slice_temp[slice_temp.date>modified_trade_date].empty: #this is a fix
                    #display(slice_.head(5))
                    #continue
                    #for term in expirs_found:
                    for i,term in enumerate(expirs_found):
                        #portfolio_dict[expir][f'{i+1} month expiration']=term
                        portfolio_dict[id_counter][f'{i+1} month expiration']=term
                        print(term)
                        term_df=slice_[(slice_.exdate==term)]
                        

                        ATM_strike_cands=term_df[~( (pd.isnull(term_df.best_bid)) | (pd.isnull(term_df.best_offer)) ) 
                                    & ~(term_df.best_bid>term_df.best_offer) 
                                    & ~(term_df.best_bid<=0)   ]
                        
                        mins_in_year=365*24*60
                        mins_to_expir=ATM_strike_cands.time_to_exp.iloc[0].total_seconds()/60
                        t=mins_to_expir/mins_in_year
                        days_to_exp=ATM_strike_cands.iloc[0].time_to_exp.days
                        print(f'{ATM_strike_cands.iloc[0].time_to_exp.days} days to expiration')
                        r=calculate_interest_rates(modified_trade_date,ATM_strike_cands.iloc[0].time_to_exp.days)
                        ert=np.exp(r*t)
                        ert_min=np.exp(-r*t)

                        def min_strike_diff(slice):
                            if ('C' in slice.cp_flag.unique()) and ('P' in slice.cp_flag.unique()):
                                return abs( slice[slice.cp_flag=='P'].midpoint_price.values[0] - slice[slice.cp_flag=='C'].midpoint_price.values[0])
                        
                        F_strike=ATM_strike_cands.groupby(['strike_price']).apply(min_strike_diff).idxmin()
                        call_put_diff=ATM_strike_cands[(ATM_strike_cands.strike_price==F_strike)].sort_values(by='cp_flag')['midpoint_price'].diff().dropna().values[0]
                        F=F_strike+np.exp(r*t)*call_put_diff
                        K0=term_df[term_df.strike_price<=F].strike_price.max()
                        
                        #doing rectangle VIX
                        F=df_fwd[(df_fwd['expiration']==term)
                                &(df_fwd['date']==modified_trade_date)]['forwardprice'].iloc[0]
                        #rectnagle vix using fuutres instead fwd
                        F=future_data_df['Close'].iloc[0]
                        S0=spot_data_df.iloc[0]['Close']

                        def filter_included_options(opt_type):
                            if opt_type=='put':
                                #OOM_opts=term_df[(term_df.strike_price<K0)&(term_df.cp_flag=='P')]
                                OOM_opts=term_df[(term_df.strike_price<F)&(term_df.cp_flag=='P')]
                                OOM_opts=OOM_opts.copy()
                                OOM_opts['excl_ind']=OOM_opts.best_bid.apply(lambda x: pd.isnull(x) or x<=0)
                                OOM_opts.sort_values(by=['strike_price'],ascending=False,inplace=True) #sort upside down for puts
                            else:
                                #OOM_opts=term_df[(term_df.strike_price>K0)&(term_df.cp_flag=='C')]
                                OOM_opts=term_df[(term_df.strike_price>F)&(term_df.cp_flag=='C')]
                                OOM_opts=OOM_opts.copy()
                                OOM_opts.sort_values(by=['strike_price'],ascending=True,inplace=True) #sort upside down for puts
                                OOM_opts['excl_ind']=OOM_opts.best_bid.apply(lambda x: pd.isnull(x) or x<=0)
                                #dont need to change sorting order for calls

                            OOM_opts['excl_ind']=OOM_opts['excl_ind'].cumsum()
                            #display(OOM_opts[OOM_opts.excl_ind>=2])
                            incl_opts=OOM_opts#[OOM_opts.excl_ind<2]
                            #incl_opts=incl_opts[incl_opts.best_bid>0]
                            if opt_type=='put':
                                incl_opts.sort_values(by=['strike_price'],ascending=True,inplace=True)#change back
                            return incl_opts

                        incl_puts,incl_calls=filter_included_options('put'),filter_included_options('call')
                        df_K0=term_df[term_df.strike_price==K0]

                        pca=pd.DataFrame.from_dict({'strike_price':K0,
                                                    'cp_flag':'P/C Avg', #put-call average
                                                    'midpoint_price':term_df[(term_df.strike_price==K0)]['midpoint_price'].mean(),
                                                    'best_bid':None,
                                                    'best_offer':None,
                                                    'optionid':None,
                                                    'delta':term_df[(term_df.strike_price==K0)]['delta'].sum(),
                                                    'forwardprice':term_df[(term_df.strike_price==K0)]['forwardprice'].unique()[0]},
                                                    orient='index').T

                        #opt_portfolio=pd.concat([incl_puts,pca,incl_calls])[['strike_price',
                        #                                                    'cp_flag',
                        #                                                    'midpoint_price',
                        #                                                    'best_bid','best_offer',
                        #                                                    'optionid',
                        #                                                    'delta',
                        #                                                    'forwardprice']]
                        opt_portfolio=pd.concat([incl_puts,incl_calls])[['strike_price',
                                                                            'cp_flag',
                                                                            'midpoint_price',
                                                                            'best_bid','best_offer',
                                                                            'optionid',
                                                                            'delta',
                                                                            'forwardprice']]
                        #display(opt_portfolio)

                        K0=opt_portfolio[opt_portfolio.cp_flag=='P']['strike_price'].max()
                        K1=opt_portfolio[opt_portfolio.cp_flag=='C']['strike_price'].min()
                        K2=opt_portfolio[opt_portfolio.cp_flag=='C']['strike_price'].nsmallest(2).iloc[-1]
                        K_min1=opt_portfolio[opt_portfolio.cp_flag=='P']['strike_price'].nlargest(2).iloc[-1]
                        Delta=K1-K0
                        Delta_1 = (K2-K0)/2 
                        Delta_0=(K1-K_min1)/2 


                        opt_portfolio.sort_values(by=['strike_price'],ascending=True,inplace=True)
                        opt_portfolio['dK']=(opt_portfolio.strike_price.shift(-1)-opt_portfolio.strike_price.shift(1))/2
                        opt_portfolio=opt_portfolio.copy()
                        opt_portfolio.iloc[0,-1]=opt_portfolio.iloc[1]['strike_price']-opt_portfolio.iloc[0]['strike_price']
                        opt_portfolio.iloc[-1,-1]=opt_portfolio.iloc[-1]['strike_price']-opt_portfolio.iloc[-2]['strike_price']


                        settle_value=float(settle_prices[(settle_prices['Month']==term.month) & (settle_prices['Year']==term.year)]['Settlement_Value'].values[0])
                        def call_payoff(s,k):
                            return max(s-k,0)
                        def put_payoff(s,k):
                            return max(k-s,0)
                        def option_payoff(row):
                            k=row['strike_price']
                            opt_type=row['cp_flag']
                            if opt_type=='C':
                                return call_payoff(settle_value,k) 
                            elif opt_type=='P':
                                return put_payoff(settle_value,k)
                            else:
                                return call_payoff(settle_value,k)+put_payoff(settle_value,k)

                        opt_portfolio['payoff']=opt_portfolio.apply(option_payoff,axis=1)

                        # VIX
                        VIX_opt_weight=opt_portfolio.dK/(opt_portfolio.strike_price**2)
                        VIX_opt_weight*=2/t*ert

                        #VIX and VIX^2
                        opt_portfolio['VIX_opt_weight']=VIX_opt_weight#*np.exp(r*t)
                        #Simpsons rule weight adjust
                        #opt_portfolio.loc[opt_portfolio.strike_price==K0,'VIX_opt_weight']+= np.exp(r*t)/(3*t)*((K1-K0-Delta_0)/(K0**2))
                        #opt_portfolio.loc[opt_portfolio.strike_price==K1,'VIX_opt_weight']+= np.exp(r*t)/(3*t)*((K1-K0-Delta_1)/(K1**2))
                        

                        portfolio_dict[id_counter][f'{i+1} month VIX']=np.sqrt((opt_portfolio.VIX_opt_weight*opt_portfolio.midpoint_price).sum())*100
                        portfolio_dict[id_counter][f'{i+1} month VIX payoff']=np.sqrt((opt_portfolio.VIX_opt_weight*opt_portfolio.payoff).sum())*100
                        opt_portfolio['VIX_bid_contribtion']=opt_portfolio.apply(lambda x: x.VIX_opt_weight*x.best_bid if x.VIX_opt_weight >0 else x.VIX_opt_weight*x.best_offer,axis=1)
                        opt_portfolio['VIX_ask_contribtion']=opt_portfolio.apply(lambda x: x.VIX_opt_weight*x.best_offer if x.VIX_opt_weight >0 else x.VIX_opt_weight*x.best_bid,axis=1)

                        #simpson_epsilon=(K1-K0)/(3*t)*(1/(K0**2) - 1/(K1**2)) + (1/t)*(2/F-1/K0-1/K1) 
                        #simpson_epsilon*=S0
                        #simpson_epsilon+=(K1-K0)/(3*t)*(1/K1-1/K0) + 1/t*(np.log(F/K0)+np.log(F/K1))
                        #simpson_epsilon/=ert
                        #simpson_epsilon_payoff=(K1-K0)/(3*t)*(1/(K0**2) - 1/(K1**2) + (1/t)*(2/F-1/K0-1/K1) )
                        #simpson_epsilon_payoff*=settle_value
                        #simpson_epsilon_payoff+=((K1-K0)/(3*t)*(1/K1-1/K0) + 1/t*(np.log(F/K0)+np.log(F/K1)))
                        
                        vix_square=(opt_portfolio.VIX_opt_weight*opt_portfolio.midpoint_price).sum()
                        vix_square_payoff=(opt_portfolio.VIX_opt_weight*opt_portfolio.payoff).sum()
                        #vix_square+=simpson_epsilon
                        #vix_square_payoff+=simpson_epsilon_payoff
                        vix_square_price=vix_square/ert
                        vix_square_bid=ert*opt_portfolio['VIX_bid_contribtion'].sum()
                        vix_square_ask=ert*opt_portfolio['VIX_ask_contribtion'].sum()
                        vix_square_spread=vix_square_ask-vix_square_bid
                        


                        opt_portfolio['VIX_square_opt_weight']=VIX_opt_weight
                        portfolio_dict[id_counter][f'{i+1} month VIX^2']=vix_square
                        portfolio_dict[id_counter][f'{i+1} month VIX^2 price']=vix_square_price
                        portfolio_dict[id_counter][f'{i+1} month VIX^2 payoff']=vix_square_payoff
                        opt_portfolio['VIX_square_bid_contribtion']=opt_portfolio.apply(lambda x: x.VIX_square_opt_weight*x.best_bid if x.VIX_square_opt_weight >0 else x.VIX_square_opt_weight*x.best_offer,axis=1)
                        opt_portfolio['VIX_square_ask_contribtion']=opt_portfolio.apply(lambda x: x.VIX_square_opt_weight*x.best_offer if x.VIX_square_opt_weight >0 else x.VIX_square_opt_weight*x.best_bid,axis=1)
                        portfolio_dict[id_counter][f'{i+1} month VIX square bid']=vix_square_bid
                        portfolio_dict[id_counter][f'{i+1} month VIX square ask']=vix_square_ask
                        portfolio_dict[id_counter][f'{i+1} month VIX square spread ($)']=vix_square_spread


                        #Delta Hedging and Realized Moments
                        hedge_df = sp500_df[(sp500_df.Date >= modified_trade_date.date()) & (sp500_df.Date < term.date())].copy()
                        hedge_df = hedge_df.rename(columns={'Index Price - Close Daily': 'S'})
                        hedge_df['Date'] = pd.to_datetime(hedge_df['Date'])
                        hedge_df = hedge_df.sort_values('Date').reset_index(drop=True)
                        hedge_df['Index Return'] = hedge_df['S'].pct_change().fillna(0.0)
                        equal_ssr = compute_realized_variance(hedge_df['Index Return'])

                        vix_square_delta_hedge_payoff = compute_dynamic_vix2_hedge(
                            hedge_df[['Date', 'S']],
                            modified_trade_date,
                            term,
                            r,
                        )
                        portfolio_dict[id_counter][f'{i+1} month VIX^2 Delta Hedging Payoff']=vix_square_delta_hedge_payoff
                        portfolio_dict[id_counter][f'Realized Variance {i+1}-month (SSR)']=equal_ssr
                        portfolio_dict[id_counter][f'Realized Variance {i+1}-month (SSR_Fwd)']=np.nan
                        portfolio_dict[id_counter][f'Realized Variance {i+1}-month (SSR_Fut)']=np.nan
                        portfolio_dict[id_counter][f'Realized Variance {i+1}-month (SSR) Reconcile']=np.nan
                        portfolio_dict[id_counter][f'Realized Variance {i+1}-month (SSR) Reconcile_2']=np.nan

                        #Returns and Payoffs
                        portfolio_dict[id_counter][f'{i+1} month VIX^2 return (%)']=(vix_square_payoff/vix_square_price-1)*100
                        portfolio_dict[id_counter][f'{i+1} month VIX^2 Delta Hedged return(%)']=((vix_square_payoff+vix_square_delta_hedge_payoff)/vix_square_price-1)*100
                        portfolio_dict[id_counter][f'{i+1} month VIX^2 Payoff w/ Delta Hedging($)']=vix_square_payoff+vix_square_delta_hedge_payoff
                        portfolio_dict[id_counter][f'{i+1}-month Realized Variance Return (%)']=((equal_ssr/t)/vix_square_price-1)*100
                        
                        #misc things to add to option portfolios
                        maturity_id=i+1
                        opt_portfolio['portfolio_id']=id_counter
                        opt_portfolio['maturity_id']=maturity_id
                        opt_portfolio['trade_date']=expir
                        opt_portfolio['modified_trade_date']=modified_trade_date

                        #countin number of options and range of moneyness
                        portfolio_dict[id_counter][f'{i+1} month number of options']=opt_portfolio.shape[0]+1
                        portfolio_dict[id_counter][f'{i+1} month max moneyness']=opt_portfolio.strike_price.max()/F
                        portfolio_dict[id_counter][f'{i+1} month min moneyness']=opt_portfolio.strike_price.min()/F
                        portfolio_dict[id_counter][f'{i+1} month market gross return']=settle_value/F
                        portfolio_dict[id_counter][f'{i+1} month F']=F
                        portfolio_dict[id_counter][f'{i+1} month S_T']=settle_value
                        portfolio_dict[id_counter][f'{i+1} month interest_rate']=r
                        portfolio_dict[id_counter][f'{i+1} month t']=t

                        if term==pd.Timestamp('2020-03-20 00:00:00'):
                            opt_portfolio['F']=F
                            opt_portfolio['r']=r
                            opt_portfolio['S_T']=settle_value
                            opt_portfolio['t']=t
                            #opt_portfolio['VIX^2']=vix_square
                            #opt_portfolio['VIX^2 price']=vix_square_price
                            #opt_portfolio['VIX^2 payoff']=vix_square_payoff
                            #testing_df=opt_portfolio.copy()

                            #hedge_df['shares_traded']=shares_traded
                            #hedge_df['SSR']=equal_ssr
                            #hedge_df['SSR (Fut)']=equal_ssr_F
                            #hedge_df['hedging_PandL']=PandL
                            #hedge_df['delta_hedge_payoff']=vix_square_delta_hedge_payoff
                            #testing_df_hedge=hedge_df.copy()
                        
                        
                        #continue

                        ###########FOR DOUBLE CHECK###########
        
                        #######################################
            
                        #Option Liquidation
                        if i+1==3:
                            liquidation_date=expirs_found[i-1]
                            #print(f'{i} month liquidation_date:{liquidation_date}')
                            #print(opt_portfolio.shape)
                            #print(opt_portfolio_2.shape)
                            #print('--------------------')
                            #print(opt_portfolio_2.optionid.size)
                            #print( len(set(opt_portfolio_2.optionid.values.tolist())) )
                            liquidation_values=option_liquidation_query('SPX',
                                                                        opt_portfolio.optionid.dropna().values.tolist(),
                                                                        liquidation_date)
                            #display(liquidation_values)
                            opt_portfolio=opt_portfolio.merge(liquidation_values,how='left',on=['optionid'])
                            opt_portfolio.rename(columns={'liquidation_midprice_date':f'{i+1}M port liquidation_midprice_date'},inplace=True)
                            #display(opt_portfolio_2[pd.isnull(opt_portfolio_2[f'{i+1}M port liquidation_midprice_date'])])
                            vix_square_liquidation_value=(opt_portfolio.VIX_opt_weight*opt_portfolio.liquidation_midprice).sum()
                            portfolio_dict[id_counter][f'{i+1} month VIX^2 liquidation']=vix_square_liquidation_value
                            

                        elif i+1==2:
                            #pass
                            liquidation_date=expirs_found[i-1]
                            #print(f'{i} month liquidation_date:{liquidation_date}')
                            #print(opt_portfolio.shape)
                            #print(opt_portfolio_2.shape)
                            #print('--------------------')
                            #print(opt_portfolio_2.optionid.size)
                            #print( len(set(opt_portfolio_2.optionid.values.tolist())) )
                            liquidation_values=option_liquidation_query('SPX',
                                                opt_portfolio.optionid.dropna().values.tolist(),
                                                liquidation_date)
                            #display(liquidation_values)
                            opt_portfolio=opt_portfolio.merge(liquidation_values,how='left',on=['optionid'])
                            opt_portfolio.rename(columns={'liquidation_midprice_date':f'{i+1}M port liquidation_midprice_date'},inplace=True)
                            #display(opt_portfolio_2[pd.isnull(opt_portfolio_2[f'{i+1}M port liquidation_midprice_date'])])
                            vix_square_liquidation_value=(opt_portfolio.VIX_opt_weight*opt_portfolio.liquidation_midprice).sum()
                            portfolio_dict[id_counter][f'{i+1} month VIX^2 liquidation']=vix_square_liquidation_value
                            

                        continue
                        ###########FOR DOUBLE CHECK###########
                        #opt_portfolio['interest_factor']=np.exp(r*t)
                        #opt_portfolio['S_T']=settle_value
             
                        #######################################
                        
                    
            

                        #print(6/0)

                        


                    id_counter+=1            

            
            #next_expir = pd.Series(slice_.exdate.unique()).nsmallest(3)
            #portfolio_dict[id_counter]={'Trade Date':expir}
            #portfolio_dict[id_counter]['modified_trade_date']=modified_trade_date

            print('----------------------------------')
    portfolio_dict
"""
x=5




