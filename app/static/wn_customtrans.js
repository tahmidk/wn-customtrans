$(document).ready(function() {
	var btn_id = '#register_novel_submit_btn';
	var modal_id = '#register_modal_push';
	var form_id= '#register_novel_form'
    $(btn_id).click(function (event) {
        event.preventDefault();
        var url = $(modal_id)[0].getAttribute("route");
        $.post(url, data = $(form_id).serialize(), function(data) {
            if (data.status == 'ok') {
                $(modal_id).modal('hide');
                location.reload();
            } else {
            	// First erase any feedback/invalid stylings that may exist from previous submissions
            	$('.invalid-feedback').remove();
            	$(form_id + " :input").each(function(){
					$(this).removeClass('is-invalid');
				});

            	// Then process the errors
                var errors_dict = JSON.parse(data);
                for (var field in errors_dict) {
                    if (errors_dict.hasOwnProperty(field)) {
                		var erroneous_input_id = 'input#' + field;
                		$(erroneous_input_id)[0].classList.add('is-invalid');
                		var invalid_feedback_div = document.createElement('div');
                		invalid_feedback_div.classList.add('invalid-feedback');
                		for(var i in errors_dict[field]){
                			var err_span = document.createElement('span');
                			err_span.classList.add('invalid_feedback_cust');
                			err_span.innerHTML = errors_dict[field][i];
                			invalid_feedback_div.appendChild(err_span);
                		}
                		$(erroneous_input_id)[0].parentElement.appendChild(invalid_feedback_div);
                    }
                }
            }
        })
    });
});

// Set AJAX to submit requests with form csrf token
var csrftoken = $('#csrf_token').attr('value');
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
})