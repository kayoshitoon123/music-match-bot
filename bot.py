import asyncio

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

import database as db
import keyboards as kb
from states import Form
from cities import nearby_cities
from config import TOKEN


bot = Bot(token=TOKEN)

dp = Dispatcher(storage=MemoryStorage())


def match_kb(user_id):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❤️", callback_data=f"match_like_{user_id}"),
                InlineKeyboardButton(text="👎", callback_data="match_skip")
            ]
        ]
    )


async def show_next_profile(user_id):

    user = await db.get_user(user_id)

    candidates = await db.get_candidates(user)

    if not candidates:
        candidates = await db.get_any(user)

    if not candidates:
        await bot.send_message(user_id, "Пока никого нет")
        return

    target = candidates[0]

    text = f"""
{target[1]}, {target[2]}
{target[3]}

{target[4]}

{target[8]}
"""

    if target[6]:

        await bot.send_photo(
            user_id,
            target[6],
            caption=text,
            reply_markup=kb.like_kb(target[0])
        )

    else:

        await bot.send_message(
            user_id,
            text,
            reply_markup=kb.like_kb(target[0])
        )


@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):

    user = await db.get_user(message.from_user.id)

    if user:

        await message.answer(
            "Твоя анкета уже существует",
            reply_markup=kb.menu_kb
        )

    else:

        await message.answer("Как тебя зовут?")
        await state.set_state(Form.name)


@dp.message(Form.name)
async def name(message: types.Message, state: FSMContext):

    await state.update_data(name=message.text)

    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)


@dp.message(Form.age)
async def age(message: types.Message, state: FSMContext):

    await state.update_data(age=int(message.text))

    await message.answer("Из какого ты города?")
    await state.set_state(Form.city)


@dp.message(Form.city)
async def city(message: types.Message, state: FSMContext):

    await state.update_data(city=message.text)

    await message.answer(
        "Кто ты?",
        reply_markup=kb.role_kb
    )

    await state.set_state(Form.role)


@dp.message(Form.role)
async def role(message: types.Message, state: FSMContext):

    await state.update_data(role=message.text)

    await message.answer(
        "Кого ищешь?",
        reply_markup=kb.search_role_kb
    )

    await state.set_state(Form.looking)


@dp.message(Form.looking)
async def looking(message: types.Message, state: FSMContext):

    await state.update_data(looking=message.text)

    await message.answer(
        "Отправь фото анкеты или пропусти",
        reply_markup=kb.skip_kb
    )

    await state.set_state(Form.photo)


@dp.message(Form.photo)
async def photo(message: types.Message, state: FSMContext):

    if message.text == "Пропустить":
        await state.update_data(photo=None)

    else:
        photo = message.photo[-1].file_id
        await state.update_data(photo=photo)

    await message.answer(
        "Отправь бит или пропусти",
        reply_markup=kb.skip_kb
    )

    await state.set_state(Form.beat)


@dp.message(Form.beat)
async def beat(message: types.Message, state: FSMContext):

    if message.text == "Пропустить":
        await state.update_data(beat=None)

    else:
        await state.update_data(beat=message.audio.file_id)

    await message.answer(
        "Напиши описание или пропусти",
        reply_markup=kb.skip_kb
    )

    await state.set_state(Form.description)


@dp.message(Form.description)
async def desc(message: types.Message, state: FSMContext):

    if message.text == "Пропустить":
        description = ""
    else:
        description = message.text

    data = await state.get_data()

    await db.add_user((

        message.from_user.id,
        data["name"],
        data["age"],
        data["city"],

        data["role"],
        data["looking"],

        data["photo"],
        data["beat"],

        description

    ))

    await message.answer(
        "Анкета создана",
        reply_markup=kb.menu_kb
    )

    await state.clear()


@dp.message(F.text == "✏️ Изменить анкету")
async def edit(message: types.Message, state: FSMContext):

    await db.delete_user(message.from_user.id)

    await message.answer("Введи имя")
    await state.set_state(Form.name)


@dp.message(F.text == "🔎 Начать поиск")
async def search(message: types.Message):

    await show_next_profile(message.from_user.id)


@dp.callback_query(F.data.startswith("like_"))
async def like_profile(callback: CallbackQuery):

    sender = callback.from_user.id
    target_id = int(callback.data.split("_")[1])

    await db.add_like(sender, target_id)

    sender_profile = await db.get_user(sender)

    text = f"""
{sender_profile[1]}, {sender_profile[2]}
{sender_profile[3]}

{sender_profile[4]}

{sender_profile[8]}
"""

    if sender_profile[6]:

        await bot.send_photo(
            target_id,
            sender_profile[6],
            caption="🔥 Ваша анкета понравилась!\n\n" + text,
            reply_markup=match_kb(sender)
        )

    else:

        await bot.send_message(
            target_id,
            "🔥 Ваша анкета понравилась!\n\n" + text,
            reply_markup=match_kb(sender)
        )

    await callback.answer("❤️ Лайк отправлен")

    await show_next_profile(sender)


@dp.callback_query(F.data.startswith("skip_"))
async def skip_profile(callback: CallbackQuery):

    user_id = callback.from_user.id
    target_id = int(callback.data.split("_")[1])

    await db.add_skip(user_id, target_id)

    await callback.answer("Анкета пропущена")

    await show_next_profile(user_id)


@dp.callback_query(F.data.startswith("match_like_"))
async def match_like(callback: CallbackQuery):

    receiver = callback.from_user.id
    sender = int(callback.data.split("_")[2])

    await db.add_like(receiver, sender)

    if await db.check_match(receiver, sender):

        user1 = await bot.get_chat(receiver)
        user2 = await bot.get_chat(sender)

        link1 = f"https://t.me/{user1.username}"
        link2 = f"https://t.me/{user2.username}"

        await bot.send_message(sender, f"🎉 У вас взаимный лайк!\n{link1}")
        await bot.send_message(receiver, f"🎉 У вас взаимный лайк!\n{link2}")

    await callback.answer("❤️ Лайк отправлен")


@dp.callback_query(F.data == "match_skip")
async def match_skip(callback: CallbackQuery):

    await callback.answer("Анкета отклонена 👎")


async def main():

    await db.init_db()

    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
