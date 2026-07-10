# -*- coding: utf-8 -*-
"""巡检点位基础接口测试。"""
from __future__ import annotations

import re
import allure


class TestPatrolPointApi:
    """覆盖巡检点位首页、分页列表、编辑页和设备级联查询。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，确保响应来自巡检点位业务接口。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("巡检点位管理首页返回完整页面")
    def test_patrol_point_index_page(self, auth_api, patrol_point_api, test_user):
        """校验首页标题、列表接口和导入入口均存在。"""
        self._login(auth_api, test_user)

        response = patrol_point_api.get_index_page()

        assert response.status_code == 200
        assert "<title>巡检点位管理</title>" in response.text
        assert "/amcs/monitorArea/findPage" in response.text
        assert "/amcs/monitorArea/import" in response.text

    @allure.title("巡检点位列表返回标准分页结构")
    def test_patrol_point_page_contract(self, auth_api, patrol_point_api, test_user):
        """校验列表总数和数据行使用稳定的分页字段。"""
        self._login(auth_api, test_user)

        body = patrol_point_api.list_points(rows=5).json()

        assert isinstance(body["total"], int)
        assert isinstance(body["rows"], list)
        assert len(body["rows"]) <= 5

    @allure.title("巡检点位列表遵守 rows 分页大小")
    def test_patrol_point_page_respects_rows(self, auth_api, patrol_point_api, test_user):
        """校验请求一条记录时接口不会返回额外数据。"""
        self._login(auth_api, test_user)

        body = patrol_point_api.list_points(rows=1).json()

        assert len(body["rows"]) == min(body["total"], 1)

    @allure.title("巡检点位数据行包含设备、摄像机和预置位字段")
    def test_patrol_point_row_contains_core_fields(self, auth_api, patrol_point_api, test_user):
        """校验首条巡检点位具备列表展示和编辑回查所需字段。"""
        self._login(auth_api, test_user)

        row = patrol_point_api.list_points(rows=1).json()["rows"][0]

        assert set(row) >= {
            "id",
            "subName",
            "equipId",
            "monitorequipId",
            "equipName",
            "cameraName",
            "presetName",
            "presetNum",
        }
        assert isinstance(row["id"], str) and row["id"]
        assert re.fullmatch(r"\d+", row["presetNum"])

    @allure.title("巡检点位新增页面包含保存和下发能力")
    def test_patrol_point_add_page_contains_save_actions(self, auth_api, patrol_point_api, test_user):
        """校验新增页面加载核心表单以及保存并下发脚本。"""
        self._login(auth_api, test_user)

        response = patrol_point_api.get_edit_page()

        assert response.status_code == 200
        assert 'id="editForm"' in response.text
        assert "saveMonitorArea" in response.text
        assert "/js/monitor/editArea.js" in response.text

    @allure.title("巡检点位设备接口返回设备和摄像机列表")
    def test_patrol_point_equipment_list(self, auth_api, patrol_point_api, test_user):
        """校验新增点位所需设备树可正常加载且包含身份字段。"""
        self._login(auth_api, test_user)

        rows = patrol_point_api.list_equipment().json()

        assert isinstance(rows, list) and rows
        assert set(rows[0]) >= {"id", "text"}

    @allure.title("不存在设备的已用预置位查询返回空列表")
    def test_patrol_point_unknown_equipment_has_no_existing_presets(
        self,
        auth_api,
        patrol_point_api,
        test_user,
    ):
        """校验无效设备标识不会返回其他摄像机的预置位数据。"""
        self._login(auth_api, test_user)

        body = patrol_point_api.list_existing_presets("NO_SUCH_EQUIP_ID").json()

        assert body == {"status": 0, "message": "", "data": []}

    @allure.title("不存在名称筛选不会命中巡检点位")
    def test_patrol_point_unknown_keyword_returns_empty_rows(self, auth_api, patrol_point_api, test_user):
        """校验唯一无效关键字筛选后的总数和数据行保持一致。"""
        self._login(auth_api, test_user)

        body = patrol_point_api.list_points({"keyword": "NO_SUCH_POINT_KEYWORD_9F7A"}).json()

        assert body["total"] == 0
        assert body["rows"] == []
