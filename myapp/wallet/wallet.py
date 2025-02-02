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




def wrapper(countries=None, sectors=None, criteria="Volatility", weight="Markowitz",
            n_co1=100, n_co2=100, n_co3=100, risk=0, beta_1=0.75, beta_2=1.25, sharpe_1=0.0, sharpe_2=0.16, a=0.95,
            markowitz_method="return-var", risk_metric_type="volatility", risk_method="proportional",
            data_start=150, data_end=200):
    #print(countries)
    #print(sectors)

    # Rozbijamy pojedynczy string w liście na listę oddzielnych wartości
    countries = countries[0].split(',')
    sectors = sectors[0].split(',')

    # Usuwamy zbędne spacje na początku i końcu każdego elementu
    countries = [country.strip() for country in countries]
    sectors = [sector.strip() for sector in sectors]

    tickers = select_tickers(countries, sectors)
    #print(tickers)
    stockdata = pd.read_csv("2ydata_old.csv")
    #stockdata = stockdata.rename(columns={"Ticker": "symbol", "Date": "date", "Close":"adjusted"})
    #print(stockdata)
    data = stockdata[stockdata["symbol"].isin(tickers)]
    market_data = pd.read_csv('sp500_old.csv', na_values='NA')
    #market_data = market_data.rename(columns={"Ticker": "symbol", "Date": "date", "Close":"adjusted"})
    #print(market_data)
    #print("Data (tickers after filtering):")
    #print(data.head())

    #print("Market data:")
    #print(market_data.head())

    # Obsługa wyboru kryterium
    criteria_functions = {
        "Volatility": volatility_fun(data, n_co=n_co1, risk=risk),
        "Beta": beta_fun(data, market_data, beta_1=beta_1, beta_2=beta_2),
        "Drawdown": drawdown_fun(data, n_co=n_co2),
        "VaR": VaR_fun(data, n_co=n_co3, a=a),
        "Sharpe": sharpe_fun(data, sharpe_1=sharpe_1, sharpe_2=sharpe_2)
    }
    #print("4")
    criteria_result = criteria_functions.get(criteria, None)
    #print(criteria_result)
    if criteria_result is None:
        raise ValueError(f"Invalid criteria: {criteria}")

    # Obsługa wyboru metody wag
    weight_functions = {
        "Markowitz": Markowitz_fun(criteria_result, method=markowitz_method),
        "Risk Metric": risk_metric_fun(criteria_result, risk_metric=risk_metric_type, method=risk_method, start=data_start, end=data_end),
        "Inverse Regression": inv_reglin_fun(criteria_result, start=data_start, end=data_end)
    }

    weight_result = weight_functions.get(weight, None)
    weight_result['weights'] = np.absolute(weight_result['weights'])
    #print(criteria_result)
    #print(weight_result)
    #print(weight_result)
    if weight_result is None:
        raise ValueError(f"Invalid weight method: {weight}")

    # Scalanie wyników
    symbols = criteria_result['symbol']
    newdata = pd.read_csv("2ydata_new.csv")
    newdata = newdata[newdata['symbol'].isin(symbols)]
    #print(criteria_result['symbol'])
    criteria_result = weight_result.merge(newdata, on='symbol', how='left')
    criteria_result['weighted_adjusted'] = criteria_result['adjusted'] * criteria_result['weights']

    # Obliczanie skumulowanych cen portfela
    prices_list = [criteria_result[criteria_result['symbol'] == symbol]['weighted_adjusted'].values for symbol in criteria_result['symbol'].unique()]
    prices = np.sum(prices_list, axis=0)

    prices_df = pd.DataFrame({
        'date': newdata['date'].unique(),
        'prices': prices
    })

    return prices_df, weight_result







'''
print(wrapper(["United States"],['Energy', 'Communication Services', 'Basic Materials', 'Consumer Cyclical',
    'Industrials', 'Unknown', 'Financial Services', 'Consumer Defensive',
    'Healthcare', 'Utilities', 'Technology', 'Real Estate'],["Volatility"],["Markovitz"]))
'''







