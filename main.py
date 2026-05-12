from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
from datetime import datetime

from services.weather import get_weather, CITY_COORDS
from services.market import get_cheap_vegetables
from services.recommender import generate_menu

app = FastAPI(title="每日菜單推薦", description="結合天氣、市場菜價、icook.tw 食譜的自動菜單平台")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "cities": list(CITY_COORDS.keys()),
        "today": datetime.now().strftime("%Y年%m月%d日"),
    })


@app.get("/api/menu")
async def api_menu(city: str = Query(default="臺北市")):
    weather, vegetables = await asyncio.gather(
        get_weather(city),
        get_cheap_vegetables(top_n=6),
    )
    menu = await generate_menu(weather, vegetables)
    return JSONResponse({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "weather": weather,
        "cheap_vegetables": vegetables,
        "menu": menu,
    })


@app.get("/api/weather")
async def api_weather(city: str = Query(default="臺北市")):
    return JSONResponse(await get_weather(city))


@app.get("/api/market")
async def api_market():
    return JSONResponse(await get_cheap_vegetables(top_n=10))
