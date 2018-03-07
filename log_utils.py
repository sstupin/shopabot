# -*- coding: utf-8 -*-
## Библиотека, содержащая служебные функции для работы с лог-файлами
import logging
import logging.handlers
import config

## Запрос на ввод целого числа
## Входные параметры:
##    file_name - имя лог-файла
##    file_size - максимальный размер лог-файла
##    file_count - количество лог-файлов: при заполнении одного файла
##                 создается следующий и так далее, пока не будет
##                 достигнуто максимальное количество. Далее первый
##                 файл затирается и т.д.
##    log_level - уровень отображаемой в лог-файле информации (константы
##                logging.DEBUG, logging.INFO, logging.WARNING,
##                logging.ERROR, logging.CRITICAL
## Возвращаемое значение:
##    созданный с указанными параметрами объект logger
def create_log(file_name, file_size, file_count, log_level=config.LOG_LEVEL, log_format='%(levelname)-8s [%(asctime)s] %(message)s'):
    logger = logging.getLogger(file_name + '_logger')
    logger.setLevel(log_level)
    handler = logging.handlers.RotatingFileHandler(file_name,
                                                   maxBytes=file_size,
                                                   backupCount=file_count,
                                                   encoding='UTF-8')
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
