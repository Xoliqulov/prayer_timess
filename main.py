import os
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup
from db_data.database import create_table, messages, write_users, check_id, write_msg
import json
import requests

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv('TOKEN')
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class BigState(StatesGroup):
    search = State()


class text(StatesGroup):
    search = State()


@dp.message_handler(commands=["start"])
async def start_handler(msg: types.Message):
    btn = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Qu'rondan sura va oyatlar ☪️")
    button2 = types.KeyboardButton("Namoz vaqtlari ⏰")
    button4 = types.KeyboardButton("admin 👤")
    btn.row(button1),
    btn.row(button2),
    btn.add(button4)
    rows = check_id()
    if (str(msg.from_user.id),) not in rows:
        write_users(msg.from_user.id, msg.from_user.first_name, msg.from_user.username)
        await msg.answer(f"Assalomu alaykum !! {msg.from_user.first_name} 👋 ", reply_markup=btn)
    else:
        await msg.answer(f"Hush kelibsiz {msg.from_user.first_name} 👋", reply_markup=btn)


@dp.message_handler(Text("Qu'rondan sura va oyatlar ☪️"))
async def process_callback_quran(message: types.Message, state=FSMContext):
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Qu'ron karim yuklab olish pdf 📥", )
    button1 = types.KeyboardButton("Muhammad Sodiq Muhammad Yusuf tarjimalari", )
    button_back = types.KeyboardButton("❌")
    reply_markup.row(button1)
    reply_markup.row(button)
    reply_markup.row(button_back)
    if message.text == "❌":
        await state.finish()
        await message.answer(text="⏪", reply_markup=reply_markup)
        return
    await message.answer("Qu'ron karimni pdf varyantda yuklab olishingiz yoki Sura va oyatlarni qidirishingiz mumkin 👇",
                         reply_markup=reply_markup)


@dp.message_handler(lambda message: message.text == "Muhammad Sodiq Muhammad Yusuf tarjimalari")
async def process_callback_quran(message: types.Message, state: FSMContext):
    with open('data.txt', 'r') as f:
        data = f.read()
    back = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    back.add(types.KeyboardButton("❌"))
    await BigState.search.set()
    await message.answer(f"{data}\nQu'ronda 114ta sura nozil bo'lgan sizga aynan qaysi sura kerak",
                         reply_markup=back)  # noqa


@dp.message_handler(state=BigState.search)
async def search_state(msg: types.Message, state: FSMContext):
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton("❌")
    reply_markup.row(button_back)
    if msg.text == "❌":
        await state.finish()
        await msg.answer(text="⏪", reply_markup=reply_markup)
        return
    with open('data.json', 'r') as f:
        data = json.load(f)
    c = msg.text.split(':')
    if msg.text.isdigit() or ":" in msg.text:
        if len(c) == 2 and int(c[0]) <= 114 and int(c[0]) > 0:
            ur1_oyat = f'https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/uzb-muhammadsodikmu/{c[0]}.json'
            r = requests.get(ur1_oyat)
            res = r.json()
            co = 0
            for i in res['chapter']:
                co += 1
            if c[0].isdigit() and c[1].isdigit() and int(c[0]) > 0 and int(c[1]) > 0:
                if int(c[0]) <= 114 and int(c[1]) <= co and int(c[0]) >= 0:
                    await msg.answer(f"qidiruvingiz 👇 😊", reply_markup=reply_markup)
                    ur1_oyat = f'https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/uzb-muhammadsodikmu/{c[0]}/{c[1]}.json'
                    r = requests.get(ur1_oyat)
                    res = r.json()
                    await msg.answer(
                        f"Qu'ronda {data[c[0]]} - surasining \n{c[1]} - oyatida shunday keltirilgan 👇\n-{res['text']}")
                else:
                    await msg.answer(f"{data[c[0]]} surasida {co} ta oyat mavjud")
            else:
                await msg.answer(f" {data[c[0]]} surasida {co} ta oyat mavjud")
        elif len(c) == 1 and int(c[0]) <= 114 and int(c[0]) > 0:
            await msg.answer(
                f"{data[c[0]]} surasi agar shu suraning oyatini qidirmoqchi bo'lsangiz \n{c[0]}:2 shu tarizda qidirishing mumkun \nya'ni qidiruvingizda {data[c[0]]} suraning 2-oyati chiqadi")
        else:
            await msg.answer(
                "114 ta sura bor 1-Al-Faatiha surasi va 114-An-Naas surasi iltimos boshqattan qidiruv bering !!")
    else:
        await msg.answer('Suralarni raqami orqali topishingiz mumkin ')


@dp.message_handler(lambda message: message.text == "Qu'ron karim yuklab olish pdf 📥")
async def send_pdf(message: types.Message):
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton("❌")
    reply_markup.row(button_back)
    await message.answer('So''rovingiz jonatilmoqda 🚀', reply_markup=reply_markup)
    with open('quron_.pdf', 'rb') as f:
        await bot.send_document(message.chat.id, document=f, caption='Bu pdf sizga manzur boladi degan umiddaman')


@dp.message_handler(lambda message: message.text == "Namoz vaqtlari ⏰")
async def process_callback_namoz(message: types.Message, state=FSMContext):
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Tashkent namoz vaqti ⏰")
    button2 = types.KeyboardButton("Samarqand namoz vaqti ⏰")
    button = types.KeyboardButton("❌")
    reply_markup.row(button2, button1)
    reply_markup.add(button)
    if message.text == "❌":
        await state.finish()
        await message.answer(text="Bosh menu!", reply_markup=reply_markup)
        return
    await message.answer(
        'Hozircha bizda 2 ta viloyat uchun namoz vaqtlari mavjud tez kunlarda boshqa viloyatlar ham qoshilad',
        reply_markup=reply_markup)


@dp.message_handler(lambda message: message.text == "admin 👤")
async def process_callback_namoz(message: types.Message, state=FSMContext):
    if str(message.from_user.id) in '1239693654':
        reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button1 = types.KeyboardButton("Foydalanuvchilar soni 👥")
        button2 = types.KeyboardButton("Takliflar 💬")
        button = types.KeyboardButton("❌")
        reply_markup.row(button1)
        reply_markup.row(button2)
        reply_markup.add(button)
        await message.answer("Hush kelibsiz admin 👋", reply_markup=reply_markup)
    else:
        btn = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button = types.KeyboardButton('Taklif va kamchiliklar jo''natish 📝')
        button1 = types.KeyboardButton("❌")
        btn.row(button)
        btn.row(button1)
        await message.answer("Adminga murojat qilishingiz mumkin 👇", reply_markup=btn)


@dp.message_handler(lambda message: message.text == "Tashkent namoz vaqti ⏰")
async def process_callback_back(message: types.Message):
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton("❌")
    reply_markup.row(button_back)
    url = "https://api.aladhan.com/v1/timingsByCity"
    params = {
        "city": "Tashkent",
        "country": "Uzbekistan",
        "method": 1,
        "school": 1,
        "apikey": "65715a43e9msh079965c003f00fbp110f95jsnb0acac670087",
    }

    response = requests.get(url, params=params)

    data = response.json()["data"]
    timings = data["timings"]
    sana = data['date']['readable']
    oy = data['date']['hijri']['month']['en']
    lac = data['meta']['timezone']
    bugun = f"{sana} yil \n{oy}: oyining namoz vaqtlari 📅 :"
    sahar = f"⏰ Sahar vaqti : {timings['Fajr']}"
    quyosh = f"⏰ Quyosh vaqti : {timings['Sunrise']}"
    peshin = f"⏰ Peshin vaqti : {timings['Dhuhr']}"
    asr = f"⏰ Asr vaqti : {timings['Asr']}"
    shom = f"⏰ Shom vaqti : {timings['Maghrib']}"
    xufton = f"⏰ Xufton vaqti : {timings['Isha']}"
    await message.answer(f"{lac} shahri 🌍\n{bugun}\n{sahar}\n{quyosh}\n{peshin}\n{asr}\n{shom}\n{xufton}\n",
                         reply_markup=reply_markup)


@dp.message_handler(lambda message: message.text == "Foydalanuvchilar soni 👥")
async def process_callback_back(message: types.Message):
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton("❌")
    reply_markup.row(button_back)
    rows = check_id()
    await message.answer(f"Botdan faydalanganlar soni {len(rows)} taga yetgan", reply_markup=reply_markup)


@dp.message_handler(lambda message: message.text == "Takliflar 💬")
async def process_callback_back(message: types.Message):
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton("❌")
    reply_markup.row(button_back)
    rows = messages()
    for i in rows:
        await message.answer(f"@{i[0]} tomonidan sizga habar bor\nXabar shundan iborat: 👇\n{i[1]}",
                             reply_markup=reply_markup)


@dp.message_handler(lambda message: message.text == 'Taklif va kamchiliklar jo''natish 📝')
async def process_callback_back(message: types.Message):
    await message.answer("Xabaringizni yozib qoldiring 📝")
    await text.search.set()


@dp.message_handler(state=text.search)
async def search_state(message: types.Message, state: FSMContext):
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton("❌")
    reply_markup.row(button_back)
    message.text.replace(":", '')
    message.text.replace(";", '')
    message.text.replace("'", '')
    if message.text == "❌":
        await state.finish()
        await message.answer(text="⏪", reply_markup=reply_markup)
        return
    write_msg(message.from_user.id, message.from_user.username, message.text)
    await message.answer("Xabaringiz jonatildi 🚀", reply_markup=reply_markup)


@dp.message_handler(lambda message: message.text == "Samarqand namoz vaqti ⏰")
async def process_callback_back(message: types.Message):
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton("❌")
    reply_markup.row(button_back)
    url = "https://api.aladhan.com/v1/timingsByCity"
    params = {
        "city": "Samarqand",
        "country": "Uzbekistan",
        "method": 1,
        "school": 1,
        "apikey": "65715a43e9msh079965c003f00fbp110f95jsnb0acac670087",
    }

    response = requests.get(url, params=params)

    data = response.json()["data"]
    timings = data["timings"]
    sana = data['date']['readable']
    oy = data['date']['hijri']['month']['en']
    lac = data['meta']['timezone']
    bugun = f"{sana}\n{oy}: oyining namoz vaqtlari 📅 :"
    sahar = f"⏰ Sahar vaqti : {timings['Fajr']}"
    quyosh = f"⏰ Quyosh vaqti : {timings['Sunrise']}"
    peshin = f"⏰ Peshin vaqti : {timings['Dhuhr']}"
    asr = f"⏰ Asr vaqti : {timings['Asr']}"
    shom = f"⏰ Shom vaqti : {timings['Maghrib']}"
    xufton = f"⏰ Xufton vaqti : {timings['Isha']}"
    await message.answer(f"{lac} shahri 🌍\n{bugun}\n{sahar}\n{quyosh}\n{peshin}\n{asr}\n{shom}\n{xufton}\n",
                         reply_markup=reply_markup)


@dp.message_handler(lambda message: message.text == '❌')
async def check_number(message: types.Message):
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Qu'rondan sura va oyatlar ☪️")
    button2 = types.KeyboardButton("Namoz vaqtlari ⏰")
    button4 = types.KeyboardButton("admin 👤 ")
    reply_markup.row(button1),
    reply_markup.row(button2),
    reply_markup.add(button4)

    await message.answer(
        "⏪ orqaga qaytingiz ",
        reply_markup=reply_markup)


@dp.message_handler()
async def check_number(message: types.Message):
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Qu'rondan sura va oyatlar ☪️")
    button2 = types.KeyboardButton("Namoz vaqtlari ⏰")
    button4 = types.KeyboardButton("admin 👤 ")
    reply_markup.row(button1),
    reply_markup.row(button2),
    reply_markup.add(button4)

    await message.answer(
        "Sizning qidiruvingizga tushunmadim 😐 kamchilik va takliflarizni adminga yo'lashingiz mukin 👇",
        reply_markup=reply_markup)


async def on_startup(dp):
    create_table()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
