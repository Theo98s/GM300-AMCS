let theMonitor = parent.monitor;
let unitNameId = "#UNIT_NAME";
let formatId = "#FORMAT";
let isRatioId = "#isRatio";
let changeRatioId = "#changeRatio";
let isOffsetId = "#isOffset";
let isStoredId = "#isStored";
let trendAlarmEnableId = "#trendAlarmEnable";
let offsetId = "#offset";
let ycFormId = "#ycForm";
let changeThresholdId = "#changeThreshold";
let trendAlarmLevelId = "#trendAlarmLevel";
let trendChangeThresholdId = "#trendChangeThreshold";
let trendIntervalId = "#trendInterval";


let numberReg = /^(\-|\+)?\d+(\.\d+)?$/;


function validate(){
    $.extend($.fn.validatebox.defaults.rules, {
        teleMinValue: {
            validator: function (value) {
                return numberReg.test(value);
            },
            message: 'è¯·è¾å¥æææ°å¼ï¼'
        }
    });
}

$(function () {
    loadYC();
    bindEvent();
    if (parent.viewFlag) {
        disableAllElement();
    }
});

function changeRatio(checked){
    if(checked){
        $(changeRatioId).textbox({
            required: true,
            readonly: false
        });
    }else{
        $(changeRatioId).textbox({
            required: false,
            readonly: true
        });
        $(changeRatioId).textbox("setValue",'');
    }
}
function changeOffset(checked){
    if(checked){
        $(offsetId).textbox({
            required: true,
            readonly: false
        });
    }else{
        $(offsetId).textbox({
            required: false,
            readonly: true
        });
        $(offsetId).textbox("setValue",'');
    }
}
function changeIsStored(checked){
    if(checked){
        $(changeThresholdId).textbox({
            required: true,
            readonly: false
        });
    }else{
        $(changeThresholdId).textbox({
            required: false,
            readonly: true
        });
        $(changeThresholdId).textbox("setValue",'');
    }
}
function changeTrendAlarmEnable(checked){
    const param = {
        required: checked,
        readonly: !checked
    }
    if (!checked){
        param.value = "";
    }
    $(trendAlarmLevelId).combobox(param);
    $(trendChangeThresholdId).textbox(param);
    $(trendIntervalId).textbox(param);
}

function bindEvent(){
    controlDelConditionBtn();
    $(addConditionBtnId).click(function(){
        if($(this).linkbutton('options').disabled){
            return;
        }
       // addAlarmDeadband();
        addCondition();
        controlDelConditionBtn();
    });
    $(delConditionBtnId).click(function(){
        if($(this).linkbutton('options').disabled){
            return;
        }
        delClickCondition(controlDelConditionBtn);
    });

}

function loadYC(){
    if(theMonitor){
        let yc = theMonitor.yc;
        if(!yc){return;}
        let ycJson = JSON.parse(yc);
        // {"FORMAT":"0.0","UNIT_NAME":"Â°"}
        $(unitNameId).textbox('setValue',ycJson.UNIT_NAME);
        $(formatId).textbox('setValue',ycJson.FORMAT);

        if(theMonitor.isRatio == 1){
            $(isRatioId).checkbox('check');
            $(changeRatioId).textbox('setValue',theMonitor.changeRatio);

        }else{
            $(isRatioId).checkbox('uncheck');
        }

        if(theMonitor.isOffset == 1){
            $(isOffsetId).checkbox('check');
            $(offsetId).textbox('setValue',theMonitor.offset);

        }else{
            $(isOffsetId).checkbox('uncheck');
        }

        if(theMonitor.isStored == 1){
            $(isStoredId).checkbox('check');
            $(changeThresholdId).textbox('setValue',theMonitor.changeThreshold);
        }else{
            $(isStoredId).checkbox('uncheck');
        }

        if(theMonitor.trendAlarmEnable == 1){
            $(trendAlarmEnableId).checkbox('check');
            $(trendChangeThresholdId).textbox('setValue',theMonitor.trendChangeThreshold);
            $(trendAlarmLevelId).textbox('setValue',theMonitor.trendAlarmLevel);
            $(trendIntervalId).textbox('setValue',theMonitor.trendInterval);
        }else{
            $(trendAlarmEnableId).checkbox('uncheck');
        }
    }

}

function getYcData(){
    let validate = $(ycFormId).form("validate");
    if(!validate){
        throw new Error("è¯·å¡«åå¿è¦åæ°ï¼");
    }
   let ycJson = $(ycFormId).serializeJSON();

   let yc = {
       FORMAT:ycJson.FORMAT,
       UNIT_NAME:ycJson.UNIT_NAME,
   };
    ycJson.yc = JSON.stringify(yc);
   delete ycJson.FORMAT
   delete ycJson.UNIT_NAME
    ycJson.isOffset = $(isOffsetId).checkbox("options").checked ? 1 : 0;
    ycJson.isRatio = $(isRatioId).checkbox("options").checked ? 1 : 0;
    ycJson.isStored = $(isStoredId).checkbox("options").checked ? 1 : 0;
    ycJson.trendAlarmEnable = $(trendAlarmEnableId).checkbox("options").checked ? 1 : 0;
    return ycJson;
}