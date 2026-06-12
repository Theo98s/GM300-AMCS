# -*- coding: utf-8 -*-
"""AMCS 菜单管理接口封装。"""
from __future__ import annotations

from typing import Any


class MenuApi:
    """封装菜单树查询接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """初始化菜单树查询地址。"""
        self.request_util = request_util
        self.config = config
        self.user_menu_tree_url = config["menu"]["user_menu_tree_url"]

    def get_user_menu_tree(self):
        """查询当前用户完整菜单树。

        和首页 initMenu 相比，这里更接近系统管理里的菜单树展示结构。
        """
        return self.request_util.send_request("get", self.user_menu_tree_url)
