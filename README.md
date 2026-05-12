# 每日菜單推薦 🍳

結合天氣、市場菜價、icook.tw 食譜，每天自動幫你決定要煮什麼。

## 功能

- **天氣感知推薦**：天熱推涼拌清炒，天冷推燉湯火鍋，下雨推暖鍋湯品
- **市場菜價**：抓取農委會批發市場即時價格，優先推薦便宜食材
- **icook.tw 食譜**：自動搜尋對應食材的早餐、午餐、晚餐食譜
- **一鍵換菜單**：不喜歡？點「換一組菜單」立刻重新推薦

## 快速啟動

### Windows（PowerShell）
```powershell
cd meal-planner
.\start.ps1
```

### 手動安裝
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

開啟瀏覽器前往 http://localhost:8000

## 資料來源

| 資料 | 來源 | 需要 API Key |
|------|------|-------------|
| 天氣預報 | [Open-Meteo](https://open-meteo.com) | ❌ 不需要 |
| 市場菜價 | [農委會開放資料](https://data.moa.gov.tw) | ❌ 不需要 |
| 食譜 | [愛料理 iCook](https://icook.tw) | ❌ 不需要 |

## API 端點

- `GET /api/menu?city=臺北市` — 完整菜單（天氣 + 菜價 + 食譜）
- `GET /api/weather?city=臺北市` — 只查天氣
- `GET /api/market` — 只查今日菜價
