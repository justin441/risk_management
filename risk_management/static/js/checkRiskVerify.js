function getRiskStatus(element) {
    let  risk = $(element);
    let  riskId = (risk.attr('id'));
    let  riskUrl = risk.attr('data-check-url');
    $.ajax({
        url: riskUrl,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            let  el = $('#' + riskId);
            if (data.error_message) {
                return false
            }
            if (data.verifie) {
                el.attr('data-status', data.verifie);
                if (data.verifie === "pending") {
                    el.html(
                        "<i class='fa fa-times-circle text-danger' style='font-size: 130%;'></i>"
                    );
                }
                if (data.verifie === 'verified') {
                    el.html(
                        "<i class='fa fa-check-circle text-success' style='font-size: 150%;'></i>"
                    );
                }
            }

        },
    });
}

function getControlStatus(el){
    let statusEl = $(el);
    let StatusID = statusEl.attr('id');
    let controlStatusUrl = statusEl.attr('data-check-url');
    $.ajax({
        url: controlStatusUrl,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            let el = $('#' + StatusID);
            if(data.result === 'Failure'){
                return false;
            }
            if(data.result === 'Success'){
                if(data.control_status === 'in_progress'){
                    el.html('<strong class="text-muted">' + data.status_display +' <i class="ml-2 fa fa-check-circle" style="font-size: 130%;"></i></strong>' );
                    el.attr('data-status', data.control_status );
                }
                if(data.control_status === 'completed'){
                     el.html('<strong class="text-success">' + data.status_display +' <i class="ml-2 fa fa-check-circle" style="font-size: 150%;"></i></strong>' );
                     el.attr('data-status', data.control_status);
                }
            }
        }

    });
}


$(document).ready(function () {
    $('.confirm-risk').each(function () {
        getRiskStatus(this);
    });
    $('.controle-status').each(function () {
        getControlStatus(this);
    });
});

function getCookie(name){
    let cookieValue = null;

    if (document.cookie && document.cookie!==''){
        let cookies = document.cookie.split(';');
        for(let i=0; i<cookies.length; i++){
            let cookie = jQuery.trim(cookies[i]);

            if (cookie.substring(0, name.length+1) === (name+"=")){
                cookieValue = decodeURIComponent(cookie.substring(name.length+1));
                break;
            }
        }
    }
    return cookieValue
}

let csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function () {
    $('.confirm-risk').on('click', function () {
        let risk = $(this);
        let url = $(this).attr('data-change-url');
        let status = $(this).attr('data-status');
        $.ajax({
             type: 'POST',
            url: url,
            data: {'verifie': status},
            success: function (data) {
                if(data.result === 'success'){
                    getRiskStatus(risk);
                }
            }

        })


    });
    $('.controle-status').on('click', 'i', function () {
        let controlStatus = $(this).closest('.controle-status');
        let changeUrl = controlStatus.attr('data-change-url');
        let status = controlStatus.attr('data-status');
        $.ajax({
            type: 'POST',
            url: changeUrl,
            data: {'status': status},
            success: function (data) {
                if(data.result === 'success'){
                    getControlStatus(controlStatus);
                }
            }
        });
    });
});


