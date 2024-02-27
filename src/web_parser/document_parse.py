# -*- coding: utf-8 -*-
# @project bilibili-down
# @file document_parse.py
# @brief
# @author yx
# @data 2024-02-05 21:55:19

from lxml import etree


def get_title(html):
    """获取标题
    """
    return etree.HTML(html).xpath("/html/head/title/text()")[0]
