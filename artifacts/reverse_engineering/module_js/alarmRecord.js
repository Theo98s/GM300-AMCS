let dg = $('#dg');
let sd = $('#startDate');
let ed = $('#endDate');
let at = $('#alarmType');
let mn = $('#monitorName');
let dataRowMap = null;
$(function () {
    initDg();
});

/**
 * åå§ådataGrid
 */
function initDg() {
    dg.datagrid({
        columns: [[
            {field: 'alarmLevel', title: 'çº§å«', width: '5%', align: 'center',formatter:formatterAlarmLevel},
            {field: 'alarmDt', title: 'æ¥è­¦æ¶é´', width: '12%', align: 'center'},
            {field: 'securityequiptype', title: 'è®¾å¤å¤§ç±»', width: '10%', align: 'center',formatter:formatterSecurityEquipType},
            {field: 'alarmSource', title: 'æ¥è­¦æ¥æº', width: '10%', align: 'center',formatter:formatterAlarmSource},
            {field: 'alarmType', title: 'æ¥è­¦ç±»å', width: '10%', align: 'center',formatter:formatterAlarmType},
            {field: 'monitor', title: 'çæ§ç¹', width: '14%', align: 'center',formatter:formatEquipName},
            {field: 'warnContent', title: 'å¼', width: '9%', align: 'center'},
            {field: 'recoverDt', title: 'æ¢å¤æ¶é´', width: '12%', align: 'center'},
            {field: 'recoverValue', title: 'æ¢å¤å¼', width: '9%', align: 'center'},
            {field: 'op', title: 'æä½', width: '10%', align: 'center',formatter:formatterOperation}

        ]],
        pagination: true,
        rownumbers: true,
        pageSize: 20,
        pageList: [10, 20, 30, 40, 50, 100],
        fit:true,
        queryParams: getQueryParams(),
        singleSelect:true,
        loader: function (param, success, error) {
            $.ajax({
                url: ctx+'/alarmRecord/getPageData',
                method: 'post',
                contentType: 'application/json;charset=utf-8',
                dataType: 'json',
                data: JSON.stringify(param),
                success: function (result) {
                    dataRowMap = {}
                    for(let i = 0; i < result.data.rows.length;i++){
                        let row = result.data.rows[i];
                        dataRowMap[row.id] = row;
                    }
                    if (result && result.status == 0) {
                        success(result.data);

                    }

                },
                error: function (result) {
                    error(result);
                }
            });
        }
    });
}

function query(){
    let param = getQueryParams();
    dg.datagrid("reload",param);
}

function exportAlarmRecord(){
    let param = getQueryParams();
    let urlSuffix ='';
    if(param.startDate){
        urlSuffix += "&startDate="+param.startDate;
    }
    if(param.endDate){
        urlSuffix += "&endDate="+param.endDate;
    }
    if(param.alarmType){
        urlSuffix += "&alarmType="+param.alarmType;
    }
    if(param.monitorName){
        urlSuffix += "&monitorName="+param.monitorName;
    }
    location.href = ctx+'/amcs/excel_2019/export?templateName=alarmRecord.xls&downloadName=æ¥è­¦è®°å½'+urlSuffix;
}
/**
 * è·åæ¥è¯¢åæ°
 */
function getQueryParams() {
    let startDate = sd.datebox("getValue");
    let endDate = ed.datebox("getValue");
    let alarmType = at.combobox("getValue");
    let monitorName = mn.textbox("getValue");
    let alarmSource = $("#alarmSource").combobox("getValue");
    let param = {};
    if(startDate) {
        param.startDate = new Date(startDate).getTime();
    }
    if(endDate) {
        param.endDate = new Date(endDate).getTime()+(24 * 60 * 60 * 1000 -1);
    }
    if(alarmSource) {
        param.alarmSource = alarmSource;
    }
    if(alarmType) {
        param.alarmType = alarmType;
    }
    if(monitorName) {
        param.monitorName = monitorName;
    }
    return param;
}

function formatterAlarmLevel(val, row, index) {
    return getValueByCodeAndType(row.alarmLevel, ALAM_LEVEL);
}

function formatterSecurityEquipType(val, row, index) {
    return formatSecurityEquipType(val);
}

function formatterAlarmType(val, row, index) {
    return formatAlarmType(val);
}
function formatterAlarmSource(val, row, index) {
    return formatAlarmSource(val);
}
function formatEquipName(val, row, index) {
    let content = row.equipName;
    if (row.alarmDataType) {
        content += '.' + row.alarmDataType;
    }
    return content;
}

function formatterOperation(val, row) {
    let html = '';
    html += '&nbsp;&nbsp;<a href="#" class="tx_blue" onclick="getCameraPresetInfo(\'' + row.id + '\' , \'' + row.hasLink + '\')">æ¥ç</a>';
    if (row.hasLink === '1') {
        let alarmDate = Date.parse(row.alarmDt);
        html += '&nbsp;&nbsp;<a href="#" class="tx_green" onclick="getCameraInfo(\'' + row.id + '\', ' + alarmDate + ' )">è§é¢åæ¾</a>'
    }
    return html;
}

function getCameraPresetInfo(alarmId, hasLink) {
    //è°ç¨åå°è·åæ°æ®
    $.ajax({
        url: ctx + '/amcs/realTimeAlarm/alarmCameraPresetsInfo?id=' + alarmId,
        contentType: "application/json",
        method: 'get',
        cache: false,
        success: function (result) {
            if (result.status === 0) {
                details(alarmId, hasLink, result.data);
            } else {
                Msg.error("è·åé¢ç½®ä½æåæºä¿¡æ¯å¤±è´¥ï¼");
            }
        },
        error: function () {
            Msg.error("è·åé¢ç½®ä½æåæºä¿¡æ¯å¤±è´¥ï¼");
        }
    });
}
function details(id, hasLink, data) {
    //è¯·æ±æ°æ®ï¼åæ¸²ææå¼dialogé¡µé¢
    let url;
    let width = $(window).width();
    let height;
    let videoInfos = [];
    let row = dataRowMap[id];
    if (hasLink === '1') {
        url = ctx + '/amcs/realTimeAlarm/alarmVideo?id=' + id + '&hasLink=' + hasLink;
        width = width * 0.76;
        height = 640;
        if (data && data.length > 0) {
            videoInfos = data;
        }
    }else if(row.trendAlarm && row.trendAlarm == '1'){
        url = ctx + '/amcs/realTimeAlarm/alarmTrend?id=' + id;
        width = 1000;
        height = 500;
    } else {
        url = ctx + '/amcs/realTimeAlarm/alarmDetail?id=' + id;
        width = 350;
        height = 500;
    }
    $('<div></div>').dialog({
        id: 'alarm_details_dialog_portal',
        title: 'æ¥è­¦è¯¦æ',
        href: url,
        width: width,
        height: height,
        draggable: false,
        modal: true,
        onClose: function () {
            $('#alarm_details_dialog_portal').dialog('destroy');
            if (hasLink === '1') {
                alarmDetailVideoDialog.closeVideo();
            }
        },
        onLoad: function () {
            alarmDetailVideoDialog.initVideoList(videoInfos);
            if (videoInfos && videoInfos.length > 0) {
                let params = {
                    divId: 'alarmVideoDiv',
                    offset: {},
                    playMode: 0,
                    controlArr:[7],
                    layout: '1x1'
                }
                params.callback = function () {
                	videoProxy.registEventListener('CALLBACK_PTZ', applyCameraAuthBy);
                    alarmDetailVideoDialog.playFirstVideo(videoInfos[0]);
                }
                alarmDetailVideoDialog.initVideoPlayer(params);
            }
        }
    });
}
function getCameraInfo(alarmId, alarmTime) {
    //è°ç¨åå°è·åæ°æ®
    $.ajax({
        url: ctx + '/amcs/realTimeAlarm/alarmCamerasInfo?id=' + alarmId,
        contentType: "application/json",
        method: 'get',
        cache: false,
        success: function (result) {
            if (result.status === 0) {
                showPlaybackVideo(result.data, alarmTime);
            } else {
                Msg.error("è·åé¢ç½®ä½æåæºä¿¡æ¯å¤±è´¥ï¼");
            }
        },
        error: function () {
            Msg.error("è·åé¢ç½®ä½æåæºä¿¡æ¯å¤±è´¥ï¼");
        }
    });
}

function showPlaybackVideo(camerasInfo, alarmTime) {
    let url = ctx + '/amcs/monitorLink/showPlaybackVideo?userV2=yes';
    $('<div></div>').dialog({
        id: 'gateway_actions_record_playVideoByPlugin_dialog',
        title: 'è§é¢åæ¾',
        width: 950,
        height: 625,
        closed: false,
        cache: false,
        draggable: false,
        modal: true,
        href: url,
        onClose: function () {
            $('#gateway_actions_record_playVideoByPlugin_dialog').dialog('destroy');
            //éæ¯è§é¢çªå£
            playbackDialog.closeVideo();
        },
        onLoad: function () {
            //åå§ååè¡¨
            //let startTimeStamp = alarmTime - 24 * 60 * 60 * 1000;
            let startTimeStamp = alarmTime - playbackPlaytimeLead * 1000;
            let endTimeStamp = startTimeStamp + playbackPlaytimeRange * 60 * 1000;
            let playTimeStamp = startTimeStamp;
            //let playTimeStamp = alarmTime - 15 * 1000;
            console.log('preset count', camerasInfo.length)
            var videoInfos = playbackDialog.mergePreset(camerasInfo, startTimeStamp, endTimeStamp, playTimeStamp);
            console.log('camera count', videoInfos.length)
            playbackDialog.initVideoList(videoInfos);
            let layout = "1x1";
            if(videoInfos.length ==2){
                layout = "2r";
            }else if(videoInfos.length>2){
                layout = "2x2";
            }
            //é»è®¤æ­æ¾ç¬¬ä¸ä¸ª
            let params = {
                divId: 'videoDiv',
                offset: {},
                playMode: 1,
                layout: layout,
            }
            params.callback = function () {
                // playbackDialog.playFirstVideo(videoInfos[0]);
                playbackDialog.playAllVideo(videoInfos)
            }

            playbackDialog.initVideoPlayer(params, true);
        },
        buttons: [{
            text: 'å³é­',
            position: 'center',
            iconCls: 'iconfont icon-roundclose',
            handler: function () {
                $("#gateway_actions_record_playVideoByPlugin_dialog").dialog('destroy'); //éæ¯dialogå¯¹è±¡
                playbackDialog.closeVideo();
            }
        }]
    });
}