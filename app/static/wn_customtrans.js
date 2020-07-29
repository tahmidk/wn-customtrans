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
		// Make spinner visible
		$(btn_id).prev().css("display", "block");

		// Make a post request to the route responsible for handling the form's backend
		var url = $(form_id)[0].action;
		$.post(url, data=$(form_id).serialize(), function(data) {
			$(btn_id).prev().css("display", "none");
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
						var erroneous_input_id = '#' + field;
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

	// Clear any errors from previous displays when being redisplayed
	$(modal_id).on('hidden.bs.modal', function (event) {
		$('.invalid-feedback').remove();
		$(form_id + " :input").each(function(){
			$(this).removeClass('is-invalid');
		});
	});
}

/*
 *  Creates a client created flash message. JS equivalent of Flask's flash()
 * 		message - The message to display
 * 		category - flash message's category
 */
function createFlashMessage(message, category, flash_loc){
	var flash_div_wrapper = document.createElement("div");
	flash_div_wrapper.classList.add("flash_msg_div");
	var flash_div = document.createElement("div");
	flash_div.classList.add("alert");
	flash_div.classList.add("alert-dismissible");
	flash_div.classList.add("fade");
	flash_div.classList.add("show");
	flash_div.classList.add("flash_msg_" + category);
	flash_div.setAttribute("role", "alert");

	var message_span = document.createTextNode(message);
	var close_btn = document.createElement("button");
	close_btn.classList.add("close");
	close_btn.setAttribute("type", "button");
	close_btn.setAttribute("data-dismiss", "alert");
	close_btn.setAttribute("aria-label", "Close");
	var close_btn_span = document.createElement("span");
	close_btn_span.setAttribute("aria-hidden", "true");
	close_btn_span.innerText = "×";

	close_btn.appendChild(close_btn_span);
	flash_div.appendChild(message_span);
	flash_div.appendChild(close_btn);
	flash_div_wrapper.appendChild(flash_div);
	$(flash_loc)[0].appendChild(flash_div_wrapper);
}

/*===================================================================*/
/*======================[ Page Setup Functions]======================*/
/*===================================================================*/
function setupLibrary(){
	// Register novel components
	var reg_novel_submit = '#register_novel_submit_btn';
	var reg_novel_modal = '#register_novel_modal_push';
	var reg_novel_form = '#register_novel_form';
	// Update library components
	var update_btn = '#menu_library_update';
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

	// Update button event sets up an SSE and listens for update progress
	var update_btn_enabled = true;
	$(update_btn).click(function(event){
		// Disable update button while event is finishing up
		if(!update_btn_enabled)	{
			return;
		}
		update_btn_enabled = false;

		// Show the progress bar
		$('#update_progress_bar')[0].setAttribute("style", "width: 0;");
		$(".progress_bar_display").fadeIn()//.css("display","flex");

		// Start SSE connection and listen for progress from server
		var source = new EventSource("/library/update");
		var ABBR_INDEX = 0;
		var CH_UPDATES_INDEX = 1;
		var CH_LATEST_INDEX = 2;
		source.onmessage = function(event) {
			progress_data = JSON.parse(event.data)

			// Update the progress bar
			var len_updated = progress_data['updated'].length;
			var value = (len_updated / progress_data['num_series']) * 100;
			var width_attr = "width: "+value+"%;";
			$('#update_progress_bar')[0].setAttribute("style", width_attr);

			// Close this connection when all entries have been updated
			if(progress_data['num_series'] == len_updated){
				source.close();
				// Show updates on page
				// progress_data[updated] is packed with info returned from updateSeries() method
				// Each entry should be in the form (abbr, num_chapter_updates, latest_ch)
				$.each(progress_data['updated'], function(index, value){
					var series_abbr = value[ABBR_INDEX];
					if(value[CH_UPDATES_INDEX] > 0){
						var update_target = '#series_' + series_abbr + " .entry_minibanner .entry_updated";
						var update_label = $(update_target);
						var latest_ch_target = "#series_" + series_abbr + " .entry_details .entry_latest pre";
						var latest_ch_label = $(latest_ch_target)[0];

						setTimeout(() => {
							update_label.css("display", "block");
							latest_ch_label.innerText = " Latest: " + value[CH_LATEST_INDEX];
						}, 1000);
					}
				});

				// Hide progress bar and re-enable this button
				setTimeout(() => {
					$(".progress_bar_display").fadeOut();//.css("display", "none");
					update_btn_enabled = true;
				}, 1000);
			}

			// Display errors
			var last = len_updated - 1;
			var series_abbr = progress_data['updated'][last][ABBR_INDEX];
			if(progress_data['updated'][last][CH_UPDATES_INDEX] < 0){
				var msg = "An network error occurred when requesting updates for " + series_abbr;
				var category = "danger";
				createFlashMessage(msg, category, ".library_mainpanel");
			}
		}
	});

	// Setup the register novel modal
	setupModalForm(reg_novel_submit, reg_novel_modal, reg_novel_form);

	// Setup the edit novel modal
	setupModalForm(edit_novel_submit, edit_novel_modal, edit_novel_form);

	//Setup the remove novel modal
	setupModalForm(remove_novel_submit, remove_novel_modal, remove_novel_form);
}

function setupTableOfContents(){
	// Bookmark events
	$('.toc_chapter_bookmark').click(function(event){
		// Make a post request to the route responsible for handling the form's backend
		var bookmark_btn = $(this)[0];
		var url = bookmark_btn.getAttribute('action');
		$.post(url, function(data) {
			if(data.status == 'ok') {
				var ch_div = $('#'+data.target_ch)[0];
				var bkmk_btn = ch_div.querySelector(".toc_chapter_bookmark");
				var bkmk_ico = bkmk_btn.querySelector("ion-icon");
				if(data.action == 'add_bookmark'){
					ch_div.classList.add("bookmarked_chapter");
					bkmk_btn.classList.add("active_bookmark");
					bkmk_ico.setAttribute("name", "bookmark");
				}
				else if(data.action == 'rmv_bookmark'){
					ch_div.classList.remove("bookmarked_chapter");
					bkmk_btn.classList.remove("active_bookmark");
					bkmk_ico.setAttribute("name", "bookmark-outline");
				}
			}
		});
	});

	// Menu button events
	$("#jump_to_curr_btn").click(function() {
		try{
			$('html, body').animate({
				scrollTop: $("#current_ch").offset().top - document.documentElement.clientHeight/2
			}, 500);
		}
		catch(err){ /* Do nothing */ }
	});
	var update_series_btn_enabled = true;
	$('#update_series_btn').click(function(){
		if(!update_series_btn_enabled){
			return
		}
		update_series_btn_enabled = false;

		// Make a post request to the route responsible for handling the form's backend
		createFlashMessage("Fetching latest chapters... please wait a few seconds", "warning", ".toc_menu_listing");
		var update_btn = $(this)[0];
		var url = update_btn.getAttribute('action');
		$.post(url, function(data) {
			if(data.status == 'ok') {
				update_series_btn_enabled = true;
				if(data.updates > 0){
					createFlashMessage("Success! Fetched " + data.updates + " new chapters!", "success", ".toc_menu_listing");
				}
				else{
					createFlashMessage("Success! This series is already up-to-date", "success", ".toc_menu_listing");
				}
				window.setTimeout(function(){
					location.reload();
				}, 1000);
			}
			else{
				createFlashMessage("We encountered an error fetching latest chapters. Try again later", "danger", ".toc_menu_listing");
			}
		});
	});
	$('#rmv_all_bkmk_btn').click(function() {
		var rmv_all_bkmk_btn = $(this)[0];
		var url = rmv_all_bkmk_btn.getAttribute('action');
		$.post(url, function(data){
			if(data.status == 'ok') {
				location.reload();
			}
		});
	});
}

function setupChapter(){
	// Credit to Codegrid for scroll indicator script: https://www.youtube.com/channel/UC7pVho4O31FyfQsZdXWejEw
	$(window).scroll(function() {
		var winTop = $(window).scrollTop();
		var docHeight = $(document).height();
		var winHeight = $(window).height();

		var percent_scrolled = (winTop / (docHeight - winHeight))*100;
		var display = (percent_scrolled < 0.01) ? 'none' : 'block';
		$('.chapter_scroll_bar#bar').css('display', display);
		$('.chapter_scroll_bar').css('height', percent_scrolled + '%');
		document.querySelector('.chapter_scroll_notch').innerText = Math.round(percent_scrolled) + '%';
	});

	// Initialize the correct icon
	var html = document.documentElement;
	var day_night_toggle_class = ".chapter_day_night_toggle_btn";
	$(day_night_toggle_class).each(function(){
		var icon_name = (html.getAttribute('data-theme') == "light") ? 'moon-outline' : 'sunny-outline';
		var icon = $(this)[0].querySelector('ion-icon');
		icon.setAttribute('name', icon_name);
	});

	// Add functionality of prev, toc, and next buttons
	var url = this.location.href;
	var ch = $('#mdata_ch').data("value");
	var latest_ch = $('#mdata_latest_ch').data("value");
	if(ch > 1){
		$('.chapter_prev_btn').click(function() {
			var prev = ch - 1;
			location.href = url.substring(0, url.lastIndexOf('/') + 1) + prev;
		});
	}
	if(ch < latest_ch){
		$('.chapter_next_btn').click(function() {
			var next = ch + 1;
			location.href = url.substring(0, url.lastIndexOf('/') + 1) + next;
		});
	}

	// Add functionality to toggle day and night UIs
	$(day_night_toggle_class).click(function(){
		html.classList.add('transition');
		window.setTimeout(function(){
			html.classList.remove('transition');
		}, 2000);

		// Toggle the theme
		if(html.getAttribute('data-theme') == "light"){
			html.setAttribute('data-theme', 'dark');
		}
		else{
			html.setAttribute('data-theme', 'light');
		}

		// Change the toggle button
		$(day_night_toggle_class).each(function(){
			var icon_name = (html.getAttribute('data-theme') == "light") ? 'moon-outline' : 'sunny-outline';
			var icon = $(this)[0].querySelector('ion-icon');
			icon.setAttribute('name', icon_name);
		});

	});
}

function setupDictionary(){

}
