# -*- coding: utf-8 -*-
# @project snowm
# @file files.py
# @brief
# @author yx
# @resources 2024-01-30 18:15:41

import os
import re
import logging
import threading
from typing import List


def read(path, encoding="utf-8"):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding=encoding) as handle:
        return handle.read()


def save(path, content, append=False, encoding="utf-8"):
    """会自动将非法字符替换为""
    :param path:
    :param content:
    :param append:
    :param encoding:
    :return:
    """
    path = sanitize_path(path)
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    with open(path, "a" if append else "w", encoding=encoding, newline="") as handle:
        handle.write(content)


def save_multiple(path, contents: List, encoding="utf-8"):
    """(多线程)将一组数据保存到一个文件(不会清空文件)
    :param path:
    :param contents:
    :param encoding:
    :return:
    """
    threads = []
    for content in contents:
        thread = threading.Thread(target=save, args=(path, content, True, encoding))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def save_media(path, content):
    path = sanitize_path(path)
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(content)


def save_multiple_media(data_pair: List):
    threads = []
    for path, content in data_pair:
        thread = threading.Thread(target=save_media, args=(path, content))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def download_media(url, path, headers=None, cookies=None, proxies=None):
    import requests
    res = requests.get(url, headers=headers, cookies=cookies, proxies=proxies)
    if res.ok:
        save_media(path, res.content)
    else:
        logging.warning(f"{url} requests failed: {res.status_code}")
        logging.warning(res.text)


def download_multiple_media(data_pair: List):
    threads = []
    for url, path in data_pair:
        thread = threading.Thread(target=download_media, args=(url, path))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def _sanitize_filename(filename):
    return re.sub(r'[ \\/*?:"<>|]', '', filename)
    # return re.sub(r'[ \\/*?:"<>|]', '', filename)


def sanitize_path(path):
    path_list = path.split(os.path.sep)
    filename = _sanitize_filename(path_list.pop())
    path_list.append(filename)
    return os.path.sep.join(path_list)
