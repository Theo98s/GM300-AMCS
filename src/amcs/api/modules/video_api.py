# -*- coding: utf-8 -*-
"""AMCS 视频监控接口封装。"""
from __future__ import annotations

from typing import Any


class VideoApi:
    """封装摄像机列表和树结构查询接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """读取视频相关接口地址。"""
        self.request_util = request_util
        self.config = config
        self.camera_tree_url = config["video"]["camera_tree_url"]
        self.preset_cameras_url = config["video"]["preset_cameras_url"]

    def get_camera_tree(self):
        """查询实时视频树结构。

        前端实时视频页左侧的摄像机树就来自这个接口。
        """
        return self.request_util.send_request("post", self.camera_tree_url, json={})

    def get_preset_cameras(self):
        """查询预置位配置页使用的摄像机列表。

        这个接口直接返回摄像机清单，适合做设备基础数据存在性校验。
        """
        return self.request_util.send_request("get", self.preset_cameras_url)
