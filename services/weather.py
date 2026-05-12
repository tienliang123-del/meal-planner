import httpx
from datetime import datetime

CITY_COORDS = {
    "臺北市": (25.04, 121.50),
    "新北市": (25.01, 121.46),
    "桃園市": (24.99, 121.30),
    "台中市": (24.14, 120.68),
    "台南市": (22.99, 120.20),
    "高雄市": (22.63, 120.27),
    "新竹市": (24.80, 120.97),
    "嘉義市": (23.48, 120.45),
    "基隆市": (25.13, 121.74),
    "花蓮縣": (23.99, 121.60),
    "宜蘭縣": (24.75, 121.75),
    "屏東縣": (22.67, 120.49),
}

WEATHER_CODE_DESC = {
    range(0, 1):   ("晴天", "☀️"),
    range(1, 4):   ("多雲", "⛅"),
    range(45, 50): ("霧", "🌫️"),
    range(51, 68): ("毛毛雨/細雨", "🌦️"),
    range(71, 78): ("降雪", "❄️"),
    range(80, 83): ("陣雨", "🌧️"),
    range(95, 100):("雷陣雨", "⛈️"),
}

def _decode_weather(code: int):
    for r, (desc, icon) in WEATHER_CODE_DESC.items():
        if code in r:
            return desc, icon
    return "未知", "🌡️"

def _get_weather_mood(temp: float, code: int) -> dict:
    is_raining = code in range(51, 100)
    is_hot     = temp >= 28
    is_cold    = temp <= 18

    if is_hot:
        mood = "炎熱"
        suggestions = ["涼拌", "清炒", "冷盤", "沙拉", "清蒸"]
        avoid = ["火鍋", "麻辣"]
    elif is_cold:
        mood = "寒冷"
        suggestions = ["燉", "煲湯", "火鍋", "熱炒", "燜"]
        avoid = ["冷盤", "涼拌"]
    else:
        mood = "舒適"
        suggestions = ["炒", "蒸", "烤", "煮", "拌"]
        avoid = []

    if is_raining:
        mood += "下雨"
        suggestions = ["湯", "暖鍋"] + suggestions

    return {"mood": mood, "cooking_styles": suggestions, "avoid": avoid, "is_raining": is_raining}

async def get_weather(city: str = "臺北市") -> dict:
    lat, lon = CITY_COORDS.get(city, (25.04, 121.50))
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        "&timezone=Asia%2FTaipei&forecast_days=1"
    )
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        current  = data["current"]
        daily    = data["daily"]
        temp     = current["temperature_2m"]
        code     = current["weather_code"]
        humidity = current["relative_humidity_2m"]
        desc, icon = _decode_weather(code)

        return {
            "city": city,
            "temp": temp,
            "temp_max": daily["temperature_2m_max"][0],
            "temp_min": daily["temperature_2m_min"][0],
            "humidity": humidity,
            "description": desc,
            "icon": icon,
            "rain_prob": daily["precipitation_probability_max"][0],
            **_get_weather_mood(temp, code),
        }
    except Exception as e:
        return {
            "city": city, "temp": 25, "temp_max": 28, "temp_min": 22,
            "humidity": 70, "description": "取得失敗", "icon": "🌡️",
            "rain_prob": 0, "mood": "舒適",
            "cooking_styles": ["炒", "蒸", "煮"],
            "avoid": [], "is_raining": False,
            "error": str(e),
        }
