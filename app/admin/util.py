# -*- coding: utf-8 -*-
# Time       : 2019/3/18 11:43
# Author     : tangdaye
# Description: admin util

al_num = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def generate_random_code(length=4):
    import random
    s = ''
    for i in range(length):
        s += random.choice(al_num)
    return s


def str_to_bool(str):
    return True if str.lower() == 'true' else False


def array2str(array, level):
    """

    :param array: 需要展示的的原数组
    :param level: 数组需要遍历的层级
    :return: 可直接展示的 word 的数组
    """
    if level == 1:
        string = "「"
        split = '，'
        string += split.join(array)
        string += "」"
    elif level == 2:
        string = "「"
        for i in range(0, len(array)):
            split = '，'
            string += ('「' + split.join(array[i]) + '」')
            if i < len(array) - 1:
                string += '，'
        string += '」'
    elif level == 3:
        string = '「'
        for i in range(0, len(array)):
            string += "「"
            for j in range(0, len(array[i])):
                split = '，'
                string += ('「' + split.join(array[i][j]) + '」')
                if j < len(array[i]) - 1:
                    string += '，'
            string += '」'
            if i < len(array) - 1:
                string += '，'
        string += '」'
    else:
        string = ''
    return string
