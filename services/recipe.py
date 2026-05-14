import httpx
import asyncio
import random

ICOOK_API    = "https://icook.tw/api/v1/recipes/search"
ICOOK_RECIPE = "https://icook.tw/recipes/{id}"
ICOOK_COVER  = "https://imageproxy.icook.tw/scale?url={url}&width=360&height=270"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    ),
    "Accept": "application/json",
    "Accept-Language": "zh-TW,zh;q=0.9",
    "Referer": "https://icook.tw/",
}

MEAL_STYLE_MAP = {
    "早餐": ["快速", "簡單", "早餐"],
    "午餐": ["家常", "便當", "下飯"],
    "晚餐": ["家常", "燉", "湯", "滷"],
}

WEATHER_STYLE_MAP = {
    "炎熱": ["涼拌", "清炒", "清蒸"],
    "寒冷": ["燉", "滷", "紅燒"],
    "下雨": ["燉", "湯"],
    "舒適": ["炒", "家常"],
}


def _build_query(ingredient: str, styles: list) -> str:
    style = styles[0] if styles else ""
    return f"{ingredient}{style}" if style else ingredient


def _parse_recipe(rec: dict) -> dict:
    rid   = rec.get("id", "")
    name  = rec.get("name", "")
    cover = rec.get("cover", "")
    # cover 有時是 list，有時是 str
    if isinstance(cover, list):
        cover = cover[0] if cover else ""
    image = ICOOK_COVER.format(url=cover) if cover else ""
    return {
        "title": name,
        "url":   ICOOK_RECIPE.format(id=rid),
        "image": image,
        "ingredient": ingredient if "ingredient" in rec else "",
    }


async def _search(query: str, ingredient: str, count: int = 2) -> list:
    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=True, headers=HEADERS) as c:
            resp = await c.get(ICOOK_API, params={"q": query, "page": 1})
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return []

    recipes = data.get("recipes", [])
    parsed  = [_parse_recipe(r) for r in recipes if r.get("id") and r.get("name")]
    for p in parsed:
        p["ingredient"] = ingredient
    random.shuffle(parsed)
    return parsed[:count]


def _clean_ingredient(name: str) -> str:
    """市場名稱常帶品種（如「冬瓜-青皮」「菠菜-甜菠菜」），搜食譜時只取主名。"""
    return name.split("-")[0].split("(")[0].strip()


async def fetch_recipes_for_component(ingredient: str, meal_type: str, weather_styles: list, count: int = 2) -> list:
    """用 icook.tw 官方 API 搜尋，回傳 count 筆真實食譜連結。"""
    clean          = _clean_ingredient(ingredient)
    meal_styles    = MEAL_STYLE_MAP.get(meal_type, ["家常"])
    primary_style  = weather_styles[0] if weather_styles else meal_styles[0]

    queries = [
        f"{clean}{primary_style}",
        f"{clean}{meal_styles[0]}",
        clean,
    ]

    for query in queries:
        results = await _search(query, ingredient, count)
        if results:
            return results
        await asyncio.sleep(0.2)

    # API 全失敗的備援連結
    from urllib.parse import quote
    return [{
        "title":      f"搜尋「{ingredient}」食譜",
        "url":        f"https://icook.tw/search/recipe?q={quote(ingredient)}",
        "image":      "",
        "ingredient": ingredient,
    }]


def build_meal_suggestions(ingredient: str, meal_type: str, weather_styles: list) -> list:
    """保留相容性，供直接呼叫（回傳 query 列表）。"""
    return [{"query": ingredient, "ingredient": ingredient, "meal_type": meal_type}]
