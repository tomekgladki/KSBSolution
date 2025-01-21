import matplotlib
matplotlib.use("Agg")  # Wyłącza interaktywne GUI

import matplotlib.pyplot as plt
import io
import base64

def generate_plot(data, weights, criteria):
    x = range(len(data))
    y = [val * weight for val, weight in zip(data, weights)]

    plt.figure(figsize=(8, 6))
    plt.plot(x, y, label=f"Wykres dla {criteria}")
    plt.title("Wynikowy wykres")
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()
    return image_base64