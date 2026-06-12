var editAlarmClassId = '#editAlarmClass';
var editMonitorId = '#editMonitorId';
var editSecurityequiptypeId = '#editSecurityequiptype';
var editEquipId = '#editEquipId';
var monitorDeviceId = '#monitorDeviceId';
var needLoadmonitorDeviceId = true;
var editAlarmDatatypeId = '#editAlarmDatatype';
var editScadaAddr10Id = '#editScadaAddr10';

var monitorEditFrameId = "#monitorEditFrame";
var monitorJsonId = "#monitorJsonId";
var conditionLinkageJsonId = "#conditionLinkageJsonId";
var monitor;
var conditionLinkageArr;
var alarmClass;

let monitorEditId = "#monitorEditId";

let equipId;
let thatTypeName;
let TYPE_CONST = ['PSCADA','å¨çº¿çæµ']


function parseData() {
    monitor = null;
    let json = $(monitorJsonId).val();
    if(json){
        // è§£ç HTMLå®ä½
        json = $('<textarea>').html(json).text();
        try {
            monitor = JSON.parse(json);
        } catch (e) {
            console.error("è§£æ monitorJson å¤±è´¥:", e);
            console.error("JSON åå®¹:", json);
            if (json && json.length > 362) {
                console.error("Position 362 around:", json.substring(Math.max(0, 362 - 20), Math.min(json.length, 362 + 20)));
            }
        }
    }
    conditionLinkageArr = null;
    json = $(conditionLinkageJsonId).val();
    if(json){
        // è§£ç HTMLå®ä½
        json = $('<textarea>').html(json).text();
        try {
            conditionLinkageArr = JSON.parse(json);
        } catch (e) {
            console.error("è§£æ conditionLinkageJson å¤±è´¥:", e);
            console.error("JSON åå®¹:", json);
            if (json && json.length > 362) {
                console.error("Position 362 around:", json.substring(Math.max(0, 362 - 20), Math.min(json.length, 362 + 20)));
            }
        }
    }
}

$(function () {
    parseData();
    initEvent();
});

function initEvent(){
    $(editAlarmClassId).combobox({
        iconWidth: 20,
        icons: [{
            iconCls: 'iconfont icon-guanbi3',
            handler: function (e) {
                $(editAlarmClassId).combobox('clear');
            }
        }],
        onSelect:function(rec){

            open4YPage(rec.code);

        },
        onLoadSuccess:function(){
            var alarmClass = $(editAlarmClassId).combobox('getValue');
            if(alarmClass){
                open4YPage(alarmClass);
            }else{
                $(editAlarmClassId).combobox('setValue','01');
            }
        }
    });
    $(editSecurityequiptypeId).combobox({
        iconWidth: 20,
        icons: [{
            iconCls: 'iconfont icon-guanbi3',
            handler: function (e) {
                $(editSecurityequiptypeId).combobox('clear');
            }
        }],
        onSelect: function (res) {
            //éæ°ç»å®è®¾å¤ä¸æç­éæ¡ä»¶ãçæµè®¾å¤ä¸æç»ä»¶
            enableOrDisableDeviceInput(res.name);
            bindingEquipBySecurityName(res.name);
        },
        onLoadSuccess: function (data) {
            if (!thatTypeName && data && data.length > 0) {
                let sbcode = null;
                let auxiliaryId = null;
                for (let i = 0; i < data.length; i++) {
                    let value = data[i];
                    let text = value.text;
                    let code = value.code;
                    if (text == TYPE_CONST[0]) {
                        sbcode = code;
                    } else if (monitor  && monitor.securityequiptype == code) {
                        auxiliaryId = code;
                        thatTypeName = text;
                        break;
                    }
                }
                if (auxiliaryId) {
                    sbcode = auxiliaryId;
                }
                if (!thatTypeName) {
                    thatTypeName = TYPE_CONST[0];
                }

                $(editSecurityequiptypeId).combobox('setValue', sbcode);
            }
        }
    });
    $(monitorDeviceId).combobox({
        url: ctx + '/poms/equip/equipDicByType?equipType=GM300_CAMS_ZXJC',
        valueField: 'id',
        textField: 'equipName',
        iconWidth: 20,
        icons: [{
            iconCls: 'iconfont icon-guanbi3',
            handler: function (e) {
                $(monitorDeviceId).combobox('clear');
            }
        }],
        onLoadSuccess: function () {
            if (monitor && needLoadmonitorDeviceId) {
                $(monitorDeviceId).combobox("setValue", monitor.monitorDeviceId);
            }
        }
    });
    $(editScadaAddr10Id).textbox({
        iconWidth: 20,
        icons: [{
            iconCls: 'iconfont icon-guanbi3',
            handler: function (e) {
                $(editScadaAddr10Id).textbox('clear');
            }
        }]
    });
    $(editAlarmDatatypeId).textbox({
        iconWidth: 20,
        icons: [{
            iconCls: 'iconfont icon-guanbi3',
            handler: function (e) {
                $(editAlarmDatatypeId).textbox('clear');
            }
        }]
    })
}

function enableOrDisableDeviceInput(typeName) {
    $(monitorDeviceId).combobox({
        required: TYPE_CONST[1] == typeName
    });
    $(monitorDeviceId).combobox(TYPE_CONST[1] == typeName ? 'enable' : 'disable');
    if (!(TYPE_CONST[1] == typeName)) {
        $(monitorDeviceId).combobox('setValue', '');
        needLoadmonitorDeviceId =false;
    }
}

/*æ ¹æ®è®¾å¤å¤§ç±»ç»å®è®¾å¤ä¸æç­éæ¡ä»¶*/
function bindingEquipBySecurityName(securityName) {
    if(securityName == TYPE_CONST[1]) {
        securityName = TYPE_CONST[0];
    }
    $(editEquipId).combobox({
        url: ctx + '/poms/equip/findSubEquipList?searchType=all&securityName=' + securityName,
        valueField: 'id',
        textField: 'equipName',
        iconWidth: 20,
        limitToList:true,
        icons: [{
            iconCls: 'iconfont icon-guanbi3',
            handler: function (e) {
                $(editEquipId).combobox('clear');
            }
        }],
        onLoadSuccess: function (data) {
            let selectedId = $(editEquipId).combobox("getValue");
            if (data && data.length > 0 && selectedId ) {
                let one = data.filter(d=>d.id == selectedId);
                if(one.length == 0) {
                    $(editEquipId).combobox("setValue", '');
                    equipId = null;
                }
            }
            if (data && data.length > 0 && equipId && thatTypeName == securityName) {
                $(editEquipId).combobox("setValue", equipId);
                equipId = null;
            }
            
        },
        onSelect: function (record) {
            bingingSecurityNameByEquipId(record.id);
        }
    });
}

//æ ¹æ®è®¾å¤åéè®¾å¤å¤§ç±»
function bingingSecurityNameByEquipId(equipId) {
    $.ajax({
        url: ctx + '/poms/equip/bingingSecurityNameByEquipId?equipId=' + equipId,
        data: '',
        cache: false,
        success: function (result) {
            if (result && result.length > 0) {
                let rText = result[0].name;
                if(rText == TYPE_CONST[0] && $(editSecurityequiptypeId).combobox('getText') == TYPE_CONST[1]) {
                    return;
                }
                let rCode = result[0].code;
                $(editSecurityequiptypeId).combobox("select", rCode);
                $(editEquipId).combobox("setValue", equipId);
            }
        },
        error: function () {
        }
    });
}

function open4YPage(theAlarmClass) {
    alarmClass = theAlarmClass;
    switch (theAlarmClass) {
        case "01":
            if(monitor && !monitor.yx){
                monitor = null;
                conditionLinkageArr = null;
            }
            break;
        case "02":
            if(monitor && !monitor.yc){
                monitor = null;
                conditionLinkageArr = null;
            }
            break;
        case "03":
            if(monitor && !monitor.yk){
                monitor = null;
                conditionLinkageArr = null;
            }
            break;
        case "04":
            if(monitor && !monitor.yt){
                monitor = null;
                conditionLinkageArr = null;
            }
            break;
    }
    let url = ctx+"/monitor/open4YPage/"+alarmClass;
    $(monitorEditFrameId).attr('src',url);
    $(monitorEditFrameId).attr('style','width:100%; height:100%');
}

function getMonitorData(windowTop){
    let validate = windowTop ? windowTop.$(monitorEditId).form("validate") : $(monitorEditId).form("validate");
    if(!validate){
       throw new Error("è¯·å¡«åå¿è¦åæ°ï¼");
    }
    let obj = {};
    obj.id = windowTop ? windowTop.$(editMonitorId).val() : $(editMonitorId).val() ;
    obj.alarmClass = windowTop ? windowTop.$(editAlarmClassId).combobox('getValue') : $(editAlarmClassId).combobox('getValue');
    obj.securityequiptype = windowTop ? windowTop.$(editSecurityequiptypeId).combobox('getValue') : $(editSecurityequiptypeId).combobox('getValue');
    obj.scadaAddr10 =  windowTop ? windowTop.$(editScadaAddr10Id).textbox('getValue') : $(editScadaAddr10Id).textbox('getValue');
    obj.equipId = windowTop ? windowTop.$(editEquipId).textbox('getValue'):$(editEquipId).textbox('getValue');
    obj.monitorDeviceId = windowTop ? windowTop.$(editEquipId).textbox('getValue') : $(monitorDeviceId).textbox('getValue');
    obj.monitorDeviceName =  windowTop ? windowTop.$(monitorDeviceId).textbox('getText') : $(monitorDeviceId).textbox('getText');
    obj.alarmDatatype =  windowTop ? windowTop.$(editAlarmDatatypeId).textbox('getValue') : $(editAlarmDatatypeId).textbox('getValue');
    obj.delConditionIds =  windowTop ? windowTop.$("#delConditionIds").val() : $("#delConditionIds").val();
    if(monitor){
        obj.id = monitor.id;
    }
    let contentWindow = windowTop? windowTop.$(monitorEditFrameId)[0].contentWindow : $(monitorEditFrameId)[0].contentWindow;
    switch (obj.alarmClass) {
        case "01":
            setData(obj,contentWindow.getYxData());
            obj.conditions = contentWindow.getConditionLinkage();
            // getYxLinkage();
            break;
        case "02":
            setData(obj,contentWindow.getYcData());
            obj.conditions = contentWindow.getConditionLinkage();
            break;
        case "03":
             let ykDataTmp= contentWindow.getYkData();
            obj.yk = JSON.stringify(ykDataTmp);
            break;
        case "04":
           let ytDataTmp = contentWindow.getYtData();
            obj.yt = JSON.stringify(ytDataTmp);
            break;
    }
    return obj;
}

function setData(monitorData,fourYData){
    for(key in fourYData){
        monitorData[key] = fourYData[key];
    }
}

function getAlarmClass(){
    return $(editAlarmClassId).combobox('getValue');;
}

/*function setDelLinkakgeIds(linkageIds) {
    if(linkageIds){
        let ids = $("#delLinkageIds").val();
        ids = ids ? ids.split(",") : [];
        linkageIds = linkageIds.split(",");
        ids.push(linkageIds);
        $("#delLinkageIds").val(ids.join(","));
    }

}*/

function setDelConditionIds(conditionIds){
    if(conditionIds){
        let ids = $("#delConditionIds").val();
        ids = ids ? ids.split(",") : [];
        conditionIds = conditionIds.split(",");
        ids.push(conditionIds);
        $("#delConditionIds").val(ids.join(","));
    }
}