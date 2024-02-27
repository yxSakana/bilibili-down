# -*- coding: utf-8 -*-
# @project snowm
# @file m3u.py
# @brief
# @author yx
# @resources 2024-01-30 18:24:38

import re


def parse_m3u(content):
    parents = [r"#EXT-X-VERSION:(\d+)", r'#EXT-X-TARGETDURATION:(\d+)', r'#EXT-X-MEDIA-SEQUENCE:(\d+)']
    names = ["version", "target_duration", "media_sequence"]
    info = {}
    for p, n in zip(parents, names):
        match = re.search(r"#EXT-X-VERSION:(\d+)", content)
        if match:
            info[n] = int(match.group(1))

    extinf_matches = re.finditer(r'#EXTINF:(\d+\.\d+),\n(.+)', content)
    info["content"] = []
    for match in extinf_matches:
        duration = float(match.group(1))
        ts_file_path = match.group(2)
        info["content"].append((duration, ts_file_path))
    return info
