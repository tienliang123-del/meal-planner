from urllib.parse import quote

ICOOK_SEARCH = "https://icook.tw/search/recipe?q={}"

MEAL_STYLE_MAP = {
    "早餐": ["快速", "簡單", "早餐"],
    "午餐": ["家常", "便當", "快炒"],
    "晚餐": ["湯", "燉", "家常菜"],
}

WEATHER_STYLE_MAP = {
    "涼拌":  ["涼拌", "冷盤", "清蒸"],
    "清炒":  ["清炒", "炒", "快炒"],
    "燉":    ["燉", "滷", "燜"],
    "煲湯":  ["湯", "煲湯", "燉湯"],
    "火鍋":  ["火鍋", "麻辣"],
    "炒":    ["炒", "快炒", "家常"],
    "蒸":    ["清蒸", "蒸"],
    "湯":    ["湯", "清湯", "羹"],
}

MEAL_ICONS = {
    "早餐": "🌅",
    "午餐": "☀️",
    "晚餐": "🌙",
}


def _build_queries(ingredient: str, meal_type: str, weather_styles: list) -> list[dict]:
    """
    為一個食材 × 三餐類型 × 天氣口味，產生 3 組搜尋建議。
    每組包含：查詢字串、推薦理由、icook.tw 連結。
    """
    suggestions = []

    # 搜尋組合 1：食材 + 天氣適合的烹調法
    primary_style = weather_styles[0] if weather_styles else "家常"
    q1 = f"{ingredient}{primary_style}"
    suggestions.append({
        "query": q1,
        "label": f"{primary_style}{ingredient}",
        "reason": f"天氣適合{primary_style}",
        "url": ICOOK_SEARCH.format(quote(q1)),
    })

    # 搜尋組合 2：食材 + 三餐特色
    meal_styles = MEAL_STYLE_MAP.get(meal_type, ["家常"])
    q2 = f"{ingredient}{meal_styles[0]}"
    suggestions.append({
        "query": q2,
        "label": f"{meal_styles[0]}{ingredient}",
        "reason": f"適合當{meal_type}",
        "url": ICOOK_SEARCH.format(quote(q2)),
    })

    # 搜尋組合 3：純食材（讓用戶自由選）
    suggestions.append({
        "query": ingredient,
        "label": f"所有{ingredient}食譜",
        "reason": "自由挑選",
        "url": ICOOK_SEARCH.format(quote(ingredient)),
    })

    return suggestions


async def search_recipes(ingredient: str, preferred_styles: list = None, count: int = 2) -> list:
    """
    回傳 icook.tw 搜尋建議連結（不爬蟲，icook 為 JS 動態渲染）。
    """
    styles = preferred_styles or ["家常"]
    meal_type = "午餐"  # 預設，由 recommender 傳入
    return _build_queries(ingredient, meal_type, styles)[:count]


def build_meal_suggestions(ingredient: str, meal_type: str, weather_styles: list) -> list:
    """供 recommender 直接呼叫，帶入三餐類型。"""
    return _build_queries(ingredient, meal_type, weather_styles)
