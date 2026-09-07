"""巡检点位 UI 筛选正反例及查询条件恢复。"""
from uuid import uuid4
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
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


@pytest.fixture
def prevent_point_writes(point_page):
    """取消编辑用例禁止保存、删除和导入请求，意外写入会被阻断并判失败。"""
    view, _ = point_page
    attempts = []

    def guard(route):
        """保留真实只读请求，阻止点位写接口访问现场。"""
        path = urlsplit(route.request.url).path
        if path in {"/amcs/monitorArea/save", "/amcs/monitorArea/delete", "/amcs/monitorArea/import"}:
            attempts.append(path)
            route.abort()
        else:
            route.continue_()

    view.page.route("**/amcs/monitorArea/**", guard)
    yield
    view.page.unroute("**/amcs/monitorArea/**", guard)
    assert not attempts, f"只读操作意外触发写请求：{attempts}"


@allure.title("UI 查看巡检点位时详情字段与列表一致")
@pytest.mark.parametrize("field,control", [("equipName", "mainEquipId"), ("cameraName", "monitorequipId"), ("presetName", "presetName")])
def test_view_detail_matches_list(point_page, prevent_point_writes, field, control):
    """检查打开的记录标识、只读参数及用户实际看到的字段值。"""
    view, baseline = point_page
    if not baseline["rows"]:
        pytest.skip("没有可查看的巡检点位")
    sample = baseline["rows"][0]
    frame, iframe = view.open_form("view")
    query = parse_qs(urlsplit(iframe.get_attribute("src")).query)
    assert query["id"] == [sample["id"]]
    assert query["readonly"] == ["1"]
    expect(view.form_input(frame, control)).to_have_value(sample.get(field) or "")


@allure.title("UI 查看巡检点位时核心字段只读且无可用保存入口")
def test_view_is_readonly(point_page, prevent_point_writes):
    """验证核心字段不能编辑，查看页不应提供可用的保存或下发按钮。"""
    view, baseline = point_page
    if not baseline["rows"]:
        pytest.skip("没有可查看的巡检点位")
    frame, _ = view.open_form("view")
    for control in ("mainEquipId", "monitorequipId", "mainPresetNum", "presetName"):
        expect(view.form_input(frame, control)).not_to_be_editable()
    # 允许模板保留隐藏或禁用按钮，但查看页不能提供可用写入入口。
    buttons = frame.locator('a[onclick^="saveMonitorArea"]:visible:not(.l-btn-disabled):not([disabled]):not([aria-disabled="true"])')
    expect(buttons).to_have_count(0)
    view.close_form()
    expect(view.rows).to_have_count(len(baseline["rows"]))


@allure.title("UI 编辑点位关闭不保存时原名称保持不变")
def test_edit_cancel_preserves_name(point_page, prevent_point_writes):
    """仅在浏览器中修改名称，关闭后重新查看应仍为原值。"""
    view, baseline = point_page
    if not baseline["rows"]:
        pytest.skip("没有可编辑的巡检点位")
    sample = baseline["rows"][0]
    frame, iframe = view.open_form("edit")
    assert parse_qs(urlsplit(iframe.get_attribute("src")).query)["id"] == [sample["id"]]
    name = view.form_input(frame, "presetName")
    expect(name).to_have_value(sample["presetName"])
    name.fill(f"UI_CANCEL_{uuid4().hex[:8]}")
    view.close_form()
    restored = view.search()
    assert restored["total"] == baseline["total"]
    row = next(row for row in restored["rows"] if row["id"] == sample["id"])
    assert row["presetName"] == sample["presetName"]
    frame, _ = view.open_form("view")
    expect(view.form_input(frame, "presetName")).to_have_value(sample["presetName"])


@allure.title("UI 新增点位关闭后不新增记录且再次打开为空表单")
def test_add_cancel_leaves_no_record(point_page, prevent_point_writes):
    """打开未填写的新增表单并关闭，验证列表不变及再次打开无旧记录残留。"""
    view, baseline = point_page
    frame, iframe = view.open_form("add")
    query = parse_qs(urlsplit(iframe.get_attribute("src")).query, keep_blank_values=True)
    assert query["id"] == [""]
    expect(view.form_input(frame, "presetName")).to_have_value("")
    expect(frame.locator('a[onclick="saveMonitorArea(0,false);"]')).to_be_visible()
    view.close_form()
    restored = view.search()
    assert restored == baseline
    frame, _ = view.open_form("add")
    expect(view.form_input(frame, "presetName")).to_have_value("")


@allure.title("UI 巡检点位导出按钮下载有效格式文件")
def test_export_download(point_page):
    """验证浏览器下载完成及真实 XLS 文件头，不将格式校验当成内容校验。"""
    view, _ = point_page
    download = view.download_export()
    assert download.suggested_filename.lower().endswith(".xls")
    with Path(download.path()).open("rb") as stream:
        assert stream.read(8) == bytes.fromhex("D0CF11E0A1B11AE1"), "下载内容不是预期 XLS 文件"
