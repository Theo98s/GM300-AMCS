# -*- coding: utf-8 -*-
"""AMCS 首页与通用字典接口封装。

这一层主要覆盖首页初始化菜单和基础字典查询，适合作为平台级 smoke。
"""
from __future__ import annotations

from typing import Any


class HomeApi:
    """封装首页初始化和字典类接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """读取首页和字典接口地址。"""
        self.request_util = request_util
        self.config = config
        self.init_menu_url = config["home"]["init_menu_url"]
        self.dict_list_url_prefix = config["home"]["dict_list_url_prefix"]

    def init_menu(self):
        """查询当前登录用户可见的首页菜单树。

        这个接口会返回整个顶层菜单结构，适合做平台可用性和权限范围的基础校验。
        """
        return self.request_util.send_request("post", self.init_menu_url, data={})

    def list_dict_no_root(self, dict_type: str):
        """按字典类型查询不带根节点的字典项列表。

        例如设备区域、告警类型等前端下拉框数据，都可以通过这类接口获取。
        """
        return self.request_util.send_request("get", f"{self.dict_list_url_prefix}/{dict_type}")
