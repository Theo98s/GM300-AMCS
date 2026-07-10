# -*- coding: utf-8 -*-
"""AMCS 巡检记录接口封装。"""
from __future__ import annotations

from typing import Any


class PatrolRecordApi:
    """封装巡检记录列表、详情、附件和报告导出入口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """读取巡检记录模块的接口地址。"""
        self.request_util = request_util
        self.config = config
        for key, value in config["patrol_record"].items():
            setattr(self, key, value)

    def get_index_page(self):
        """打开巡检记录首页。"""
        return self.request_util.send_request("get", self.index_url)

    def list_records(
        self,
        payload: dict[str, Any] | None = None,
        *,
        page: int = 1,
        rows: int = 10,
    ):
        """分页查询巡检记录，并允许附加日期和卡片名称条件。"""
        request_data = {"page": page, "rows": rows}
        if payload:
            request_data.update(payload)
        return self.request_util.send_request("post", self.page_url, data=request_data)

    def get_detail_page(self, record_id: str):
        """打开指定巡检记录的详情页面。"""
        return self.request_util.send_request(
            "get",
            self.detail_page_url,
            params={"id": record_id},
        )

    def get_record(self, record_id: str):
        """按记录标识查询巡检任务主信息。"""
        return self.request_util.send_request(
            "get",
            self.record_url,
            params={"id": record_id},
        )

    def list_record_details(
        self,
        record_id: str,
        payload: dict[str, Any] | None = None,
        *,
        page: int = 1,
        rows: int = 10,
    ):
        """分页查询巡检记录中的点位执行明细。"""
        request_data = {"page": page, "rows": rows}
        if payload:
            request_data.update(payload)
        return self.request_util.send_request(
            "get",
            self.detail_list_url,
            params={"recordId": record_id, **request_data},
        )

    def get_attaches(self, detail_id: str):
        """查询巡检明细关联的原图或截图附件。"""
        return self.request_util.send_request(
            "get",
            self.attaches_url,
            params={"recordDetailId": detail_id},
        )

    def can_export(self, record_id: str):
        """校验巡检记录是否允许导出报告。"""
        return self.request_util.send_request(
            "post",
            self.can_export_url,
            params={"id": record_id},
        )

    def get_export_dialog(
        self,
        record_id: str,
        sub_name: str,
        card_name: str,
        start_time: str,
    ):
        """打开巡检报告下载方式选择弹窗。"""
        return self.request_util.send_request(
            "get",
            self.export_dialog_url,
            params={
                "id": record_id,
                "subName": sub_name,
                "cardName": card_name,
                "startTime": start_time,
            },
        )

    def get_export_page(self):
        """打开巡检报告生成与下载执行页面。"""
        return self.request_util.send_request("get", self.export_page_url)
