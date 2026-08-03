import asyncio
import random

from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config import BOT_TOKEN, CHANNEL_ID, MANAGER_USERNAME


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


users = set()

total_signals = 0
wins = 0
losses = 0

active_signals = {}

# =====================
# МЕНЮ
# =====================

def start_menu():

    builder = ReplyKeyboardBuilder()

    builder.button(text="🚀 Почати")

    return builder.as_markup(
        resize_keyboard=True
    )


def main_menu():

    builder = ReplyKeyboardBuilder()

    builder.button(text="📊 Отримати сигнал")
    builder.button(text="📈 Статистика")
    builder.button(text="💬 Менеджер")
    builder.button(text="ℹ️ Інструкція")
    builder.button(text="⬅️ Повернутись в меню")

    builder.adjust(2, 2, 1)

    return builder.as_markup(
        resize_keyboard=True
    )


def time_menu():

    builder = ReplyKeyboardBuilder()

    builder.button(text="⏱ 1 хв")
    builder.button(text="⏱ 2 хв")
    builder.button(text="⏱ 5 хв")

    builder.adjust(3)

    return builder.as_markup(
        resize_keyboard=True
    )

# =====================
# START
# =====================

@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
"""
🚀 <b>OTC Signal Bot від MAKSUDOVA FAM</b>

Ласкаво просимо!

Тепер торгувати OTC-парами стало ще простіше.

🤖 Автоматичне формування сигналів
📈 Сигнали для OTC-пар
🗓 Торгуйте навіть у вихідні дні
🎯 Готові точки входу
⏱ Час входу та закриття угоди
📊 Загальна статистика сигналів

💼 Простий та зрозумілий інтерфейс.

🔒 Доступ до сигналів мають лише учасники закритого ком'юніті MAKSUDOVA FAM.

👇 Натисніть кнопку <b>«🚀 Почати»</b>, щоб перевірити доступ.
""",
        parse_mode="HTML",
        reply_markup=start_menu()
    )


@dp.message(F.text == "🚀 Почати")
async def check_access(message: Message):

    user_id = message.from_user.id

    try:

        member = await bot.get_chat_member(
            CHANNEL_ID,
            user_id
        )

        if member.status not in [
            "member",
            "administrator",
            "creator"
        ]:

            await message.answer(
                "❌ Доступ до сигналів закритий.\n\n"
                "Для отримання безкоштовного доступу зверніться до менеджера.\n\n"
                f"💬 @{MANAGER_USERNAME}"
            )
            return

    except Exception:

        await message.answer(
            "❌ Не вдалося перевірити підписку.\n"
            "Спробуйте ще раз пізніше."
        )
        return

    users.add(user_id)

    await message.answer(
        "✅ Доступ підтверджено!\n\n"
        "Ласкаво просимо! Оберіть потрібний пункт меню 👇",
        reply_markup=main_menu()
    )


# =====================
# ПОВЕРНУТИСЬ В МЕНЮ
# =====================

@dp.message(F.text == "⬅️ Повернутись в меню")
async def back_menu(message: Message):

    await message.answer(
        "⬅️ Меню",
        reply_markup=main_menu()
    )


# =====================
# ОТРИМАТИ СИГНАЛ
# =====================

@dp.message(F.text == "📊 Отримати сигнал")
async def get_signal(message: Message):

    await message.answer(
        "⏱ Оберіть час угоди:",
        reply_markup=time_menu()
    )


# =====================
# СТВОРЕННЯ СИГНАЛУ
# =====================

@dp.message(
    F.text.in_(
        [
            "⏱ 1 хв",
            "⏱ 2 хв",
            "⏱ 5 хв"
        ]
    )
)
async def create_signal(message: Message):

    global total_signals

    pairs = [
        "EUR/USD OTC",
        "GBP/USD OTC",
        "USD/JPY OTC",
        "AUD/USD OTC",
        "USD/CAD OTC",
        "USD/CHF OTC",
        "NZD/USD OTC",

        "EUR/GBP OTC",
        "EUR/JPY OTC",
        "EUR/AUD OTC",
        "EUR/CAD OTC",
        "EUR/CHF OTC",
        "EUR/NZD OTC",

        "GBP/JPY OTC",
        "GBP/AUD OTC",
        "GBP/CAD OTC",
        "GBP/CHF OTC",
        "GBP/NZD OTC",

        "AUD/JPY OTC",
        "AUD/CAD OTC",
        "AUD/CHF OTC",
        "AUD/NZD OTC",

        "CAD/JPY OTC",
        "CAD/CHF OTC",

        "CHF/JPY OTC",

        "NZD/JPY OTC",
        "NZD/CAD OTC",
        "NZD/CHF OTC"
        ]

    pair = random.choice(pairs)

    direction = random.choice(
        [
            "🟢 CALL",
            "🔴 PUT"
        ]
    )


        minutes = int(
        message.text
        .replace("⏱ ", "")
        .replace(" хв", "")
    )


    now = datetime.now()

    entry = now + timedelta(
        minutes=1
    )

    close = entry + timedelta(
        minutes=minutes
    )


    total_signals += 1


    active_signals[
        message.from_user.id
    ] = {

        "pair": pair,
        "direction": direction,
        "close": close

    }


        await message.answer(
        f"""
        
🎯 OTC SIGNAL

💱 Пара:
{pair}

📈 Напрям:
{direction}

⏰ Час входу:
{entry.strftime("%H:%M")}

⌛ Час закриття:
{close.strftime("%H:%M")}

⏱ Експірація:
{minutes} хв

⏳ Очікуємо завершення...
""",

        reply_markup=main_menu()

    )


    asyncio.create_task(
        wait_finish(
            message.from_user.id
        )
    )


# =====================
# ОЧІКУВАННЯ ЗАКРИТТЯ
# =====================

async def wait_finish(user_id):

    signal = active_signals[user_id]


    seconds = (
        signal["close"]
        -
        datetime.now()
    ).total_seconds()


    if seconds > 0:

        await asyncio.sleep(seconds)



    keyboard = InlineKeyboardMarkup(

        inline_keyboard=[

            [

                InlineKeyboardButton(
                    text="✅ Зайшло",
                    callback_data="win"
                ),

                InlineKeyboardButton(
                    text="❌ Не зайшло",
                    callback_data="loss"
                )

            ]

        ]

    )


    await bot.send_message(

        user_id,

f"""
⌛ Угода завершена

💱 Пара:
{signal["pair"]}

📈 Напрям:
{signal["direction"]}

Оцініть результат:
""",

reply_markup=keyboard

    )



# =====================
# РЕЗУЛЬТАТ
# =====================

@dp.callback_query(F.data == "win")
async def win(call):

    global wins

    wins += 1


    await call.message.edit_reply_markup(
        reply_markup=None
    )


    await call.message.answer(
        "✅ Результат записано: Зайшло",
        reply_markup=main_menu()
    )



@dp.callback_query(F.data == "loss")
async def loss(call):

    global losses

    losses += 1


    await call.message.edit_reply_markup(
        reply_markup=None
    )


    await call.message.answer(
        "❌ Результат записано: Не зайшло",
        reply_markup=main_menu()
    )



# =====================
# СТАТИСТИКА
# =====================

@dp.message(F.text == "📈 Статистика")
async def stats(message: Message):

    total = wins + losses

    percent = 0

    if total:
        percent = round(
            wins / total * 100,
            1
        )


    await message.answer(

f"""
📊 Загальна статистика

👥 Користувачів:
{len(users)}

🎯 Сигналів:
{total_signals}

✅ Зайшло:
{wins}

❌ Не зайшло:
{losses}

📈 Точність:
{percent}%
"""
    )



# =====================
# МЕНЕДЖЕР
# =====================

@dp.message(F.text == "💬 Менеджер")
async def manager(message: Message):

    await message.answer(
        f"💬 Менеджер:\n@{MANAGER_USERNAME}"
    )



# =====================
# ІНСТРУКЦІЯ
# =====================

@dp.message(F.text == "ℹ️ Інструкція")
async def instruction(message: Message):

    await message.answer(
"""
ℹ️ Інструкція

1️⃣ Отримайте сигнал
2️⃣ Виберіть час угоди
3️⃣ Дочекайтесь закриття
4️⃣ Вкажіть результат
"""
    )



# =====================
# ЗАПУСК
# =====================

async def main():

    print("✅ OTC BOT запущено")

    await dp.start_polling(bot)



if __name__ == "__main__":

    asyncio.run(main())
