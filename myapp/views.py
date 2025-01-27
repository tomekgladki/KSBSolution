
from django.shortcuts import render, redirect
from .utils.plot_utils import generate_plot  # Import funkcji generującej wykres
from django.contrib.auth.decorators import login_required
from .models import UserPreferences
from django.contrib import messages
from .forms import UserRegisterForm
from .forms import PreferencesForm
from myapp.wallet.wallet import wrapper
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import os
from django.conf import settings


def home(request):
    # Przykładowe dane
    lista_krajów = ["AAPL", "GOOG", "TSLA"]
    sektory = [0.4, 0.3, 0.3]
    kryterium = "Przykładowe kryterium"

    # Przykładowe dane do wykresu
    data = [100, 200, 300]

    # Wygenerowanie wykresu
    plot_image = generate_plot(data, sektory, kryterium)

    # Renderowanie wykresu w HTML
    return render(request, "plot.html", {"plot_image": plot_image})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Twoje konto zostało utworzone! Możesz się teraz zalogować.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


COUNTRIES = [
    'Poland',
    'Luxembourg',
    'Australia',
    'Unknown',
    'United Kingdom',
    'Cyprus',
    'United States',
    'Ireland',
    'Switzerland',
    'Bermuda',
    'Canada',
    'Netherlands',
    'Singapore'
]

SECTORS = [
    'Energy', 'Communication Services', 'Basic Materials', 'Consumer Cyclical',
    'Industrials', 'Unknown', 'Financial Services', 'Consumer Defensive',
    'Healthcare', 'Utilities', 'Technology', 'Real Estate'
]

CRITERIA = [
    'Volatility', 'Beta', 'Drawdown', 'VaR', 'Sharpe'
]

WEIGHTS = [
    'Markovitz','Risk Metric','Inverse Reglin'
]


@login_required
def user_dashboard(request):
    preferences = request.user.preferences

    # Przekształcenie zapisanych danych tekstowych w listy
    selected_countries = preferences.lista_krajów.split(',') if preferences.lista_krajów else []
    selected_sectors = preferences.sektory.split(',') if preferences.sektory else []
    selected_criteria = preferences.kryterium.split(',') if preferences.kryterium else []
    selected_weights = preferences.wagi.split(',') if preferences.wagi else []

    context = {
        'selected_countries': selected_countries,
        'selected_sectors': selected_sectors,
        'selected_criteria': selected_criteria,
        'selected_weights': selected_weights,
    }
    return render(request, 'dashboard.html', context)



@login_required
def edit_preferences(request):
    preferences = request.user.preferences
    if request.method == 'POST':
        # Pobieranie zaznaczonych wartości z formularza
        selected_countries = request.POST.getlist('countries')
        selected_sectors = request.POST.getlist('sectors')
        selected_criteria = request.POST.get('criteria')
        selected_weights = request.POST.get('weights')

        # Zapisanie wybranych wartości jako ciąg tekstowy
        preferences.lista_krajów = ','.join(selected_countries)
        preferences.sektory = ','.join(selected_sectors)
        preferences.kryterium = selected_criteria
        preferences.wagi = selected_weights
        preferences.save()

        return redirect('dashboard')  # Powrót do dashboardu

    # Konwersja zapisanych wartości na listę (dla zaznaczenia w formularzu)
    current_countries = preferences.lista_krajów.split(',') if preferences.lista_krajów else []
    current_sectors = preferences.sektory.split(',') if preferences.sektory else []
    current_criteria = [preferences.kryterium] if preferences.kryterium else []
    current_weights = [preferences.wagi] if preferences.wagi else []

    context = {
        'countries': COUNTRIES,
        'sectors': SECTORS,
        'criteria': CRITERIA,
        'weights': WEIGHTS,
        'current_countries': current_countries,
        'current_sectors': current_sectors,
        'current_criteria': current_criteria,
        'current_weights': current_weights,
    }
    return render(request, 'edit_preferences.html', context)

'''
@login_required
def wrap_wallet(request):
    if request.method == "POST":
        try:
            # Sprawdzamy, czy dane przychodzą poprawnie
            print("Received POST request to wrap_wallet")

            countries = request.POST.get("countries", "").split(",")
            sectors = request.POST.get("sectors", "").split(",")
            criteria = request.POST.get("criteria", "Volatility")
            weight = request.POST.get("weight", "Markovitz")

            
            # Debugowanie
            print(f"Countries: {countries}")
            print(f"Sectors: {sectors}")
            print(f"Criteria: {criteria}")
            print(f"Weight: {weight}")

            # Uruchomienie obliczeń
            result, actions = wrapper(countries, sectors, criteria, weight)
            print("Portfolio calculation completed")




            # Przekazanie wyników do szablonu
            context = {"portfolio": actions.to_dict(orient="records")}
            return render(request, "portfolio.html", context)

        except Exception as e:
            print(f"Error in wrap_wallet: {e}")
            return render(request, "dashboard.html", {"error": str(e)})

    return render(request, "dashboard.html")
'''



@login_required
def wrap_wallet(request):
    if request.method == "POST":
        try:
            print("Received POST request to wrap_wallet")

            # Pobranie danych z formularza
            countries = request.POST.get("countries", "").split(",")
            sectors = request.POST.get("sectors", "").split(",")
            criteria = request.POST.get("criteria", "Volatility")
            weight = request.POST.get("weight", "Markovitz")

            print(f"Countries: {countries}")
            print(f"Sectors: {sectors}")
            print(f"Criteria: {criteria}")
            print(f"Weight: {weight}")

            # Uruchomienie obliczeń
            prices_df, weights = wrapper(countries, sectors, criteria, weight)
            print("Portfolio calculation completed")
            print(prices_df)
            print(weights)

            # Tworzenie folderu dla wykresów
            img_dir = os.path.join(settings.MEDIA_ROOT, "plots")
            os.makedirs(img_dir, exist_ok=True)
            
            # Wczytanie danych rynkowych
            market_data = pd.read_csv("sp500_data.csv", na_values="NA")
            market_data["date"] = pd.to_datetime(market_data["date"])
            prices_df["date"] = pd.to_datetime(prices_df["date"])
            
            # Skalowanie cen
            prices_df["scaled_prices"] = prices_df["prices"] / prices_df["prices"].iloc[0].item()
            market_data["scaled_adjusted"] = market_data["adjusted"] / market_data["adjusted"].iloc[0].item()
            
            # Histogram zwrotów
            prices_df["daily_returns"] = prices_df["prices"].pct_change() * 100  
            prices_df = prices_df.dropna(subset=["daily_returns"])
            
            # Sortowanie wag
            if isinstance(weights, np.ndarray):
                weights = pd.DataFrame(weights, columns=["symbol", "weights"])
            weights_sorted = weights.sort_values(by="weights", ascending=False)
            
            # Tworzenie wykresów
            fig, axs = plt.subplots(2, 2, figsize=(18, 12))
            plt.style.use("classic")
            print("6")
            # Wykres I: Ceny portfela vs rynek
            print(prices_df)
            prices_df_dates = prices_df["date"].values
            prices_df_prices = prices_df["scaled_prices"].values
            market_data_dates = market_data["date"].values
            market_data_prices = market_data["scaled_adjusted"].values
            axs[0, 0].plot(prices_df_dates, prices_df_prices, label="Portfolio", color="purple", linewidth=1.5)
            print("6.1")
            axs[0, 0].plot(market_data_dates, market_data_prices, label="SP500", color="orange", linewidth=1.5)
            print("6.5")
            axs[0, 0].set_title("Portfolio Prices vs The Market", fontsize=14)
            axs[0, 0].set_xlabel("Date")
            axs[0, 0].set_ylabel("Scaled Prices")
            axs[0, 0].legend()
            axs[0, 0].grid()
            axs[0, 0].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            axs[0, 0].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
            axs[0, 0].tick_params(axis="x", rotation=45)
            print("7")
            # Wykres II: Dzienne zwroty
            colors = np.where(prices_df["daily_returns"] > 0, "green", "red")
            axs[0, 1].bar(prices_df["date"], prices_df["daily_returns"], color=colors, edgecolor="black", alpha=0.7)
            axs[0, 1].set_title("Daily Returns", fontsize=14)
            axs[0, 1].set_xlabel("Date")
            axs[0, 1].set_ylabel("Return (%)")
            axs[0, 1].grid(axis="y", alpha=0.3)
            axs[0, 1].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            axs[0, 1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
            axs[0, 1].tick_params(axis="x", rotation=45)
            print("8")
            # Wykres III: Histogram zwrotów
            # Create bins for the histogram
            bins = 30  # Number of bins in the histogram
            hist_values, bin_edges = np.histogram(prices_df['daily_returns'], bins=bins)

            # Split bins into two groups: negative (left of zero) and positive (right of zero)
            bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])  # Calculate bin centers
            colors = ['red' if center < 0 else 'green' for center in bin_centers]  # Red for negative, green for positive

            # Plot each bar on the histogram
            for i in range(len(hist_values)):
                axs[1, 0].bar(bin_centers[i], hist_values[i],
                    width=bin_edges[1] - bin_edges[0],
                    color=colors[i], edgecolor='black', alpha=1)
            '''
            axs[1, 0].hist(prices_df["daily_returns"], bins=30, color="blue", edgecolor="black", alpha=0.7)
            axs[1, 0].set_title("Histogram of Daily Returns", fontsize=14)
            axs[1, 0].set_xlabel("Returns (%)")
            axs[1, 0].set_ylabel("Frequency")
            axs[1, 0].grid(axis="y", alpha=0.3)
            '''
            
            axs[1, 0].set_title('Histogram of Daily Returns', fontsize=16)
            axs[1, 0].set_xlabel('Daily Returns (%)', fontsize=12)
            axs[1, 0].set_ylabel('Days', fontsize=12)
            axs[1, 0].grid(axis='y', alpha=0.3)
            print("9")
            # Wykres IV: Wagi aktywów
            axs[1, 1].bar(weights_sorted["symbol"], weights_sorted["weights"], color="darkorange", edgecolor="black", alpha=0.8)
            axs[1, 1].set_title("Asset Allocation", fontsize=14)
            axs[1, 1].set_xlabel("Ticker")
            axs[1, 1].set_ylabel("Weight")
            axs[1, 1].tick_params(axis="x", rotation=90)
            axs[1, 1].grid(axis="y", alpha=0.3)
            print("10")
            # Zapisanie wykresu
            plot_path = os.path.join(img_dir, "portfolio_plot.png")
            plt.tight_layout()
            plt.savefig(plot_path, dpi=300)
            plt.close()

            # Przekazanie ścieżki do szablonu
            context = {"portfolio": weights.to_dict(orient="records"), "plot_url": f"/media/plots/portfolio_plot.png"}
            return render(request, "portfolio.html", context)

        except Exception as e:
            print(f"Error in wrap_wallet: {e}")
            return render(request, "dashboard.html", {"error": str(e)})

    return render(request, "dashboard.html")




'''
    if request.method == 'POST':
        form = PreferencesForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PreferencesForm(instance=preferences)
    return render(request, 'edit_preferences.html', {'form': form})
'''