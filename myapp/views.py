
from django.shortcuts import render, redirect
from .utils.plot_utils import generate_plot  # Import funkcji generującej wykres
from django.contrib.auth.decorators import login_required
from .models import UserPreferences
from django.contrib import messages
from .forms import UserRegisterForm
from .forms import PreferencesForm


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
    if request.method == 'POST':
        form = PreferencesForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PreferencesForm(instance=preferences)
    return render(request, 'edit_preferences.html', {'form': form})
'''