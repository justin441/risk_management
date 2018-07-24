function getRiskStatus(element) {
    var risk = $(element);
    var riskId = (risk.attr('id'));
    var riskUrl = risk.attr('data-check-url');
    $.ajax({
        url: riskUrl,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            var el = $('#' + riskId);
            if (data.error_message) {
                return false
            }
            if (data.verifie) {
                el.attr('data-status', data.verifie);
                if (data.verifie === "pending") {
                    el.html(
                        "<i class='fa fa-times-circle text-danger'></i>"
                    );
                }
                if (data.verifie === 'verified') {
                    el.html(
                        "<i class='fa fa-check-circle text-success' style='font-size: 110%'></i>"
                    );
                }
            }

        },
    });
}


$(document).ready(function () {
    $('.confirm-risk').each(function () {
        getRiskStatus(this)
    });
});

function getCookie(name){
    var cookieValue = null;

    if (document.cookie && document.cookie!==''){
        var cookies = document.cookie.split(';');
        for(var i=0; i<cookies.length; i++){
            var cookie = jQuery.trim(cookies[i]);

            if (cookie.substring(0, name.length+1) === (name+"=")){
                cookieValue = decodeURIComponent(cookie.substring(name.length+1));
                break;
            }
        }
    }
    return cookieValue
}

var csrftoken = getCookie('csrftoken');

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
        var risk = $(this)
        var url = $(this).attr('data-change-url');
        var status = $(this).attr('data-status');
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
});


