from aiogram.dispatcher.filters.state import StatesGroup, State


class AddStory(StatesGroup):
    title = State()
    comment = State()


class EditStory(StatesGroup):
    title = State()
    comment = State()
