import os
import asyncio
import logging
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Кнопка
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💰 Получить цену P2P", callback_data="get_price")]
    ]
)


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Привет! Нажми кнопку ниже, чтобы узнать цену:", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == "get_price")
async def handle_callback(callback: types.CallbackQuery):
    await callback.answer("Запрашиваю цену...")
    offers = await fetch_p2p_data()

    if not offers:
        await callback.message.answer("❌ Не удалось получить цену.")
        return

    # Берём строки с 6 по 11 (индексация с 0 — это 5 по 10)
    selected = offers[5:11]
    prices = [float(i["price"]) for i in selected]
    avg_price = sum(prices) / len(prices)

    text = f"📈 <b>Средняя цена (6–11 строки):</b>\n\n{hbold(round(avg_price, 2))} ₽"
    await callback.message.answer(text)


async def fetch_p2p_data():
    url = "https://api2.bybit.com/fiat/otc/item/online"

    payload = {
        "userId": "",
        "tokenId": "USDT",
        "currencyId": "RUB",
        "payment": ["Local Green Bank"],  # если нужна конкретная оплата
        "side": "1",  # 1 = покупка, 0 = продажа
        "size": "",
        "page": 1,
        "amount": "",
        "authMaker": False
    }

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            print("DEBUG: BYBIT API RESPONSE:", data)  # Логируем полный ответ

            if data.get("result", {}).get("items"):
                return data["result"]["items"]

        except Exception as e:
            print("Ошибка при получении данных от Bybit:", e)

    return None


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
