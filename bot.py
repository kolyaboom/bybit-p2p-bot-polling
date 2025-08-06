import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
import httpx

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💰 Получить курс", callback_data="get_price")]
])

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=keyboard)

@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    if callback.data == "get_price":
        await callback.message.edit_text("⏳ Получаю цену...")
        offers = await fetch_p2p_data()
        if offers:
            avg_price = round(sum(offers) / len(offers), 2)
            await callback.message.edit_text(f"Средняя цена с 6 по 11 строку: <b>{avg_price} RUB</b>")
        else:
            await callback.message.edit_text("Не удалось получить цену.")

async def fetch_p2p_data():
    url = "https://api2.bybit.com/fiat/otc/item/online"
    payload = {
        "userId": "",
        "tokenId": "USDT",
        "currencyId": "RUB",
        "payment": ["Local Green Bank"],
        "side": "1",
        "size": "",
        "page": 1,
        "rows": 20,
        "amount": "",
        "authMaker": False
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload)
            data = response.json()
            items = data.get("result", {}).get("items", [])
            prices = [float(item["price"]) for item in items[5:11]]
            return prices
    except Exception as e:
        print("Ошибка при получении данных:", e)
        return []

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())