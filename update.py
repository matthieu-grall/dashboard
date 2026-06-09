# =============================================================================
# update.py
# Fetches weather data and news, then writes data/dashboard.json.
# Run once manually or schedule with cron / start.sh to refresh periodically.
# =============================================================================

import json
import requests
import feedparser
from datetime import datetime

# -----------------------------------------------------------------------------
# Location & timezone — adjust to your city
# -----------------------------------------------------------------------------

LAT      = 48.1173
LON      = -1.6778
TIMEZONE = "Europe/Paris"

# -----------------------------------------------------------------------------
# Weather — Open-Meteo (free, no API key required)
# Fetches current conditions + 7-day daily forecast.
# weather_code follows the WMO 4677 standard (0 = clear sky, 95+ = thunderstorm)
# -----------------------------------------------------------------------------

METEO_URL = (
    f"https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}"
    f"&longitude={LON}"
    "&current=temperature_2m,wind_speed_10m,weather_code"
    "&daily="
        "weather_code,"
        "temperature_2m_max,"
        "temperature_2m_min,"
        "precipitation_probability_max,"
        "precipitation_sum,"
        "sunrise,"
        "sunset"
    "&forecast_days=7"
    f"&timezone={TIMEZONE}"
)

meteo = requests.get(METEO_URL, timeout=15).json()

# -----------------------------------------------------------------------------
# Air quality — Open-Meteo air quality API (free, no API key required)
# Returns the European AQI (0–500 scale).
# Silently falls back to None if the request fails.
# -----------------------------------------------------------------------------

AIR_URL = (
    f"https://air-quality-api.open-meteo.com/v1/air-quality"
    f"?latitude={LAT}"
    f"&longitude={LON}"
    "&current=european_aqi"
)

try:
    air = requests.get(AIR_URL, timeout=10).json()
    aqi = air["current"]["european_aqi"]
except Exception:
    aqi = None

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def air_label(aqi):
    """Return a human-readable French label for the European AQI value."""
    if aqi is None:  return "N/A"
    if aqi <= 20:    return "Bon"
    if aqi <= 40:    return "Moyen"
    if aqi <= 60:    return "Dégradé"
    return "Mauvais"

def rss_titles(url, nb=2):
    """Fetch an RSS feed and return the titles of the first `nb` entries."""
    feed = feedparser.parse(url)
    return [entry.title for entry in feed.entries[:nb]]

# -----------------------------------------------------------------------------
# Today's data — current conditions + daily summary for day 0
# -----------------------------------------------------------------------------

today_data = {
    "weather_code": meteo["current"]["weather_code"],          # WMO code for icon mapping
    "temp_now":     round(meteo["current"]["temperature_2m"]), # °C
    "wind":         round(meteo["current"]["wind_speed_10m"]), # km/h
    "temp_min":     round(meteo["daily"]["temperature_2m_min"][0]),
    "temp_max":     round(meteo["daily"]["temperature_2m_max"][0]),
    "rain":         meteo["daily"]["precipitation_probability_max"][0], # %
    "rain_mm":      meteo["daily"]["precipitation_sum"][0],             # mm
    "sunrise":      meteo["daily"]["sunrise"][0][11:16],  # HH:MM
    "sunset":       meteo["daily"]["sunset"][0][11:16],   # HH:MM
    "aqi":          aqi,
    "air_label":    air_label(aqi),
}

# -----------------------------------------------------------------------------
# 6-day forecast — days 1 to 6 (day 0 is today, already in today_data)
# -----------------------------------------------------------------------------

DAYS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

forecast = []
for i in range(1, 7):
    date_obj = datetime.fromisoformat(meteo["daily"]["time"][i])
    forecast.append({
        "day":          DAYS_FR[date_obj.weekday()],
        "weather_code": meteo["daily"]["weather_code"][i],
        "min":          round(meteo["daily"]["temperature_2m_min"][i]),
        "max":          round(meteo["daily"]["temperature_2m_max"][i]),
        "rain":         meteo["daily"]["precipitation_probability_max"][i],
        "rain_mm":      meteo["daily"]["precipitation_sum"][i],
    })

# -----------------------------------------------------------------------------
# News — RSS feeds
# Keys must match the lookup strings used in app.js
# -----------------------------------------------------------------------------

news = {
    "Rennes (Ouest France)":          rss_titles("https://rennes.maville.com/flux/rss/actu.php?c=loc&code=rn"),
    "Monde (Courrier international)": rss_titles("https://www.courrierinternational.com/feed/all/rss.xml"),
}

# -----------------------------------------------------------------------------
# Assemble and write dashboard.json
# -----------------------------------------------------------------------------

dashboard = {
    "today":    today_data,
    "forecast": forecast,
    "news":     news,
}

with open("data/dashboard.json", "w", encoding="utf-8") as f:
    json.dump(dashboard, f, ensure_ascii=False, indent=2)

# -----------------------------------------------------------------------------
# Debug output (also captured by start.sh into start.log)
# -----------------------------------------------------------------------------

print("\nDashboard generated\n")
print("Weather code:", dashboard["today"]["weather_code"])
print("Temperature: ", dashboard["today"]["temp_now"], "°C")
print("AQI:         ", dashboard["today"]["aqi"], dashboard["today"]["air_label"])
print("Rain:        ", dashboard["today"]["rain"], "% /", dashboard["today"]["rain_mm"], "mm")
print("Sunrise:     ", dashboard["today"]["sunrise"])
print("Sunset:      ", dashboard["today"]["sunset"])