let linkageLiId = "linkage_id_";
let linkageEnableId = "linkage_enable_id_";
let formId = "form_id_";
let hiddenDataId = "hidden_data_id_";
let commandId = "command_id_";
let linkequipId = "linkequip_id_";
let controlEquipId = "control_quip_id_";
let relateEquipId = "relate_equip_id_";
let multiPresetId = "multi_preset_id_";
let propId = "prop_id_";
let residenceTimeId = "residenceTime_id_";
let videoTypeRadioId = "videoTypeRadio_id_";
let controlTypeRadioId = "controlTypeRadio_id_";
let linkResourceULId = "#linkage_list";
let remoteControlId='remote_control_id_';


/**
 * æ¯å¦ä¸ºå¯ç§»å¨å·¡æ£è®¾å¤
 */
let equipOnMoveableMap = {};

let videoDivId = "video_id_";
let controlDivId = "control_id_";

var LINKAGE_INDEX = 1;

let conditionFlag = "conditionFlag_";


let relateEquipData = [];
let controlEquipData = [];
let controlEquipAttributeData = {};
let equipControlCommandData = {};
let cameraPresetData = [];
let multiPresetData = [];

$(function(){
    initRelateEquipData();
    initControlEquipData();
    initCameraData();
});

function ajaxAsync(url, callback){
    $.ajax({
        url: url,
        method: 'get',
        async: false,
        dataType: "json",
        success: function(result) {
            if (result && callback) {
                callback(result);
            }
        }
    });
}
function initRelateEquipData() {
    ajaxAsync(ctx + '/amcs/monitorArea/queryEquipPresetList', function(result) {
        relateEquipData = result.map((ele, index, arr) => {
            return {
                equipId: ele.equipId,
                equipName: ele.equipName
            }
        });
    });
}
function initControlEquipData(){
    ajaxAsync(ctx + '/monitor/queryMonitorByType?type=YK', function(result){
        controlEquipData = result.map((ele, index, arr) => {
            {
                let attributeArr = controlEquipAttributeData[ele.equipId] || [];
                attributeArr.push(ele);
                controlEquipAttributeData[ele.equipId] = attributeArr;
            }

            {
                let ykArr = JSON.parse(ele.yk);
                let controlCommandArr = equipControlCommandData[ele.id] || []
                for(let i in ykArr){
                    let ykItem = ykArr[i];
                    let button_name =ykItem["BUTTON_NAME"];
                    let send_value = ykItem["SEND_VALUE"];
                    controlCommandArr.push({
                        sendValue:send_value,
                        buttonName:button_name,
                    })
                }
                equipControlCommandData[ele.id]= controlCommandArr;
            }
            return {
                equipId: ele.equipId,
                equipName: ele.equipName
            };
        });
    });
}
function initCameraData(){
    ajaxAsync(ctx + '/amcs/monitorArea/queryCameraPresetList', function(result){
        cameraPresetData = result.map((ele) => {
            return {
                equipId: ele.equipId,
                id: ele.id,
                equipName: ele.equipName
            }
        });
    });
}


function addLinkageByIndex(index, conditionIndex) {
    let tmpId = linkageLiId + index;
    conditionIndex = conditionIndex ? conditionIndex : "";
    let theConditionFlag = conditionFlag + conditionIndex;
    let html = "<li id='" + tmpId + "' index='" + index + "' conditionFlag='" + theConditionFlag + "'>";
    html += "<fieldset style='padding:5px 0px;'>";
    html += "<legend>å¯ç¨èå¨èµæº<input id='" + linkageEnableId + index + "' type='text' class='easyui-checkbox' name='isEnable'  data-toggle='topjui-checkbox' data-options='onChange:changeLinkage'/></legend>";
    html += "<form id='" + formId + index + "'>";
    html += "<input type='hidden' id='" + hiddenDataId + index + "' name='id' />";
    html += "<input type='hidden' value='" + index + "' name='exeNo' />";
    html += "<lit class='linkageType'><lit>èå¨ç±»å&nbsp;&nbsp;&nbsp;<input class='easyui-radiobutton' id='" + videoTypeRadioId + index + "' name='linktype' data-options='onChange:changeLinkType' index='" + index + "' value='1' label='è§é¢'> </lit><lit><input class='easyui-radiobutton' id='" + controlTypeRadioId + index + "' data-options='onChange:changeLinkType' name='linktype' index='" + index + "' value='2' label='æ§å¶'></lit></lit>";
    html += videoTypeLinkageHtml(index);
    html += controlTypeLinkageHtml(index);
    html += "</form>";
    html += "</fieldset>";
    html += "</li>";
    $(linkResourceULId).append(html);
    $.parser.parse("#" + tmpId);
    ulSubLibindClick('linkage_list');
    bindLinkageEvent(index,conditionIndex);
    setClear(tmpId);
}

function setClear(id){
    let arrEle = $("#"+id).find("*[addClear]");
    forEachSetAddClear(arrEle);
}

function selectVideoLinkage(index) {
    $("#" + videoTypeRadioId + index).radiobutton("check", true);
}

function checkLinkType(index) {
    $("#" + linkageEnableId + index).checkbox("check");
}

function bindLinkageEvent(index,conditionIndex) {
    $("#" + relateEquipId + index).combobox({
        data:relateEquipData,
        valueField: 'equipId',
        textField: 'equipName',
        onChange: function (newValue,oldValue) {
            // var data = cameraPresetData.filter(ele=>ele.equipId==newValue);
            let data = [];
            $.ajax({
                //amcs/monitorArea/queryEquipPresetList
                url:ctx+'/amcs/monitorArea/queryCameraList?equipId='+newValue,
                method:'get',
                async:false,
                success:function(res){
                    if(res && res.status ==0){
                        data = res.data;
                    }

                }
            });

            $("#" + linkequipId + index).combobox('clear');
            $("#" + linkequipId + index).combobox('loadData', data);
            $('#' + multiPresetId + index).combobox('clear');
        }
    });


    $("#" + linkequipId + index).combobox({
        data: cameraPresetData,
        valueField: 'id',
        textField: 'equipName',
        onSelect: function (ret) {
            let theConditionFlag = conditionFlag + conditionIndex;
            let lis = $(linkResourceULId).find("li[conditionFlag=" + theConditionFlag + "]");
            let i;
            let exists = false;
            for (i = 0; i < lis.length; i++) {
                let li = lis[i];
                let theIndex = $(li).attr("index");
                if(theIndex != index){
                    let theId = $("#" + linkequipId + theIndex).combobox('getValue');
                    if(exists = (theId == ret.id)){
                        $('#' + linkequipId + index).combobox('setValue', '');
                        $('#' + multiPresetId + index).combobox('loadData', []);
                        $('#' + multiPresetId + index).combobox('setValue', '');
                        let equipName = ret.equipName;
                        Msg.error(equipName+" å·²å­å¨ï¼");
                        return;
                    }
                }
            }
            if(!exists){
                judgeOnMoveable(ret.id);
                queryPresetList(ret.id, index);
            }
        },
        onUnselect: function () {
            $('#' + multiPresetId + index).combobox('setValue', '');
            $('#' + multiPresetId + index).combobox('loadData', []);
        },
        onLoadSuccess: function () {
            let loadedLinkage = getLoadedLinkage(index);
            if(loadedLinkage){
                $("#" + linkequipId + index).combobox('setValue', loadedLinkage?.linkequip);
            }
        },
    });

    $("#" + controlEquipId + index).combobox({
        data:controlEquipData,
        valueField: 'equipId',
        textField: 'equipName',
        onSelect: function (ret) {
            queryAttribute(ret.equipId, index);
        },
        onLoadSuccess: function (data) {
            let loadedLinkage = getLoadedLinkage(index);
            if(loadedLinkage) {
                $("#" + controlEquipId + index).combobox('setValue', loadedLinkage.linkequip);
            }
        },
    });
}

function queryAttribute(equipId, index) {
    $("#" + propId + index).combobox({
        data: controlEquipAttributeData[equipId]||[],
        valueField: 'alarmDatatype',
        textField: 'alarmDatatype',
        onSelect: function (ret) {
            queryRemoteControl(ret.id,index);
        },
        onUnselect: function (ret) {
            $('#' + remoteControlId + index).combobox('setValue', '');
        },
        onLoadSuccess: function (data) {
            let loadedLinkage = getLoadedLinkage(index);
            if(loadedLinkage) {
                $("#" + propId + index).combobox('setValue', loadedLinkage.monitorequip);
            }
        },
    });
}

function queryRemoteControl(monitorTypeId,index){
    $('#'+remoteControlId+index).combobox({
        data: equipControlCommandData[monitorTypeId]||[],
        method:'get',
        valueField: 'sendValue',
        textField: 'buttonName',
        panelHeight:100,
        onLoadSuccess: function (data) {
            let loadedLinkage = getLoadedLinkage(index);
            if(loadedLinkage) {
                $("#" + remoteControlId + index).combobox('setValue', loadedLinkage.isremote == 1 ? 'true' : 'false');
            }
        },
    });
}

function judgeOnMoveable(equipId){
    let flag = equipOnMoveableMap[equipId];
    if(isEmpty(flag)){
        $.ajax({
            type: "get",
            url: ctx+"/amcs/video/equip/onMoveable",
            async:false,
            data: { equipId: equipId },
            success: function (result) {
                equipOnMoveableMap[equipId] = result.data;
            },
            error: function (err) {
                console.log("/amcs/video/equip/onMoveable",err)
            }
        });
    }

}

function singlePresetOnMoveable(index,value){
    let equipId = $( "#" + linkequipId + index).combobox('getValue');
    let onMoveable = equipOnMoveableMap[equipId];
    let moveablePreset = null;
    let multiPresetArr =  $("#" + multiPresetId + index).combobox("getValues");
    if(onMoveable && multiPresetArr.length > 0 && (moveablePreset = multiPresetArr[0]) != value){
        Msg.error("ç§»å¨å·¡æ£è®¾å¤è¥éè¦è°ç¨å¤ä¸ªé¢ç½®ä½ï¼å¯éç¨æ¡ä»¶è§¦åå·¡æ£ã");
        let theId = '#' + multiPresetId + index;
        setTimeout(function(){
            $(theId +" ~ span:first").find("input[value='"+value+"']").remove();
            $(theId).combobox("clear");
            $(theId).combobox('setValues',[moveablePreset]);
        },100)
    }
}

function queryPresetList(equipId, index) {
    let theRelatedEquipId = $("#" + relateEquipId + index).combobox('getValue');
    theRelatedEquipId = theRelatedEquipId ? theRelatedEquipId : "";
        ajaxAsync(ctx + '/amcs/monitorArea/preset/list?equipId=' + equipId + '&pid=' + theRelatedEquipId, function(result){
            multiPresetData[index] = result.map((ele, index, arr) => {
                return {
                    valueField: ele.valueField,
                    presetPointName: ele.presetPointName
                }
            });
        })
    $('#' + multiPresetId + index).combobox({
        data: multiPresetData[index] || [],
        valueField: 'valueField',
        textField: 'presetPointName',
        onLoadSuccess: function () {
            let loadedLinkage = getLoadedLinkage(index);
            if (loadedLinkage) {
                $("#" + multiPresetId + index).combobox('setValues', loadedLinkage.monitorequip?.split(","));
            }
        },
        onSelect: function (ret) {
            singlePresetOnMoveable(index,ret.valueField);
        }
    });
}

function changeLinkage(ret) {
    let theIndex = $(this).parent().parent().parent().attr("index");

    let validate = $("#" + formId + theIndex).form("validate");
    if (!ret && !validate) {
        $(this).checkbox("check");
        return;
    }

    let status = ret ? "enable" : "disable";
    $("#" + videoTypeRadioId + theIndex).radiobutton(status);
    $("#" + controlTypeRadioId + theIndex).radiobutton(status);
    //disable readonly
    $("#" + residenceTimeId + theIndex).textbox(status);
    $("#" + residenceTimeId + theIndex).textbox(status);
    $("#" + relateEquipId + theIndex).combobox(status);
    $("#" + linkequipId + theIndex).combobox(status);
    $("#" + multiPresetId + theIndex).combobox(status);
    $("#" + commandId + theIndex).switchbutton(status);
    $("#" + controlEquipId + theIndex).combobox(status);
    $("#" + propId + theIndex).combobox(status);
    $("#" + remoteControlId  + theIndex).combobox(status);
}

function changeLinkType(ret) {
    let theIndex = $(this).attr("index");
    let options = $(this).radiobutton('options');
    let value = options.value;
    let checked = options.checked;
    let theControlEquipId = "#" + controlEquipId + theIndex;
    let thePropIdId = "#" + propId + theIndex;
    let theRelateEquipId = "#" + relateEquipId + theIndex;
    let theLinkequipId = "#" + linkequipId + theIndex;
    let theMultiPresetId = "#" + multiPresetId + theIndex;
    let theRemoteControlIdId='#'+remoteControlId + theIndex;
    $(thePropIdId).combobox("setValue", '');
    $(theControlEquipId).combobox("setValue", '');
    $(theRelateEquipId).combobox("setValue", '');
    $(theLinkequipId).combobox("setValue", '');
    $(theMultiPresetId).combobox("setValue", '');
    $(theRemoteControlIdId).combobox("setValue", '');
    if (value == 1 && checked) {
        $("#" + videoDivId + theIndex).show();
        $("#" + controlDivId + theIndex).hide();

        $(thePropIdId).combobox({
            required: false
        });
        $(theControlEquipId).combobox({
            required: false
        });
        $(theLinkequipId).combobox({
            required: true
        });
        $(theMultiPresetId).combobox({
            required: true
        });
        $(theRemoteControlIdId).combobox({
            required: false
        });
    } else {
        $("#" + videoDivId + theIndex).hide();
        $("#" + controlDivId + theIndex).show();


        $(thePropIdId).combobox({
            required: true
        });
        $(theControlEquipId).combobox({
            required: true
        });

        $(theRelateEquipId).combobox({
            required: false
        });
        $(theLinkequipId).combobox({
            required: false
        });
        $(theMultiPresetId).combobox({
            required: false
        });
        $(theRemoteControlIdId).combobox({
            required: true
        });
    }
}

/**
 * ç¨äºåæ¾ä½¿ç¨,åæ¾å®æ¯éæ¯
 * @type {*[]}
 */
let loadedLinkageArr = undefined
function setLoadedLinkageArr(linkageArr){
    loadedLinkageArr = loadedLinkageArr ? [...loadedLinkageArr,...linkageArr] : [...linkageArr]
}

function clearLoadedLinkageArr(){
    loadedLinkageArr = undefined;
}

function getLoadedLinkage(index){
    if(loadedLinkageArr && loadedLinkageArr.length != 0
        && loadedLinkageArr.length >= index
        && loadedLinkageArr[index - 1]){
        return loadedLinkageArr[index - 1];
    }
    return undefined;
}

function loadLinkage(conditionIndex, linkageIndex, linkage) {
    let videoLinkage = "1";
    let controlLinkage = "2";

    $("#" + hiddenDataId + linkageIndex).val(linkage.id);
    if (videoLinkage == linkage.linktype) {
        $("#" + videoTypeRadioId + linkageIndex).radiobutton("check", true);
        $("#" + residenceTimeId + linkageIndex).textbox("setValue", linkage.residenceTime);
        $("#" + linkequipId + linkageIndex).combobox('reload', cameraPresetData);

        if(!linkage.monitorequip){
            $("#" + multiPresetId + linkageIndex).combobox('loadData', []);
        }

    } else if (controlLinkage == linkage.linktype) {
        $("#" + controlTypeRadioId + linkageIndex).radiobutton("check", true);
        $("#" + controlEquipId + linkageIndex).combobox('reload');
        $("#" + propId + linkageIndex).combobox('reload');
        $("#" + remoteControlId + linkageIndex).combobox('reload');

    }
    setTimeout(function () {
        $("#" + linkageEnableId + linkageIndex).checkbox(linkage.isenable == 1 ? 'check' : 'uncheck');
    }, 550);

}

function videoTypeLinkageHtml(index) {
    let html = "<div id='" + videoDivId + index + "' class='linkageDiv'>";
    html += "<p class='linkage'>";
    html += "<lit>åçæ¶é´&nbsp;<input class='easyui-textbox' style='width: 50px' id='" + residenceTimeId + index + "' name='residenceTime' value='5' type='number' /></lit>";
    html += "<lit><select addClear='true' class='easyui-combobox' style='width: 195px;' id='" + relateEquipId + index + "' name='relateEquip'   prompt='å³èè®¾å¤' /></lit>";
    html += "<lit><select addClear='true' class='easyui-combobox' style='width: 195px;' id='" + linkequipId + index + "' name='linkequip'   prompt='æåæº'  editable='false' required /></lit>";
    html += "</p>";
    html += "<lit class='multiPreset' >é¢ç½®ä½&nbsp;<select addClear='true' style='width: 460px' class='easyui-combobox' id='" + multiPresetId + index + "'  data-options='multiple:true,multiline:true' editable='false' id='" + multiPresetId + index + "' name='monitorequip'  prompt='è¯·éæ©...' editable='false' addClear required /></lit>";
    html += "</div>";
    return html;
}

function controlTypeLinkageHtml(index) {
    let html = "<div id='" + controlDivId + index + "' class='linkageDiv'>";
    html += "<p class='linkage'>";
  //  html += "<lit>é¥æ§å½ä»¤&nbsp;<input id='" + commandId + index + "' class='easyui-switchbutton' data-options='onText:\"å¯å¨\",offText:\"åæ­¢\",height:\"26px\"' ></lit>";
    html += "<lit><select addClear='true' class='easyui-combobox' id='" + controlEquipId + index + "' style='width: 190px' name='linkequip'   prompt='ç®æ è®¾å¤' required /></lit>";
    html += "<lit><select addClear='true' style='width: 190px' class='easyui-combobox' id='" + propId + index + "'  prompt='å±æ§' editable='false' required /></lit>";
    html += "<lit><select addClear='true' style='width: 110px' class='easyui-combobox' id='" + remoteControlId + index + "'  prompt='é¥æ§å½ä»¤' editable='false' required /></lit>";
    html += "</p>";
    html += "</div>";
    return html;
}

function showCurLinkage(conditionIndex) {
    let showConditionFlag = conditionFlag + conditionIndex;
    let lis = $(linkResourceULId)[0].children;
    let i;
    for (i = 0; i < lis.length; i++) {
        let theConditionFlag = $(lis[i]).attr("conditionFlag");
        if (theConditionFlag == showConditionFlag) {
            $(lis[i]).show();
        } else {
            $(lis[i]).hide();
        }
    }
}


function delLinkageByConditionIndex(index) {
    let theConditionFlag = conditionFlag + index;
    let lis = $(linkResourceULId).find("li[conditionFlag=" + theConditionFlag + "]");
    let i;
    for (i = 0; i < lis.length; i++) {
        let li = lis[i];
        /*let index = $(li).attr("index");
        //è·åèå¨id
        let id = $(hiddenDataId + index).val();
        if (id) {


        }*/
        li.remove();
    }

}

function delClickLinkage() {
    let selector = linkResourceULId + " li.clickli";
    var li = $(selector)[0];
    if (!li) {
        Msg.error("è¯·éæ©éè¦å é¤çèå¨èµæºï¼");
        return;
    }
    $.messager.confirm('æç¤º', 'ç¡®å®è¦å é¤éå®çèå¨èµæºåï¼', function (r) {
        if (r) {

            let index = $(li).attr("index");

            //è·åèå¨id
            // parent.setDelLinkakgeIds($("#" + hiddenDataId + index).val());
            li.remove();
        }
    });
}


function moveLinkage(direction) {
    let selector = linkResourceULId + " li.clickli";
    let theLi = $(selector)[0];
    let theConditionFlag = $(theLi).attr("conditionFlag");
    let moveLi;
    switch (direction) {
        case "up":
            moveLi = $(selector).prev("li[conditionFlag=" + theConditionFlag + "]")[0];
            break;
        case "down":
            moveLi = $(selector).next("li[conditionFlag=" + theConditionFlag + "]")[0];
            break;
    }
    if (moveLi && theLi && $(moveLi).attr("conditionFlag") == $(theLi).attr("conditionFlag")) {
        swapExeNo(moveLi, theLi)
        var newNode = document.createElement('li');
        moveLi.parentNode.insertBefore(newNode, moveLi)
        moveLi.parentNode.insertBefore(moveLi, theLi)
        moveLi.parentNode.insertBefore(theLi, newNode)
        moveLi.parentNode.removeChild(newNode)
    }
}

function swapExeNo(theLi, otherLi) {
    let otherExeNoInput = $(otherLi).find("input[name=exeNo]");
    let theExeNoInput = $(theLi).find("input[name=exeNo]");
    let otherExeNo = otherExeNoInput.val();
    let theExeNo = theExeNoInput.val();
    otherExeNoInput.val(theExeNo);
    theExeNoInput.val(otherExeNo);
}

function getLinkageIndex(){
    let temp = LINKAGE_INDEX;
    ++LINKAGE_INDEX;
    return temp;
}

function addLinkage(conditionIndex, linkageIndex) {
    let theIndex = linkageIndex ? linkageIndex : getLinkageIndex();
    addLinkageByIndex(theIndex, conditionIndex);
    checkLinkType(theIndex);
    selectVideoLinkage(theIndex);
}


function getLinkage(conditionIndex) {
    let theConditionFlag = conditionFlag + conditionIndex;
    let linkageList = $(linkResourceULId).find("li[conditionFlag=" + theConditionFlag + "]");
    let linkageArr;
    if (linkageList) {
        linkageArr = [];
        let VIDEO = "1";
        let CONTROL = "2";
        for (let i = 0; i < linkageList.length; i++) {
            let index = $(linkageList[i]).attr('index');
            let theFormId = '#' + formId + index;
            let validate = $(theFormId).form('validate');
            if (!validate) {
                throw new Error("è¯·æ£æ¥èå¨éç½®æ¯å¦å¡«åå®æ¯ï¼");
            }
            let json = $(theFormId).serializeJSON();
            json.linktype = $("#" + videoTypeRadioId + index).radiobutton('options').checked ? VIDEO : CONTROL;
            let theLinkageEnableId = "#" + linkageEnableId + index;
            let isenableOptions = $(theLinkageEnableId).checkbox("options");
            json.isenable = isenableOptions.checked ? 1 : 0;
            json.relateEquip = null;
            json.linkequip = $("#" + linkequipId + index).combobox('getValue');

            if (json.linktype == VIDEO) {
                json.isremote = null;
                let exeNo = json.exeNo;
                let multiPresetArr = $("#" + multiPresetId + index).combobox("getValues");
                for (let j = 0; j < multiPresetArr.length; j++) {
                    let obj = {};
                    for (key in json) {
                        obj[key] = json[key];
                    }
                    obj.monitorequip = multiPresetArr[j];
                    obj.exeNo = exeNo++;
                    linkageArr.push(obj);
                }
            } else if (json.linktype == CONTROL) {
                json.residenceTime = null;
                json.linkequip = null;
                json.linkequip = $("#" + controlEquipId + index).combobox('getValue');
                json.monitorequip = $("#" + propId + index).combobox('getValue');
                let theCommandId = "#" + remoteControlId + index;
                json.isremote = $(theCommandId).combobox('getValue')=='true' ? 1 : 0;
                linkageArr.push(json);
            }
        }
    }
    return linkageArr;
}