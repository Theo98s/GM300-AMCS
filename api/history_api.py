# -*- coding: utf-8 -*-
"""AMCS 历史记录接口封装。"""
from __future__ import annotations

from typing import Any


class HistoryApi:
    """封装联动历史查询接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """初始化历史记录接口地址。"""
        self.request_util = request_util
        self.config = config
        self.monitor_link_history_url = config["history"]["monitor_link_history_url"]

    def find_monitor_link_history(self, payload: dict[str, Any] | None = None):
        """查询联动历史分页数据。

        目前页面首次加载允许空请求体，因此这里默认发空对象。
        """
        return self.request_util.send_request(
            "post",
            self.monitor_link_history_url,
            data=payload or {},
        )
