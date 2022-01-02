import datetime
import time
import vk_api
import requests
import pyrebase
import asyncio
from aiogram.types.message import ParseMode
from config import db
import config
from config import keywords
import aiogram.utils.markdown as fmt
import aioschedule
from aiogram import Bot, Dispatcher, executor, types

token = Bot(token="2057472245:AAHXiB2teJOWQa7CXwH0uLd8cJItn4YvD4A")
bot = Dispatcher(token)
@bot.message_handler(commands="start")
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Добавить ключевые слова", "Удалить ключевые слова", "Показать ключевые слова", "Закончить ввод"]
    keyboard.add(*buttons)
    db.child("users").update({message.from_user.id: ""})
    await message.answer("Приветствую", reply_markup=keyboard)

@bot.message_handler(lambda message: message.text=="Добавить ключевые слова")
async def add(message: types.Message):
    config.flag = "add"
    await message.answer("Введите ключевые слова, которые хотите добавить.")

@bot.message_handler(lambda message: message.text=="Удалить ключевые слова")
async def remove(message: types.Message):
    config.flag = "remove"
    await message.answer("Введите ключевые слова, которые хотите удалить.")

@bot.message_handler(lambda message: message.text=="Закончить ввод")
async def stop(message: types.Message):
    config.flag = ""
    await message.answer("Ввод закончен.")

@bot.message_handler(lambda message: message.text=="Показать ключевые слова")
async def show(message: types.Message):
    await message.answer(db.child("users").child(message.from_user.id).get().val())   

@bot.message_handler(lambda message: message.text != "Добавить ключевые слова" and message.text != "Удалить ключевые слова" and message.text !=  "Показать ключевые слова" and message.text !=  "Закончить ввод")
async def words(message: types.Message):
    if config.flag == "add":
        keywords = db.child("users").child(message.from_user.id).get().val()
        db.child("users").update({message.from_user.id: f"{keywords}{message.text.lower()}, "})
    if config.flag == "remove":
        keywords = db.child("users").child(message.from_user.id).get().val().replace(message.text.lower()+ ", ", "")
        db.child("users").update({message.from_user.id: keywords})


__prefix = 'https://api.vk.com/method/'

def __str(obj):
    if isinstance(obj, list or tuple):
        str_values = (str(val) for val in obj)
        return (',').join(str_values)
    return str(obj)

class VKError(Exception):
    pass

def parse_response(response):
    try:
        return response['response']
    except KeyError:
        print(VKError(response['error']['error_msg']))

class Config:
    token = "ff84888cbc3d717524586b88f55e2373dd96e1e4f95ba0f2bdce1589ae6ad03c81dc97dd8d12230af0dbc"
    version = '5.81'


def call(method, **params):
    url = __prefix + method
    params = {k: __str(v) for k,v in params.items() if v != None}
    if Config.token:
        params['access_token'] = Config.token
    if Config.version:
        params['v'] = Config.version 
    request = requests.get(url, params=params)
    return request.json()

def search(q=None, extended=None, count=None, latitude=None, longitude=None,\
           start_time=None, end_time=None, start_from=None, fields=None,\
           start_id=None, offset=None):
    """
    Returns search results by statuses. 
    https://vk.com/dev/newsfeed.search
    """
    params = {
        'q': q,
        'extended': extended,
        'count': count,
        'latitude': latitude,
        'longitude': longitude,
        'start_time': start_time,
        'end_time': end_time,
        'start_from': start_from,
        'fields': fields,
        'start_id': start_id,
        'offset': offset
    }
    result = call('newsfeed.search', **params)
    return parse_response(result)

def getNews():
    myTime = time.mktime((datetime.datetime.now()+datetime.timedelta(hours=2)).timetuple())
    users = db.child("users").get().val().keys()
    for user in users:
        userKeywords = db.child("users").child(user).get().val().split(", ")[:-1]
        for keyword in userKeywords:
            news = search(q = keyword, count = 200, extended=1, start_time=myTime)
            if db.child("news").child("user").get().val()==None:   length = 0
            else: length = len(db.child("news").child("user").get().val())
            db.child("news").child(user).update({length: news['items']})
            print(news)
        


async def scheduler():
    aioschedule.every(1).hours.do(getNews)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    asyncio.create_task(scheduler())

if __name__ == '__main__':
    executor.start_polling(bot, skip_updates=False, on_startup=on_startup)
