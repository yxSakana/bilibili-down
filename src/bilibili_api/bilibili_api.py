# -*- coding: utf-8 -*-
# @project bilibili-down
# @file bilibili_api.py
# @brief
# @author yx
# @resources 2024-02-05 17:21:11

import re
import time
import json
from typing import Optional

import requests
from lxml import etree

import tools.files
import tools.ffmpeg
import web_parser.headers
import web_parser.document_parse
from bilibili_api.parse_types import (
    UserInfo, VideoInfo, ActionToken,
    UserCollect, UserCollects, UserCollectIterator,
    HistoryInfo, HistoryIterator,
    VideoDownloadInfo
)


class BilibiliApi(object):
    _UserAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    _api = {
        "video_info": "https://api.bilibili.com/x/web-interface/view?bvid={bv}",  # 获取视频信息 GET
        "action_token_on_video": "https://api.bilibili.com/x/web-interface/archive/relation?bvid={bv}",  # 获取用户对视频做过的操作 GET
        "like_video": "https://api.bilibili.com/x/web-interface/archive/like",  # 对视频进行点赞操作, POST
        "coin_video": "https://api.bilibili.com/x/web-interface/coin/add",  # 对视频进行投币 POST
        "follow_user": "https://api.bilibili.com/x/relation/modify",  # 关注用户 POST
        "collect_video": "https://api.bilibili.com/x/v3/fav/resource/deal",  # 收藏视频 POST
        "collect_article": "https://api.bilibili.com/x/article/favorites/add",  # 收藏文章 POST
        "cancel_collect_article": "https://api.bilibili.com/x/article/favorites/del",  # 取消收藏文章 POST
        "read_favorites": "https://api.bilibili.com/x/v3/fav/folder/created/list-all?type=2&rid=686758293&up_mid={uid}",  # 读取收藏夹信息
        "history": "http://api.bilibili.com/x/v2/history?pn={page}",  # 历史记录
    }
    _video_download_headers = {
        "User-Agent": _UserAgent,
        'Origin': 'https://www.bilibili.com',
        'Referer': 'https://www.bilibili.com/',
    }

    def __init__(self, cookie: str = None):
        self.session = requests.session()
        self.session.cookies = web_parser.headers.get_cookies_from_str(cookie)
        self.session.headers = {
            "User-Agent": BilibiliApi._UserAgent,
            "referer": "https://www.bilibili.com/video/",
            'authority': 'api.bilibili.com'
        }

        self.csrf = "bf359010606c22af55863705981486dc"  # 校验码 需要更新, 不知道如何产生的加密参数

    def set_cookie(self, cookie: str) -> None:
        self.session.cookies = web_parser.headers.get_cookies_from_str(cookie)

    def search_user(self, uid: str) -> Optional[UserInfo]:
        """获取用户信息

        :param uid: 用户 UID
        :return:
        """
        url = f'https://api.bilibili.com/x/space/acc/info?mid={uid}'
        json_data = self.session.get(url).json()
        return UserInfo(
            uid       = json_data["data"]["mid"],
            name      = json_data["data"]["name"],
            sex       = json_data["data"]["sex"],
            face      = json_data["data"]["face"],
            sign      = json_data["data"]["sign"],
            top_photo = json_data["data"]["top_photo"],
        ) if json_data["code"] == 0 else None

    def search_video(self, bv: str) -> Optional[VideoInfo]:
        """获取视频信息

        :param bv: 视频BV
        :return:
        """
        url = BilibiliApi._api["video_info"].format(bv=bv)
        json_data = self.session.get(url).json()
        tools.files.save("tmp/video_info.json", json.dumps(json_data, indent=2, ensure_ascii=False))
        return VideoInfo(
            uid            = json_data["data"]["owner"]["mid"],
            uname          = json_data["data"]["owner"]["name"],
            bv             = json_data["data"]["bvid"],
            av             = json_data["data"]["aid"],
            videos         = json_data["data"]["videos"],
            push_time      = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(json_data["data"]["pubdate"])),
            view_time      = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(json_data["data"]["ctime"])),
            url            = 'https://www.bilibili.com/' + json_data["data"]["bvid"],
            desc           = json_data["data"]["desc"],
            tag            = json_data["data"]["tname"],
            picture_url    = json_data["data"]["pic"],
            title          = json_data["data"]["title"],
            owner_name     = json_data["data"]["owner"]["name"],
            owner_uid      = json_data["data"]["owner"]["mid"],
            owner_face_url = json_data["data"]["owner"]["face"],
            view           = json_data["data"]["stat"]["view"],
            like           = json_data["data"]["stat"]["like"],
            dislike        = json_data["data"]["stat"]["dislike"],  # 踩
            coin           = json_data["data"]["stat"]["coin"],  # 投币
            favorite       = json_data["data"]["stat"]["favorite"],  # 收藏
            share          = json_data["data"]["stat"]["share"],
            danmu          = json_data["data"]["stat"]["danmaku"],
            reply          = json_data["data"]["stat"]["reply"],  # 评论
            pay            = json_data["data"]["is_chargeable_season"],
        ) if json_data["code"] == 0 else None

    def search_action_token_one_video(self, bv: str) -> Optional[ActionToken]:
        """获取本用户对视频做过的操作

        :param bv:
        :return:
        """
        url = BilibiliApi._api["action_token_on_video"].format(bv=bv)
        json_data = self.session.get(url).json()
        return ActionToken(
            attention = json_data["data"]["attention"],
            like = json_data["data"]["like"],
            dislike = json_data["data"]["dislike"],
            coin = json_data["data"]["coin"],
            favorite = json_data["data"]["favorite"],
        ) if json_data["code"] == 0 else None

    def like_video(self, av: str) -> bool:
        """点赞
        B站官方api code: 0: 点赞成功; 65006: 已点赞, 无法重复点赞
        :param av: 视频aid
        :return: 是否点赞成功;
        """
        url = BilibiliApi._api["like_video"]
        data_like = {
            'aid': av,
            'csrf': self.csrf,
            'like': 1,
            'eab_x': 2,
            'ramval': 0
        }
        return self.session.post(url, params=data_like).json()["code"] in [0, 65006]

    def coin_video(self, av: str) -> bool:
        """投币一个硬币
        B站官方api code: 0， 投币成功; 34005: 超过投币上限
        :param av: 视频 av
        :return:
        """
        url = BilibiliApi._api["coin_video"]
        params = {
            'aid': av,
            'multiply': 1,
            'select_like': 1,
            'cross_domain': 'true',
            'csrf': self.csrf,  # 校验码 需要更新, 不知道如何产生的加密参数
            'ga': 1
        }
        return self.session.post(url, params=params).json()["code"] in [0, 34005]

    def follow_user(self, uid: str, action: bool = True) -> bool:
        """关注用户
        B站官方api code: 0， 成功; 22014: 已经关注; 22001: 对自己操作
        :param uid: 用户uid
        :param action: 取消/关注
        :return:
        """
        url = BilibiliApi._api["follow_user"]
        params = {
            'fid': uid,  # 关注的人
            'act': 1 if action else 2,  # 1 关注, 2取消关注 ?
            'csrf': self.csrf
        }
        res = self.session.post(url, params=params).json()
        return res["code"] == 0

    def read_favorites(self, uid: str) -> Optional[UserCollects]:
        """

        :param uid:
        :return:
        """
        url = BilibiliApi._api["read_favorites"].format(uid=uid)
        res = self.session.get(url).json()
        if res["code"] == 0:
            return UserCollects(
                count    = res["data"]["count"],
                collects = UserCollectIterator([UserCollect(
                    attr        = item["attr"],
                    fav_state   = item["fav_state"],
                    fid         = item["fid"],
                    id          = item["id"],
                    media_count = item["media_count"],
                    mid         = item["mid"],
                    title       = item["title"],
                ) for item in res["data"]["list"]])
            )
        return None

    def collect_video(
            self,
            av: str,
            action: bool = True,
            dir_id: str = None
    ) -> bool:
        """

        :param av:
        :param action: 取消/收藏
        :param dir_id: 收藏夹id
        :return:
        """
        url = BilibiliApi._api["collect_video"]
        params = {
            'rid': av,  # av号
            'type': 2,
            'add_media_ids': dir_id,  # 收藏夹的ID参数
            'csrf': self.csrf
        } if action else {
            'rid': av,  # av号
            'type': 2,
            'del_media_ids': dir_id,  # 收藏夹的ID参数
            'csrf': self.csrf
        }
        res = self.session.post(url, params=params).json()
        return res["code"] == 0

    def collect_article(self, cvid: str, action: bool = True) -> bool:
        """
        B站官方api code: -111: 校验失败;
        :param cvid:
        :param action: 取消/收藏
        :return:
        """
        url = (
            BilibiliApi._api["collect_article"] if action
            else BilibiliApi._api["cancel_collect_article"]
        )
        params = {
            'csrf': self.csrf,
            'id': cvid
        }
        res = self.session.post(url, params=params).json()
        return res["code"]

    def history(self, page: int) -> Optional[HistoryIterator]:
        import time

        url = BilibiliApi._api["history"].format(page=page)
        json_data = self.session.get(url).json()
        main_data = json_data["data"]
        if json_data["code"] == 0:
            return HistoryIterator([HistoryInfo(
                video_info = VideoInfo(
                    uid            = "",
                    uname          = "",
                    av             = item["aid"],
                    bv             = item["bvid"],
                    tag            = item["tname"],
                    videos         = item["videos"],
                    push_time      = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item["pubdate"])),
                    view_time      = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item["ctime"])),
                    picture_url    = item["pic"],
                    title          = item["title"],
                    desc           = item["desc"],
                    owner_name     = item["owner"]["name"],
                    owner_uid      = item["owner"]["mid"],
                    owner_face_url = item["owner"]["face"],
                    view           = item["stat"]["view"],  # 评论
                    like           = item["stat"]["like"],
                    coin           = item["stat"]["coin"],  # 投币
                    favorite       = item["stat"]["favorite"],  # 收藏
                    share          = item["stat"]["share"],
                    danmu          = item["stat"]["danmaku"],
                    reply          = item["stat"]["reply"],  # 评论
                    dislike        = item["stat"]["dislike"],  # 踩
                    url            = item["short_link_v2"],
                    pay            = False
                )
            ) for item in main_data])
        return None

    def get_video_download_info(self, url: str) -> Optional[VideoDownloadInfo]:
        res = self.session.get(url, headers=BilibiliApi._video_download_headers)
        if not res.ok:
            return None
        json_data = json.loads(re.search(r'__playinfo__=(.*?)</script><script>', res.text).group(1))
        try:
            video_url = json_data['data']['dash']['video'][0]['baseUrl']
            audio_url = json_data['data']['dash']['audio'][0]['baseUrl']
            only_video = False
        except KeyError:  # 可能没有音轨
            video_url = json_data['data']['durl'][0]['url']
            only_video = True
        title = web_parser.document_parse.get_title(res.text)
        image_url = etree.HTML(res.text).xpath('//meta[@property="og:image"]/@content')[0]
        if image_url[:4] in ["//i0", "//i1", "//i2"]:
            image_url = "https:" + re.search("(.*?)@.*", image_url).group(1)
        return VideoDownloadInfo(
            title      = title,
            image_url  = image_url,
            video_url  = video_url,
            audio_url  = None if only_video else audio_url,
            only_video = only_video,
        )

    def download_video(self, url: str, path: str) -> None:
        res = self.get_video_download_info(url)
        headers = BilibiliApi._video_download_headers
        v_file = f"{path}/{res.title}/v.mp4"
        a_file = f"{path}/{res.title}/a.mp4"
        i_file = f"{path}/{res.title}/image.{res.image_url.split('.')[-1]}"
        tools.files.download_media(res.video_url, v_file, headers=headers)
        if not res.only_video:
            tools.files.download_media(res.audio_url, a_file)
        tools.files.download_media(res.image_url, i_file)
        tools.ffmpeg.merge(v_file, a_file, f"{path}/{res.title}/{res.title}.mp4")
