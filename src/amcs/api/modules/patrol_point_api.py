# -*- coding: utf-8 -*-
"""AMCS 巡检点位管理接口封装。"""
from __future__ import annotations

from typing import Any


class PatrolPointApi:
    """封装巡检点位列表、编辑页和级联查询接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """读取巡检点位模块的接口地址。"""
        self.request_util = request_util
        self.config = config
        point_config = config["patrol_point"]
        self.index_url = point_config["index_url"]
        self.page_url = point_config["page_url"]
        self.edit_page_url = point_config["edit_page_url"]
        self.equip_list_url = point_config["equip_list_url"]
        self.existing_preset_url = point_config["existing_preset_url"]
        self.can_delete_url = point_config["can_delete_url"]
        self.export_url = point_config["export_url"]

    def get_index_page(self):
        """打开巡检点位管理首页。"""
        return self.request_util.send_request("get", self.index_url)

    def list_points(
        self,
        payload: dict[str, Any] | None = None,
        *,
        page: int = 1,
        rows: int = 10,
    ):
        """分页查询巡检点位，并允许附加名称筛选条件。"""
        request_data = {"page": page, "rows": rows}
        if payload:
            request_data.update(payload)
        return self.request_util.send_request("post", self.page_url, data=request_data)

    def get_edit_page(self, point_id: str = "", readonly: int = 0):
        """打开巡检点位新增、编辑或只读查看页面。"""
        return self.request_util.send_request(
            "get",
            self.edit_page_url,
            params={"id": point_id, "readonly": readonly},
        )

    def list_equipment(self):
        """查询巡检点位可选择的设备和摄像机列表。"""
        return self.request_util.send_request("get", self.equip_list_url)

    def list_existing_presets(self, equip_id: str):
        """按摄像机设备标识查询已占用的预置位编号。"""
        return self.request_util.send_request(
            "get",
            self.existing_preset_url,
            params={"equipId": equip_id},
        )

    def can_delete(self, points: list[dict[str, Any]]):
        """删除前校验巡检点位是否已被其他业务配置引用。"""
        return self.request_util.send_request(
            "post",
            self.can_delete_url,
            json=points,
        )

    def export_points(self, filters: dict[str, Any] | None = None):
        """按当前筛选条件导出巡检点位。"""
        return self.request_util.send_request(
            "get",
            self.export_url,
            params=filters or {},
        )
