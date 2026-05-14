import asyncio
import random
from .recipe import fetch_recipes_for_component

HOT_MEATS  = ["雞胸肉", "魚片", "蝦仁", "透抽", "鮭魚", "豆腐"]
COLD_MEATS = ["豬五花", "排骨", "牛肉", "羊肉", "豬腱"]
MILD_MEATS = ["雞腿", "豬里肌", "雞翅", "豬絞肉", "鯛魚片"]

HOT_SOUPS  = ["冬瓜湯", "絲瓜蛤蠣湯", "味噌湯", "番茄蛋花湯", "苦瓜排骨湯"]
COLD_SOUPS = ["排骨湯", "蘿蔔湯", "雞湯", "玉米濃湯", "麻油雞湯", "薑母鴨"]
MILD_SOUPS = ["蛋花湯", "豆腐湯", "絲瓜湯", "紫菜湯", "玉米蛋花湯"]

EGG_DISHES = ["番茄炒蛋", "蒸蛋", "滷蛋", "蔥花炒蛋", "皮蛋豆腐", "荷包蛋", "玉子燒"]

WEATHER_STYLES = {
    "炎熱": ["涼拌", "清炒", "清蒸", "水炒"],
    "寒冷": ["燉", "滷", "紅燒", "熱炒"],
    "下雨": ["燉", "煮", "熱炒"],
    "舒適": ["炒", "蒸", "家常", "快炒"],
}

MEAL_CONFIGS = {
    "早餐": {"components": ["菜"], "styles_bonus": ["快速", "簡單"]},
    "午餐": {"components": ["菜", "肉", "湯", "蛋"], "styles_bonus": ["家常", "便當"]},
    "晚餐": {"components": ["菜", "肉", "湯", "蛋"], "styles_bonus": ["家常", "下飯"]},
}

COMPONENT_META = {
    "菜": {"icon": "🥬", "label": "蔬菜"},
    "肉": {"icon": "🥩", "label": "肉類"},
    "湯": {"icon": "🍲", "label": "湯品"},
    "蛋": {"icon": "🥚", "label": "蛋料理"},
}


def _pick_ingredient(comp: str, weather: dict, veg: dict) -> str:
    temp = weather.get("temp", 25)
    if comp == "菜":
        return veg["name"]
    if comp == "肉":
        if temp >= 28: return random.choice(HOT_MEATS)
        if temp <= 18: return random.choice(COLD_MEATS)
        return random.choice(MILD_MEATS)
    if comp == "湯":
        if temp >= 28: return random.choice(HOT_SOUPS)
        if temp <= 18: return random.choice(COLD_SOUPS)
        return random.choice(MILD_SOUPS)
    return random.choice(EGG_DISHES)  # 蛋


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

    # 建立所有 (meal, component) 的搜尋任務，全部並行執行
    tasks = []
    task_meta = []
    for i, (meal_name, cfg) in enumerate(MEAL_CONFIGS.items()):
        combined = styles + cfg["styles_bonus"]
        veg = veg_pool[i % len(veg_pool)]
        for comp in cfg["components"]:
            ingredient = _pick_ingredient(comp, weather, veg)
            tasks.append(fetch_recipes_for_component(ingredient, meal_name, combined, count=2))
            task_meta.append({"meal": meal_name, "comp": comp, "ingredient": ingredient, "veg": veg})

    all_results = await asyncio.gather(*tasks)

    # 重組成結構化菜單
    meals_dict: dict = {}
    idx = 0
    for i, (meal_name, cfg) in enumerate(MEAL_CONFIGS.items()):
        veg = veg_pool[i % len(veg_pool)]
        components = []
        for comp in cfg["components"]:
            meta = task_meta[idx]
            recipes = all_results[idx]
            badge = {"price": veg["price"], "unit": veg["unit"]} if comp == "菜" else {}
            components.append({
                "type": comp,
                "icon": COMPONENT_META[comp]["icon"],
                "label": COMPONENT_META[comp]["label"],
                "ingredient": meta["ingredient"],
                "badge_info": badge,
                "recipes": recipes,
            })
            idx += 1
        meals_dict[meal_name] = {
            "meal_type": meal_name,
            "meal_icon": {"早餐": "🌅", "午餐": "☀️", "晚餐": "🌙"}[meal_name],
            "components": components,
        }

    return list(meals_dict.values())
