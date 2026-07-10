# -*- coding: utf-8 -*-
"""AMCS 图像识别配置接口封装。"""
from __future__ import annotations

from pathlib import Path
from typing import Any


class ImageRecognitionApi:
    """封装图像识别配置列表、级联字典、详情和校验接口。"""

    def __init__(self, request_util, config: dict[str, Any]):
        """读取图像识别配置模块的接口地址。"""
        self.request_util = request_util
        self.config = config
        recognition_config = config["image_recognition"]
        for key, value in recognition_config.items():
            setattr(self, key, value)

    def get_config_page(self):
        """打开图像识别配置首页。"""
        return self.request_util.send_request("get", self.config_page_url)

    def list_configs(
        self,
        payload: dict[str, Any] | None = None,
        *,
        page: int = 1,
        rows: int = 10,
    ):
        """分页查询图像识别配置。"""
        request_data = {"page": page, "rows": rows}
        if payload:
            request_data.update(payload)
        return self.request_util.send_request("post", self.page_url, data=request_data)

    def get_edit_page(self, config_id: str = "", view: bool = False):
        """打开图像识别配置新增、编辑或查看页面。"""
        params: dict[str, Any] = {}
        if config_id:
            params["id"] = config_id
        if view:
            params["view"] = "true"
        return self.request_util.send_request("get", self.edit_page_url, params=params)

    def get_detail(self, config_id: str):
        """按配置标识查询完整图像识别配置。"""
        return self.request_util.send_request(
            "get",
            self.detail_url,
            params={"configId": config_id},
        )

    def validate_config(self, payload: dict[str, Any]):
        """保存前校验图像识别配置中的识别项和参数。"""
        return self.request_util.send_request("post", self.validate_url, json=payload)

    def list_recognition_types(self):
        """查询系统支持的图像识别类型字典。"""
        return self.request_util.send_request("get", self.recognition_type_url)

    def list_configured_equipment(self):
        """查询已有图像识别配置的目标设备。"""
        return self.request_util.send_request("get", self.configured_equip_url)

    def list_configured_cameras(self, equip_id: str = ""):
        """按目标设备查询已有配置使用的摄像机。"""
        return self.request_util.send_request(
            "get",
            self.configured_camera_url,
            params={"equipId": equip_id} if equip_id else {},
        )

    def list_configured_presets(self, payload: dict[str, Any] | None = None):
        """按目标设备和摄像机查询已有配置使用的预置位。"""
        return self.request_util.send_request(
            "post",
            self.configured_preset_url,
            json=payload or {},
        )

    def list_monitored_equipment(self):
        """查询新增配置时可选择的被监测设备。"""
        return self.request_util.send_request("get", self.monitored_equip_url)

    def list_equipment_cameras(self, equip_id: str):
        """按被监测设备查询可使用的摄像机。"""
        return self.request_util.send_request(
            "get",
            self.equip_camera_url,
            params={"equipId": equip_id},
        )

    def list_presets(self, payload: dict[str, Any] | None = None):
        """按设备和摄像机查询新增配置可选择的预置位。"""
        return self.request_util.send_request(
            "post",
            self.preset_url,
            json=payload or {},
        )

    def list_recognition_items(self, equip_id: str):
        """按目标设备查询可绑定的监控点识别项。"""
        return self.request_util.send_request(
            "get",
            self.recognition_item_url,
            params={"equipId": equip_id},
        )

    def get_type_by_camera_and_preset(self, camera_id: str, preset_num: str):
        """按摄像机和预置位查询已绑定的识别类型与监控点。"""
        url = f"{self.recognition_type_by_preset_url}/{camera_id}/{preset_num}"
        return self.request_util.send_request("get", url)

    def get_import_export_page(self):
        """打开图像识别配置导入导出页面。"""
        return self.request_util.send_request("get", self.import_export_page_url)

    def download_import_template(self):
        """下载图像识别配置 Excel 导入模板。"""
        return self.request_util.send_request(
            "get",
            self.config["database"]["monitor_template_download_url"],
            params={
                "templateName": self.import_template_name,
                "downloadName": self.download_name,
            },
        )

    def export_configs(self, filters: dict[str, Any] | None = None):
        """按当前筛选条件导出图像识别配置。"""
        params = {
            "templateName": self.export_template_name,
            "downloadName": self.download_name,
        }
        if filters:
            params.update(filters)
        return self.request_util.send_request(
            "get",
            self.config["database"]["monitor_excel_export_url"],
            params=params,
        )

    def import_configs(self, file_path: str):
        """上传图像识别配置 Excel 文件并执行导入。"""
        path = Path(file_path)
        with path.open("rb") as file:
            return self.request_util.send_request(
                "post",
                self.config["database"]["monitor_excel_import_url"],
                params={"templateName": self.export_template_name},
                files={"file": (path.name, file, "application/vnd.ms-excel")},
            )
