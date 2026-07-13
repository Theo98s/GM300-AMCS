# -*- coding: utf-8 -*-
"""设备管理基础接口测试。"""
from __future__ import annotations

import allure
import pytest


class TestEquipmentApi:
    """覆盖设备管理首页、列表、筛选、类型树、编辑页和文件导出。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，确保访问设备管理业务接口。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _first_row(equipment_api):
        """获取首条设备数据作为详情与筛选样本。"""
        rows = equipment_api.list_equipment(rows=1).json()["rows"]
        if not rows:
            pytest.skip("当前环境没有设备数据。")
        return rows[0]

    @staticmethod
    def _assert_xls(response):
        """统一校验响应为有效旧版 Excel 文件。"""
        assert response.status_code == 200
        assert "application/vnd.ms-excel" in response.headers.get("Content-Type", "")
        assert "attachment" in response.headers.get("Content-Disposition", "")
        assert response.content.startswith(bytes.fromhex("D0CF11E0A1B11AE1"))
        assert len(response.content) > 1024

    @staticmethod
    def _assert_all_rows_match(body: dict, field: str, expected_value: str):
        """统一校验筛选结果中的每一条记录都满足目标条件。"""
        assert body["rows"]
        assert all(item[field] == expected_value for item in body["rows"])

    @allure.title("设备管理首页包含列表和导入导出入口")
    def test_equipment_index_page(self, auth_api, equipment_api, test_user):
        """校验首页可加载设备列表、模板下载、导入和导出脚本。"""
        self._login(auth_api, test_user)

        response = equipment_api.get_index_page()

        assert response.status_code == 200
        assert "/poms/equip/equipmentPageList" in response.text
        assert "/poms/equip/doImport" in response.text
        assert "templateName=equip.xls" in response.text

    @allure.title("设备列表返回标准分页结构")
    def test_equipment_page_contract(self, auth_api, equipment_api, test_user):
        """校验设备总数和数据行使用稳定分页字段。"""
        self._login(auth_api, test_user)

        body = equipment_api.list_equipment(rows=5).json()

        assert isinstance(body["total"], int)
        assert isinstance(body["rows"], list)
        assert len(body["rows"]) <= 5

    @allure.title("设备列表遵守 rows 分页大小")
    def test_equipment_page_respects_rows(self, auth_api, equipment_api, test_user):
        """校验请求一条设备时接口不会返回额外数据。"""
        self._login(auth_api, test_user)

        body = equipment_api.list_equipment(rows=1).json()

        assert len(body["rows"]) == min(body["total"], 1)

    @allure.title("设备列表行包含类型、区域和状态字段")
    def test_equipment_row_contains_core_fields(self, auth_api, equipment_api, test_user):
        """校验首条设备具备列表展示和编辑回查所需字段。"""
        self._login(auth_api, test_user)

        row = self._first_row(equipment_api)

        assert set(row) >= {
            "id",
            "equipName",
            "equipStatus",
            "equipTypeId",
            "equiptypename",
            "equiptypecode",
            "areacode",
            "areaname",
            "deleted",
        }
        assert isinstance(row["id"], str) and row["id"]
        assert isinstance(row["equipName"], str) and row["equipName"]

    @allure.title("设备名称精确筛选可回查原设备")
    def test_equipment_filter_by_existing_name(self, auth_api, equipment_api, test_user):
        """校验列表中的设备名称可作为筛选条件命中自身。"""
        self._login(auth_api, test_user)
        row = self._first_row(equipment_api)

        body = equipment_api.list_equipment({"equipName": row["equipName"]}, rows=50).json()

        self._assert_all_rows_match(body, "equipName", row["equipName"])
        assert any(item["id"] == row["id"] for item in body["rows"])

    @allure.title("不存在的设备名称筛选返回空分页")
    def test_equipment_unknown_name_returns_empty_page(self, auth_api, equipment_api, test_user):
        """校验唯一无效名称不会命中现场设备。"""
        self._login(auth_api, test_user)

        body = equipment_api.list_equipment({"equipName": "NO_SUCH_EQUIPMENT_8D7F"}).json()

        assert body == {"total": 0, "rows": []}

    @allure.title("设备类型编码筛选后每条记录都属于目标类型")
    def test_equipment_filter_by_existing_type_code(self, auth_api, equipment_api, test_user):
        """校验设备类型编码筛选不会混入其他类型数据。"""
        self._login(auth_api, test_user)
        row = self._first_row(equipment_api)

        body = equipment_api.list_equipment({"equiptypecode": row["equiptypecode"]}, rows=50).json()

        self._assert_all_rows_match(body, "equiptypecode", row["equiptypecode"])
        assert any(item["id"] == row["id"] for item in body["rows"])

    @allure.title("不存在的设备类型编码筛选返回空分页")
    def test_equipment_unknown_type_code_returns_empty_page(self, auth_api, equipment_api, test_user):
        """校验无效设备类型编码不会退化成默认全量查询。"""
        self._login(auth_api, test_user)

        body = equipment_api.list_equipment({"equiptypecode": "NO_SUCH_TYPE_CODE_8D7F"}).json()

        assert body == {"total": 0, "rows": []}

    @allure.title("设备类型树返回可用层级节点")
    def test_equipment_type_tree(self, auth_api, equipment_api, test_user):
        """校验设备类型树节点包含身份、文本、状态和模型数据。"""
        self._login(auth_api, test_user)

        nodes = equipment_api.get_type_tree().json()

        assert isinstance(nodes, list) and nodes
        assert set(nodes[0]) >= {"id", "text", "state", "children", "model"}
        assert isinstance(nodes[0]["children"], list)

    @allure.title("已有设备可打开编辑页面并回显名称")
    def test_equipment_list_to_edit_page(self, auth_api, equipment_api, test_user):
        """校验列表设备标识可进入编辑页并保留保存接口和设备名称。"""
        self._login(auth_api, test_user)
        row = self._first_row(equipment_api)

        response = equipment_api.get_edit_page(row["id"])

        assert response.status_code == 200
        assert "<title>设备实例基本信息</title>" in response.text
        assert row["id"] in response.text
        assert row["equipName"] in response.text
        assert "/poms/equip/save" in response.text

    @allure.title("设备管理导入模板可正常下载")
    def test_equipment_template_download(self, auth_api, equipment_api, test_user):
        """校验设备模板返回附件形式的有效 XLS 文件。"""
        self._login(auth_api, test_user)

        self._assert_xls(equipment_api.download_template())

    @allure.title("设备管理现有数据可正常导出")
    def test_equipment_export(self, auth_api, equipment_api, test_user):
        """校验设备导出返回可供后续回灌的 XLS 文件。"""
        self._login(auth_api, test_user)

        self._assert_xls(equipment_api.export_equipment())
