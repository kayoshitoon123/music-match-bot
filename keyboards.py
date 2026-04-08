from aiogram.types import *


role_kb = ReplyKeyboardMarkup(

keyboard=[

[KeyboardButton(text="🎧 Битмейкер")],
[KeyboardButton(text="🎚 Звукарь")],
[KeyboardButton(text="🎤 Артист")]

],

resize_keyboard=True

)


search_role_kb = ReplyKeyboardMarkup(

keyboard=[

[KeyboardButton(text="🎧 Битмейкера")],
[KeyboardButton(text="🎚 Звукаря")],
[KeyboardButton(text="🎤 Артиста")],
[KeyboardButton(text="🎵 Все равно")]

],

resize_keyboard=True

)


skip_kb = ReplyKeyboardMarkup(

keyboard=[

[KeyboardButton(text="Пропустить")]

],

resize_keyboard=True

)


menu_kb = ReplyKeyboardMarkup(

keyboard=[

[KeyboardButton(text="🔎 Начать поиск")],
[KeyboardButton(text="✏️ Изменить анкету")]

],

resize_keyboard=True

)


def like_kb(user_id):

    return InlineKeyboardMarkup(

    inline_keyboard=[

    [
    InlineKeyboardButton(text="❤️",callback_data=f"like_{user_id}"),
    InlineKeyboardButton(text="👎",callback_data=f"skip_{user_id}")
    ]

    ]

)