/*
 *  Sets up a given modal form element to communicate with Flask backend and sets up
 *	Proper form feedback on erroneous inputs
 * 		btn_id - the id of the button that triggered this modal
 * 		modal_id - the id of the bootstrap modal itself (should have role="dialog" attribute)
 * 		form_id - the id of the <form> being hosted on this modal
 */
function setupModalForm(btn_id, modal_id, form_id){
	// Set up the trigger button and error display
	$(btn_id).click(function (event) {
		event.preventDefault();
		var url = $(form_id)[0].action;
		$.post(url, data=$(form_id).serialize(), function(data) {
			if (data.status == 'ok') {
				$(modal_id).modal('hide');
				location.reload();
			}
			else{
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
						var erroneous_input = $(modal_id)[0].querySelector(erroneous_input_id);
						erroneous_input.classList.add('is-invalid');
						var invalid_feedback_div = document.createElement('div');
						invalid_feedback_div.classList.add('invalid-feedback');
						for(var i in errors_dict[field]){
							var err_span = document.createElement('span');
							err_span.classList.add('invalid_feedback_cust');
							err_span.innerHTML = errors_dict[field][i];
							invalid_feedback_div.appendChild(err_span);
						}
						erroneous_input.parentElement.appendChild(invalid_feedback_div);
					}
				}
			}
		})
	});

	// Dynamically set action on form
	//$()

	// Clear any errors from previous displays when being redisplayed
	$(modal_id).on('hidden.bs.modal', function (event) {
		$('.invalid-feedback').remove();
		$(form_id + " :input").each(function(){
			$(this).removeClass('is-invalid');
		});
	});
}

function setupLibrary(){
	// Register novel components
	var reg_novel_submit = '#register_novel_submit_btn';
	var reg_novel_modal = '#register_modal_push';
	var reg_novel_form = '#register_novel_form';
	// Edit novel components
	var edit_novel_submit = '#edit_novel_submit_btn';
	var edit_novel_modal = '#edit_modal_push';
	var edit_novel_form = '#edit_novel_form';
	var edit_novel_action_base = $(edit_novel_form)[0].action.substr(0,
		$(edit_novel_form)[0].action.lastIndexOf("/"));
	// Remove novel components
	var remove_novel_submit = '#remove_novel_submit_btn';
	var remove_novel_modal = '#remove_modal_push';
	var remove_novel_form = '#remove_novel_form';
	var remove_novel_action_base = $(remove_novel_form)[0].action.substr(0,
		$(remove_novel_form)[0].action.lastIndexOf("/"));

	// On show Edit Modal events
	$(edit_novel_modal).on('shown.bs.modal', function (event) {
		var action_bar = $(event.relatedTarget)[0].closest('.entry_action_bar');
		var title = action_bar.querySelector('.entry_info .info_title').innerText.trim();
		var abbr = action_bar.querySelector('.entry_info .info_abbr').innerText.trim();
		var code = action_bar.querySelector('.entry_info .info_code').innerText.trim();

		// Set the defaults for the form fields
		$(edit_novel_modal)[0].querySelector('#title').defaultValue = title;
		$(edit_novel_modal)[0].querySelector('#abbr').defaultValue = abbr;
		// Customize the edit form's action to the specific series
		$(edit_novel_form)[0].action = edit_novel_action_base + '/' + code;
	});

	// On show Remove Modal events
	$(remove_novel_modal).on('shown.bs.modal', function (event) {
		var action_bar = $(event.relatedTarget)[0].closest('.entry_action_bar');
		var abbr = action_bar.querySelector('.entry_info .info_abbr').innerText.trim();
		var code = action_bar.querySelector('.entry_info .info_code').innerText.trim();

		// Customize the remove form's action to the specific series
		$(remove_novel_form)[0].action = remove_novel_action_base + '/' + code;
	});

	// Setup the register novel modal
	setupModalForm(reg_novel_submit, reg_novel_modal, reg_novel_form);

	// Setup the edit novel modal
	setupModalForm(edit_novel_submit, edit_novel_modal, edit_novel_form);

	//Setup the remove novel modal
	setupModalForm(remove_novel_submit, remove_novel_modal, remove_novel_form);
}

// Set AJAX to submit requests with form csrf token
var csrftoken = $('#csrf_token').attr('value');
$.ajaxSetup({
	beforeSend: function(xhr, settings) {
		if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken)
		}
	}
})