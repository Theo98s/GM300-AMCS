# -*- coding: utf-8 -*-
"""AMCS 基础数据设备管理接口封装。"""
from __future__ import annotations

from pathlib import Path
from typing import Any


class EquipmentApi:
    """封装设备列表、类型树、编辑页、删除校验和文件接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """读取设备管理与通用 Excel 接口地址。"""
        self.request_util = request_util
        self.config = config
        equipment_config = config["equipment"]
        for key, value in equipment_config.items():
            setattr(self, key, value)

    def get_index_page(self):
        """打开设备管理首页。"""
        return self.request_util.send_request("get", self.index_url)

    def list_equipment(
        self,
        payload: dict[str, Any] | None = None,
        *,
        page: int = 1,
        rows: int = 10,
    ):
        """分页查询设备，并允许附加设备名称和类型筛选。"""
        request_data = {"page": page, "rows": rows}
        if payload:
            request_data.update(payload)
        return self.request_util.send_request("post", self.page_url, data=request_data)

    def get_type_tree(self):
        """查询设备类型树。"""
        return self.request_util.send_request("get", self.type_tree_url)

    def get_edit_page(self, equipment_id: str = ""):
        """打开设备新增或编辑页面。"""
        return self.request_util.send_request(
            "get",
            self.edit_page_url,
            params={"id": equipment_id},
        )

    def save_equipment(self, payload: dict[str, Any], equipment_id: str = ""):
        """新增或修改设备管理数据。"""
        request_data = dict(payload)
        request_data["id"] = equipment_id
        return self.request_util.send_request("post", self.save_url, data=request_data)

    def can_delete(self, equipment: list[dict[str, Any]]):
        """删除前校验设备是否被监控点或其他业务引用。"""
        return self.request_util.send_request(
            "post",
            self.can_delete_url,
            json=equipment,
        )

    def delete_by_ids(self, equipment_ids: list[str]):
        """按设备标识批量删除测试生成的数据。"""
        return self.request_util.send_request(
            "get",
            self.delete_url,
            params={"ids": ",".join(equipment_ids)},
        )

    def download_template(self):
        """下载设备管理 Excel 导入模板。"""
        return self.request_util.send_request(
            "get",
            self.config["database"]["monitor_template_download_url"],
            params={"templateName": self.template_name, "downloadName": self.download_name},
        )

    def export_equipment(self, system: str = ""):
        """导出当前系统的设备数据。"""
        return self.request_util.send_request(
            "get",
            self.config["database"]["monitor_excel_export_url"],
            params={
                "templateName": self.template_name,
                "downloadName": self.export_name,
                "system": system,
            },
        )

    def import_equipment(self, file_path: str):
        """上传设备 Excel 文件并执行导入。"""
        path = Path(file_path)
        with path.open("rb") as file:
            return self.request_util.send_request(
                "post",
                self.import_url,
                data={"templateName": self.template_name},
                files={"uploadFile": (path.name, file, "application/vnd.ms-excel")},
            )
