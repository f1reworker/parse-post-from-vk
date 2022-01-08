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
        db.child('errors').update({str(datetime.datetime.now()).replace(".", "-"): str(VKError(response['error']['error_msg']))})
        print(VKError(response['error']['error_msg']))

class Config:
    token = "ff84888cbc3d717524586b88f55e2373dd96e1e4f95ba0f2bdce1589ae6ad03c81dc97dd8d12230af0dbc"
    version = '5.131'


def call(method, **params):
    url = __prefix + method
    params = {k: __str(v) for k,v in params.items() if v != None}
    if Config.token:
        params['access_token'] = Config.token
    if Config.version:
        params['v'] = Config.version 
    request = requests.get(url, params=params)
    return request.json()





        
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

def getById(posts=None, extended=None, copy_history_depth=None, fields=None):
    """
    Returns a list of posts from user or community walls
    by their IDs.
    https://vk.com/dev/wall.getById
    """
    params = {
        'posts': posts,
        'extended': extended,
        'copy_history_depth': copy_history_depth,
        'fields': fields
    }
    result = call('wall.getById', **params)
    return parse_response(result)


def getComment(owner_id=None, comment_id=None, extended=None, fields = None):
    """
    Returns a list of comments on a post on a user wall
    or community wall.
    https://vk.com/dev/wall.getComment
    """
    params = {
        'owner_id': owner_id,
        'comment_id': comment_id,
        'extended': extended,
        'fields': fields
    }
    result = call('wall.getComment', **params)
    return parse_response(result)



async def checkKey(keywords, owner_id, post_id, text, typee):
    for word in keywords:
        if(word in text):           
            postAndGroup = str(abs(owner_id))+"_"+ str(post_id)
            url = "https://vk.com/wall-"+postAndGroup
            await senMessage(text=text, word=word, url=url, typee=typee)
            db.child("news").update({postAndGroup: {"keyword": word, "text": text[:1000], "url": url, "type": typee}})
            break



async def senMessage(text, word, url, typee):
    await bot.bot.send_message(1017900791, f'Новый {typee} с ключевым словом\nКлючевое слово: {word}\nСсылка на пост: {url}\nТекст:\n{text}')
    await bot.bot.send_message(2125738023, f'Новый {typee} с ключевым словом\nКлючевое слово: {word}\nСсылка на пост: {url}\nТекст:\n{text}')

async def getNews():

    while True:
        time.sleep(200)
        keywords = db.child("users").child(1017900791).child("keywords").get().val()[:-2].split(", ")
        groups = db.child("users").child(1017900791).child("groups").get().val()[:-2].split(", ")
        lastDate = db.child("news").child("lastDate").get().val()
        for group in groups:
            news = get(filters="post", source_ids=group, start_time=lastDate)["items"]
            postIds = []
            if news!=None:  db.child('groups').child(int(group)).update({"lastPost": news[00]['post_id']})
            for new in news:
                if new['date']>db.child("news").child("lastDate").get().val(): db.child("news").update({"lastDate": new['date']}) 
                await checkKey(keywords=keywords, owner_id=new['source_id'], post_id=new['post_id'], text=new['text'].lower(), typee="пост") 
                postIds.append(new['post_id'])
            if len(postIds)==1: postIds.append(db.child('groups').child(int(group)).child("lastPost").get().val())
            if len(postIds)>=2:
                for i in range(postIds[-1], postIds[0]):
                    time.sleep(3)
                    if i not in postIds:
                        comment = getComment(owner_id=int(group), comment_id=i)
                        if comment!=None:
                            comment = comment['items'][0]
                            if comment['date']>db.child("news").child("lastDate").get().val(): db.child("news").update({"lastDate": comment['date']})  
                            await checkKey(keywords=keywords, owner_id=comment['owner_id'], post_id=i, text=comment['text'].lower(), typee="комментарий")
                    
                
                
        
        


async def scheduler():
    await getNews()
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    asyncio.create_task(scheduler())

if __name__ == '__main__':
    executor.start_polling(bot, skip_updates=False, on_startup=on_startup)
