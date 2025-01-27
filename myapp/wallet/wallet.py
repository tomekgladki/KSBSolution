import pandas as pd
from myapp.wallet.fun import volatility_fun, beta_fun, VaR_fun, sharpe_fun, drawdown_fun, Markowitz_fun, risk_metric_fun, inv_reglin_fun
import numpy as np



def select_tickers(countries= None, sectors = None):
  url = 'https://raw.githubusercontent.com/Pterogrom/KSBSolution/main/TickersInfo.csv'
  data = pd.read_csv(url)
  #data = pd.read_csv("TickersInfo.csv")
  if countries is not None:
      data = data[data['Country'].isin(countries)]
  if sectors is not None:
      data = data[data['Sector'].isin(sectors)]

  return data['Ticker'].tolist()

'''
def wrapper(countries:[], sectors:[], criteria, weight):
    tickers = select_tickers(countries, sectors)
    #url2 = 'https://raw.githubusercontent.com/Pterogrom/KSBSolution/main/stock_data.csv'
    stockdata = pd.read_csv("stonks_data.csv")
    data = stockdata[stockdata["symbol"].isin(tickers)]
    market_data = pd.read_csv('sp500_data.csv', na_values='NA')
    criteria=criteria[0]
    criteria_switch = {
        "Volatility": volatility_fun(data),
        "Beta": beta_fun(data, market_data),
        "Drawdown": drawdown_fun(data),
        "VaR": VaR_fun(data),
        "Sharpe": sharpe_fun(data),
    }

    criteria_result = criteria_switch.get(criteria, None)

    weight=weight[0]
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
'''

def wrapper(countries:[], sectors:[], criteria, weight):
    # Jeżeli przychodzą jako lista, przekształcamy je na pojedynczy string
    criteria = criteria[2:-2]
    weight = weight[2:-2]

    tickers = select_tickers(countries, sectors)
    stockdata = pd.read_csv("stonks_data.csv")
    print("stock: ",stockdata)
    data = stockdata[stockdata["symbol"].isin(tickers)]
    print("data: ", data)
    market_data = pd.read_csv('sp500_data.csv', na_values='NA')
    market_data = market_data[["date", "adjusted"]]
    
    print("market: ",market_data)

    criteria_switch = {
        "Volatility": volatility_fun(data),
        "Beta": beta_fun(data, market_data),
        "Drawdown": drawdown_fun(data),
        "VaR": VaR_fun(data),
        "Sharpe": sharpe_fun(data),
    }
    #print("criteria: ", criteria)
    criteria_result = criteria_switch.get(criteria, None)
    #print("criteria_result: ", criteria_result)

    weight_switch = {
        "Markovitz": Markowitz_fun(criteria_result),
        "Risk Metric": risk_metric_fun(criteria_result),
        "Inverse Reglin": inv_reglin_fun(criteria_result),
    }
    weight_result = weight_switch.get(weight, None)
    criteria_result = weight_result.merge(criteria_result, on='symbol', how='left')
    unique_symbols_weights = criteria_result[['symbol', 'weights']].drop_duplicates()
    unique_symbols_weights['weights'] = np.absolute(unique_symbols_weights['weights'])
    #print(unique_symbols_weights)

    # Wyświetlanie wyników
    criteria_result['weighted_adjusted'] = criteria_result['adjusted'] * criteria_result['weights']
    print(criteria_result)

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

    return prices_df, unique_symbols_weights

'''
print(wrapper(["United States"],['Energy', 'Communication Services', 'Basic Materials', 'Consumer Cyclical',
    'Industrials', 'Unknown', 'Financial Services', 'Consumer Defensive',
    'Healthcare', 'Utilities', 'Technology', 'Real Estate'],["Volatility"],["Markovitz"]))
'''







