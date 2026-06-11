# -*- coding: utf-8 -*-
"""AMCS RDAC 基础数据接口封装。"""
from __future__ import annotations

from typing import Any


class RdacApi:
    """封装 RDAC 站点和点位查询接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """读取 RDAC 模块接口地址。"""
        self.request_util = request_util
        self.config = config
        self.station_list_url = config["rdac"]["station_list_url"]
        self.station_items_page_url = config["rdac"]["station_items_page_url"]
        self.station_item_list_url = config["rdac"]["station_item_list_url"]

    def list_stations(self):
        """查询 RDAC 站点列表。"""
        return self.request_util.send_request("post", self.station_list_url, json={})

    def get_station_items_page(self, sub_name: str, protocol: str):
        """打开某个站点的点位配置页面 HTML。"""
        return self.request_util.send_request(
            "get",
            self.station_items_page_url,
            params={"subName": sub_name, "protocol": protocol},
        )

    def list_station_items(self, sub_name: str, protocol: str):
        """查询某个站点的点位配置 JSON。"""
        return self.request_util.send_request(
            "post",
            self.station_item_list_url,
            json={"subName": sub_name, "protocol": protocol},
        )
