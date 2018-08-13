/* Project specific Javascript goes here. */

/*
Formatting hack to get around crispy-forms unfortunate hardcoding
in helpers.FormHelper:

    if template_pack == 'bootstrap4':
        grid_colum_matcher = re.compile('\w*col-(xs|sm|md|lg|xl)-\d+\w*')
        using_grid_layout = (grid_colum_matcher.match(self.label_class) or
                             grid_colum_matcher.match(self.field_class))
        if using_grid_layout:
            items['using_grid_layout'] = True

Issues with the above approach:

1. Fragile: Assumes Bootstrap 4's API doesn't change (it does)
2. Unforgiving: Doesn't allow for any variation in template design
3. Really Unforgiving: No way to override this behavior
4. Undocumented: No mention in the documentation, or it's too hard for me to find
*/
$('.form-group').removeClass('row');

function getRiskStatus(element) {
    let risk = $(element);
    let riskId = (risk.attr('id'));
    let riskUrl = risk.attr('data-check-url');
    $.ajax({
        url: riskUrl,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            let el = $('#' + riskId);
            if (data.error_message) {
                return false
            }
            if (data.verifie) {
                el.attr('data-status', data.verifie);
                if (data.verifie === "pending") {
                    el.before("<strong class='d-inline-block'>" + gettext('Confirmer') + "</strong>");
                    el.html(
                        "<i class='fa fa-times-circle text-danger ml-2' style='font-size: 120%;' data-toggle='tooltip' data-placement='right'></i>"
                    ).find('i').attr('title', gettext('Confirmer le risque'));
                }
                if (data.verifie === 'verified') {
                    el.before("<strong class='d-inline-block'>" + gettext('Confirmé') + "</strong>")
                    el.html(
                        "<i class='fa fa-check-circle text-success ml-2' style='font-size: 130%;' data-toggle='tooltip' data-placement='right'></i>"
                    ).find('i').attr('title', gettext('Annuler'));
                }
            }

        },
    });
}

function getControlStatus(el) {
    let statusEl = $(el);
    let StatusID = statusEl.attr('id');
    let controlStatusUrl = statusEl.attr('data-check-url');
    $.ajax({
        url: controlStatusUrl,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            let el = $('#' + StatusID);
            if (data.result === 'failure') {
                return false;
            }
            if (data.result === 'success') {
                if (data.control_status === 'in_progress') {
                    el.html(data.status_display + '<strong style="font-size: 130%;"> <i class="ml-2 fa fa-check-circle" data-toggle="tooltip" data-placement="right"></i></strong>')
                        .find('i').attr('title', gettext('Terminer'));
                    el.attr('data-status', data.control_status);

                }
                if (data.control_status === 'completed') {
                    el.html(data.status_display + '<strong class="text-success" style="font-size: 150%;"><i class="ml-2 fa fa-check-circle" data-toggle="tooltip" data-placement="right"></i></strong>')
                        .find('i').attr('title', gettext('Reinitialiser'));
                    el.attr('data-status', data.control_status);
                }
            }
        }

    });
}

function ControlApprovedValidated(el) {
    let link = $(el);
    let linkID = link.attr('id');
    let url = link.attr('data-check-url');
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            let element = $("#" + linkID);
            if (data.result === 'success') {
                element.attr('data-checked', data.checked);
                if (data.checked === true) {
                    element.find('i').remove();
                    element.next().toggle(true);
                    element.append('<i class="ml-2 fa fa-check-circle text-success"></i>');
                    element.attr('title', gettext('Non'));
                }
                else {
                    element.find('i').remove();
                    element.next().toggle(false);
                    element.append('<i class="ml-2 fa fa-times-circle text-muted"></i>');
                    element.attr('title', gettext('Oui'));
                }
            }
            else {
                return false;
            }
        }
    });
}

$(document).ready(function () {

});

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);

            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
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
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function () {
    let riskConfirm = $('.confirm-risk');
    let controlStatus = $('.controle-status');
    let validateLink = $('.validate');
    let approveLink = $('.approve');
    riskConfirm.each(function () {
        getRiskStatus(this);
    });
    controlStatus.each(function () {
        getControlStatus(this);
    });
    validateLink.each(function () {
        ControlApprovedValidated(this);
    });
    approveLink.each(function () {
        ControlApprovedValidated(this);
    });
    riskConfirm.on('click', function () {
        let risk = $(this);
        let url = $(this).attr('data-change-url');
        let status = $(this).attr('data-status');
        $.ajax({
            type: 'POST',
            url: url,
            data: {'verifie': status},
            success: function (data) {
                if (data.result === 'success') {
                    risk.prev().remove();
                    getRiskStatus(risk);
                }
            }

        })


    });
    controlStatus.on('click', 'i', function () {
        let controlStatus = $(this).closest('.controle-status');
        let changeUrl = controlStatus.attr('data-change-url');
        let status = controlStatus.attr('data-status');
        $.ajax({
            type: 'POST',
            url: changeUrl,
            data: {'status': status},
            success: function (data) {
                if (data.result === 'success') {
                    getControlStatus(controlStatus);
                }
            }
        });
    });
    approveLink.on('click', function (e) {
        $(this).parent().is(".show") && e.stopPropagation();
        e.preventDefault();
        let element = $(this);
        let url = element.attr('data-change-url');
        let approved = element.attr('data-checked');
        element.parent().toggle(true);
        $.ajax({
            type: 'POST',
            url: url,
            data: {'est_approuve': approved},
            success: function (data) {
                if (data.result === 'success') {
                    ControlApprovedValidated(element);
                    ControlApprovedValidated(element.next());
                }
                else {
                    console.log(data.error_message);
                    return false;
                }
            }
        });
    });
    validateLink.on('click', function (e) {
        e.preventDefault();
        let element = $(this);
        let url = element.attr('data-change-url');
        let validated = element.attr('data-checked');
        $.ajax({
            type: 'POST',
            url: url,
            data: {'est_valide': validated},
            success: function (data) {
                if (data.result === 'success') {
                    ControlApprovedValidated(element.prev())
                    ControlApprovedValidated(element);
                }
                else {
                    console.log(data.error_message);
                    return false;
                }
            }

        })
    });
});




