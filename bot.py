import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import httpx

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# Кнопка
keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text="📊 Получить цену", callback_data="get_price")
)

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Нажми кнопку, чтобы получить цену:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "get_price")
async def handle_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer("⏳ Получаю цену...")
    price = await fetch_p2p_data()
    if price:
        await callback_query.message.answer(f"💵 Средняя цена: <b>{price}</b> ₽")
    else:
        await callback_query.message.answer("❌ Не удалось получить цену.")

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
        "amount": "",
        "order": "",
        "sortType": "",
        "sideType": "1",
        "language": "ru-RU"
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            items = data.get("result", {}).get("items", [])
            if len(items) < 11:
                return None
            selected = items[5:11]
            prices = [float(i["price"]) for i in selected]
            avg_price = round(sum(prices) / len(prices), 2)
            return avg_price
    except Exception as e:
        print(f"❌ Ошибка при получении данных: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
