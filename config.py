# -*- coding: utf-8 -*-
import logging
import os

## параметры бота
BOT_TOKEN = os.environ.get("TOKEN", "291679236:AAFzyPF6TLJEBF-rgtWij-NmQqC8lWb_fH0")
URL = "https://api.telegram.org/bot{0}".format(BOT_TOKEN)
UPDATE_INTERVAL = 5

## параметры доступа
MY_ID = 25863149 ## User(id=25863149, first_name=u'Sergey', last_name=u'Stupin', username=u'sstupin')
USERS = [25863149,   ## Sergey Stupin
         258108994]  ## Sergey А (fablet)
ADMINS = [25863149,   ## Sergey Stupin
          258108994]  ## Sergey А (fablet)


## парамтры логирования
LOG_FILENAME = "shopabot.log"
LOG_SIZE = 5242880
LOG_COUNT = 10
LOG_LEVEL = logging.INFO


## параметры БД
DB = os.environ.get("DATABASE_URL")


## ссылка на канал с новостями
NEWS_CHANNEL_URL = 'https://t.me/joinchat/AAAAAEIXijn8_1JvInvvhQ'
