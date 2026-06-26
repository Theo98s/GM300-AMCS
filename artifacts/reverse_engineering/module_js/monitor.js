var tableId = '#dg';
var tableUrl = ctx + '/monitor/page';
var alarmClassId = '#alarmClass';
var equipNameId = '#equipName';
var pointAddressId = '#pointAddress';
var alarmDatatypeId = '#alarmDatatype';
var searchButId = "#searchButId";
var cleanButId = "#cleanButId";
var sourceId = "#source";
var addButId = "#addButId";
var importButId = "#importButId";
var deleteButId = "#deleteButId";
var editPageId = "editPageId";
var importPageId = "importPageId";
var syncPhmtDcButId = "#syncPhmtDcButId";
var clearPhmtDcButId = "#clearPhmtDcButId";


/**
 * åå§åæ°æ®å­å¸æ°æ®
 */
function initDicData() {
    $(alarmClassId).combobox({
        url: ctx + '/home/listDictNoRoot/CAMS_ALAM_DATACLASS',
        valueField: 'code',
        textField: 'name'
    });
}

/**
 * åå§åæç´¢è¡¨å
 */
function initEvent() {
    $(searchButId).click(function () {
        search();
    });
    $(cleanButId).click(function () {
        clean();
    });
    $(addButId).click(function () {
        edit();
    });

    $(deleteButId).click(function () {
        batchDelete();
    });

    $(importButId).click(function () {
        openImportPage();
    });

    $(syncPhmtDcButId).click(function () {
        syncMonitorPhmtDc();
    });
    $(clearPhmtDcButId).click(function () {
        clearMonitorPhmtDc();
    });
}

function commonGetRequest(url) {
    $.ajax({
        url: url,
        data: {},
        type: "get",
        dataType: "json",
        success: function (result) {
            disLoad();
            if (result.status == 0) {
                reloadTable();
                Msg.success("æç¤º", result.message);
            } else {
                Msg.error("éè¯¯", result.message);
            }
        },
        error: function (error) {
            disLoad();
            console.log(error);
        }
    });
}

function openImportPage() {
    var url = ctx + '/monitor/openImportPage';
    var title = 'å¯¼å¥å¯¼åºçæ§ç¹';
    $("<div/>").dialog({
        id: importPageId,
        href: url,
        title: title,
        width: 450,
        height: 200,
        modal: true,
        onClose: function () {
            $("#" + importPageId).dialog('destroy'); //éæ¯dialogå¯¹è±¡
        },
        onLoad: function () {
            $("#" + importPageId).dialog('dialog').find('.dialog-button a').css('margin-left', '0px');
        },
        buttons: [{
            text: 'å³é­',
            position: 'center',
            iconCls: 'iconfont icon-guanbi',
            handler: function () {
                $("#" + importPageId).dialog('destroy'); //éæ¯dialogå¯¹è±¡
            }
        }]
    });
}


function batchDelete() {
    var rows = $(tableId).datagrid('getSelections');
    if (rows.length <= 0) {
        Msg.warning("è­¦å", "è¯·éæ©è®°å½å é¤ï¼");
        return;
    }
    let monitors = [];
    for (var i = 0; i < rows.length; i++) {
        let monitor = {};
        monitor.id = rows[i].id;
        monitor.equipName = rows[i].equipName;
        monitor.alarmDataType = rows[i].alarmDatatype;
        monitors.push(monitor);
    }
    deleteAlarmDataType(rows, monitors);
}

/*å é¤èå¨ç®¡ç*/
function deleteAlarmDataType(rows, monitors) {

    let idMonitorMap = {};
    monitors.forEach(e => idMonitorMap[e.id] = e);
    let monitorIds = Object.keys(idMonitorMap);
    $.ajax({
        url: ctx + '/monitor/canDeleteMonitor/',
        data: monitorIds.join(","),
        type: "post",
        contentType: "application/plain",
        dataType: "json",
        cache: false,
        success: function (result) {
            disLoad();
            if (result.status == 0) {
                let map = result.data;
                let data = map.image;
                let canDelete = true;
                let tips = "";
                if (data && data.length > 0) {
                    for (let i = 0; i < data.length; i++) {
                        let errorId = data[i];
                        let obj = idMonitorMap[errorId];
                        if (errorId == obj.id) {
                            tips += "è®¾å¤åç§°ï¼â" + obj.equipName + "âï¼å±æ§ï¼â" + obj.alarmDataType + "â<br/>";
                        }
                    }

                    if (tips) {
                        canDelete = false;
                        $("#remindMsg_dialog").dialog("open");
                        var tipHtml = "ä»¥ä¸è®¾å¤ççæ§ç¹å±æ§å·²ç¨äºå¾åè¯å«éç½®çè¯å«é¡¹ï¼è¯·åå é¤ç¸åºå¾åè¯å«éç½®æåæ´å¶è¯å«é¡¹ååè¡å é¤çæ§ç¹ã<br/>";
                        tips = tipHtml + "<font style='color:Lightcoral;'>" + tips + "</font><br>";
                    }
                }

                if (canDelete) {
                    doDelete(monitorIds);
                } else {
                    $("#dg").datagrid('unselectAll');
                    $("#remindMsg_dialog").dialog("open");
                    $("#remindMsg_dialog").html(tips);
                }
            } else {
                doDelete(monitorIds);
            }
        },
        error: function () {
            disLoad();
            doDelete(monitorIds);
        }
    });
}

function doDelete(idList) {
    $.messager.confirm('æç¤º', 'ç¡®å®è¦å é¤éå®ç' + idList.length + 'ä¸ªçæ§ç¹åï¼', function (r) {
        if (r) {
            load();
            let monitorIdListJson = JSON.stringify(idList);
            $.ajax({
                url: ctx+'/monitor/deleteMonitorByIds',
                data: monitorIdListJson,
                type: "post",
                contentType: "application/json;charset=utf-8",
                dataType: "json",
                cache: false,
                success: function (result) {
                    disLoad();
                    if (result.status == 0) {
                        reloadTable();
                        Msg.success("æç¤º", result.message);
                    } else {
                        Msg.error("éè¯¯", result.message);
                    }
                },
                error: function () {
                    disLoad();
                    reloadTable();
                    Msg.error("éè¯¯", "å é¤å¤±è´¥!");
                }
            });
        } else {
            disLoad();
        }
    });
}

function reloadTable() {
    $(tableId).datagrid('unselectAll');
    $(tableId).datagrid('reload');
}

function edit(id) {

    var url = ctx + '/monitor/toEditPage?id=' + id;
    var title = 'æ°å¢çæ§ç¹';
    if (id) {
        title = 'ç¼è¾çæ§ç¹';
    }

    $("<div/>").dialog({
        id: editPageId,
        href: url,
        title: title,
        width: '95%',
        height: '90%',
        modal: true,
        onClose: function () {
            $("#" + editPageId).dialog('destroy'); //éæ¯dialogå¯¹è±¡
        },
        onLoad: function () {

        },
        buttons: [{
            text: 'ä¿å­',
            position: 'center',
            iconCls: 'iconfont icon-zhengque',
            handler: function () {
                load();
                try {
                    let monitorData = getMonitorData();
                    //éªè¯å±æ§åç¹è¡¨å°åæ¯å¦å­å¨ã
                    $.ajax({
                        url: ctx + "/monitor/validateMonitor",
                        method: 'post',
                        data: JSON.stringify(monitorData),
                        contentType: "application/json;charset=utf-8",
                        dataType: 'json',
                        async: false,
                        success: function (res) {
                            if (res) {
                                if (res.status == 0) {
                                    $.ajax({
                                        url: ctx + "/monitor/saveOrUpdate",
                                        data: JSON.stringify(monitorData),
                                        type: "post",
                                        contentType: "application/json;charset=utf-8",
                                        dataType: "json",
                                        success: function (result) {
                                            disLoad();
                                            if (result.status == 0) {
                                                $("#" + editPageId).dialog('destroy'); //éæ¯dialogå¯¹è±¡
                                                reloadTable();
                                                Msg.success("æç¤º", result.message);
                                            } else {
                                                Msg.error("éè¯¯", result.message);
                                            }
                                        },
                                        error: function (error) {
                                            disLoad();
                                            console.log(error);
                                        }
                                    });
                                } else {
                                    Msg.error("éè¯¯", res.message);
                                    disLoad();
                                }
                            }
                        },
                        error: function (error) {
                            disLoad();
                            console.log(error);
                        }

                    });


                } catch (e) {
                    disLoad();
                    console.log("çæ§ç¹ä¿å­å¤±è´¥ï¼", e);
                    Msg.error("éè¯¯", e.message);
                }
            }
        },
            {
                text: 'å³é­',
                position: 'center',
                iconCls: 'iconfont icon-guanbi',
                handler: function () {
                    $("#" + editPageId).dialog('destroy'); //éæ¯dialogå¯¹è±¡
                }
            }]
    });
}


/**
 * æ¥è¯¢
 */
function search() {
    $(tableId).datagrid('load', getSearchCondition());
}

/**
 * è·åæ¥è¯¢æ¡ä»¶
 */
function getSearchCondition() {
    let obj = {};
    obj.alarmClass = $(alarmClassId).combobox('getValue');
    obj.securityequiptype = $('#securityequiptype').combobox('getValue');
    obj.equipName = $(equipNameId).textbox('getValue');
    obj.alarmDatatype = $(alarmDatatypeId).textbox('getValue');
    obj.scadaAddr10 = $(pointAddressId).textbox('getValue');
    return obj;
}

/**
 * æ¸é¤æ¥è¯¢æ¡ä»¶
 */
function clean() {
    resetAll();
}

$(function () {
    initDataGrid();
    initDicData();
    initEvent();
});
let first = true;

/**
 * åå§ååè¡¨
 */
function initDataGrid() {
    $(tableId).datagrid({
        url: tableUrl,
        singleSelect: false,
        multiSort: true,
        border: false,
        fit: false,
        rownumbers: true,
        fitColumns: false,
        pagination: true,
        checkOnSelect: true,
        idField: 'id',
        checkbox: true,
        frozenColumns: [[
            {title: 'id', field: 'id', checkbox: true/*,width: 50*/},
            {field: 'linkageStatus', title: "èå¨ç¶æ", align: 'center', formatter: formatLinkageStatus, width: 100},
            {field: 'operate', title: "æä½", align: 'center', formatter: formatOperation, width: 120},
            {field: 'securityequiptypeName', title: 'è®¾å¤å¤§ç±»', align: 'center', width: 120},
            {field: 'equipName', title: 'è®¾å¤åç§°', align: 'center', width: '25%'},
            {field: 'alarmDatatype', title: 'å±æ§', width: '25%'},
            {field: 'alarmClass', title: 'æ°æ®ç±»å', align: 'center', formatter: formatAlarmClass, width: 120},
            {field: 'scadaAddr10', title: 'ç¹ä½å°å', align: 'center', width: 120}
        ]],
        onLoadSuccess: function (data) {
            if (first) {
                search();
                first = false;
            }

        }
    });

}

/**
 * æ ¼å¼åæä½å
 * @param val
 * @param row
 * @param index
 */
function formatOperation(val, row, index) {
    var opStr = '<a href="javascript:void(0);" onclick="edit(\'' + row.id + '\');" title="ç¼è¾" class="tx_green" >ç¼è¾</a>&nbsp;&nbsp;&nbsp;';
    return opStr;
}

/**
 * æ ¼å¼åèå¨ç¶æ
 * @param val
 * @param row
 * @param index
 */
function formatLinkageStatus(val, row, index) {
    return val ? (val == 0 ? 'åç¨' : 'å¯ç¨') : "-";
}



