import random
from .recipe import build_meal_suggestions

# ── 肉類：依天氣挑 ──────────────────────────────────────────
HOT_MEATS  = ["雞胸肉", "魚片", "蝦仁", "透抽", "鮭魚", "豆腐"]
COLD_MEATS = ["豬五花", "排骨", "牛肉", "羊肉", "豬腱"]
MILD_MEATS = ["雞腿", "豬里肌", "雞翅", "豬絞肉", "鯛魚片"]

# ── 湯底：依天氣挑 ──────────────────────────────────────────
HOT_SOUPS  = ["冬瓜湯", "絲瓜蛤蠣湯", "味噌湯", "番茄蛋花湯", "苦瓜排骨湯"]
COLD_SOUPS = ["排骨湯", "蘿蔔湯", "雞湯", "玉米濃湯", "麻油雞湯", "薑母鴨"]
MILD_SOUPS = ["蛋花湯", "豆腐湯", "絲瓜湯", "紫菜湯", "玉米蛋花湯"]

# ── 蛋料理 ──────────────────────────────────────────────────
EGG_DISHES = ["番茄炒蛋", "蒸蛋", "滷蛋", "蔥花炒蛋", "皮蛋豆腐", "荷包蛋", "玉子燒"]

# ── 烹調風格 ────────────────────────────────────────────────
WEATHER_STYLES = {
    "炎熱": ["清炒", "涼拌", "清蒸", "水炒"],
    "寒冷": ["燉", "滷", "紅燒", "熱炒"],
    "下雨": ["燉", "煮", "熱炒"],
    "舒適": ["炒", "蒸", "家常", "快炒"],
}

MEAL_CONFIGS = {
    "早餐": {
        "components": ["菜"],   # 早餐只有一道蔬菜建議
        "styles_bonus": ["快速", "簡單", "早餐"],
    },
    "午餐": {
        "components": ["菜", "肉", "湯", "蛋"],
        "styles_bonus": ["家常", "便當"],
    },
    "晚餐": {
        "components": ["菜", "肉", "湯", "蛋"],
        "styles_bonus": ["家常", "下飯"],
    },
}

COMPONENT_META = {
    "菜": {"icon": "🥬", "label": "蔬菜"},
    "肉": {"icon": "🥩", "label": "肉類"},
    "湯": {"icon": "🍲", "label": "湯品"},
    "蛋": {"icon": "🥚", "label": "蛋料理"},
}


def _pick_meat(weather: dict) -> str:
    temp = weather.get("temp", 25)
    if temp >= 28:
        return random.choice(HOT_MEATS)
    if temp <= 18:
        return random.choice(COLD_MEATS)
    return random.choice(MILD_MEATS)


def _pick_soup(weather: dict) -> str:
    temp = weather.get("temp", 25)
    if temp >= 28:
        return random.choice(HOT_SOUPS)
    if temp <= 18:
        return random.choice(COLD_SOUPS)
    return random.choice(MILD_SOUPS)


def _pick_egg() -> str:
    return random.choice(EGG_DISHES)


def _weather_styles(weather: dict) -> list:
    mood = weather.get("mood", "舒適")
    for keyword, styles in WEATHER_STYLES.items():
        if keyword in mood:
            return styles
    return weather.get("cooking_styles", ["炒", "煮"])


async def generate_menu(weather: dict, vegetables: list) -> list:
    styles = _weather_styles(weather)
    veg_pool = (vegetables[:3] if len(vegetables) >= 3 else (vegetables * 3))[:3]
    random.shuffle(veg_pool)

    meals = []
    for i, (meal_name, cfg) in enumerate(MEAL_CONFIGS.items()):
        combined_styles = styles + cfg["styles_bonus"]
        veg = veg_pool[i % len(veg_pool)]

        # 為每個 component 產生搜尋建議
        components = []
        for comp in cfg["components"]:
            if comp == "菜":
                ingredient = veg["name"]
                badge_info = {"price": veg["price"], "unit": veg["unit"], "market": veg.get("market", "")}
            elif comp == "肉":
                ingredient = _pick_meat(weather)
                badge_info = {}
            elif comp == "湯":
                ingredient = _pick_soup(weather)
                badge_info = {}
            else:  # 蛋
                ingredient = _pick_egg()
                badge_info = {}

            suggestions = build_meal_suggestions(ingredient, meal_name, combined_styles)
            meta = COMPONENT_META[comp]
            components.append({
                "type": comp,
                "icon": meta["icon"],
                "label": meta["label"],
                "ingredient": ingredient,
                "badge_info": badge_info,
                "suggestions": suggestions,
            })

        meals.append({
            "meal_type": meal_name,
            "meal_icon": {"早餐": "🌅", "午餐": "☀️", "晚餐": "🌙"}[meal_name],
            "components": components,
        })

    return meals
