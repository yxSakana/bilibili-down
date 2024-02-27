# -*- coding: utf-8 -*-
# @project bilibili-down
# @file parse_types.py
# @brief
# @author yx
# @resources 2024-02-05 17:33:13

from typing import List
import dataclasses


@dataclasses.dataclass
class UserInfo:
    uid:       str
    name:      str
    sex:       str
    face:      str
    sign:      str
    top_photo: str


@dataclasses.dataclass
class VideoInfo:
    uid:            str
    uname:          str
    av:             str
    bv:             str
    url:            str
    desc:           str
    tag:            str
    picture_url:    str
    title:          str
    videos:         int
    push_time:      str
    view_time:      str
    # UP information
    owner_name:     str
    owner_uid:      str
    owner_face_url: str
    view:           int  # 播放量
    like:           int
    dislike:        int
    coin:           int  # 投币
    favorite:       int  # 收藏
    share:          int
    danmu:          int  # 弹幕
    reply:          int  # 评论
    pay:            bool


@dataclasses.dataclass
class ActionToken:
    attention: bool
    like:      bool
    dislike:   bool
    coin:      int
    favorite:  bool


@dataclasses.dataclass
class UserCollect:
    attr: int
    fav_state: int
    fid: str
    id: str
    media_count: int
    mid: str
    title: str


class UserCollectIterator:
    def __init__(self, collects):
        self.collects = collects
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.collects):
            res = self.collects[self.index]
            self.index += 1
            return res
        else:
            raise StopIteration


@dataclasses.dataclass
class UserCollects:
    count: int  # 收藏总视频数量
    collects: UserCollectIterator


@dataclasses.dataclass
class HistoryInfo:
    video_info: VideoInfo


class HistoryIterator:
    def __init__(self, histories):
        self.items = histories
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.items):
            res = self.items[self.index]
            self.index += 1
            return res
        else:
            raise StopIteration


@dataclasses.dataclass
class VideoDownloadInfo:
    title: str
    image_url: str
    video_url: str
    audio_url: str
    only_video: bool
