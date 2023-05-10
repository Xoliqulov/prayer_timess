import os
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup

from buttons.inline_btn import repos_btn
from buttons.reply_btn import welcome_btn
from db_data.database import create_table, get_user, cur, con, get_all_stories, get_my_stories
from state.states import AddStory, EditStory

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv('TOKEN')
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

info = dict()


@dp.message_handler(commands=['start'])
async def welcome_page(msg: types.Message):
    await bot.set_my_commands([BotCommand('start', "Restart Bot!"), BotCommand('help', "Get help!")])
    if not get_user(str(msg.from_user.id)):
        query = 'insert into users(user_id, name, username) values (%s, %s, %s)'
        cur.execute(query, (str(msg.from_user.id), msg.from_user.first_name, msg.from_user.username))
        con.commit()
    await msg.answer(text='Botga Xush kelibsiz!', reply_markup=welcome_btn())


@dp.message_handler(Text("🗂 Stories"))
async def all_stories(msg: types.Message):
    stories = get_all_stories()
    n = 1  # noqa
    if stories and len(stories) > 1:
        end = InlineKeyboardButton('🔙', callback_data=f'back_{len(stories) if n == 1 else n - 1}')  # noqa
        work = InlineKeyboardButton('📖', callback_data=f'work_{n}')
        next = InlineKeyboardButton('🔜', callback_data=f'next_{1 if n == len(stories) else n + 1}')  # noqa
        btn = InlineKeyboardMarkup(inline_keyboard=[[end, work, next]])
        await msg.answer(text=f"Author: {stories[n - 1][2]}\n\nTitle: {stories[n - 1][3]}\n\nTime: {stories[n - 1][6]}",
                         reply_markup=btn)
    elif stories and len(stories) == 1:
        await msg.answer(text=f"Author: {stories[n - 1][2]}\n\nTitle: {stories[n - 1][3]}\n\nStory: "
                              f"{stories[n - 1][4]}\n\nTime: {stories[n - 1][6]}")
    else:
        await msg.answer(text='Hozircha Storylar mavjud emas!')


@dp.callback_query_handler(lambda callback: callback.data.split('_')[0] in ['back', 'work', 'next'])
async def callback_handler(callback: types.CallbackQuery):
    stories = get_all_stories()
    n = 1
    text = callback.data.split('_')
    if text[0] == 'back':
        n = int(text[1])
    elif text[0] == 'work':
        await callback.message.delete()
        index = int(callback.data.split('_')[1])
        await bot.send_message(callback.from_user.id,
                               text=f"Author: {stories[index - 1][2]}\n\nTitle: {stories[index - 1][3]}\n\nStory: "
                                    f"{stories[index - 1][4]}\n\nTime: {stories[index - 1][6]}")
        return
    elif text[0] == 'next':
        n = int(text[1])
    end = InlineKeyboardButton('🔙', callback_data=f'back_{len(stories) if n == 1 else n - 1}')  # noqa
    work = InlineKeyboardButton('📖', callback_data=f'work_{n}')
    next = InlineKeyboardButton('🔜', callback_data=f'next_{1 if n == len(stories) else n + 1}')  # noqa
    btn = InlineKeyboardMarkup(inline_keyboard=[[end, work, next]])
    await bot.edit_message_text(
        f"Author: {stories[n - 1][2]}\n\nTitle: {stories[n - 1][3]}\n\nTime: {stories[n - 1][6]}",
        callback.from_user.id,
        callback.message.message_id,
        reply_markup=btn)
    await callback.answer(str(n))


@dp.message_handler(Text('📓 My Stories'))
async def my_stories(msg: types.Message):
    stories = get_my_stories(str(msg.from_user.id))  # noqa
    n = 1  # noqa
    if stories and len(stories) > 1:
        end = InlineKeyboardButton('🔙', callback_data=f'back.{len(stories) if n == 1 else n - 1}')
        work = InlineKeyboardButton('📖', callback_data=f'work.{n}')
        delete = InlineKeyboardButton('❌', callback_data=f'delete.{stories[n - 1][0]}')
        edit = InlineKeyboardButton('📝', callback_data=f'edit.{stories[n - 1][0]}')
        next = InlineKeyboardButton('🔜', callback_data=f'next.{1 if n == len(stories) else n + 1}')  # noqa
        btn = InlineKeyboardMarkup(inline_keyboard=[[end, work, next], [edit, delete]])
        await msg.answer(text=f"Author: {stories[n - 1][2]}\n\nTitle: {stories[n - 1][3]}\n\nTime: {stories[n - 1][6]}",
                         reply_markup=btn)
    elif stories and len(stories) == 1:
        delete = InlineKeyboardButton('❌', callback_data=f'delete.{stories[n - 1][0]}')
        edit = InlineKeyboardButton('📝', callback_data=f'edit.{stories[n - 1][0]}')
        btn = InlineKeyboardMarkup(inline_keyboard=[[edit, delete]])
        await msg.answer(text=f"Author: {stories[n - 1][2]}\n\nTitle: {stories[n - 1][3]}\n\nStory: "
                              f"{stories[n - 1][4]}\n\nTime: {stories[n - 1][6]}",
                         reply_markup=btn)
    else:
        await msg.answer(text='Hozircha Storylar mavjud emas!')


@dp.callback_query_handler(lambda msg: msg.data.split('.')[0] in ['back', 'work', 'next', 'delete', 'edit'])
async def callback_handler_story(callback: types.CallbackQuery, state: FSMContext):
    stories = get_my_stories(str(callback.from_user.id))
    n = 1
    text = callback.data.split('.')
    if text[0] == 'back':
        n = int(text[1])
    elif text[0] == 'work':
        await callback.message.delete()
        await bot.send_message(callback.from_user.id,
                               text=f"Author: {stories[int(text[1]) - 1][2]}\n\nTitle: {stories[int(text[1]) - 1][3]}\n\nStory: "  # noqa
                                    f"{stories[int(text[1]) - 1][4]}\n\nTime: {stories[int(text[1]) - 1][6]}")
        return
    elif text[0] == 'delete':
        query = 'delete from stores where id = %s'
        cur.execute(query, (int(text[1]),))
        con.commit()
        await callback.message.delete()
        await bot.send_message(callback.from_user.id, text="Story muvaffaqiyatli o'chirildi!")
        return
    elif text[0] == 'edit':
        await callback.message.delete()
        await bot.send_message(callback.from_user.id,
                               text=f"{callback.from_user.first_name} Tahrirlash oynasiga xush kelibsiz!")
        async with state.proxy() as data:
            data['id'] = text[1]
        await EditStory.title.set()
        await bot.send_message(callback.from_user.id,
                               text="Stores sarlavhasini kiriting: ")
        return
    elif text[0] == 'next':
        n = int(text[1])
    end = InlineKeyboardButton('🔙', callback_data=f'back.{len(stories) if n == 1 else n - 1}')  # noqa
    work = InlineKeyboardButton('📖', callback_data=f'work.{n}')
    next = InlineKeyboardButton('🔜', callback_data=f'next.{1 if n == len(stories) else n + 1}')  # noqa
    delete = InlineKeyboardButton('❌', callback_data=f'delete.{stories[n - 1][0]}')
    edit = InlineKeyboardButton('📝', callback_data=f'edit.{stories[n - 1][0]}')
    btn = InlineKeyboardMarkup(inline_keyboard=[[end, work, next], [edit, delete]])
    await bot.edit_message_text(
        f"Author: {stories[n - 1][2]}\n\nTitle: {stories[n - 1][3]}\n\nTime: {stories[n - 1][6]}",
        callback.from_user.id,
        callback.message.message_id,
        reply_markup=btn)
    await callback.answer(str(n))


@dp.message_handler(state=EditStory.title)
async def edit_story(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = msg.text
    await EditStory.comment.set()
    await msg.answer(text="Stores matnini kiriting: ")


@dp.message_handler(state=EditStory.comment)
async def edit_comment(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['summary'] = msg.text
        query = 'UPDATE stores SET story_title = %s, story = %s WHERE id = %s'
        cur.execute(query, (data['title'], data['summary'], int(data['id'])))
        con.commit()
    await msg.answer(text="Tahrirlash saqlandi!")
    await state.finish()


@dp.message_handler(Text('✍️ Add Story'))
async def add_story_handler(msg: types.Message):
    await AddStory.title.set()
    await msg.answer(text="Stores sarlavhasini kiriting: ")


@dp.message_handler(state=AddStory.title)
async def add_story_title(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["title"] = msg.text
    await AddStory.comment.set()
    await msg.answer(text="Stores matnini kiriting: ")


@dp.message_handler(state=AddStory.comment)
async def add_story_comment(msg: types.Message, state: FSMContext):
    global info
    async with state.proxy() as data:
        data["summary"] = msg.text
        info = data
    await state.finish()
    await msg.answer("Siz yozgan Story holatini belgilang!", reply_markup=repos_btn())


@dp.callback_query_handler(lambda msg: msg.data in ['public', 'private'])
async def private_handler(callback: types.CallbackQuery):
    bools = True
    if callback.data == 'public':
        bools = True
    elif callback.data == 'private':
        bools = False
    query = 'insert into stores(author_id, author_name, story_title, story, public) values (%s, %s, %s, %s, %s)'
    cur.execute(query,
                (str(callback.from_user.id), callback.from_user.first_name, info['title'], info['summary'], bools))
    con.commit()
    await callback.message.delete()
    await bot.send_message(callback.from_user.id, text="Sizning yozgan Story qabul qilindi!")


async def on_startup(dp):
    create_table()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
