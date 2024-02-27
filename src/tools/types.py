# -*- coding: utf-8 -*-
# @project PixivSpider
# @file types.py
# @brief
# @author yx
# @resources 2024-02-01 15:57:56


def try_to_int(item):
    try:
        return int(item)
    except ValueError:
        return None
