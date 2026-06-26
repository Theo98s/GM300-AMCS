# -*- coding: utf-8 -*-
"""AMCS 地图与三维配置接口封装。"""
from __future__ import annotations

from typing import Any


class GisApi:
    """封装二维地图、三维地图和 GIS 配置查询接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """读取 GIS 相关接口地址。"""
        self.request_util = request_util
        self.config = config
        self.d2_data_path_url = config["gis"]["d2_data_path_url"]
        self.d2_map_prop_url = config["gis"]["d2_map_prop_url"]
        self.d3_map_prop_url = config["gis"]["d3_map_prop_url"]
        self.d3_gis_config_url = config["gis"]["d3_gis_config_url"]

    def get_d2_data_path(self, payload: dict[str, Any] | None = None):
        """查询二维地图数据路径。

        如果缺少地图类型参数，接口会返回业务提示信息，这也适合做入参保护校验。
        """
        return self.request_util.send_request("post", self.d2_data_path_url, json=payload or {})

    def get_d2_map_prop(self):
        """查询二维地图属性配置。

        实际返回里会包含 SVG 文件路径、缩放参数和区域视角配置。
        """
        return self.request_util.send_request("get", self.d2_map_prop_url)

    def get_d3_map_prop(self):
        """查询三维地图属性配置。

        主要用于确认三维 tiles 数据目录和相关属性是否已配置。
        """
        return self.request_util.send_request("get", self.d3_map_prop_url)

    def get_d3_gis_config(self):
        """查询 GIS 全局配置。

        可用于确认 GIS 总开关、三维巡检开关、主题等运行参数。
        """
        return self.request_util.send_request("post", self.d3_gis_config_url, json={})
