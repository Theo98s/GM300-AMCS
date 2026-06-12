# -*- coding: utf-8 -*-
"""AMCS 基础数据库相关接口封装。"""
from __future__ import annotations

from pathlib import Path
from typing import Any


class DatabaseApi:
    """封装监控点、报警配置、联动配置相关接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """初始化基础数据库模块用到的接口地址。"""
        self.request_util = request_util
        self.config = config
        database_config = config["database"]

        self.monitor_page_url = database_config["monitor_page_url"]
        self.monitor_validate_url = database_config["monitor_validate_url"]
        self.monitor_save_url = database_config["monitor_save_url"]
        self.monitor_can_delete_url = database_config["monitor_can_delete_url"]
        self.monitor_delete_url = database_config["monitor_delete_url"]
        self.monitor_edit_page_url = database_config["monitor_edit_page_url"]
        self.monitor_import_page_url = database_config["monitor_import_page_url"]
        self.monitor_xml_export_url = database_config["monitor_xml_export_url"]
        self.monitor_template_download_url = database_config["monitor_template_download_url"]
        self.monitor_excel_import_url = database_config["monitor_excel_import_url"]
        self.monitor_excel_export_url = database_config["monitor_excel_export_url"]
        self.monitor_related_equip_url = database_config["monitor_related_equip_url"]
        self.monitor_camera_list_url = database_config["monitor_camera_list_url"]
        self.monitor_preset_list_url = database_config["monitor_preset_list_url"]

    def list_monitors(
        self,
        payload: dict[str, Any] | None = None,
        *,
        page: int = 1,
        rows: int = 200,
    ):
        """查询监控点列表，默认放大分页方便测试侧做精确查找。"""
        request_data = {"page": page, "rows": rows}
        if payload:
            request_data.update(payload)
        return self.request_util.send_request("post", self.monitor_page_url, data=request_data)

    def validate_monitor(self, payload: dict[str, Any]):
        """调用监控点保存前校验接口。"""
        return self.request_util.send_request(
            "post",
            self.monitor_validate_url,
            json=payload,
        )

    def save_or_update_monitor(self, payload: dict[str, Any]):
        """保存监控点以及附带的报警、联动配置。"""
        return self.request_util.send_request(
            "post",
            self.monitor_save_url,
            json=payload,
        )

    def can_delete_monitor(self, monitor_ids: list[str]):
        """删除前先校验监控点是否允许删除。"""
        return self.request_util.send_request(
            "post",
            self.monitor_can_delete_url,
            data=",".join(monitor_ids),
            headers={"Content-Type": "application/plain"},
        )

    def delete_monitor_by_ids(self, monitor_ids: list[str]):
        """批量删除监控点。"""
        return self.request_util.send_request(
            "post",
            self.monitor_delete_url,
            json=monitor_ids,
        )

    def get_monitor_edit_page(self, monitor_id: str):
        """打开监控点编辑页，用于回查隐藏字段中的配置数据。"""
        return self.request_util.send_request(
            "get",
            self.monitor_edit_page_url,
            params={"id": monitor_id},
        )

    def get_monitor_import_page(self):
        """打开监控点导入导出页。"""
        return self.request_util.send_request("get", self.monitor_import_page_url)

    def download_template(self, template_name: str, download_name: str):
        """下载导入模板。"""
        return self.request_util.send_request(
            "get",
            self.monitor_template_download_url,
            params={
                "templateName": template_name,
                "downloadName": download_name,
            },
        )

    def import_excel(self, template_name: str, file_path: str):
        """上传 Excel 文件到对应导入接口。"""
        path = Path(file_path)
        with path.open("rb") as file:
            return self.request_util.send_request(
                "post",
                self.monitor_excel_import_url,
                params={"templateName": template_name},
                files={
                    "file": (
                        path.name,
                        file,
                        "application/vnd.ms-excel",
                    )
                },
            )

    def export_excel(
        self,
        template_name: str,
        download_name: str,
        params: dict[str, Any] | None = None,
    ):
        """导出监控点、报警配置或联动配置。"""
        request_params = {
            "templateName": template_name,
            "downloadName": download_name,
        }
        if params:
            request_params.update(params)
        return self.request_util.send_request(
            "get",
            self.monitor_excel_export_url,
            params=request_params,
        )

    def export_monitor_xml(self):
        """导出监控点 XML 点表。"""
        return self.request_util.send_request("post", self.monitor_xml_export_url)

    def query_related_equip_list(self):
        """查询联动配置中的关联设备列表。"""
        return self.request_util.send_request("get", self.monitor_related_equip_url)

    def query_camera_list(self, equip_id: str):
        """按设备查询可联动的视频设备。"""
        return self.request_util.send_request(
            "get",
            self.monitor_camera_list_url,
            params={"equipId": equip_id},
        )

    def query_preset_list(self, camera_equip_id: str, related_equip_id: str):
        """查询摄像机预置位列表。"""
        return self.request_util.send_request(
            "get",
            self.monitor_preset_list_url,
            params={"equipId": camera_equip_id, "pid": related_equip_id},
        )
