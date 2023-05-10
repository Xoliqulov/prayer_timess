from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def repos_btn():
    public = InlineKeyboardButton("Public", callback_data='public')
    private = InlineKeyboardButton("Private", callback_data='private')
    btn = InlineKeyboardMarkup(inline_keyboard=[[public, private]])
    return btn
