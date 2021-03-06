import datetime
import time
import requests
import asyncio
from config import db, token, Config
import aiogram.utils.markdown as fmt
import aioschedule
from aiogram import Bot, Dispatcher, executor, types

bot = Dispatcher(token)

@bot.message_handler(commands="группа")
async def addGroup(message: types.Message):
    url = message.text.split("vk.com/")[-1]
    groupId = getById(group_id=url)
    if groupId==None:
        await message.answer('Что-то пошло не так, попробуйте позже или сообщите разработчику')
    
    elif type(groupId)==VKError:
        await message.answer('Что-то пошло не так, попробуйте позже или сообщите разработчику')
        await bot.bot.send_message(2125738023, groupId)
        await bot.bot.send_message(2125738023, message.text)
    else:
        try: 
            groups = db.child("users").child(message.from_user.id).child("groups").get().val()
            if groups == None: groups = ""
            groups+="-"+str(groupId[0]['id'])+", "
            db.child("users").child(message.from_user.id).update({'groups': groups})
        except:
            await message.answer('Что-то пошло не так, попробуйте позже или сообщите разработчику')
        else:
            await message.answer(f"Группа {message.text.split('/группа ')[-1]} добавлена",)


@bot.message_handler(commands="угруппа")
async def removeGroup(message: types.Message):
    url = message.text.split("vk.com/")[-1]
    groupId = getById(group_id=url)    
    if groupId==None:
        await message.answer('Что-то пошло не так, попробуйте позже или сообщите разработчику')
    elif type(groupId)==VKError:
        await message.answer('Что-то пошло не так, попробуйте позже или сообщите разработчику')
        await bot.bot.send_message(2125738023, groupId)
        await bot.bot.send_message(2125738023, message.text)
    else:
        try: 
            groups = db.child("users").child(message.from_user.id).child("groups").get().val()
            if groups == None: groups = ""
            rg = "-"+str(groupId[0]['id'])+","
            groups = groups.replace(rg, "")
            db.child("users").child(message.from_user.id).update({'groups': groups})
        except:
            await message.answer('Что-то пошло не так, попробуйте позже или сообщите разработчику')
        else:
            await message.answer(f"Группа {message.text.split('/угруппа ')[-1]} удалена")

@bot.message_handler(commands="слово")
async def addKeyword(message: types.Message):
    keywords = db.child("users").child(message.from_user.id).child("keywords").get().val()
    if keywords == None: keywords = ""
    newWord = message.text.lower().split("/слово ")[-1].replace("[", " ").replace("]", " ")
    db.child("users").child(message.from_user.id).update({'keywords': f"{keywords}{newWord}, "})
    nw = fmt.hbold(newWord)
    await message.answer(f'Слово {nw} добавлено', parse_mode=types.ParseMode.HTML)

@bot.message_handler(commands="услово")
async def addKeyword(message: types.Message):
    keywords = str(db.child("users").child(message.from_user.id).child("keywords").get().val())
    if keywords == None: keywords = ""
    newWord = message.text.lower().split("/услово ")[-1].replace("[", " ").replace("]", " ")+", "
    keywords = keywords.replace(newWord, '')
    db.child("users").child(message.from_user.id).update({'keywords': keywords})
    nw = fmt.hbold(newWord)
    await message.answer(f'Слово {nw} удалено',  parse_mode=types.ParseMode.HTML)

@bot.message_handler(commands="частота")
async def addKeyword(message: types.Message):
    timeout = int(message.text.split("/частота ")[-1])
    db.child("users").child(message.from_user.id).update({"timeout": timeout})
    await message.answer(f"Перерыв {timeout} секунд установлен")


@bot.message_handler(commands="start")
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Помощь", "Показать ключевые слова"]
    keyboard.add(*buttons)
    await message.answer("Приветствую", reply_markup=keyboard)

@bot.message_handler(lambda message: message.text=="Показать ключевые слова")
async def show(message: types.Message):
    await message.answer(db.child("users").child(message.from_user.id).get().val())   

@bot.message_handler(lambda message: message.text=="Помощь")
async def show(message: types.Message):
    timeout = db.child("users").child(message.from_user.id).child("timeout").get().val()
    await message.answer(f"Команды:\n\n/группа - добавить группу\nПример: /группа https://vk.com/palatavol12\
        \n\n/угруппа - удалить группу\nПример: /угруппа https://vk.com/palatavol12 \n\n/слово - добавить ключевое слово\
        \nПример: /слово ключевое слово\nАббревиатуры в квадратные скобки - [ск]\n\n/услово - удалить ключевое слово (все так же, как и с добавлением)\
        \n\n/частота - раз во сколько проверять новые записи,\nВаша частота - раз в {timeout} секунд.\nПример: /частота 3500\nВремя указывать в секундах", disable_web_page_preview=True)   

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
        return VKError(response['error']['error_msg'])


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
            await senMessage(text=text[:3000], word=word, url=url, typee=typee)
            db.child("news").update({postAndGroup: {"keyword": word, "text": text[:3000], "url": url, "type": typee}})
            break


async def senMessage(text, word, url, typee):
    await bot.bot.send_message(1017900791, f'Новый {typee} с ключевым словом\nКлючевое слово: {word}\nСсылка на пост: {url}\nТекст:\n{text}')

async def getNews():

    while True:
        timeout = db.child("users").child(1017900791).child("timeout").get().val()
        await asyncio.sleep(timeout)
        keywords = db.child("users").child(1017900791).child("keywords").get().val()[:-2].split(", ")
        groups = db.child("users").child(1017900791).child("groups").get().val()[:-2].split(", ")
        
        
        for group in groups:
            lastDate = db.child('groups').child(int(group)).child("lastDate").get().val()
            lastPost = db.child('groups').child(int(group)).child("lastPost").get().val()
            news = get(filters="post", source_ids=group, start_time=lastDate)["items"]

            if type(news)==VKError:
                await bot.bot.send_message(2125738023, news)
                await asyncio.sleep(100)
                continue

            postIds = []
         
            if news!=None and news!=[]:  
                db.child('groups').child(int(group)).update({"lastPost": news[0]['post_id']})
                db.child('groups').child(int(group)).update({"lastDate": news[0]['date']+1}) 
            for new in news:
                await checkKey(keywords=keywords, owner_id=new['source_id'], post_id=new['post_id'], text=new['text'].lower(), typee="📝 пост") 
                postIds.append(new['post_id'])
            postIds.append(lastPost)
            if len(postIds)>=2:
                for i in range(postIds[-1], postIds[0]):
                    await asyncio.sleep(3)
                    if i not in postIds:
                        comment = getComment(owner_id=int(group), comment_id=i)
                        if type(comment)==VKError:
                            if comment.args[0]!="Access denied: post was not found check post_id param" and comment.args[0]!="Access denied: post was deleted": 
                                await bot.bot.send_message(2125738023, comment)
                                await asyncio.sleep(100)
                            continue
                        if comment!=None:
                            comment = comment['items'][0] 
                            try:
                                if comment['text']!='':
                                    await checkKey(keywords=keywords, owner_id=comment['owner_id'], post_id=i, text=comment['text'].lower(), typee="💬 комментарий")
                            except:
                                await bot.bot.send_message(2125738023, f"Ошибка {comment}") 
                
                
        
        


async def on_startup(x):
    asyncio.create_task(getNews())

if __name__ == '__main__':
    executor.start_polling(bot, skip_updates=False, on_startup=on_startup)
