from traceback import print_tb

import pandas as pd
from django.shortcuts import render
from requests import Response

from .fun import *
import numpy as np
import cvxpy as cp
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import yfinance as yf
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required

url = 'https://raw.githubusercontent.com/Pterogrom/KSBSolution/main/TickersInfo.csv'
url2 = 'https://raw.githubusercontent.com/Pterogrom/KSBSolution/main/stock_data.csv'
# Reading the CSV file from GitHub
data = pd.read_csv(url)
stockdata = pd.read_csv(url2)

def select_tickers(countries= None, sectors = None):
  data = pd.read_csv("TickersInfo.csv")
  if countries is not None:
      data = data[data['Country'].isin(countries)]
  if sectors is not None:
      data = data[data['Sector'].isin(sectors)]

  return data['Ticker'].tolist()

# CRITERIA = [
#     'Volatility', 'Beta', 'Drawdown', 'VaR', 'Sharpe'
# ]
#
# WEIGHTS = [
#     'Markovitz','Risk Metric','Inverse Reglin'
# ]



def wrapper(countries:[], sectors:[], criteria:str, weight:str):
    tickers = select_tickers(countries, sectors)

    data = stockdata[stockdata["symbol"].isin(tickers)]
    market_data = pd.read_csv('/content/sp500_data.csv', na_values='NA')
    criteria_switch = {
        "Volatility": volatility_fun(data),
        "Beta": beta_fun(data, market_data),
        "Drawdown": drawdown_fun(data),
        "VaR": VaR_fun(data),
        "Sharpe": sharpe_fun(data),
    }

    criteria_result = criteria_switch.get(criteria, None)

    weight_switch = {
        "Markovitz" : Markowitz_fun(criteria_result),
        "Risk Metric" : risk_metric_fun(criteria_result),
        "Inverse Reglin" : inv_reglin_fun(criteria_result),
    }

    weight_result = weight_switch.get(weight, None)
    criteria_result = weight_result.merge(criteria_result, on='symbol', how='left')
    criteria_result['weighted_adjusted'] = criteria_result['adjusted'] * criteria_result['weights']

    prices_list = []

    for symbol in criteria_result['symbol'].unique():
        symbol_data = criteria_result[criteria_result['symbol'] == symbol]['weighted_adjusted'].values
        prices_list.append(symbol_data)

    # Sum up all weighted prices
    prices = np.sum(prices_list, axis=0)
    prices_df = pd.DataFrame({
        'date': stockdata['date'].unique(),
        'prices': prices
    })

    return prices_df



@login_required
def wrap_wallet(request):
    data = request.data
    criteria = data.get("criteria")
    weight = data.get("weight")
    countries_data = data.get("countries")
    countries = []
    for c in countries_data:
        countries.append(c)
    sectors_data = data.get("sectors")
    sectors = []
    for s in sectors_data:
        sectors.append(s)

    result = wrapper(countries, sectors, criteria, weight)

    return render(request, 'portfolio.html', result)








