import requests
import collections
import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api import VkUpload
from PIL import Image
from urllib.request import urlopen

Set0 = {"конкретное место" , "места рядом" , "привет" , "маршрут" , "Введите свое местоположение?"}
set_t= {"art_gallery" , "cafe" , "museum" , "park" , "restaurant" }
Num = {'0','1','2','3','4','5','6','7','8','9'}

def location(s0):
    """очищает строки от ненужных для данного проекта html-символов, вход/выход-строка"""
    s = "https://maps.googleapis.com/maps/api/geocode/json?address=" + s0 + "&key=AIzaSyADGsGU8emVpO5QLlfZY5XnvYHh5B02Mi4"
    place = requests.get(s)
    place_parse = json.loads(place.text)
    lat = str(place_parse["results"][0]["geometry"]["location"]["lat"])
    lng = str(place_parse["results"][0]["geometry"]["location"]["lng"])
    return lat, lng

def html_to_text(s):
    import re
    s = re.sub('<br', '\n<', s)
    s = re.sub('<div', '\n<', s)
    ds = re.sub('<[^>]*>', '', s)
    # ds = []
    # fl=True
    # for i in range(len(s)):
    #     if s[i]=='<':
    #         fl=False
    #     elif s[i]=='>':
    #         fl = True
    #         continue
    #     if fl:
    #         ds.append(s[i])
    # ds = ''.join(ds)

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

def nearbysearch_type(s0, r, uid):
    c1, c2 = users[uid]
    s = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+c1+','+c2+'&radius=' + r + '&type='+ s0 + '&key=AIzaSyADGsGU8emVpO5QLlfZY5XnvYHh5B02Mi4&language=ru'
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

def roads(s0, uid): #place_id
    с1, с2 = users[uid]
    s = 'https://maps.googleapis.com/maps/api/directions/json?origin='+c1+','+c2+'&destination=place_id:'+ s0 +'&key=AIzaSyADGsGU8emVpO5QLlfZY5XnvYHh5B02Mi4&language=ru'
    place = requests.get(s)
    place_parse = json.loads(place.text)
    print(place_parse)
    message=''
    for i in place_parse['routes']:
        for k in i['legs']:
            for j in k['steps']:
                message+= html_to_text(j["html_instructions"])+'\n'
    return message

def Find_place(s0, uid):
    s = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?key=AIzaSyADGsGU8emVpO5QLlfZY5XnvYHh5B02Mi4&input=" + s0 + "&inputtype=textquery&language=ru&fields=formatted_address,geometry,icon,name,permanently_closed,photos,place_id,plus_code,types"
    place = requests.get(s)
    place_parse = json.loads(place.text)
    try:
        if place_parse["status"]=="ZERO_RESULTS":
            vk.messages.send(user_id=event.user_id, message='К сожалению, мы ничего не знаем об этом месте', keyboard=create_keyboard(1), random_id=0)
        else:
            t = 0
            for i in place_parse["candidates"]:
                if t >= 1:    # кол-во вывода
                    break
                message = i['name'] + '\n' + i['formatted_address']
                massage_photo("https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=" + i["photos"][0][
                    "photo_reference"] + "&key=AIzaSyADGsGU8emVpO5QLlfZY5XnvYHh5B02Mi4", message)
                vk.messages.send(user_id=event.user_id, message=roads(i['place_id'], uid), random_id=0)
                t+=1
    except KeyError:
        print("Попробуйте пойти в другое место)")

def create_keyboard(response):
    keyboard = VkKeyboard(one_time=True)

    if response == 1:

        keyboard.add_button('Конкретное место', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Места рядом', color=VkKeyboardColor.POSITIVE)

    elif response ==  2:

        keyboard.add_button('cafe', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('museum', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('art_gallery', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('restaurant', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('park', color=VkKeyboardColor.NEGATIVE)



    elif response == 3:
        keyboard.add_button('Тест', color=VkKeyboardColor.POSITIVE)
        print('закрываем клаву')
        return keyboard.get_empty_keyboard()

    return keyboard.get_keyboard()
users = collections.defaultdict(int)
lasq = collections.defaultdict(int)
type_=''

session = requests.Session()
vk_session = vk_api.VkApi(token='44afd0f665c16a98fe9178b549b7253e8a693f9caa63dd28a8b44a8539d78250aac0d2e46d022851bac90')
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
       # response = event.text.lower()
       # keyboard = create_keyboard(response)
        print(event.text.lower())
        if lasq[event.user_id] in set_t:
            nearbysearch_type(type_, event.text.lower(), event.user_id)
            lasq[event.user_id] = ''
        elif event.text.lower() == 'конкретное место' :
            print("event1")
            vk.messages.send(user_id=event.user_id, message='Какое конкретно место?', random_id=0)
        elif event.text.lower() == 'места рядом' :
            print("event2")
            vk.messages.send(user_id=event.user_id, message='Введите тип места, из предложенного ниже для поиска', keyboard=create_keyboard(2), random_id=0)
        elif event.text.lower() == 'привет' :
            print("event3")
            vk.messages.send(user_id=event.user_id, message='Введите свое местоположение?', random_id=0)
        elif event.text.lower().find(',')!= -1 :
            print("event4")
            users[event.user_id] = location(event.text.lower())
            print(users[event.user_id])
            vk.messages.send(user_id=event.user_id, message='Что надо?', keyboard=create_keyboard(1), random_id=0)
        elif event.text.lower() not in set_t and event.text.lower() not in Set0:
            print("event5")
            Find_place(event.text.lower(), event.user_id)
        elif event.text.lower() in set_t:
            vk.messages.send(user_id=event.user_id, message='Введите радиус', random_id=0)
            lasq[event.user_id] = event.text.lower()
        else:
            vk.messages.send(user_id=event.user_id, message='Я таких слов не знаю', keyboard=create_keyboard(1), random_id=0)

