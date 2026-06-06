async function loadDashboard() {

    const response =
        await fetch("data/dashboard.json");

    const data =
        await response.json();

    document.getElementById(
        "today-panel"
    ).innerHTML = `

        <h1>Aujourd'hui</h1>

        <div class="today-date">
            ${data.today.weekday} ${data.today.date}
        </div>

        <div class="big-temp">
            ${data.today.icon}
            ${data.today.temp_now}°
        </div>

        <div>
            Min ${data.today.temp_min}°
            / Max ${data.today.temp_max}°
        </div>

        <div>
            Risque pluie : ${data.today.rain} %
        </div>

        <div>
            Cumul prévu : ${data.today.rain_mm} mm
        </div>

        <div>
            Vent : ${data.today.wind} km/h
        </div>

        <div>
            Air :
            ${data.today.aqi}
            (${data.today.air_label})
        </div>

        <div>
            Lever : ${data.today.sunrise}
            / Coucher : ${data.today.sunset}
        </div>

    `;

    let forecastHtml =
        "<h1>Prévisions</h1>";

    for (const day of data.forecast) {

        forecastHtml += `

            <div class="day-line">

                <span>${day.day}</span>

                <span>${day.icon}</span>

                <span>
                    ${day.min}°
                    /
                    ${day.max}°
                </span>

                <span>
                    ☂ ${day.rain}%
                    •
                    ${day.rain_mm} mm
                </span>

            </div>
        `;
    }

    document.getElementById(
        "forecast-panel"
    ).innerHTML =
        forecastHtml;

    let infoHtml =
        "<h1>Informations</h1>";

    for (
        const [category, titles]
        of Object.entries(data.news)
    ) {

        infoHtml += `

            <div class="category">

                <div class="category-title">
                    ${category}
                </div>

        `;

        const list =
            Array.isArray(titles)
                ? titles
                : [titles];

        for (const title of list) {

            const shortTitle =
                title.length > 120
                    ? title.substring(0, 117) + "..."
                    : title;

            infoHtml += `
                <div>
                    • ${shortTitle}
                </div>
            `;
        }

        infoHtml += `
            </div>
        `;
    }

    document.getElementById(
        "info-panel"
    ).innerHTML =
        infoHtml;
}

loadDashboard();