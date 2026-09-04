"""巡检点位 UI 筛选正反例及查询条件恢复。"""
from uuid import uuid4
import allure
import pytest
from tests_blackbox_ui.pages.patrol_point_page import PatrolPointPage


@pytest.fixture
def point_page(logged_in_page):
    """打开列表并保存基线样本。"""
    view = PatrolPointPage(logged_in_page)
    return view, view.open()


@allure.title("UI 单条件过滤后每条记录都满足条件")
@pytest.mark.parametrize("field,column", [("equipName", "equipName"), ("cameraName", "cameraName"), ("keyword", "presetName")])
def test_filter_matches_every_row(point_page, field, column):
    """按模糊查询语义逐行校验，并确认目标记录存在。"""
    view, baseline = point_page
    sample = next((row for row in baseline["rows"] if row.get(column)), None)
    if sample is None:
        pytest.skip(f"当前环境没有可用于 {column} 查询的样本")
    value = sample[column]
    body = view.search(**{field: value})
    assert body["rows"], "已有样本未查询到结果"
    assert all(value in (row.get(column) or "") for row in body["rows"])
    assert sample["id"] in {row["id"] for row in body["rows"]}


@allure.title("UI 不存在条件返回空表格和零总数")
@pytest.mark.parametrize("field", ["equipName", "cameraName", "keyword"])
def test_unknown_filter_returns_empty(point_page, field):
    """每个筛选项独立覆盖负例，防止服务端忽略参数。"""
    view, _ = point_page
    body = view.search(**{field: f"UI_NONE_{uuid4().hex}"})
    assert body["rows"] == []
    assert body["total"] == 0


@allure.title("UI 组合查询条件按交集过滤")
def test_combined_filter_requires_both_conditions(point_page):
    """有效设备名称搭配不存在摄像机，必须返回空结果。"""
    view, baseline = point_page
    sample = next((row for row in baseline["rows"] if row.get("equipName")), None)
    if sample is None:
        pytest.skip("当前环境没有设备名称样本")
    body = view.search(equipName=sample["equipName"], cameraName=f"UI_NONE_{uuid4().hex}")
    assert body["total"] == 0
    assert body["rows"] == []


@allure.title("UI 清空筛选后恢复原始列表")
def test_clear_filters_restores_list(point_page):
    """先筛选空结果再清空条件，验证总数和列表记录恢复。"""
    view, baseline = point_page
    assert baseline["rows"], "恢复测试需要至少一条基线数据"
    assert view.search(keyword=f"UI_NONE_{uuid4().hex}")["total"] == 0
    restored = view.search()
    assert restored["total"] == baseline["total"]
    assert {row["id"] for row in restored["rows"]} == {row["id"] for row in baseline["rows"]}
