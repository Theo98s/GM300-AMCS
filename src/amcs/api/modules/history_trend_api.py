# -*- coding: utf-8 -*-
"""AMCS 历史趋势接口封装。"""
from __future__ import annotations

from typing import Any


class HistoryTrendApi:
    """封装历史趋势设备树、监控属性、条件和时序数据接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """读取历史趋势模块的接口地址。"""
        self.request_util = request_util
        self.config = config
        for key, value in config["history_trend"].items():
            setattr(self, key, value)

    def get_index_page(self):
        """打开历史趋势首页。"""
        return self.request_util.send_request("get", self.index_url)

    def get_tree(self):
        """查询可展示历史趋势的设备类型与设备树。"""
        return self.request_util.send_request("get", self.tree_url)

    def get_trend_page(self, equipment_id: str, equipment_name: str, tab_index: int = 0):
        """打开指定设备的历史趋势图表页面。"""
        return self.request_util.send_request(
            "get",
            self.trend_page_url,
            params={
                "equipId": equipment_id,
                "equipName": equipment_name,
                "tabIndex": tab_index,
            },
        )

    def list_attributes(self, equipment_id: str):
        """查询设备可绘制趋势的遥测监控属性。"""
        return self.request_util.send_request(
            "get",
            self.attribute_url,
            params={"equipId": equipment_id},
        )

    def get_compare_equipment_page(self, equipment_id: str):
        """打开历史趋势设备对比选择页面。"""
        return self.request_util.send_request(
            "get",
            self.compare_equipment_url,
            params={"equipId": equipment_id},
        )

    def list_conditions(self, alarm_type_id: str):
        """查询监控属性配置的越限条件。"""
        return self.request_util.send_request(
            "get",
            f"{self.condition_url_prefix}/{alarm_type_id}",
        )

    def query_condition_data(self, payload: dict[str, Any]):
        """按监控属性和时间范围查询历史趋势及越限条件数据。"""
        return self.request_util.send_request(
            "post",
            self.condition_data_url,
            json=payload,
        )

    def query_online_data(self, payload: dict[str, Any]):
        """按设备属性和缩放时间范围查询增量趋势数据。"""
        return self.request_util.send_request(
            "post",
            self.online_data_url,
            json=payload,
        )
