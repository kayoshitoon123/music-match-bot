from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):

    name = State()
    age = State()
    city = State()

    role = State()
    looking = State()

    photo = State()
    beat = State()

    description = State()