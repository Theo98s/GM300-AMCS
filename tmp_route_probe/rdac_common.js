/**
 * 
 */
function ajaxJson(url, param, success, error){
	$.ajax({
        type: 'post',
        url: url,
        dataType: 'json',
        contentType: 'application/json;charset=utf-8', // è®¾ç½®è¯·æ±å¤´ä¿¡æ¯
        data: JSON.stringify(param),
        success: function (result) {
            success(result);
        },
        error: function (result) {
			if(error){
	            error(result);
			}
        }
    });
}
function ajaxJsonAsync(url, param, success, error){
	$.ajax({
        type: 'post',
        url: url,
        dataType: 'json',
		async: false,
        contentType: 'application/json;charset=utf-8', // è®¾ç½®è¯·æ±å¤´ä¿¡æ¯
        data: JSON.stringify(param),
        success: function (result) {
            success(result);
        },
        error: function (result) {
			if(error){
	            error(result);
			}
        }
    });
}

function getAjaxJson(url, param, success, error){
	$.ajax({
		type: 'get',
		url: url,
		dataType: 'json',
		// contentType: 'application/json;charset=utf-8', // è®¾ç½®è¯·æ±å¤´ä¿¡æ¯
		data: {},
		success: function (result) {
			success(result);
		},
		error: function (result) {
			if(error){
				error(result);
			}
		}
	});
}
function MsgError(content){
	new jBox('Notice', {
		title: "æ¸©é¦¨æç¤º",
		content : content,
		theme: 'NoticeBorder',
		color : 'red',
		stack: false, 
		animation: 'flip',  
		stack: false, 
		autoClose: 10000,
		attributes: {
			x: "right",
			y: "top"
		},
		position: { 
			x: 5,
			y: 5
		}
	});
};