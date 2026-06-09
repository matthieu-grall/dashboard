// =============================================================================
// app.js
// Loads dashboard.json and renders the three panels (today, forecast, news).
// Called once on page load; the clock refreshes every 30 seconds in-place.
// =============================================================================

// -----------------------------------------------------------------------------
// Date & time helpers
// -----------------------------------------------------------------------------

// Returns the current date (long French format) and time (HH:MM).
function getDateTime() {
    const now = new Date();

    const date = now.toLocaleDateString("fr-FR", {
        weekday: "long",
        day:     "2-digit",
        month:   "long"
    });

    const time = now.toLocaleTimeString("fr-FR", {
        hour:   "2-digit",
        minute: "2-digit"
    });

    return { date: capitalize(date), time };
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// -----------------------------------------------------------------------------
// WMO weather code → Weather Icons CSS class
// Reference: https://open-meteo.com/en/docs (WMO 4677 code table)
// -----------------------------------------------------------------------------

function wiClass(code) {
    if (code === 0)  return "wi-day-sunny";           // Clear sky
    if (code <= 1)   return "wi-day-sunny-overcast";  // Mainly clear
    if (code <= 2)   return "wi-day-cloudy";          // Partly cloudy
    if (code <= 3)   return "wi-cloudy";              // Overcast
    if (code <= 48)  return "wi-fog";                 // Fog / rime fog
    if (code <= 57)  return "wi-sprinkle";            // Drizzle
    if (code <= 65)  return "wi-rain";                // Rain
    if (code <= 67)  return "wi-rain-mix";            // Freezing rain
    if (code <= 77)  return "wi-snow";                // Snow
    if (code <= 82)  return "wi-showers";             // Rain showers
    if (code <= 86)  return "wi-snow";                // Snow showers
    return "wi-thunderstorm";                         // Thunderstorm (95–99)
}

// -----------------------------------------------------------------------------
// European AQI → CSS class for colour coding
// Good ≤20 (green), Medium ≤40 (amber), Poor >40 (red)
// -----------------------------------------------------------------------------

function aqiClass(aqi) {
    if (aqi === null || aqi === undefined) return "";
    if (aqi <= 20) return "aqi-good";
    if (aqi <= 40) return "aqi-mid";
    return "aqi-bad";
}

// -----------------------------------------------------------------------------
// Main render — fetches dashboard.json and populates all three panels
// -----------------------------------------------------------------------------

async function loadDashboard() {
    const response = await fetch("data/dashboard.json");
    const data = await response.json();

    const { date, time } = getDateTime();

    // -------------------------------------------------------------------------
    // TODAY PANEL — current conditions + daily summary
    // -------------------------------------------------------------------------

    document.getElementById("today-panel").innerHTML = `
        <div class="date-block">
            <span class="date">${date}</span>
            <span class="clock">${time}</span>
        </div>

        <div class="big-temp-wrapper">
            <div class="big-temp">
                <i class="wi wi-fw ${wiClass(data.today.weather_code ?? 0)}"></i>
                <span class="temp-value">${data.today.temp_now}°</span>
            </div>

            <div class="weather-details">
                <div class="detail">
                    <i class="wi wi-fw wi-thermometer"></i>
                    <span class="val temp-min">${data.today.temp_min}°</span>
                    <span style="color:var(--border);margin:0 2px">/</span>
                    <span class="val temp-max">${data.today.temp_max}°</span>
                </div>
                <div class="detail">
                    <i class="wi wi-fw wi-sunrise"></i>
                    <span class="val">${data.today.sunrise}</span>
                    <span style="color:var(--border);margin:0 4px">·</span>
                    <i class="wi wi-fw wi-sunset"></i>
                    <span class="val">${data.today.sunset}</span>
                </div>
                <div class="detail">
                    <i class="wi wi-fw wi-umbrella"></i>
                    <span class="val">${data.today.rain}%</span>
                    <span style="color:var(--border);margin:0 4px">·</span>
                    <span class="val">${data.today.rain_mm} mm</span>
                </div>
                <div class="detail">
                    <i class="wi wi-fw wi-strong-wind"></i>
                    <span class="val">${data.today.wind} km/h</span>
                </div>
                <div class="detail">
                    <i class="wi wi-fw wi-dust"></i>
                    <span class="val ${aqiClass(data.today.aqi)}">
                        ${data.today.aqi ?? "—"} · ${data.today.air_label}
                    </span>
                </div>
            </div>
        </div>
    `;

    // -------------------------------------------------------------------------
    // FORECAST PANEL — 6-day outlook, one row per day
    // Rows are distributed evenly across the full panel height via flexbox.
    // -------------------------------------------------------------------------

    let forecastHtml = "";

    for (const day of data.forecast) {
        forecastHtml += `
        <div class="day-line">
            <span class="day-name">${day.day}</span>
            <i class="wi wi-fw ${wiClass(day.weather_code ?? 0)}"></i>
            <span class="temps">
                <span class="t-min">${day.min}°</span>
                <span class="sep">/</span>
                <span class="t-max">${day.max}°</span>
            </span>
            <span class="rain">
                <span class="rain-pct">${day.rain}%</span>
                <span> · ${day.rain_mm} mm</span>
            </span>
        </div>`;
    }

    document.getElementById("forecast-panel").innerHTML = forecastHtml;

    // -------------------------------------------------------------------------
    // NEWS PANEL — 2×2 grid: local news (left) | world news (right)
    // Headlines are never truncated; source label shown below each title.
    // -------------------------------------------------------------------------

    const rennes = (data.news["Rennes (Ouest France)"] || []).slice(0, 2);
    const monde  = (data.news["Monde (Courrier international)"] || []).slice(0, 2);

    // Build grid column by column: Rennes[0], Monde[0], Rennes[1], Monde[1]
    // CSS grid-template-columns: 1fr 1fr places them side by side automatically.
    let newsHtml = `<div class="news-grid">`;

    for (let i = 0; i < 2; i++) {
        if (rennes[i]) {
            newsHtml += `
            <div class="news-item">
                <span class="headline">${rennes[i]}</span>
                <span class="source">Ouest-France · Rennes</span>
            </div>`;
        }
        if (monde[i]) {
            newsHtml += `
            <div class="news-item">
                <span class="headline">${monde[i]}</span>
                <span class="source">Courrier international</span>
            </div>`;
        }
    }

    newsHtml += `</div>`;
    document.getElementById("info-panel").innerHTML = newsHtml;

    // -------------------------------------------------------------------------
    // Clock — refresh the time display every 30 seconds without re-rendering
    // -------------------------------------------------------------------------

    setInterval(() => {
        const el = document.querySelector(".clock");
        if (el) {
            el.textContent = new Date().toLocaleTimeString("fr-FR", {
                hour:   "2-digit",
                minute: "2-digit"
            });
        }
    }, 30000);
}

// Kick off the initial render
loadDashboard();