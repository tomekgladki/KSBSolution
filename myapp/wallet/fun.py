import numpy as np
import cvxpy as cp
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import yfinance as yf
from bs4 import BeautifulSoup

def volatility_fun(stonks_data, n_co=100, risk=0):
    n = len(stonks_data['symbol'].unique())

    if n_co > n:
        return "Given number of companies in portfolio is greater than on the given stock market."

    # Calculate volatility
    volatility = stonks_data.groupby('symbol').apply(
        lambda x: pd.Series({
            'returns_sd': x['adjusted'].pct_change().std(skipna=True)
        })
    ).reset_index()
    volatility = volatility.sort_values('returns_sd')

    n_1 = int(risk * (n - n_co))
    n_2 = int(n_co + risk * (n - n_co))
    n_co = n_2 - n_1

    portfolio = volatility.iloc[n_1:n_2].copy()
    portfolio = portfolio.drop(columns=['returns_sd'])
    portfolio_stonks = portfolio.merge(stonks_data, on='symbol', how='left')

    return portfolio_stonks

def beta_fun(stonks_data, market_data, beta_1=0.75, beta_2=1.25):
    # Calculate market returns
    market_data = market_data.copy()
    market_data['returns'] = market_data['adjusted'].pct_change()

    # Calculate stock returns and add market returns
    stonks_data = stonks_data.copy()
    stonks_data['returns'] = stonks_data.groupby('symbol')['adjusted'].transform(
        lambda x: x.pct_change()
    )

    # Calculate betas for each stock
    betas = stonks_data.groupby('symbol').apply(
        lambda x: pd.Series({
            'beta': np.cov(x['returns'].dropna(), market_data['returns'].dropna())[0,1] / np.var(market_data['returns'].dropna())
        })
    ).reset_index()

    portfolio = betas[
            (betas['beta'] > beta_1) &
            (betas['beta'] < beta_2)
        ].copy()

    portfolio = portfolio.drop(columns=['returns','beta'])
    portfolio_stonks = portfolio.merge(stonks_data, on='symbol', how='left')

    return portfolio_stonks

def drawdown_fun(stonks_data, n_co = 100):

    drawdowns = stonks_data.groupby('symbol').apply(
        lambda x: pd.Series({
            'max_drawdown': (x['adjusted']/x['adjusted'].cummax(axis=0) - 1).min()
        })
    ).reset_index()
    drawdowns = drawdowns.sort_values('max_drawdown')

    portfolio = drawdowns.tail(n_co).copy()
    portfolio = portfolio.drop(columns=['max_drawdown'])
    portfolio_stonks = portfolio.merge(stonks_data, on='symbol', how='left')

    return portfolio_stonks

def VaR_fun(stonks_data, n_co = 100, a = 0.95):

    VaR = stonks_data.groupby('symbol').apply(
        lambda x: pd.Series({
            'VaR': x['adjusted'].pct_change().dropna().quantile(1-a)
        })
    ).reset_index()
    VaR = VaR.sort_values('VaR')

    portfolio = VaR.tail(n_co).copy()
    portfolio = portfolio.drop(columns=['VaR'])
    portfolio_stonks = portfolio.merge(stonks_data, on='symbol', how='left')

    return portfolio_stonks

def sharpe_fun(stonks_data, risk_free = 0.0575/230, sharpe_1 = 0.0, sharpe_2 = 0.16):

    sharpe = stonks_data.groupby('symbol').apply(
        lambda x: pd.Series({
            'sharpe': (x['adjusted'].pct_change().dropna().mean() - risk_free)/x['adjusted'].pct_change().dropna().std()
        })
    ).reset_index()

    portfolio = sharpe[
            (sharpe['sharpe'] > sharpe_1) &
            (sharpe['sharpe'] < sharpe_2)
        ].copy()

    portfolio = portfolio.drop(columns=['sharpe'])
    portfolio_stonks = portfolio.merge(stonks_data, on='symbol', how='left')

    return portfolio_stonks

def Markowitz_fun(dataset, method = 'return-var'):

    returns_df = dataset.sort_values(by=['symbol', 'date'], ascending=[True, True])
    returns_df['returns'] = returns_df.groupby('symbol')['adjusted'].transform(
        lambda x: x.pct_change()
    )
    tickers = returns_df['symbol'].unique()

    returns_m = returns_df.drop(columns=['adjusted'])
    returns_m = returns_m.pivot(index='date', columns='symbol', values='returns').reset_index()
    returns_m = returns_m.drop(columns=['date'])
    returns_m = returns_m.dropna().to_numpy()
    # in return_m assets (columns) are ordered alphabetically

    returns_means = np.mean(returns_m, axis=0)
    returns_covs = np.cov(returns_m, rowvar=False)
    returns_ncol = returns_m.shape[1]

    n = returns_ncol
    mu = returns_means
    Sigma = returns_covs

    # Long only portfolio optimization.
    w = cp.Variable(n)
    gamma = cp.Parameter(nonneg=True)
    ret = mu.T @ w
    risk = cp.quad_form(w, Sigma)
    prob = cp.Problem(cp.Maximize(ret - gamma * risk), [cp.sum(w) == 1, w >= 0])

    # Compute trade-off curve.
    SAMPLES = 100
    risk_data = np.zeros(SAMPLES)
    ret_data = np.zeros(SAMPLES)
    gamma_vals = np.logspace(-2, 3, num=SAMPLES)
    for i in range(SAMPLES):
        gamma.value = gamma_vals[i]
        prob.solve()
        risk_data[i] = cp.sqrt(risk).value
        ret_data[i] = ret.value

    # Methods to choose optimal point on the trade-off curve
    if method == 'return-var':
        k = np.argmax(ret_data/risk_data)
    elif method == 'min-var':
        k = np.argmin(risk_data)
    elif method == 'max-return':
        k = np.argmax(ret_data)

    # Solve problem for specific gamma and access weights.
    gamma.value = gamma_vals[k]
    prob.solve()
    weights = w.value
    weights = np.round(weights,6)
    weights = pd.DataFrame({'symbol': tickers, 'weights': weights})

    return weights


def risk_metric_fun(dataset, risk_metric='volatility', method='proportional', a=0.95, start = 150, end = 200):

    # Risk metric selection
    if risk_metric == 'volatility':

        volatility = dataset.groupby('symbol').apply(
            lambda x: pd.Series({
                'returns_sd': x['adjusted'].pct_change().std(skipna=True)
            })
        ).reset_index()

        tickers = volatility['symbol'].unique()
        metric = volatility['returns_sd'].to_numpy()

    elif risk_metric == 'drawdown':

        drawdowns = dataset.groupby('symbol').apply(
            lambda x: pd.Series({
                'max_drawdown': (x['adjusted']/x['adjusted'].cummax(axis=0) - 1).min()
            })
        ).reset_index()

        tickers = drawdowns['symbol'].unique()
        metric = drawdowns['max_drawdown'].to_numpy()

    elif risk_metric == 'VaR':

        VaR = dataset.groupby('symbol').apply(
            lambda x: pd.Series({
                'VaR': x['adjusted'].pct_change().dropna().quantile(1-a)
            })
        ).reset_index()

        tickers = VaR['symbol'].unique()
        metric = VaR['VaR'].to_numpy()
        metric = metric + np.abs(np.min(metric))

    elif risk_metric == 'dwell':

        dwell = dataset.groupby('symbol').apply(
            lambda group: pd.Series({
                'dwell': ((start <= group['adjusted']) & (end >= group['adjusted'])).mean()
            })
        ).reset_index()

        tickers = dwell['symbol'].unique()
        metric = dwell['dwell'].to_numpy()

    # Risk metric characteristics
    metric_len = len(metric)
    metric_sum = np.sum(metric)
    metric_mean = np.full(metric_len, metric_sum/metric_len)

    # Weights calculation
    if method == 'proportional':
        weights = metric/metric_sum
    elif method == 'equal':
        w = metric_mean/metric
        w_norm = np.linalg.norm(w)
        weights = w / w_norm

    weights = np.round(weights,6)
    weights = pd.DataFrame({'symbol': tickers, 'weights': weights})

    return weights


def inv_reglin_fun(dataset, start=150, end=200):

    dataset = (
        dataset.groupby('symbol')
        .filter(lambda group: (group['adjusted'].apply(np.floor) == 150).any())
        .reset_index(drop=True)
    )

    dataset = dataset.sort_values(by=['symbol', 'date'], ascending=[True, True])
    tickers = dataset['symbol'].unique()

    adjusted_m = dataset.pivot(index='date', columns='symbol', values='adjusted').reset_index()
    adjusted_m = adjusted_m.drop(columns=['date'])
    adjusted_m = adjusted_m.dropna().to_numpy()
    # in adjusted_m assets (columns) are ordered alphabetically

    x_L = adjusted_m.shape[0]
    y_1 = 150
    y_2 = 200
    a = (y_2-y_1)/x_L
    b = y_1
    x = np.linspace(0, x_L-1, x_L)
    y = a * x + b

    # find the assets that are the closest to the given line
    n = adjusted_m.shape[1]
    w = cp.Variable(n)
    prices = (adjusted_m @ w).T
    objective = cp.sum(cp.square(prices - y))
    prob = cp.Problem(cp.Minimize(objective), [cp.sum(w) == 1, w >= 0])
    prob.solve(solver=cp.SCS, max_iters=10000)

    weights = w.value
    weights = np.round(weights,6)
    weights = pd.DataFrame({'symbol': tickers, 'weights': weights})

    return weights