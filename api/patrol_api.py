# -*- coding: utf-8 -*-
"""AMCS 巡检管理查询接口封装。"""
from __future__ import annotations

from typing import Any


class PatrolApi:
    """封装巡检卡片和巡检计划查询接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """读取巡检模块接口地址。"""
        self.request_util = request_util
        self.config = config
        self.patrol_card_list_url = config["patrol"]["patrol_card_list_url"]
        self.patrol_plan_list_url = config["patrol"]["patrol_plan_list_url"]

    def list_patrol_cards(self):
        """查询巡检卡片列表。

        前端这里使用 POST，但不需要额外请求体。
        """
        return self.request_util.send_request("post", self.patrol_card_list_url, data={})

    def list_patrol_plans(self):
        """查询巡检计划视图列表。"""
        return self.request_util.send_request("get", self.patrol_plan_list_url)
