# -*- coding: utf-8 -*-
"""AMCS 系统级接口封装。

这里先收口首页和系统健康类接口，适合作为第一批 smoke 用例。
后续如果继续补巡检管理、基础数据、系统配置，也建议保持同样的封装风格。
"""
from __future__ import annotations

from typing import Any


class SystemApi:
    """封装首页/系统健康类接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """读取系统类接口地址，避免在测试里写死路径。"""
        self.request_util = request_util
        self.config = config
        self.sys_logo_url = config["system"]["sys_logo_url"]
        self.alarm_count_url = config["system"]["alarm_count_url"]
        self.timestamp_url = config["system"]["timestamp_url"]
        self.health_url = config["system"]["health_url"]

    def get_sys_logo(self):
        """查询系统 logo 配置。该接口当前可匿名访问。"""
        return self.request_util.send_request("get", self.sys_logo_url)

    def get_alarm_count(self):
        """查询实时告警数量。

        这里关闭自动重定向，方便用例明确断言“未登录会跳登录页”。
        """
        return self.request_util.send_request("get", self.alarm_count_url, allow_redirects=False)

    def get_timestamp(self):
        """查询服务器时间戳。

        实际返回是一个整数，而不是标准对象结构，所以单独保留一个方法。
        """
        return self.request_util.send_request("get", self.timestamp_url, allow_redirects=False)

    def get_health(self):
        """查询系统健康状态和服务列表。"""
        return self.request_util.send_request("get", self.health_url)
