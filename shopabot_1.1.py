# -*- coding: utf-8 -*-
import time
import sys
import logging
import logging.handlers
import sqlite3
import binascii
import twx.botapi
from twx.botapi import ReplyKeyboardMarkup
from emoji import emojize
import log_utils
import bot_utils
import config


def command_add(arguments, db_conn, lists, message):
    response = {'chat': message.chat}
    list_id = lists.get(message.sender.id)
    product_list = bot_utils.parse_list(message.text)
    for p in product_list:
        product_id = add_product(db_conn, p)
        added = add_product_to_list(db_conn, list_id, product_id)
    response['text'] = command_show(None, db_conn, lists, message)['text']
    return response


def command_show(arguments, db_conn, lists, message):
    response = {'chat': message.chat}
    if arguments and len(arguments) > 0 and is_admin(message.sender.id):
        list_id = arguments[0]
    else:
        list_id = lists.get(message.sender.id)
    products = get_products_from_list(db_conn, list_id)
    n = len(products)
    news_msg = u'\nПодписывайтесь на новости бота:\n{0}'.format(config.NEWS_CHANNEL_URL)
    if len(products) > 0:
        text = u'Вот ваш список ({0}):\n'.format(n)
        l = u''.join(emojize(':o:', use_aliases=True) + ' ' + products[i][1] + u' /pdel_{0}'.format(products[i][0]) + u'\n' for i in range(n))
        response['text'] = text + l + news_msg
    else:
        response['text'] = u'Список пока пуст ' + emojize(':smirk:', use_aliases=True) + news_msg
    return response

def command_start(arguments, db_conn, lists, message):
    response = {'chat': message.chat}
    text = u'Привет! Я помогу составлять списки покупок! ' + emojize(':meat_on_bone:', use_aliases=True) + emojize(':tomato:', use_aliases=True) + emojize(':cake:', use_aliases=True)
    text = text + u'\nДля просмотра списка доступных команд введите команду \'/help\'\n'
    text = text + u'\nCвои пожелания и предложения отправляйте @sstupin\n'
    response['text'] = text
    return response

def command_new(arguments, db_conn, lists, message):
    lists.pop(message.sender.id, None)
    list_id = get_product_list(db_conn, True, message.sender.id)
    lists[message.sender.id] = list_id
    print 'new list id:', list_id
    response = {'chat': message.chat}
    response['text'] = u'Создан новый список ' + emojize(':pencil:', use_aliases=True)
    return response

def command_del_product_from_list(arguments, db_conn, lists, message):
    response = {'chat': message.chat}
    r = u''
    if arguments and len(arguments) > 0:
        ## удалить продукт из списка
        list_id = lists.get(message.sender.id)
        try:
            product_id = int(arguments[0])
            product = del_product_from_list(db_conn, list_id, product_id)
            if product:
                r = u'Элемент \'{0}\' удален из списка.\n'.format(product)
        except:
            r = u'Не удалось удалить элемент {0} из списка.\n'.format(product_id)
    response['text'] = r + command_show(None, db_conn, lists, message)['text']
    return response

def command_help(arguments, db_conn, lists, message):
    response = {'chat': message.chat}
    text = emojize(':arrow_right:', use_aliases=True) + u' Для добавления продукта в список просто отправьте его название в чат.\n'
    text = text + emojize(':arrow_right:', use_aliases=True) + u' Для просмотра списка введите команду \'/show\'\n'
    text = text + emojize(':arrow_right:', use_aliases=True) + u' Для создания нового списка введите команду \'/new\'\n'
    text = text + emojize(':arrow_right:', use_aliases=True) + u' Cвои пожелания и предложения отправляйте @sstupin'
    response['text'] = text
    keyboard = [['/show', '/new'], ['/help']]
    reply_markup = ReplyKeyboardMarkup.create(keyboard, True, True)
    response['reply_markup'] = reply_markup
    return response

def command_not_found(arguments, db_conn, lists, message):
    response = {'chat': message.chat}
    text = u'Команда \'{0}\' не поддерживается. Используй команду \'/help\' для справки.'.format(message.text)
    response['text'] = text
    return response

def command_show_all_products(arguments, db_conn, lists, message):
    response = {'chat': message.chat}
    if is_admin(message.sender.id):
        products = get_all_products(db_conn)
        if len(products) > 0:
            text = u'Полный список продуктов:\n'
            l = u''.join(emojize(':o:', use_aliases=True) + ' ' + products[i] + u'\n' for i in range(len(products)))
            response['text'] = text + l
            if len(response['text']) > 4096:
                response['text'] = u'Всего продуктов: {0}. См. лог-файл.'.format(len(products))
                logger.info(u'Полный список продуктов:\n' + l)
        else:
            response['text'] = u'Продуктов пока нет.'
    else:
        response['text'] = u'Команда \'{0}\' не поддерживается. Используй команду \'/help\' для справки.'.format(message.text)
    return response

def command_show_all_users(arguments, db_conn, lists, message):
    response = {'chat': message.chat}
    if is_admin(message.sender.id):
        users = get_all_users(db_conn)
        if len(users) > 0:
            text = u'Полный список пользователей ({0}):\n'.format(len(users))
            l = u''.join(str(i+1).ljust(5) + ': ' + '(' + users[i][0] + ', ' + users[i][1] + ', ' + users[i][2] + ', ' + users[i][3] + ', ' + users[i][4] + u')\n' for i in range(len(users)))
            response['text'] = text + l
            if len(response['text']) > 4096:
                response['text'] = u'Всего пользователей: {0}. См. лог-файл.'.format(len(users))
                logger.info(u'Полный список пользователей:\n' + l)
        else:
            response['text'] = u'Пользователей пока нет.'
    else:
        response['text'] = u'Команда \'{0}\' не поддерживается. Используй команду \'/help\' для справки.'.format(message.text)
    return response

def unknown_user_response(message):
    user = message.sender
    print '*** Unknown user: {0}, {1} {2} ({3})'.format(user.id, user.first_name, user.last_name, user.username)
    logger.warning('Unknown user: {0}, {1} {2} ({3})'.format(user.id, user.first_name, user.last_name, user.username))
    response = {'chat': message.chat}
    text = u'Прости, но я не тебя пока не знаю.\nОбратись к @sstupin за помощью.'
    response['text'] = text
    return response
    
## Обработка всех входящих сообщений и команд
def handle_msg(bot, db_conn, lists, message):
    text = message.text
    logger.info(u'Message received: ({0}, {1})'.format(message.chat.id, text))
    logger.debug(message)
    if text: ##message.sender.id in config.USERS:
        ## get last list id
        list_id = lists.get(message.sender.id)
        if not list_id:
            list_id = get_product_list(db_conn, False, message.sender.id)
            lists[message.sender.id] = list_id
        cmd, args, text = bot_utils.parse_cmd(text)
        if cmd:
            response = CMD.get(cmd, command_not_found)(args, db_conn, lists, message)
        else:
            response = command_add(None, db_conn, lists, message)
    else:
        response = command_not_found(None, db_conn, lists, message)
    send_response(bot, response)
        
## maximum response size = 4096
def send_response(bot, response):
    text = response.get('text', '')
    r = bot.send_message(response['chat'], text, reply_markup=response.get('reply_markup'))
    logger.info(u'Response sent: ({0}, {1})'.format(response['chat'].id, text))


def is_admin(sender):
    return sender in config.ADMINS

CMD = {'start': command_start, 'add': command_add, 'show': command_show, 'new': command_new, 'help': command_help, 'showproducts': command_show_all_products, 'showusers': command_show_all_users, 'pdel': command_del_product_from_list}


## DB operations

def get_product_list(db_conn, create_new_list, user_id):
    cursor = db_conn.cursor()
    if create_new_list:
        sql = u'insert into list (list, user) values(?, ?)'
        cursor.execute(sql, ('', user_id))
        db_conn.commit()
        return cursor.lastrowid
    else:
        sql = 'select max(id) from list where user=?'
        cursor.execute(sql, (user_id,))
        row = cursor.fetchone()
        print u'list found:', row[0]
        logger.debug(u'{0}: {1}'.format(row[0], sql))
        if row[0]:
            return row[0]
        else:
            sql = u'insert into list (list, user) values(?, ?)'
            cursor.execute(sql, ('', user_id))
            db_conn.commit()
            list_id = cursor.lastrowid
            logger.debug(u'{0}: {1}'.format(list_id, sql))
            return list_id

def add_product(db_conn, product_name):
    cursor = db_conn.cursor()
    p = product_name.lower().strip()
    crc32 = binascii.crc32(p.encode('utf-8'))
    ## добавить индекс по полю crc32 и сразу добавлять продукт, обрабатывая исключение,
    ## если продукт уже существует
    sql = 'select id from product where crc32=?'
    cursor.execute(sql, (crc32,))
    r = cursor.fetchone()
    if r:
        prod_id = r[0]
        print u'product found:', prod_id
        logger.info(u'product found:'.format(prod_id))
    else:
        sql = u'insert into product (product, crc32) values(?, ?)'
        cursor.execute(sql, (p, crc32))
        prod_id = cursor.lastrowid
        logger.info(u'product added: {0}'.format(prod_id))
        db_conn.commit()
        print u'product added:', prod_id
    return prod_id

def add_product_to_list(db_conn, list_id, product_id):
    cursor = db_conn.cursor()
    try:
        sql = 'insert into products_in_list (list_id, product_id) values(?, ?);'
        cursor.execute(sql, (list_id, product_id))
        print u'product {0} added to list {1}'.format(product_id, list_id)
        logger.info(u'product {0} added to list {1}'.format(product_id, list_id))
        db_conn.commit()
        return True
    except sqlite3.IntegrityError:
        print u'product {0} already exists in list {1}'.format(product_id, list_id)
        logger.info(u'product {0} already exists in list {1}'.format(product_id, list_id))
        return False
    except:
        print u'error while adding product {0} to list {1}'.format(product_id, list_id)
        logger.error(u'error while adding product {0} to list {1}'.format(product_id, list_id))
        return False


def del_product_from_list(db_conn, list_id, product_id):
    cursor = db_conn.cursor()
    try:
        sql = 'delete from products_in_list where list_id=? and product_id=?'
        cursor.execute(sql, (list_id, product_id))
        was_in_list = cursor.rowcount
        db_conn.commit()
        if was_in_list > 0:
            sql = 'select product from product where id=?'
            cursor.execute(sql, (product_id,))
            row = cursor.fetchone()
            product = row[0]
            print(u'product {0} found: {1}'.format(product_id, product))
            logger.debug(u'{0}, {1}: {2}'.format(sql, product_id, product))
            print(u'product {0}:{1} deleted from list {2}'.format(product_id, product, list_id))
            logger.info(u'product {0}:{1} deleted from list {2}'.format(product_id, product, list_id))
            return product
        return None
    except:
        print(sys.exc_info())
        print(u'error while deleting product {0} from list {1}'.format(product_id, list_id))
        logger.error(u'error while deleting product {0} from list {1}'.format(product_id, list_id))
        return None        

def get_products_from_list(db_conn, list_id):
    cursor = db_conn.cursor()
    sql = 'select product.id, product.product \
           from  products_in_list, list, product \
           where products_in_list.list_id=? \
             and products_in_list.list_id=list.id \
             and products_in_list.product_id=product.id'
    products = list()
    for row in cursor.execute(sql, (list_id,)):
        p = list()
        p.append(row[0])
        p.append(row[1])
        products.append(p)
    return products

def log_user(db_conn, user_id, first_name, last_name, username):
    cursor = db_conn.cursor()
    try:
        sql_insert = 'insert into users (user, first_name, last_name, username, role, first_access_time, last_access_time) values (?, ?, ?, ?, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);'
        cursor.execute(sql_insert, (user_id, first_name, last_name, username))
        print(u'user {0}, {1}, {2}, {3} added'.format(user_id, first_name, last_name, username))
        logger.info(u'user {0}, {1}, {2}, {3} added'.format(user_id, first_name, last_name, username))
        db_conn.commit()
        return True
    except sqlite3.IntegrityError:
        logger.info(u'user {0} already exists'.format(user_id))
        sql_update = 'update users set first_name=?, last_name=?, username=?, last_access_time=CURRENT_TIMESTAMP where user=?;'
        cursor.execute(sql_update, (first_name, last_name, username, user_id))
        logger.info(u'user {0}, {1}, {2}, {3} updated'.format(user_id, first_name, last_name, username))
        db_conn.commit()
        return False
    except:
        print u'error while adding user {0}'.format(user_id)
        logger.error(u'error while adding user {0}'.format(user_id))
        return False

## FOR ADMINS ONLY
def get_all_products(db_conn):
    cursor = db_conn.cursor()
    sql = 'select product from product order by id'
    products = list()
    for row in cursor.execute(sql):
        products.append(row[0])
    return products

def get_all_users(db_conn):
    cursor = db_conn.cursor()
    sql = 'select user, first_name, last_name, username, role, first_access_time, last_access_time from users order by last_access_time;'
    users = list()
    for row in cursor.execute(sql):
        user = list()
        user_id = row[0]
        full_user_name = ''
        if row[1]: full_user_name = row[1]
        if row[2]: full_user_name = full_user_name + ' ' + row[2]
        if row[3]: full_user_name = full_user_name + ' (' + row[3] + ')'
        user_role = row[4]
        first_access_time = row[5]
        last_access_time = row[6]
        user.append(str(user_id).ljust(12))
        user.append(full_user_name.ljust(40))
        user.append(str(user_role))
        user.append(str(first_access_time))
        user.append(str(last_access_time))
        users.append(user)
    return users

if __name__ == '__main__':
    ## SET LOGGING OPTIONS
    logger = log_utils.create_log(file_name=config.LOG_FILENAME, file_size=config.LOG_SIZE, file_count=config.LOG_COUNT)
    ## open DB
    db_conn = sqlite3.connect(config.DB)
    ##########
    last = 0
    bot = twx.botapi.TelegramBot(config.BOT_TOKEN)
    bot.update_bot_info().wait()
    print u'{0} started...'.format(bot.username)
    logger.info(u'{0} started...'.format(bot.username))
    lists = dict()
    ## get users from DB
    ##########
    while True:
        try:
            updates = bot.get_updates(last+1, 5, 0).wait()
            for update in updates:
                last = update.update_id
                if update.message: ## can be None!!!
                    user = update.message.sender
                    print u'User: {0}, {1} {2} ({3})'.format(user.id, user.first_name, user.last_name, user.username)
                    logger.info(u'User: {0}, {1} {2} ({3})'.format(user.id, user.first_name, user.last_name, user.username))
                    log_user(db_conn, user.id, user.first_name, user.last_name, user.username)
                    handle_msg(bot, db_conn, lists, update.message)
                else:
                    print('Message is None: {0}'.format(update))
            time.sleep(config.UPDATE_INTERVAL)
        except (KeyboardInterrupt, SystemExit, GeneratorExit):
            break
        except:
            print(sys.exc_info())
            logger.error(u'Unexpected error: {0}'.format(sys.exc_info()))
            continue
    print bot.username + u' stopped...'
    db_conn.close()
    logger.info(u'{0} stopped. DB connection was closed.'.format(bot.username))
