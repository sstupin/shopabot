# -*- coding: utf-8 -*-
import logging

## параметры бота
BOT_TOKEN = ''
URL = 'https://api.telegram.org/bot{0}'.format(BOT_TOKEN)
UPDATE_INTERVAL = 5

## параметры доступа
MY_ID = 25863149 ## User(id=25863149, first_name=u'Sergey', last_name=u'Stupin', username=u'sstupin')
USERS = [25863149,   ## Sergey Stupin
         258108994]  ## Sergey А (fablet)
ADMINS = [25863149,   ## Sergey Stupin
          258108994]  ## Sergey А (fablet)


## парамтры логирования
LOG_FILENAME = 'shopping_list.log'
LOG_SIZE = 5242880
LOG_COUNT = 10
LOG_LEVEL = logging.INFO


## параметры БД
DB = 'shopping_list.db'


## ссылка на канал с новостями
NEWS_CHANNEL_URL = 'https://t.me/joinchat/AAAAAEIXijn8_1JvInvvhQ'
