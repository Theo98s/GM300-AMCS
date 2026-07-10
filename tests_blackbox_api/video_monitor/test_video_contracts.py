# -*- coding: utf-8 -*-
"""视频监控字段、空值、预置位、行与树结构契约测试。"""
from __future__ import annotations

import allure


class TestVideoContractsExtra:
    """补充校验预置位摄像机与树结构返回的稳定性。"""

    @allure.title("预置位摄像机列表前几项 id 保持唯一")
    def test_preset_camera_ids_are_unique(self, auth_api, video_api, test_user):
        """校验预置位摄像机列表第一页结果的 id 保持唯一。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = video_api.get_preset_cameras().json()["data"]
        ids = [item["id"] for item in body]
        assert len(ids) == len(set(ids))

    @allure.title("预置位摄像机列表可空所亭字段保持可空字符串契约")
    def test_preset_camera_station_fields_keep_nullable_string_contract(self, auth_api, video_api, test_user):
        """校验预置位摄像机的站点相关字段在返回记录中保持可空字符串契约。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = video_api.get_preset_cameras().json()["data"]
        for item in body[:5]:
            assert item["subId"] is None or isinstance(item["subId"], str)
            assert item["subName"] is None or isinstance(item["subName"], str)


class TestVideoFieldContractsExtra:
    """补充校验视频接口中的跨字段对齐关系。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("摄像机树前几条记录保持节点与模型图标一致")
    def test_camera_tree_first_rows_keep_icon_alignment_with_model(self, auth_api, video_api, test_user):
        """校验前几条摄像机树记录的节点图标与模型图标保持一致。"""
        self._login(auth_api, test_user)

        rows = video_api.get_camera_tree().json()[:5]
        for row in rows:
            assert row["iconCls"] == row["model"]["iconCls"]
            assert row["text"] == row["model"]["text"]
            assert row["url"] == row["model"]["url"]

    @allure.title("预置位摄像机前几条记录保持 customCode 与图标字段稳定")
    def test_preset_cameras_first_rows_keep_custom_code_and_icon_contract(self, auth_api, video_api, test_user):
        """校验前几条预置位摄像机记录保持非空 customCode 和图标样式字段。"""
        self._login(auth_api, test_user)

        rows = video_api.get_preset_cameras().json()["data"][:5]
        for row in rows:
            assert isinstance(row["customCode"], str)
            assert row["customCode"]
            assert isinstance(row["iconCls"], str)
            assert row["iconCls"]
            assert "iconfont" in row["iconCls"]

    @allure.title("摄像机树与预置位列表前几条记录保持 customCode 对齐")
    def test_video_views_first_rows_keep_custom_code_alignment(self, auth_api, video_api, test_user):
        """校验前几条摄像机树模型类型与预置位列表 customCode 保持对齐。"""
        self._login(auth_api, test_user)

        camera_rows = video_api.get_camera_tree().json()[:5]
        preset_rows = video_api.get_preset_cameras().json()["data"][:5]
        for camera_row, preset_row in zip(camera_rows, preset_rows):
            assert preset_row["id"] == camera_row["id"]
            assert preset_row["customCode"] == camera_row["model"]["type"]


class TestVideoNullableContractsMore:
    """补充校验视频接口中的可空字段和默认值模式。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("摄像机树前几条记录保持空子节点和空站点标识")
    def test_camera_tree_first_rows_keep_empty_children_and_null_subid(self, auth_api, video_api, test_user):
        """校验前几条摄像机树记录保持空 children 和空 subId 模式。"""
        self._login(auth_api, test_user)

        rows = video_api.get_camera_tree().json()[:5]
        for row in rows:
            assert row["children"] == []
            assert row["model"]["children"] == []
            assert row["model"]["subId"] is None
            assert row["model"]["url"] == ""

    @allure.title("预置位摄像机前几条记录保持可空元数据字段")
    def test_preset_cameras_first_rows_keep_nullable_metadata_fields(self, auth_api, video_api, test_user):
        """校验前几条预置位摄像机记录保持当前可空元数据字段模式。"""
        self._login(auth_api, test_user)

        rows = video_api.get_preset_cameras().json()["data"][:5]
        for row in rows:
            assert row["typeName"] is None
            assert row["subId"] is None
            assert row["subName"] is None
            assert row["equipCode"] is None
            assert row["cameraIndexCode"] is None
            assert row["equipTypeCode"] is None
            assert row["ptypeName"] is None

    @allure.title("预置位摄像机前几条记录保持空子节点和默认布尔值")
    def test_preset_cameras_first_rows_keep_empty_children_and_false_flags(self, auth_api, video_api, test_user):
        """校验前几条预置位摄像机记录保持空 children 与默认布尔标记。"""
        self._login(auth_api, test_user)

        rows = video_api.get_preset_cameras().json()["data"][:5]
        for row in rows:
            assert row["children"] == []
            assert row["moveable"] is False
            assert row["railMachine"] is False


class TestVideoPresetContractsMore:
    """补充校验预置位摄像机行级格式。"""

    @allure.title("预置位前五项展示文本与设备名保持一致")
    def test_preset_camera_first_rows_keep_text_and_name_alignment(self, auth_api, video_api, test_user):
        """校验前几条预置位记录的 text 与 equipName 保持一致。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        rows = video_api.get_preset_cameras().json()["data"][:5]
        for row in rows:
            assert row["text"] == row["equipName"]

    @allure.title("预置位前五项通道号保持数字字符串")
    def test_preset_camera_first_rows_keep_digit_channel_numbers(self, auth_api, video_api, test_user):
        """校验前几条预置位记录的通道号保持数字字符串格式。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        rows = video_api.get_preset_cameras().json()["data"][:5]
        for row in rows:
            assert isinstance(row["channelNo"], str)
            assert row["channelNo"].isdigit()


class TestVideoRowContractsMore:
    """补充校验摄像机树和预置位列表的行级契约。"""

    @allure.title("视频树前五项 id 唯一且默认展开未勾选")
    def test_camera_tree_first_rows_keep_unique_open_unchecked_contract(self, auth_api, video_api, test_user):
        """校验前五条摄像机树记录保持唯一 id 和默认展开未勾选状态。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = video_api.get_camera_tree().json()[:5]
        ids = [item["id"] for item in body]
        assert len(ids) == len(set(ids))
        for item in body:
            assert item["checked"] is False
            assert item["state"] == "open"

    @allure.title("预置位前五项通道号与视频树模型通道号保持一致")
    def test_first_preset_rows_keep_channel_alignment_with_camera_tree(self, auth_api, video_api, test_user):
        """校验前几条预置位记录在通道号上与前几条摄像机树模型保持对齐。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        camera_rows = video_api.get_camera_tree().json()[:5]
        preset_rows = video_api.get_preset_cameras().json()["data"][:5]
        for camera_row, preset_row in zip(camera_rows, preset_rows):
            assert preset_row["channelNo"] == str(camera_row["model"]["channelNum"])
            assert preset_row["channelNo"].isdigit()


class TestVideoTreeContractsMore:
    """补充校验摄像机树与预置位摄像机的一致性。"""

    @allure.title("视频树前几项模型类型保持非空并带模块前缀")
    def test_camera_tree_first_models_keep_expected_type_prefix(self, auth_api, video_api, test_user):
        """校验前几条摄像机模型的 type 字段保持非空并带有预期模块前缀。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = video_api.get_camera_tree().json()
        for node in body[:3]:
            assert node["model"]["type"].startswith("GM300_CAMS_SP_")

    @allure.title("预置位摄像机前几项轨道机字段保持布尔类型")
    def test_preset_camera_first_rows_keep_boolean_rail_machine_field(self, auth_api, video_api, test_user):
        """校验前几条预置位摄像机记录的 railMachine 字段保持布尔值。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = video_api.get_preset_cameras().json()["data"]
        for item in body[:5]:
            assert isinstance(item["railMachine"], bool)
