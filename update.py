import json
import requests
import feedparser

from datetime import datetime


# ==================================================
# MÉTÉO RENNES
# ==================================================

METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=48.1173"
    "&longitude=-1.6778"
    "&current=temperature_2m,wind_speed_10m"
    "&daily="
    "weather_code,"
    "temperature_2m_max,"
    "temperature_2m_min,"
    "precipitation_probability_max,"
    "precipitation_sum,"
    "sunrise,"
    "sunset"
    "&forecast_days=7"
    "&timezone=Europe/Paris"
)

meteo = requests.get(
    METEO_URL,
    timeout=15
).json()


# ==================================================
# QUALITÉ DE L'AIR
# ==================================================

AIR_URL = (
    "https://air-quality-api.open-meteo.com/v1/air-quality"
    "?latitude=48.1173"
    "&longitude=-1.6778"
    "&current=european_aqi"
)

try:

    air_data = requests.get(
        AIR_URL,
        timeout=15
    ).json()

    european_aqi = (
        air_data["current"]["european_aqi"]
    )

except Exception:

    european_aqi = None


# ==================================================
# OUTILS
# ==================================================

def icon(code):

    if code == 0:
        return "☀"

    if code <= 3:
        return "⛅"

    if code <= 48:
        return "☁"

    if code <= 67:
        return "🌧"

    return "⛈"


def air_label(aqi):

    if aqi is None:
        return "Indisponible"

    if aqi <= 20:
        return "Excellent"

    if aqi <= 40:
        return "Bon"

    if aqi <= 60:
        return "Moyen"

    if aqi <= 80:
        return "Dégradé"

    if aqi <= 100:
        return "Mauvais"

    return "Très mauvais"


def rss_titles(url, nb=2):

    try:

        feed = feedparser.parse(url)

        titles = [
            entry.title.strip()
            for entry in feed.entries[:nb]
        ]

        return (
            titles
            if titles
            else ["Aucune information"]
        )

    except Exception:

        return ["Source indisponible"]


# ==================================================
# JOUR DE SEMAINE
# ==================================================

jours_semaine = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche"
]

today = datetime.now()

weekday = jours_semaine[
    today.weekday()
]


# ==================================================
# PRÉVISIONS
# ==================================================

jours = [
    "Aujourd'hui",
    "Demain",
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi"
]

forecast = []

for i in range(1, 7):

    forecast.append({

        "day":
            jours[i],

        "min":
            round(
                meteo["daily"]
                ["temperature_2m_min"][i]
            ),

        "max":
            round(
                meteo["daily"]
                ["temperature_2m_max"][i]
            ),

        "rain":
            meteo["daily"]
            ["precipitation_probability_max"][i],

        "rain_mm":
            round(
                meteo["daily"]
                ["precipitation_sum"][i],
                1
            ),

        "icon":
            icon(
                meteo["daily"]
                ["weather_code"][i]
            )
    })


# ==================================================
# INFORMATIONS
# ==================================================

news = {

    "Monde (Courrier international)":
        rss_titles(
            "https://www.courrierinternational.com/feed/all/rss.xml"
        ),

    "Rennes (Ouest France)":
        rss_titles(
            "https://rennes.maville.com/flux/rss/actu.php?c=loc&code=rn"
        ),

    "Sécurité de l'information (ANSSI)":
        rss_titles(
            "https://cyber.gouv.fr/actualites/rss/"
        ),

    "Protection de la vie privée (EDPB)":
        rss_titles(
            "https://edpb.europa.eu/feed/news_en"
        ),

    "Tech (Numerama)":
        rss_titles(
            "https://www.numerama.com/feed/"
        )
}


# ==================================================
# DASHBOARD
# ==================================================

dashboard = {

    "updated":
        datetime.now().isoformat(),

    "today": {

        "weekday":
            weekday,

        "date":
            datetime.now().strftime(
                "%d/%m/%Y"
            ),

        "temp_now":
            round(
                meteo["current"]
                ["temperature_2m"]
            ),

        "temp_min":
            round(
                meteo["daily"]
                ["temperature_2m_min"][0]
            ),

        "temp_max":
            round(
                meteo["daily"]
                ["temperature_2m_max"][0]
            ),

        "rain":
            meteo["daily"]
            ["precipitation_probability_max"][0],

        "rain_mm":
            round(
                meteo["daily"]
                ["precipitation_sum"][0],
                1
            ),

        "wind":
            round(
                meteo["current"]
                ["wind_speed_10m"]
            ),

        "sunrise":
            meteo["daily"]
            ["sunrise"][0][-5:],

        "sunset":
            meteo["daily"]
            ["sunset"][0][-5:],

        "aqi":
            european_aqi,

        "air_label":
            air_label(
                european_aqi
            ),

        "icon":
            icon(
                meteo["daily"]
                ["weather_code"][0]
            )
    },

    "forecast":
        forecast,

    "news":
        news
}


# ==================================================
# SAUVEGARDE
# ==================================================

with open(
    "data/dashboard.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        dashboard,
        f,
        ensure_ascii=False,
        indent=2
    )

print()
print("Dashboard généré")
print()
print(
    "Jour :",
    dashboard["today"]["weekday"]
)
print(
    "AQI :",
    dashboard["today"]["aqi"],
    dashboard["today"]["air_label"]
)
print(
    "Pluie :",
    dashboard["today"]["rain"],
    "%",
    "/",
    dashboard["today"]["rain_mm"],
    "mm"
)
print(
    "Lever :",
    dashboard["today"]["sunrise"]
)
print(
    "Coucher :",
    dashboard["today"]["sunset"]
)