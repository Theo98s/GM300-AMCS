# -*- coding: utf-8 -*-
"""AMCS 报警事件接口封装。"""
from __future__ import annotations

from typing import Any


class AlarmApi:
    """封装报警记录查询接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """初始化报警查询地址。"""
        self.request_util = request_util
        self.config = config
        self.alarm_record_page_url = config["alarm"]["alarm_record_page_url"]

    def get_alarm_record_page(self, payload: dict[str, Any] | None = None):
        """查询报警记录列表。

        页面初始加载允许空 JSON 请求体，所以这里默认发送空对象。
        """
        return self.request_util.send_request(
            "post",
            self.alarm_record_page_url,
            json=payload or {},
        )
