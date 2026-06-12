let theMonitor = parent.monitor;
let falseLabelId = "#FALSE_LABEL";
let trueLabelId = "#TRUE_LABEL";
let isStoredId = "#isStored";

let yxFormId = "#yxForm";

$(function () {
    loadYX();
    /*if (theMonitor == null || parent.conditionLinkageArr == null) {
        addYXCondition();
    }*/
    bindEvent();
});

function loadYX() {
    if (theMonitor) {
        let yx = theMonitor.yx;
        let yxJson = JSON.parse(yx);
        $(falseLabelId).textbox('setValue', yxJson.FALSE_LABEL);
        $(trueLabelId).textbox('setValue', yxJson.TRUE_LABEL);
        
        // å è½½å¯ç¨å­å¨åå²éç½®
        if(theMonitor.isStored == 1){
            $(isStoredId).checkbox('check');
        }else{
            $(isStoredId).checkbox('uncheck');
        }
    }
}

function bindEvent() {
    controlConditionBtn();
    $(addConditionBtnId).click(function () {
        if($(this).linkbutton('options').disabled){
            return;
        }
        addYXCondition();
        controlConditionBtn();
    });
    $(delConditionBtnId).click(function () {
        if($(this).linkbutton('options').disabled){
            return;
        }
        delClickCondition(controlConditionBtn);
    });

}

function getYxData() {
    let yxObj = {};
    let yxJson = {};
    let validate = $(yxFormId).form("validate");
    if(!validate){
        throw new Error("è¯·å¡«åå¿è¦åæ°ï¼");
    }
    yxJson.FALSE_LABEL = $(falseLabelId).textbox('getValue',);
    yxJson.TRUE_LABEL = $(trueLabelId).textbox('getValue');
    yxObj.yx = JSON.stringify(yxJson);
    
    // è·åå¯ç¨å­å¨åå²éç½®
    let options = $(isStoredId).checkbox('options');
    yxObj.isStored = options.checked ? 1 : 0;
    return yxObj;
}

