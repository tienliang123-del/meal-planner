import httpx
from datetime import datetime, timedelta
from collections import defaultdict

MARKET_API = "https://data.moa.gov.tw/Service/OpenData/FromM/FarmTransData.aspx"

VEGETABLE_CATEGORIES = {
    "葉菜類": ["高麗菜", "白菜", "菠菜", "空心菜", "地瓜葉", "莧菜", "青江菜", "韭菜", "韭黃",
               "茼蒿", "萵苣", "芹菜", "蔥", "香菜", "小白菜"],
    "瓜果類": ["苦瓜", "絲瓜", "冬瓜", "南瓜", "茄子", "番茄", "青椒", "甜椒", "小黃瓜", "大黃瓜"],
    "根莖類": ["蘿蔔", "紅蘿蔔", "馬鈴薯", "洋蔥", "大蒜", "薑", "芋頭", "地瓜", "山藥"],
    "豆菜類": ["四季豆", "豌豆", "毛豆", "長豇豆", "豆芽"],
    "菇蕈類": ["香菇", "金針菇", "杏鮑菇", "鴻喜菇", "木耳"],
}

ALL_VEGETABLES = [v for vlist in VEGETABLE_CATEGORIES.values() for v in vlist]

def _parse_price(val) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0

def _get_price_level(price: float) -> str:
    if price <= 10:   return "超便宜 💰"
    if price <= 20:   return "便宜 👍"
    if price <= 35:   return "普通 😊"
    if price <= 60:   return "稍貴 😅"
    return "偏貴 💸"

def _get_category(name: str) -> str:
    for cat, items in VEGETABLE_CATEGORIES.items():
        if any(item in name for item in items):
            return cat
    return "其他"

async def get_cheap_vegetables(top_n: int = 6) -> list:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                MARKET_API,
                params={"$format": "json"},
                headers={"User-Agent": "Mozilla/5.0 MealPlanner/1.0"},
            )
            resp.raise_for_status()
            raw = resp.json()

        # 聚合同名蔬菜的平均價（取台北一市場優先）
        price_map: dict[str, list] = defaultdict(list)
        for item in raw:
            name = item.get("作物名稱", "").strip()
            avg  = _parse_price(item.get("平均價"))
            if avg > 0 and any(v in name for v in ALL_VEGETABLES):
                price_map[name].append({
                    "price": avg,
                    "market": item.get("市場名稱", ""),
                    "date": item.get("交易日期", ""),
                    "volume": _parse_price(item.get("交易量")),
                })

        results = []
        for name, entries in price_map.items():
            # 優先台北一，否則取平均
            tp_entries = [e for e in entries if "台北" in e["market"]]
            target = tp_entries if tp_entries else entries
            avg_price = sum(e["price"] for e in target) / len(target)
            results.append({
                "name": name,
                "price": round(avg_price, 1),
                "unit": "元/公斤",
                "market": target[0]["market"],
                "date": target[0]["date"],
                "level": _get_price_level(avg_price),
                "category": _get_category(name),
            })

        results.sort(key=lambda x: x["price"])
        return results[:top_n]

    except Exception as e:
        # 回傳示範資料，避免整個頁面壞掉
        return [
            {"name": "高麗菜", "price": 8.5,  "unit": "元/公斤", "market": "台北一", "date": "", "level": "超便宜 💰", "category": "葉菜類"},
            {"name": "地瓜葉", "price": 10.0, "unit": "元/公斤", "market": "台北一", "date": "", "level": "超便宜 💰", "category": "葉菜類"},
            {"name": "空心菜", "price": 12.0, "unit": "元/公斤", "market": "台北一", "date": "", "level": "便宜 👍",   "category": "葉菜類"},
            {"name": "豆芽",   "price": 14.0, "unit": "元/公斤", "market": "台北一", "date": "", "level": "便宜 👍",   "category": "豆菜類"},
            {"name": "茄子",   "price": 18.0, "unit": "元/公斤", "market": "台北一", "date": "", "level": "便宜 👍",   "category": "瓜果類"},
            {"name": "蘿蔔",   "price": 20.0, "unit": "元/公斤", "market": "台北一", "date": "", "level": "便宜 👍",   "category": "根莖類"},
        ]
