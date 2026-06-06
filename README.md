# Dashboard Project

A simple dashboard application designed for a fixed display in your living room on a Raspberry Pi. The dashboard automatically refreshes at regular intervals to provide you with up-to-date information.

## Features

- **Current Weather**: Displays real-time temperature, humidity, wind speed, and precipitation risk with an intuitive weather icon
- **Weather Forecast**: 6-day weather forecast showing daily min/max temperatures and rain probability
- **Air Quality**: Real-time European AQI (Air Quality Index) with a descriptive label
- **Sunrise/Sunset Times**: Shows daily sunrise and sunset times
- **News Feed**: Aggregated news from multiple sources:
  - International news (Courrier International)
  - Local news (Ouest France - Rennes region)
  - Cybersecurity updates (ANSSI)
  - Privacy protection news (EDPB)
  - Tech news (Numerama)

## How It Works

- `update.py`: Fetches weather data from Open-Meteo API and news from RSS feeds, generates `dashboard.json`
- `app.js`: Loads the dashboard data and renders it in the browser
- `style.css`: Responsive design that adapts to different screen sizes
- Automatic refresh: Schedule `update.py` with cron (Linux/RPi) or Task Scheduler (Windows) to update regularly

## Requirements

- Python 3.7+
- `requests` library
- `feedparser` library
- A modern web browser

## Installation

```bash
pip install requests feedparser
```

## Usage

1. Run `update.py` to generate the dashboard data:
   ```bash
   python update.py
   ```

2. Open `index - v0.4.html` in your browser to view the dashboard

3. (Optional) Set up a cron job on your RPi to refresh the data periodically:
   ```bash
   */15 * * * * cd /path/to/dashboard && python update.py
   ```

## Location

Currently configured for **Rennes, France** (latitude: 48.1173, longitude: -1.6778). Modify the coordinates in `update.py` to use a different location.
