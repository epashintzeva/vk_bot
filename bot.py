import requests
import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api import VkUpload
from PIL import Image
from urllib.request import urlopen

Set = {"art_gallery" , "cafe" , "museum" , "park" , "restaurant" , "конкретное место" , "места рядом" , "привет" , "маршрут"}
Num = {'0','1','2','3','4','5','6','7','8','9'}

def html_to_text(s):
    ds = ''
    fl=True
    for i in range(len(s)):
        if s[i]=='<':
            fl=False
        elif s[i]=='>':
            fl = True
            continue
        if fl:
            ds+=s[i]
    return ds

def splt(s):
    num = ''
    st = ''
    for i in range(len(s)):
        if s[i] in Num :
            num += s[i]
        elif s[i]!=' ':
            st += s[i]
    return st, num

def massage_photo(s_url, message):
    attachments = []
    upload = VkUpload(vk_session)
    image_url = s_url
    image = session.get(image_url, stream=True)
    photo = upload.photo_messages(photos=image.raw)[0]
    attachments.append(
        'photo{}_{}'.format(photo['owner_id'], photo['id'])
    )
    vk.messages.send( user_id=event.user_id, attachment=','.join(attachments), message= message, random_id=0)

def nearbysearch_type(s0, r):
    s = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=55.9495800,37.5018300&radius=' + r + '&type='+ s0 + '&key=AIzaSyADGsGU8emVpO5QLlfZY5XnvYHh5B02Mi4&language=ru'
    place = requests.get(s)
    place_parse = json.loads(place.text)
    try:
        t = 0
        for i in place_parse['results']:
            if t>=3:
                break
            message = i['name']+'\n'+i['vicinity']+'\n'+str(i['rating'])
            massage_photo("https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference="+i["photos"][0]["photo_reference"]+"&key=AIzaSyADGsGU8emVpO5QLlfZY5XnvYHh5B02Mi4", message)
            print()
            t+=1
    except KeyError:
        print('нет информации')

def roads(s0): #place_id
    s = 'https://maps.googleapis.com/maps/api/directions/json?origin=55.9495800,37.5018300&destination=place_id:'+ s0 +'&key=AIzaSyADGsGU8emVpO5QLlfZY5XnvYHh5B02Mi4&language=ru'
    place = requests.get(s)
    place_parse = json.loads(place.text)
    message=''
    for i in place_parse['routes']:
        for k in i['legs']:
            for j in k['steps']:
                message+= html_to_text(j["html_instructions"])+'\n'
    return message

def Find_place(s0):
    s = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?key=AIzaSyADGsGU8emVpO5QLlfZY5XnvYHh5B02Mi4&input=" + s0 + "&inputtype=textquery&language=ru&fields=formatted_address,geometry,icon,name,permanently_closed,photos,place_id,plus_code,types"
    place = requests.get(s)
    place_parse = json.loads(place.text)
    try:
        if place_parse["status"]=="ZERO_RESULTS":
            vk.messages.send(user_id=event.user_id, message='К сожалению, мы ничего не знаем об этом месте', random_id=0)
        else:
            for i in place_parse["candidates"]:
                message = i['name'] + '\n' + i['formatted_address']
                massage_photo("https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=" + i["photos"][0][
                    "photo_reference"] + "&key=AIzaSyADGsGU8emVpO5QLlfZY5XnvYHh5B02Mi4", message)
                vk.messages.send(user_id=event.user_id, message=roads(i['place_id']), random_id=0)
    except KeyError:
        print("Попробуйте пойти в другое место)")

"""def create_keyboard(response):
    keyboard = VkKeyboard(one_time=True)

    if response == 'Куда собираетесь?':

        keyboard.add_button('Конкретное место', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Место рядом', color=VkKeyboardColor.POSITIVE)

    elif response == 'привет':
        keyboard.add_button('Тест', color=VkKeyboardColor.POSITIVE)

    elif response == 'котики':
        keyboard.add_button('Котики!', color=VkKeyboardColor.POSITIVE)

    elif response == 'закрыть':
        print('закрываем клаву')
        return keyboard.get_empty_keyboard()

    keyboard = keyboard.get_keyboard()
    return keyboard"""

session = requests.Session()
vk_session = vk_api.VkApi(token='44afd0f665c16a98fe9178b549b7253e8a693f9caa63dd28a8b44a8539d78250aac0d2e46d022851bac90')
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
       # response = event.text.lower()
       # keyboard = create_keyboard(response)

        if event.text.lower() == 'конкретное место' :
            vk.messages.send(user_id=event.user_id, message='Какое конкретно место?', random_id=0)
        elif event.text.lower() == 'места рядом' :
            vk.messages.send(user_id=event.user_id, message='Введите тип места, из предложенного ниже и радиус окрестности для поиска \n "art_gallery" , "cafe" , "museum" , "park" , "restaurant"  ', random_id=0)
        elif event.text.lower() == 'привет' :
            vk.messages.send(user_id=event.user_id, message='Куда собираетесь?', random_id=0)
        elif event.text.lower() not in Set and event.text.lower()[-1] not in Num:
            Find_place(event.text.lower())
        elif event.text.lower() not in Set and event.text.lower()[-1] in Num:
            type_ , r = splt(event.text.lower())
            nearbysearch_type(type_, str(r))
        else:
            vk.messages.send(user_id=event.user_id, message='Я таких слов не знаю', random_id=0)

