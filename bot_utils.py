# -*- coding: utf-8 -*-
## Библиотека, содержащая служебные функции для работы с ботами

## Разбор полученного текста на команду и аргументы
## Входные параметры:
##    s - строка 
## Возвращаемое значение:
##    три значения:
##        1. команда, строка
##        2. аргументы, отделенные от команды символом '_', список
##        3. текст, отделенный от команды пробелом
## например, для входной строки '/cmd_long_201 text text'
##     будут возвращены значения
##         ('cmd', ['long', '201'], 'text text')
def parse_cmd(s):
    cmd = None
    args = None
    text = None
    if s:
        if s[0] =='/':
            s1 = s[1:].lower().split()
            if len(s1) > 1:
                text = ' '.join(s1[i] for i in range(1, len(s1)))
            s2 = s1[0].lower().split('_')
            cmd = s2[0]
            if len(s2) > 1:
                args = [s2[i] for i in range(1, len(s2))]
        else:
            text = s
    return cmd, args, text


def parse_list(s):
    res = s.split('\n')
    res1 = list()
    for el in res:
        if el.strip() != '':
            res1.append(el.strip())
    return res1
