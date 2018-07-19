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

// modal for risk creation

 $('#fm-modal').on('shown.bs.modal', function () {
    var risque = $('#id_risque');
    if(risque){
      if(risque.val()){
      var url = '/risk-register/risk-detail/' + risque.val() + '/';
      $.get(url, function (data, status) {
        if(status==='success'){
          $('#detail-risque').html(data);
        }
        else {
          $('#detail-risque').html('');
        }
      });
    }
    risque.on('change', function (e) {
       if(risque.val().length){
         var url = '/risk-register/risk-detail/' + risque.val() + '/';
         $.get(url, function (data, status){
           if(status==='success'){
              $('#detail-risque').html(data);
           }
           else {
             $('#detail-risque').html('');
           }
         });
       }
    });
    risque.on('select2:unselecting', function () {
        $('#detail-risque').html('');
    });
    }

  });
