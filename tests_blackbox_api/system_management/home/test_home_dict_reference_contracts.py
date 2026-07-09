# -*- coding: utf-8 -*-
"""More AMCS home-dictionary reference contract tests."""
from __future__ import annotations

import allure


@allure.feature("首页接口")
class TestHomeDictReferenceContracts:
    """Extra checks for stable EQUIP_AREA reference data."""

    @allure.title("设备区域字典数量保持为十三项")
    def test_equip_area_dict_count_is_stable(self, auth_api, home_api, test_user):
        """Verify the current EQUIP_AREA dictionary exposes thirteen entries."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = home_api.list_dict_no_root("EQUIP_AREA").json()
        assert len(body) == 13

    @allure.title("设备区域字典关键编码映射保持稳定")
    def test_equip_area_dict_core_code_mapping_is_stable(self, auth_api, home_api, test_user):
        """Verify core EQUIP_AREA codes still map to the expected area names."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = home_api.list_dict_no_root("EQUIP_AREA").json()
        area_map = {item["code"]: item["name"] for item in body}
        assert area_map["02"] == "主变区"
        assert area_map["04"] == "控制室"
        assert area_map["10"] == "屋顶"
        assert area_map["12"] == "其他"

