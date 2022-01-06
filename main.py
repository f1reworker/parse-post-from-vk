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


def getById(group_ids=None, group_id=None, fields=None):
    """
    Returns information about communities by their IDs.
    https://vk.com/dev/groups.getById
    """
    params = {
        'group_ids': group_ids,
        'group_id': group_id,
        'fields': fields
    }
    result = call('groups.getById', **params)
    return parse_response(result)

ff = getById(group_id='y_o_12')
print(ff)
        
def get(filters=None, return_banned=None, start_time=None, end_time=None,\
        max_photos=None, source_ids=None, start_from=None, count=None, fields=None,\
        from_=None, offset=None):
    """
    Returns data required to show newsfeed for the current
    user.
    https://vk.com/dev/newsfeed.get
    """
    params = {
        'filters': filters,
        'return_banned': return_banned,
        'start_time': start_time,
        'end_time': end_time,
        'max_photos': max_photos,
        'source_ids': source_ids,
        'start_from': start_from,
        'count': count,
        'fields': fields,
        'from_': from_,
        'offset': offset
    }
    result = call('newsfeed.get', **params)
    return parse_response(result)


async def senMessage(text, word, url):
    await bot.bot.send_message(1017900791, f'Новый пост с ключевым словом\nКлючевое слово: {word}\nСсылка на пост: {url}\nТекст:\n{text}')

async def getNews():

    while True:
        time.sleep(2)
        keywords = db.child("users").child(1017900791).child("keywords").get().val()[:-2].split(", ")
        groups = db.child("users").child(1017900791).child("groups").get().val()
        lastNews = db.child("news").child("lastNews").get().val()
        news = get(filters="post", source_ids=groups, start_from=lastNews)
        if news == None:
            time.sleep(600)
            continue
        if  "next_form" in list(news.keys()):
            db.child("news").update({"lastNews": news["next_from"]})
        newsList = news["items"]
        newsList.reverse()
        if newsList[-1]['date']>db.child("news").child("lastDate").get().val():
            for item in newsList:
                for word in keywords:
                    if(word in item["text"]):
                        if item["date"]>db.child("news").child("lastDate").get().val():
                            db.child("news").update({"lastDate": item["date"]})                  
                            postAndGroup = str(abs(item["source_id"]))+"_"+ str(item["post_id"])
                            url = "https://vk.com/wall-"+postAndGroup
                            await senMessage(text=item["text"], word=word, url=url)
                            db.child("news").update({postAndGroup: {"keyword": word, "text": item["text"][:2000], "url": url}})
                            break
        


async def scheduler():
    await getNews()
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    asyncio.create_task(scheduler())

# if __name__ == '__main__':
#     executor.start_polling(bot, skip_updates=False, on_startup=on_startup)
