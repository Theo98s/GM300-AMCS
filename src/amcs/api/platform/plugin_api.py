# -*- coding: utf-8 -*-
"""AMCS 插件定义接口封装。"""
from __future__ import annotations

from typing import Any


class PluginApi:
    """封装插件查询接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """初始化插件查询地址。"""
        self.request_util = request_util
        self.config = config
        self.find_plugin_url = config["plugin"]["find_plugin_url"]

    def find_plugin(self):
        """查询系统已加载的插件列表。

        返回结果里包含 menuContent XML，可用于反查系统菜单定义和页面路由。
        """
        return self.request_util.send_request("get", self.find_plugin_url)
