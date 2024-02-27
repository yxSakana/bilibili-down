# -*- coding: utf-8 -*-
# @project bilibili-down
# @file test_bilibili_api.py
# @brief
# @author yx
# @resources 2024-02-05 17:38:29

from pprint import pprint

from bilibili_api.bilibili_api import BilibiliApi
import tools.files


cookie = tools.files.read("resources/cookie")
api = BilibiliApi(cookie)


def test_get_user_info():
    headers = {
        "User-Agent": BilibiliApi._UserAgent,
        "referer": "https://www.bilibili.com/video/",
        'authority': 'api.bilibili.com',
        "cookie": cookie
    }
    res = api.search_user("287470883")
    assert res is None


def test_get_video_info():
    res = api.search_video("BV1SB421k7NY")
    pprint(res)


def test_get_action_token_on_video():
    res = api.search_action_token_one_video("BV1SB421k7NY")
    pprint(res)


def test_like_video():
    test_get_action_token_on_video()
    res = api.like_video("1350014593")
    print(res)
    test_get_action_token_on_video()


def test_coin_video():
    test_get_action_token_on_video()
    res = api.coin_video("1350014593")
    print(res)
    test_get_action_token_on_video()


def test_follow_user():
    res = api.follow_user("287470883", False)
    print(res)


def test_read_favorites():
    res = api.read_favorites("287470883")
    print(res)
    for i in res.collects:
        pprint(i)


def test_collect_video():
    res = api.collect_video("1350014593", dir_id="0")
    print(res)


def test_follow_article():
    res = api.collect_article("30756801", False)
    print(res)


def test_history():
    res = api.history(1)
    for item in res:
        pprint(item)


def test_get_video_download_info():
    url = "https://www.bilibili.com/video/BV1Ba4y1k7W7/?spm_id_from=333.1007.tianma.4-3-13.click&vd_source=de98ab7cb832cfeabeab01be4ca136ce"
    res = api.get_video_download_info(url)
    pprint(res)


def test_download_video():
    url = "https://www.bilibili.com/video/BV1Ba4y1k7W7/?spm_id_from=333.1007.tianma.4-3-13.click&vd_source=de98ab7cb832cfeabeab01be4ca136ce"
    api.download_video(url, "data")


if __name__ == '__main__':
    # tset_api()
    # test_get_user_info()
    # test_get_video_info()
    # test_get_action_token_on_video()
    # test_like_video()
    # test_coin_video()
    # test_follow_user()
    # test_follow_article()
    # test_read_favorites()
    # test_history()
    # test_get_video_download_info()
    test_download_video()
