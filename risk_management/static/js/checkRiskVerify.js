function getRiskStatus(element) {
    var risk = $(element);
    var riskId = (risk.attr('id'));
    var riskUrl = risk.attr('data-url');
    $.ajax({
        url: riskUrl,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            var el = $('#' + riskId)
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


