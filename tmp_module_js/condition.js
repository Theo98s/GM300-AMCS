let conditionLiId = "condition_li_id_";
let conditionListId = "#condition_list";

let addLinkageId = "addLinkage_id_";

var CONDITION_INDEX = 1;
let alarmTypeId = "alarmType_id_";
let alarmLevelId = "alarmLevel_id_";

let conditionIsenableId="conditionIsenable_id_";
let conditionId="condition_id_";
let trigeconditionId="trigecondition_id_";
let teleMinValueId="teleMinValue_id_";

let theConditionLinkageArr = parent.conditionLinkageArr;

let number = /^(\-|\+)?\d+(\.\d+)?$/;

var addConditionBtnId = "#addConditionBtn";
var delConditionBtnId = "#delConditionBtn";

let additionalInfoId = 'additionalInfo';


//let alarmDeadbandId = 'alarmDeadband';
// let alarmDeadbandEnableId = 'alarmDeadbandEnable';
// let alarmDeadbandDivId = 'alarmDeadbandDiv';

let thresholdId = "thresholdId_id_";
// let alarmDeadbandId = 'alarmDeadband_id_';
let lThresholdIds=[];
let hThresholdIds=[];

$(function () {
    loadThresholdIds();
    validate();
   if(theConditionLinkageArr){
       loadCondition(theConditionLinkageArr);
   }
})

function validate(){
    $.extend($.fn.validatebox.defaults.rules, {
        teleMinValue: {
            validator: function (value) {
                return number.test(value);
            },
            message: 'è¯·è¾å¥æææ°å¼ï¼'
        }
    });
}

function addConditionByIndex(index) {
    let tmpId = conditionLiId + index;
    let html = '<li id="' + tmpId + '" index="' + index + '">';
    html += '<form style="width:100%">';
    html += '<input type="hidden" name="id" id="' + conditionId + index + '">';
    html += '<p>';
    html += 'è§¦åæ¡ä»¶&nbsp<select class="easyui-combobox" id="' + trigeconditionId + index + '" name="trigecondition"  panelHeight="auto" style="width:110px;"><option value="3">è¶é«é</option><option value="2">è¶ä½é</option></select>';
    html += '</p><p>';
    html += 'éå¼ç¼å·&nbsp<input class="easyui-combobox" id="'+thresholdId+index+'" name="thresholdId" style="width:110px" data-options="prompt:\'è¯·éæ©...\',textField:\'name\',valueField:\'code\',panelHeight:\'150px\',editable:false" required >';
    html += '</p><p>';
    html += 'é&nbsp&nbsp&nbsp&nbsp&nbsp&nbspå¼&nbsp<input addClear="true" class="easyui-textbox" type="number" validType=\'teleMinValue\' id="' + teleMinValueId + index + '" name="teleMinValue" style="width:110px" required>';
    html += '</p>';
    html += '<p style="clear:both">';
    html += 'å¯ç¨æ¥è­¦&nbsp<input  class="easyui-checkbox" name="isenable" id="' + conditionIsenableId + index + '" >';
    html += '</p>';
    html += '<span id="'+additionalInfoId+index+'" >';
    html += '<p style="clear:both">';
    html += 'æ¥è­¦çº§å«&nbsp<input addClear="true" class="easyui-combobox" name="alarmLevel" id="' + alarmLevelId + index + '" data-options="url:\'' + ctx + '/dicData/listDictNoRoot/CAMS_ALAM_LEVEL\',method:\'get\',valueField: \'code\',textField: \'name\'"  panelHeight="auto" style="width:110px;">';
    html += '</p><p>';
    html += 'æ¥è­¦ç±»å&nbsp';
    html += '<input addClear="true" class="easyui-combobox" name="alarmType" id="' + alarmTypeId + index + '"  data-options="data:alamTypeData,valueField: \'code\',textField: \'name\'"  panelHeight="auto" style="width:110px;">';
    html += '</p>';
    /*html += 'æ¥è­¦æ­»åº&nbsp<input  class="easyui-textbox" value="0"  type="number" id="'+alarmDeadbandId+index+'" name="alarmDeadband"  style="width:110px" >';
    html += '</p></span>';*/
    html += '</span>';
    html += '<a class="easyui-linkbutton float_r" id="' + addLinkageId + index + '" style="margin:3px 10px 0px 0px;" data-options="iconCls:\'iconfont icon-tianjia tx_red\'">å¢å èå¨èµæº</a>';;
    html += '</form>';
    html += '</li>';
    $(conditionListId).append(html);
    $.parser.parse("#" + tmpId);
    bindLiClick('condition_list');
    bindConditionEvent(index);
    setClear(tmpId);
}

function addYxConditionByIndex(index) {
    let tmpId = conditionLiId + index;
    let html = '<li id="' + tmpId + '" index="' + index + '">';
    html += '<form>';
    html += '<input type="hidden" name="id" id="' + conditionId + index + '">';
    html += '<p>';
    html += '<lit>è§¦åæ¡ä»¶&nbsp;</lit>';
    html += '<select class="easyui-combobox" name="teleMinValue" id="' + trigeconditionId + index + '"  panelHeight="auto" style="width:110px;"><option value="true">true</option><option value="false">false</option></select>';
    html += '&nbsp&nbsp&nbspå¯ç¨æ¥è­¦&nbsp;<input class="easyui-checkbox" name="isenable" id="' + conditionIsenableId + index + '" >';
    html += '<a class="easyui-linkbutton float_r" id="' + addLinkageId + index + '" style="margin:3px 10px 0px 0px;" data-options="iconCls:\'iconfont icon-tianjia tx_red\'">å¢å èå¨èµæº</a>';
    html += '</p>';
    /* html += '<lit >';
     html += '</lit>';*/
    html += '<p id="'+additionalInfoId+index+'">';
    html += '<lit>æ¥è­¦çº§å«&nbsp;</lit>';
    html += '<input addClear="true" class="easyui-combobox" name="alarmLevel" id="' + alarmLevelId + index + '" data-options="url:\'' + ctx + '/dicData/listDictNoRoot/CAMS_ALAM_LEVEL\',method:\'get\',valueField: \'code\',textField: \'name\'"  panelHeight="auto" style="width:110px;">';
    html += '&nbsp&nbsp&nbspæ¥è­¦ç±»å&nbsp;';
    html += '<input addClear="true" class="easyui-combobox" name="alarmType" id="' + alarmTypeId + index + '"  data-options="data:alamTypeData,valueField: \'code\',textField: \'name\'"  panelHeight="auto" style="width:110px;">';
    html += '</p>';
    html += '</form>';
    html += '</li>';
    $(conditionListId).append(html);
    $.parser.parse("#" + tmpId);
    bindLiClick('condition_list');
    bindConditionEvent(index);
    setClear(tmpId);
}

function setClear(id){
    let arrEle = $("#"+id).find("*[addClear]");
    forEachSetAddClear(arrEle);
}

function loadCondition(conditionLinkageArr){
    let i;
    let j;
    let linkageIndex;
    for(i = 0; i < conditionLinkageArr.length; i++){
        let ele = conditionLinkageArr[i];
        let condition = ele.condition;
        let linkageList = ele.linkageList;
        let theIndex = i + 1;
        {
            let alarmClass = theMonitor.alarmClass;
            if("01" == alarmClass){
                addYxConditionByIndex(theIndex);
                $("#"+trigeconditionId+theIndex).combobox('setValue',condition.teleMinValue);
            }else if("02" == alarmClass){
                //addAlarmDeadband();
                /*if(i == 0){
                    $("#"+alarmDeadbandId).textbox('setValue',condition.alarmDeadband);
                    $("#"+alarmDeadbandEnableId).checkbox(condition.alarmDeadband ? 'check' : 'uncheck');
                }*/
                addConditionByIndex(theIndex);
                $("#"+trigeconditionId+theIndex).combobox('setValue',condition.trigecondition);
                $("#"+teleMinValueId+theIndex).textbox('setValue',condition.teleMinValue);
            }
            $("#"+conditionId+theIndex).val(condition.id);
            $("#"+conditionIsenableId+theIndex).checkbox(condition.isenable == 1 ? 'check' : 'uncheck');
            $("#"+alarmTypeId+theIndex).combobox('setValue',condition.alarmType);
            $("#"+alarmLevelId+theIndex).combobox('setValue',condition.alarmLevel);
            $("#"+thresholdId+theIndex).combobox('setValue',condition.thresholdId);
            // $("#"+alarmDeadbandId+theIndex).textbox('setValue',condition.alarmDeadband);
        }

        {
            if(linkageList && linkageList.length){
                linkageList.sort((a,b)=>{
                    return a.exeNo - b.exeNo;
                });
                setLoadedLinkageArr(linkageList);
                for (j = 0; j < linkageList.length; j++) {
                    linkageIndex = getLinkageIndex();
                    addLinkage(theIndex, linkageIndex);
                    loadLinkage(theIndex, linkageIndex, linkageList[j]);
                }
            }
        }
        $("#"+conditionLiId + 1).click();
    }
    clearLoadedLinkageArr();
    CONDITION_INDEX = conditionLinkageArr.length + 1;
}

function bindConditionEvent(index){
    let theAddLinkageId = "#"+addLinkageId+index;
    $(theAddLinkageId).click(function(){
        addLinkage(index);
    });

    /**
     * é»è®¤ä¸å¯ç¨æ¥è­¦
     */
    $("#"+additionalInfoId+index).hide();
    enableAlarm(false,"#"+alarmTypeId+index);
    enableAlarm(false,"#"+alarmLevelId+index);

    let theconditionIsenableId = "#" + conditionIsenableId + index;
    let yxAlarmClass = '01';
    let ycAlarmClass = '02';
    $(theconditionIsenableId).checkbox({
        onChange: function (ret) {
            if(ret){
                $("#"+additionalInfoId+index).show();
            }else{
                $("#"+additionalInfoId+index).hide();
            }
            enableAlarm(ret,"#"+alarmTypeId+index);
            enableAlarm(ret,"#"+alarmLevelId+index);
            // controlTextbox(ret,"#"+alarmDeadbandId+index);
            if(parent.alarmClass == yxAlarmClass && ret){
                let siblingIndex;
                if((siblingIndex = getOtherLiIndex(index)) >= 0){
                    $("#" + conditionIsenableId + siblingIndex).checkbox('uncheck');
                }
            }
        }
    });

    if(ycAlarmClass == parent.alarmClass){
        twoConditionSetValue(index,function(v){
            let value = '2';
            if(v == value){
                value = '3';
            }
            return value;
        });

        $('#' + trigeconditionId + index).combobox({
            onChange: function (newValue, oldValue) {
                if (newValue == '2') {
                    let value = $("#" + thresholdId + index).combobox('getValue');
                    if (value.indexOf('H') != -1) {
                        let obj = {};
                        obj.code = value;
                        obj.name = value;
                        hThresholdIds.push(obj);
                        hThresholdIds.sort(function(a,b){
                            return  a.code.localeCompare(b.code);
                        });
                    }
                    $("#" + thresholdId + index).combobox('loadData', lThresholdIds);
                    $("#" + thresholdId + index).combobox("setValue",'');
                } else {
                    let value = $("#" + thresholdId + index).combobox('getValue');
                    if (value.indexOf('L') != -1) {
                        let obj = {};
                        obj.code = value;
                        obj.name = value;
                        lThresholdIds.push(obj);
                        lThresholdIds.sort(function(a,b){
                            return  a.code.localeCompare(b.code);
                        });
                    }
                    $("#" + thresholdId + index).combobox('loadData', hThresholdIds)
                    $("#" + thresholdId + index).combobox("setValue",'');
                }
            }
        });

        $("#" + thresholdId + index).combobox({
            onChange: function (newValue, oldValue) {
                if (newValue.indexOf("H") != -1) {
                    for (let i = 0; i < hThresholdIds.length; i++) {
                        if (hThresholdIds[i].code == newValue) {
                            hThresholdIds.splice(i, 1);
                            break;
                        }
                    }
                    if(oldValue && oldValue !='') {
                        let obj = {};
                        obj.code = oldValue;
                        obj.name = oldValue;
                        hThresholdIds.push(obj);
                        hThresholdIds.sort(function(a,b){
                            return a.code.localeCompare(b.code);
                        });
                    }
                } else {
                    if (newValue.indexOf("L")!= -1) {
                        for (let i = 0; i < lThresholdIds.length; i++) {
                            if (lThresholdIds[i].code == newValue) {
                                lThresholdIds.splice(i, 1);
                                break;
                            }
                        }
                        if(oldValue && oldValue !='') {
                            let obj = {};
                            obj.code = oldValue;
                            obj.name = oldValue;
                            lThresholdIds.push(obj);
                            lThresholdIds.sort(function(a,b){
                                return  a.code.localeCompare(b.code);
                            });
                        }
                    }
                }
            },
            onShowPanel: function () {
                let value = $('#' + trigeconditionId + index).combobox('getValue');
                if (value == '2') {
                    $(this).combobox('loadData', lThresholdIds)
                } else {
                    $(this).combobox('loadData', hThresholdIds)
                }
            },
            icons:[{
                iconCls:'iconfont icon-aui-icon-close',
                handler: function(e){
                    let value = $("#" + thresholdId + index).combobox('getValue');
                    if (value.indexOf('H') != -1) {
                        let obj = {};
                        obj.code = value;
                        obj.name = value;
                        hThresholdIds.push(obj);
                        hThresholdIds.sort(function(a,b){
                            return  a.code.localeCompare(b.code);
                        });
                    }else{
                        let obj = {};
                        obj.code = value;
                        obj.name = value;
                        lThresholdIds.push(obj);
                        lThresholdIds.sort(function(a,b){
                            return  a.code.localeCompare(b.code);
                        });
                    }
                    $("#" + thresholdId + index).combobox('setValue','');
                }
            }]
        })

    }

    if(yxAlarmClass == parent.alarmClass){
        twoConditionSetValue(index,function(v){
            let value = 'true';
            if(v == value){
                value = 'false';
            }
            return value;
        });
        $("#" + trigeconditionId + index).combobox({
            onChange: function (newValue, oldValue) {
                twoConditionSetValue(index, function (v) {
                    let value = 'true';
                    if (v == value) {
                        value = 'false';
                    }
                    return value;
                });
            }
        });
    }
}

function twoConditionSetValue(index,callback){
    let siblingIndex;
    if((siblingIndex = getOtherLiIndex(index)) >= 0){
        let siblingTrigeconditionSelector = "#" + trigeconditionId + siblingIndex;
        let value = callback($(siblingTrigeconditionSelector).combobox('getValue'));
        $("#" + trigeconditionId + index).combobox('setValue',value);
    }
}

function getOtherLiIndex(index){
    let siblings = $("#"+conditionLiId + index).siblings("li");
    if(siblings.length == 1) {
        return $(siblings[0]).attr("index");
    }
    return -1;
}

function bindLiClick(id){
    $('#'+id).find('li').click(function(){
        $(this).addClass("clickli").siblings().removeClass("clickli");
        $('#'+id).find('div').removeClass("clickli");
        $(this).find('div').addClass("clickli");
        let theIndex = $(this).attr("index");
        showCurLinkage(theIndex);
    });
}

function delClickCondition(callback){
    let clickLiSelector = conditionListId + " li.clickli";
    let conditionLi = $(clickLiSelector)[0];
    if(!conditionLi){
        Msg.error("è¯·éæ©éè¦å é¤çè§¦åæ¡ä»¶ï¼");
        return;
    }
    $.messager.confirm('æç¤º', 'ç¡®å®è¦å é¤éå®çè§¦åæ¡ä»¶åï¼', function(r) {
        if (r) {
            let index = $(conditionLi).attr("index");
            let YC = "02";
            if(YC == parent.getAlarmClass()){
                let th =  $("#" + thresholdId + index).combobox('getValue');
                reloadThreshold(th);
            }
            //è·åæ¡ä»¶id
            parent.setDelConditionIds($("#"+conditionId+index).val());
            //å é¤å½åè§¦åæ¡ä»¶
            conditionLi.remove();
            //å é¤å½åèå¨èµæº
            delLinkageByConditionIndex(index);
            clickLiSelector = conditionListId + " li";
            let firstCondition =  $(clickLiSelector).first();
            if(firstCondition.length > 0){
                $(firstCondition).click();
            }else{
                $(conditionListId).empty();
            }
            if(callback){
                callback();
            }
        }
    });
}

function addCondition(){
    let temp = CONDITION_INDEX;
    ++CONDITION_INDEX;
    addConditionByIndex(temp);
}

function addYXCondition(){
    let temp = CONDITION_INDEX;
    ++CONDITION_INDEX;
    addYxConditionByIndex(temp);
}

function getConditionLinkage(){
    let lis = $("#condition_list li");
    let conditionArr;
    if(lis.length){
        let alarmClass = parent.getAlarmClass();
        let YX = "01";
       // let alarmDeadband = YX == alarmClass ? '' : $("#"+alarmDeadbandId).textbox('getValue');
        conditionArr = [];
        for(let i = 0; i < lis.length;i++){
            let form = $(lis[i]).find("form");
            let validate = form.form('validate');

            let theIndex = $(lis[i]).attr('index');
            if(!validate){
                throw new Error("è¯·æ£æ¥è§¦åæ¡ä»¶æ¯å¦å¡«åå®æ¯ï¼");
            }

            let json = form.serializeJSON();
          //  json.alarmDeadband = alarmDeadband;
            let isenableOptions = $("#"+conditionIsenableId+theIndex).checkbox("options");
            json.isenable = isenableOptions.checked ? 1 : 0;
            if(!isenableOptions.checked){
                json.alarmLevel = '';
                json.alarmType = '';
            }
            if(YX == alarmClass){
                json.trigecondition = 1;
            }
            let linakgeArr = getLinkage(theIndex);
            if(linakgeArr){
                json.linkages = linakgeArr;
            }
            conditionArr.push(json);
        }
    }
    return conditionArr;
}

function controlConditionBtn() {
    let liList = $("#condition_list li");
    if (liList.length <= 1) {
        $(addConditionBtnId).linkbutton('enable');
    } else {
        $(addConditionBtnId).linkbutton('disable');
    }

    if(liList.length > 1){
        $(delConditionBtnId).linkbutton('enable');
    }else{
        $(delConditionBtnId).linkbutton('disable');
    }
}

function controlConditionBtn(){
    controlAddConditionBtn();
    controlDelConditionBtn();
}

function controlAddConditionBtn() {
    if ($("#condition_list li").length <= 1) {
        $(addConditionBtnId).linkbutton('enable');
    } else {
        $(addConditionBtnId).linkbutton('disable');
    }
}

function controlDelConditionBtn(){
    if ($("#condition_list li").length >= 1) {
        $(delConditionBtnId).linkbutton('enable');
    } else {
        $(delConditionBtnId).linkbutton('disable');
    }
}

/*function changeAlarmDeadband(checked){
    if(checked){
        $("#"+alarmDeadbandId).textbox({
            required: true,
            readonly: false
        });
    }else{
        $("#"+alarmDeadbandId).textbox({
            required: false,
            readonly: true
        });
        $("#"+alarmDeadbandId).textbox("setValue",'');
    }
}*/

/*function addAlarmDeadband(){//ä»æ°æ®ç±»åä¸ºé¥æµçæ¶åéè¦æ·»å 
    let length = $(conditionListId + " li").first().length;
    if(length == 0){//ä»æ·»å ä¸æ¬¡
        let html = '<div id="'+alarmDeadbandDivId+'">';
        html+='<lit>å¯ç¨æ¥è­¦æ­»åº<input class="easyui-checkbox" id="'+alarmDeadbandEnableId+'" data-options="onChange:changeAlarmDeadband"></lit>';
        html+='<input class="easyui-textbox" type="number" readonly  data-options="prompt:\'æ¥è­¦æ­»åº\'" name="alarmDeadband" style="width:110px;margin-top: 10px" id="'+alarmDeadbandId+'" addClear>';
        html+='</div>';
        $(conditionListId).append(html);
        $.parser.parse("#"+alarmDeadbandDivId);
        setClear(alarmDeadbandDivId);
    }
}*/

function loadThresholdIds(){
    $.ajax({
        url:  ctx + '/home/listDictNoRoot/CAMS_ALAM_THRESHOLD',
        method:'get',
        async:false,
        dataType:"json",
        success:function(result){
            if (result) {
                for (let i = 0; i < result.length; i++) {
                    let obj = {};
                    let code = result[i].code;
                    let name = result[i].name;
                    obj.code = code;
                    obj.name = name;
                    if (code.indexOf('H') != -1) {
                        hThresholdIds.push(obj);
                    } else {
                        lThresholdIds.push(obj);
                    }

                }
            }
        }
    })
}
function reloadThreshold(th){
    //å½è¿éå¼ç¼å·
    if(th.indexOf('H') != -1){
        let obj = {};
        obj.code = th;
        obj.name = th;
        hThresholdIds.push(obj);
        hThresholdIds.sort(function(a,b){
            return  a.code.localeCompare(b.code);
        });
    }else{
        let obj = {};
        obj.code = th;
        obj.name = th;
        lThresholdIds.push(obj);
        lThresholdIds.sort(function(a,b){
            return  a.code.localeCompare(b.code);
        });
    }
}