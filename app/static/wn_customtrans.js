/*=======================================================================
 *  Copyright (c) 2020, Tahmid Khan
 *  All rights reserved.
 *
 *  Licensed under the BSD 3-Clause license found in the LICENSE file
 *=======================================================================*/

/*===================================================================*/
/* General Utility Functions
/*===================================================================*/
function strong(text){
	return "<strong>" + text + "</strong>";
}

// The following describe flash message categories
const SUCCESS = "success";
const WARNING = "warning";
const CRITICAL = "danger";

// The following are common constants prepended to flash messages
const SUCCESS_BOLD= strong("Success: ");
const WARNING_BOLD= strong("Warning: ");
const CRITICAL_BOLD= strong("Aborted: ");

/*
 *  Sets up a given modal form element to communicate with Flask backend and sets up
 *	Proper form feedback on erroneous inputs
 * 		btn_id - the id of the button that triggered this modal
 * 		modal_id - the id of the bootstrap modal itself (should have role="dialog" attribute)
 * 		form_id - the id of the <form> being hosted on this modal
 * 		flashpanel - the id of the flashed messages panel to append flashed messages to
 */
function setupModalForm(btn_id, modal_id, form_id, flashpanel){
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
			else if (data.status == 'error') {
				createFlashMessage(data.msg, data.severity, flashpanel);
				$(modal_id).modal('hide');
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
 * 		message - the message to display
 * 		category - flash message's category
 * 		flash_loc - the complete flash message's display destination
 */
function createFlashMessage(message, category, flash_loc){
	var flash_div_wrapper = document.createElement("div");
	flash_div_wrapper.classList.add("flash_msg_div");
	var flash_div = document.createElement("div");
	flash_div.classList.add("alert");
	flash_div.classList.add("alert-dismissible");
	flash_div.classList.add("fade");
	flash_div.classList.add("show");
	flash_div.classList.add("alert-" + category);
	flash_div.classList.add("notranslate");
	flash_div.setAttribute("role", "alert");

	var message_span = document.createElement("div");
	message_span.innerHTML = message;
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
/*  Tagged Placeholders Algorithms
/*===================================================================*/
/*
 *  Creates a client created flash message. JS equivalent of Flask's flash()
 * 		line_num - number representing the id portion of the line to process
 */
function replace_placeholders(line_num)
{
	// Validity check
	if(line_num <= 0){
		return;
	}

	var line_elem = document.querySelector('.content_line#l'+line_num);
	var placeholders = line_elem.getElementsByClassName('placeholder')
	// Replace each placeholder on this line
	for(let elem of placeholders){
		if( elem.innerHTML.toLowerCase().includes("placeholder") ){
			var word_meta = '#mdata_definition_' + elem.id.substring(1);
			var word = $(word_meta).data("translation");
			var pattern = new RegExp("(?:the\\s|a\\s)?placeholder", 'gi');

			var replacement = "<span class=\'notranslate word\'>" + word + "</span>";
			elem.innerHTML = elem.innerHTML.replace(pattern, replacement);
		}
	}

	// At this point, translation and substitution for this line is complete. Do
	// some post processing (like remove unnecessary articles) to increase readability
	var siblingPlaceholders = document.querySelectorAll('.content_line#l'+line_num+' font .placeholder');
	for(let placeholder_elem of siblingPlaceholders)
	{
		var preceding_elem = placeholder_elem.previousSibling;
		if(preceding_elem != null && !preceding_elem.classList.contains("placeholder"))
		{
			var remove_articles = new RegExp("(the|a)(\\s*)$", 'gi');
			preceding_elem.innerText = preceding_elem.innerText.replace(remove_articles, "$2");
		}
	}
}

/*
 *  Runs the Tagged Placeholders Algorithm
 */
function tagged_placeholders(){
	var dummies = document.getElementsByClassName('dummy');
	var checkpoint = new Array(dummies.length).fill(false);
	var line_processed = new Array(dummies.length - 1).fill(false);
	for(let d of dummies){
		var dummy = document.getElementById(d.id);
		// A dummy is "triggered" when it's translated by google translate
		$(dummy).on('DOMSubtreeModified', dummy, function() {
			$(this).unbind();
			var dummy_curr_id = parseInt(this.id.substring(1));
			checkpoint[dummy_curr_id] = true;

			// If D and D-1 are both triggered, then the line between them, L=D-1
			// should be completely translated and ready to postprocess
			var dummy_prev_id = dummy_curr_id - 1;
			if(dummy_prev_id > 0 && checkpoint[dummy_prev_id]){
				if(!line_processed[dummy_prev_id]){
					replace_placeholders(dummy_prev_id);
					line_processed[dummy_prev_id] = true;
				}
			}

			// If D and D+1 are both triggered, then the line between them, L=D
			// should be completely translated and ready to postprocess
			var dummy_next_id = dummy_curr_id + 1;
			if(dummy_next_id < checkpoint.length && checkpoint[dummy_next_id]){
				if(!line_processed[dummy_curr_id]){
					replace_placeholders(dummy_curr_id);
					line_processed[dummy_curr_id] = true;
				}
			}
		});
	}
}

/*===================================================================*/
/*  Page Setup Functions
/*===================================================================*/
function setupLibrary(){
	const lib_flashpanel = '#library_flashpanel';

	// Register novel components
	const reg_novel_submit = '#register_novel_submit_btn';
	const reg_novel_modal = '#register_novel_modal_push';
	const reg_novel_form = '#register_novel_form';
	// Update library components
	const update_btn = '#menu_library_update_btn';
	// Edit novel components
	const edit_novel_submit = '#edit_novel_submit_btn';
	const edit_novel_modal = '#edit_modal_push';
	const edit_novel_form = '#edit_novel_form';
	const edit_novel_action_base = $(edit_novel_form)[0].action.substr(0,
		$(edit_novel_form)[0].action.lastIndexOf("/"));
	// Remove novel components
	const remove_novel_submit = '#remove_novel_submit_btn';
	const remove_novel_modal = '#remove_modal_push';
	const remove_novel_form = '#remove_novel_form';
	const remove_novel_action_base = $(remove_novel_form)[0].action.substr(0,
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
	var update_error = false;
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
				if(!update_error){
					setTimeout(() => {
						var msg = "<strong>Success</strong> Fetched updates for all series in the library!";
						var category = "success";
						createFlashMessage(msg, category, lib_flashpanel)
					}, 1000);
				}
			}

			// Display errors
			var last = len_updated - 1;
			var series_abbr = progress_data['updated'][last][ABBR_INDEX];
			if(progress_data['updated'][last][CH_UPDATES_INDEX] < 0){
				update_error = true;
				var msg = "A network error occurred when requesting updates for <strong>" + series_abbr + "</strong>";
				var category = "danger";
				createFlashMessage(msg, category, lib_flashpanel);
			}
		}
	});

	// Setup the register novel modal
	setupModalForm(reg_novel_submit, reg_novel_modal, reg_novel_form, lib_flashpanel);

	// Setup the edit novel modal
	setupModalForm(edit_novel_submit, edit_novel_modal, edit_novel_form, lib_flashpanel);

	//Setup the remove novel modal
	setupModalForm(remove_novel_submit, remove_novel_modal, remove_novel_form, lib_flashpanel);
}

function setupTableOfContents(){
	const toc_flashpanel = "#toc_flashpanel"

	// Bookmark events
	$('.toc_chapter_bookmark').click(function(event){
		// Make a post request to the route responsible for handling the form's backend
		var bookmark_btn = $(this)[0];
		var url = bookmark_btn.getAttribute('action');
		$.post(url, function(data) {
			if(data.status == 'ok') {
				var ch_div = $('#'+data.target_ch)[0];
				var action_bar = ch_div.querySelector(".toc_chapter_actionbar");
				var bkmk_btn = ch_div.querySelector(".toc_chapter_bookmark");
				var bkmk_ico = bkmk_btn.querySelector("ion-icon");
				if(data.action == 'add_bookmark'){
					ch_div.classList.add("bookmarked_chapter");
					action_bar.classList.add("active_actionbar");
					bkmk_btn.classList.add("active_bookmark");
					bkmk_ico.setAttribute("name", "bookmark");
				}
				else if(data.action == 'rmv_bookmark'){
					ch_div.classList.remove("bookmarked_chapter");
					action_bar.classList.remove("active_actionbar");
					bkmk_btn.classList.remove("active_bookmark");
					bkmk_ico.setAttribute("name", "bookmark-outline");
				}
			}
			else{
				var msg = CRITICAL_BOLD + "An unexpected error occurred while trying to toggle bookmark";
				createFlashMessage(msg, CRITICAL, toc_flashpanel);
			}
		});
	});

	// Setcurrent events
	$('.toc_chapter_setcurrent').click(function(event){
		var setcurrent_btn = $(this)[0];
		var url = setcurrent_btn.getAttribute('action');
		$.post(url, function(data) {
			if(data.status == 'ok') {
				var chapters = $('.toc_chapter').each(function(index){
					if($(this).attr('id') == data.target_ch){
						$(this).addClass('current_chapter').removeClass('viewed_chapter');
					}
					else if($(this).attr('id') < data.target_ch){
						$(this).removeClass('current_chapter').addClass('viewed_chapter');
					}
					else{
						$(this).removeClass('current_chapter viewed_chapter');
					}
				});
			}
			else if(data.status = 'trivial_abort'){
				var msg = "Chapter " + data.target_ch + " is already set as the current chapter";
				createFlashMessage(msg, WARNING, toc_flashpanel);
			}
			else{
				var msg = CRITICAL_BOLD + "An unexpected error occurred while trying to set the current chapter";
				createFlashMessage(msg, CRITICAL, toc_flashpanel);
			}
		});
	});

	// Menu button events
	$("#jump_to_curr_btn").click(function() {
		try{
			$('html, body').animate({
				scrollTop: $(".current_chapter").offset().top - document.documentElement.clientHeight/2
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
		createFlashMessage(
			"Fetching latest chapters... please wait a few seconds",
			WARNING,
			toc_flashpanel);
		var update_btn = $(this)[0];
		var url = update_btn.getAttribute('action');
		$.post(url, function(data) {
			if(data.status == 'ok') {
				update_series_btn_enabled = true;
				if(data.updates > 0){
					createFlashMessage(
						SUCCESS_BOLD + "Fetched " + data.updates + " new chapters!",
						SUCCESS,
						toc_flashpanel);
				}
				else{
					createFlashMessage(
						SUCCESS_BOLD + "This series is already up-to-date",
						SUCCESS,
						toc_flashpanel);
				}
				window.setTimeout(function(){
					location.reload();
				}, 1000);
			}
			else{
				createFlashMessage(
					CRITICAL_BOLD + "Encountered an error while fetching latest chapters. Try again later",
					CRITICAL,
					toc_flashpanel);
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
	// Run the postprocessing algorithm
	tagged_placeholders();

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
	const dict_flashpanel = "#dictionary_flashpanel";
	$('.action_toggle_enable').click(function() {
		var url = this.getAttribute('action');
		var dict_entry = this.closest('.dictionary_entry');
		var toggle = this.querySelector('ion-icon');
		$.post(url, function(data) {
			if(data.status == 'ok') {
				$(dict_entry).toggleClass('dictionary_entry_disabled');
				if(data.toggle == 0){
					toggle.setAttribute("name", "square-outline");
				}else{
					toggle.setAttribute("name", "checkbox-outline");
				}
			}
			else{
				createFlashMessage(
					CRITICAL_BOLD + "An unexpected error occurred while trying to toggle dictionary: " + series_abbr,
					CRITICAL,
					dict_flashpanel);
			}
		})
	});
}
