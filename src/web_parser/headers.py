# -*- coding: utf-8 -*-
# @project snowm
# @file headers.py
# @brief
# @author yx
# @resources 2024-01-30 22:41:43

import requests.cookies


def from_jar_get_cookie(cookie: requests.cookies.RequestsCookieJar) -> str:
    return ";".join((f"{k}={v}" for k, v in cookie.items()))


def get_cookies_from_str(s: str) -> requests.cookies.RequestsCookieJar:
    jar = requests.cookies.RequestsCookieJar()
    for c in s.split(";"):
        k, v = c.split("=", 1)
        jar.set(k, v)
    return jar
