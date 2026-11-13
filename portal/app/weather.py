"""Weather on the home page: Open-Meteo (no key), cached 30 min. WEATHER_PLACES = "Bakı:40.4093:49.8671;…"."""
import os
import threading
import time

import requests

PLACES = [(n, float(a), float(b)) for n, a, b in
          (x.split(":") for x in os.environ.get("WEATHER_PLACES", "Bakı:40.4093:49.8671").split(";") if x.count(":") == 2)]
TTL = 1800
# WMO weather codes → (emoji, Azerbaijani, English)
CODES = {0: ("☀️", "Açıq", "Clear"), 1: ("🌤️", "Əsasən açıq", "Mainly clear"), 2: ("⛅", "Az buludlu", "Partly cloudy"),
         3: ("☁️", "Buludlu", "Overcast"), 45: ("🌫️", "Duman", "Fog"), 48: ("🌫️", "Duman", "Fog"),
         51: ("🌦️", "Çiskin", "Drizzle"), 53: ("🌦️", "Çiskin", "Drizzle"), 55: ("🌦️", "Çiskin", "Drizzle"),
         56: ("🌧️", "Buzlu çiskin", "Freezing drizzle"), 57: ("🌧️", "Buzlu çiskin", "Freezing drizzle"),
         61: ("🌧️", "Yağış", "Rain"), 63: ("🌧️", "Yağış", "Rain"), 65: ("🌧️", "Güclü yağış", "Heavy rain"),
         66: ("🌧️", "Buzlu yağış", "Freezing rain"), 67: ("🌧️", "Buzlu yağış", "Freezing rain"),
         71: ("🌨️", "Qar", "Snow"), 73: ("🌨️", "Qar", "Snow"), 75: ("❄️", "Güclü qar", "Heavy snow"), 77: ("🌨️", "Qar", "Snow"),
         80: ("🌦️", "Leysan", "Showers"), 81: ("🌦️", "Leysan", "Showers"), 82: ("⛈️", "Güclü leysan", "Heavy showers"),
         85: ("🌨️", "Qar", "Snow showers"), 86: ("🌨️", "Qar", "Snow showers"),
         95: ("⛈️", "Tufan", "Thunderstorm"), 96: ("⛈️", "Dolu", "Hail"), 99: ("⛈️", "Dolu", "Hail")}


RU = {0: 'Ясно', 1: 'Преимущественно ясно', 2: 'Переменная облачность', 3: 'Пасмурно', 45: 'Туман', 48: 'Туман', 51: 'Морось', 53: 'Морось', 55: 'Морось', 56: 'Ледяная морось', 57: 'Ледяная морось', 61: 'Дождь', 63: 'Дождь', 65: 'Сильный дождь', 66: 'Ледяной дождь', 67: 'Ледяной дождь', 71: 'Снег', 73: 'Снег', 75: 'Сильный снег', 77: 'Снег', 80: 'Ливень', 81: 'Ливень', 82: 'Сильный ливень', 85: 'Снег', 86: 'Снег', 95: 'Гроза', 96: 'Град', 99: 'Град'}


def _code(c):
    e, az, en = CODES.get(int(c or 0), ("🌡️", "", ""))
    return {"icon": e, "az": az, "en": en, "ru": RU.get(int(c or 0), en)}


class Weather:
    def __init__(self):
        self._cache, self._at = None, 0
        self._lock = threading.Lock()

    def get(self):
        with self._lock:
            if self._cache is not None and time.time() - self._at < TTL:
                return self._cache
        out = []
        for name, lat, lon in PLACES:
            try:
                j = requests.get("https://api.open-meteo.com/v1/forecast", timeout=8, params={
                    "latitude": lat, "longitude": lon, "timezone": "Asia/Baku", "forecast_days": 4, "wind_speed_unit": "ms",
                    "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min"}).json()
                cur, d = j["current"], j["daily"]
                out.append({"place": name, "temp": round(cur["temperature_2m"]), "feels": round(cur["apparent_temperature"]),
                            "wind": round(cur["wind_speed_10m"]), **_code(cur["weather_code"]),
                            "days": [{"date": d["time"][i], "max": round(d["temperature_2m_max"][i]),
                                      "min": round(d["temperature_2m_min"][i]), **_code(d["weather_code"][i])}
                                     for i in range(1, len(d["time"]))]})
            except Exception:
                continue
        with self._lock:
            if out or self._cache is None:
                self._cache, self._at = out, time.time()
            return self._cache
