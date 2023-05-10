from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def welcome_btn():
    btn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=3)
    btn.add(KeyboardButton("🗂 Stories"), KeyboardButton('📓 My Stories'), KeyboardButton('✍️ Add Story'))
    return btn
