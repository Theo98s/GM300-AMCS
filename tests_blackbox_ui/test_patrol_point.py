"""巡检点位 UI 筛选正反例及查询条件恢复。"""
from uuid import uuid4
import allure
import pytest
from playwright.sync_api import expect
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
    rows = view.all_filtered_rows(body)
    assert all(value in (row.get(column) or "") for row in rows)
    assert sample["id"] in {row["id"] for row in rows}


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


@allure.title("UI 巡检点位下一页与上一页正确切换")
def test_page_forward_and_back(point_page):
    """检查相邻页不重复，返回首页后恢复原记录集合。"""
    view, first = point_page
    if first["total"] <= len(first["rows"]):
        pytest.skip("当前数据不足两页，无法验证翻页")
    second = view.change_page("next")
    assert second["rows"]
    assert second["total"] == first["total"]
    assert not {row["id"] for row in first["rows"]}.intersection(row["id"] for row in second["rows"])
    restored = view.change_page("prev")
    assert [row["id"] for row in restored["rows"]] == [row["id"] for row in first["rows"]]


@allure.title("UI 巡检点位切换每页条数")
@pytest.mark.parametrize("size", [20, 50])
def test_page_size(point_page, size):
    """切换分页大小后同时检查显示条数、总数与原始记录保留。"""
    view, first = point_page
    body = view.change_page_size(size)
    assert body["total"] == first["total"]
    assert len(body["rows"]) == min(size, body["total"])
    assert {row["id"] for row in first["rows"]} <= {row["id"] for row in body["rows"]}


@allure.title("UI 在第二页发起新查询后回到第一页")
def test_filter_resets_page(point_page):
    """确保新查询不会沿用旧页码而出现假空结果。"""
    view, first = point_page
    if first["total"] <= len(first["rows"]):
        pytest.skip("当前数据不足两页")
    sample = next((row for row in first["rows"] if row.get("presetName")), None)
    if sample is None:
        pytest.skip("当前环境没有预置位名称样本")
    view.change_page("next")
    body = view.search(keyword=sample["presetName"])
    assert body["rows"], "新查询不应沿用旧页码而漏掉已有样本"
    assert all(sample["presetName"] in (row.get("presetName") or "") for row in body["rows"])
    assert sample["id"] in {row["id"] for row in body["rows"]}
    expect(view.page.locator(".datagrid-pager input.pagination-num")).to_have_value("1")
    restored = view.search()
    assert [row["id"] for row in restored["rows"]] == [row["id"] for row in first["rows"]]


@allure.title("UI 未选择记录删除时提示选择记录")
def test_delete_without_selection(point_page):
    """仅点击未选择记录的删除按钮，不触发实际删除操作。"""
    view, baseline = point_page
    view.page.locator('#areaToolbar a[onclick="batchDelete();"]').click()
    expect(view.page.get_by_text("请选择一条记录来删除！", exact=True)).to_be_visible()
    expect(view.rows).to_have_count(len(baseline["rows"]))


@allure.title("UI 导入弹窗可打开关闭并重新打开")
def test_import_dialog_close_and_reopen(point_page):
    """验证弹窗关闭后不遮挡列表，再次打开仍显示文件选择入口。"""
    view, baseline = point_page
    dialog = view.open_import()
    window = dialog.locator("xpath=..")
    expect(dialog.locator('input[type="file"]')).to_have_count(1)
    window.locator(".panel-tool .icon-guanbi3").click()
    expect(dialog).not_to_be_visible()
    expect(view.rows).to_have_count(len(baseline["rows"]))
    view.open_import()


@allure.title("UI 未选择文件开始导入时显示必填提示")
def test_import_without_file(point_page):
    """不上传任何文件，验证页面必填校验和弹窗保留。"""
    view, _ = point_page
    dialog = view.open_import()
    dialog.locator('a[onclick="importMonitorArea();"]').click()
    expect(view.page.get_by_text("请选择需要导入的文件！", exact=True)).to_be_visible()
    expect(dialog).to_be_visible()
