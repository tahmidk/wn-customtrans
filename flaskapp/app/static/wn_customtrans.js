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
	return `<strong>${text}</strong>`;
}

// The following describe flash message categories
const SUCCESS = "success";
const WARNING = "warning";
const CRITICAL = "danger";

// The following are common constants prepended to flash messages
const SUCCESS_BOLD= strong("Success:");
const WARNING_BOLD= strong("Warning:");
const CRITICAL_BOLD= strong("Aborted:");

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
		var modal_spinner = $(btn_id).parent().prev();
		modal_spinner.css("display", "block");

		// Make a post request to the route responsible for handling the form's backend
		var url = $(form_id).attr('action');
		$.post(url, data=$(form_id).serialize(), function(data) {
			modal_spinner.css("display", "none");
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
						if(erroneous_input != null){
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
 *  Initializes the given word element to display the user comment associated with this
 * 	definition in the user dict file as a dismissable popover. Intended to be used by a
 *	placeholder replacer function only
 * 		word_id - the static id of the word to setup
 * 		word_metaid - the id of the meta dictionary definition this word corresponds to
 */
function setupCommentPopover(word_id, word_metaid){
	var comment = $(`#mdata_definition_${word_metaid}`).data("comment");
	comment = (comment !== "None") ? comment : "No comment";
	$('body').on('mouseover', `#w${word_id}`, function(event){
		var word = $(`#w${word_id}`);

		// Prepare the comment popover
		word.attr("tabindex", "0");
		word.attr("role", "button");
		word.attr("data-toggle", "popover");

		// Trigger the popover
		word.popover({
			trigger: 'focus',
			placement: 'top',
			content: comment,
			template:`
				<div class="popover word_popover_cust notranslate" role="tooltip">
					<div class="arrow"></div>
					<h3 class="popover-header word_popover_header_cust"></h3>
					<div class="popover-body word_popover_body_cust"></div>
				</div>`
		})
	});
}

/*
 *  Creates a client-side created flash message. JS equivalent of Flask's flash()
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
	$(flash_loc).append(flash_div_wrapper);
}

/*
 *  Creates and flashes a client-side created toast message. Only displays
 * 	a toast if its id is not the same as an existing toast
 * 		message - the message to display
 * 		category - flash message's category
 * 		id - the new toast's id value (not prepended by '#')
 * 		toast_loc - the complete toast message's display destination
 */
function createToast(message, category, id, toast_loc){
	if($('#'+id).length == 0){
		var toast_div = document.createElement("div");
		toast_div.setAttribute("id", id);
		toast_div.classList.add("toast_cust");
		toast_div.classList.add(`toast_${category}`);
		var toast_message = document.createElement("div");
		toast_message.classList.add("toast_message");
		toast_message.innerText = message;

		toast_div.appendChild(toast_message);
		$(toast_loc).append(toast_div);

		// Display toast for a few seconds
		const toast_duration = 3000; 			// 3 sec
		const animation_duration = 400; 		// should match the css transition property under 'toast_cust'
		setTimeout(function () {
			$(toast_div).addClass("toast_cust_visible");
			setTimeout(function(){
				$(toast_div).removeClass("toast_cust_visible");
				setTimeout(function(){
					// You're served your purpose well toast, time to die...
					$(toast_div).remove();
				}, animation_duration);
			}, toast_duration);
		}, animation_duration);
	}
}

function handleUploadDict(input){
	document.cookie = `filesize=${input.files[0].size}`
	input.form.submit();
}

/*===================================================================*/
/*  Tagged Placeholders Algorithm
/*===================================================================*/
/*
 *  Replaces all placeholders in the given content line with an html
 * 	structure representing the postprocessed word translation
 * 		line_num - number representing the id portion of the line to process
 *
 *	@return Updated word_num
 */
function tp_replace_placeholders(line_num, word_num)
{
	var line_elem = $(`#l${line_num} .content_maintext_trans`);

	// Un-nest nested font tags introduced by Google translate
	line_elem.find('font').each(function(){
		$(this).prop('outerHTML', $(this).prop('innerHTML'));
	});

	// Replace each placeholder on this line
	line_elem.find('.placeholder').each( function(){
		if( $(this).html().toLowerCase().includes("placeholder") ){
			var id = $(this).attr('id').substring(1);
			var word = $(`#mdata_definition_${id}`).data("translation");
			var pattern = new RegExp("(?:the\\s|a\\s)?placeholder", 'gi');

			var html_content = $(this).html();
			var replacement = `<a class=\'notranslate word\' id=\'w${word_num}\'>${word}</a>`;
			$(this).html(html_content.replace(pattern, replacement));

			setupCommentPopover(word_num, id);
			word_num += 1;
		}
		else{
			// No match, false alarm, remove the placeholder wrapper div
			$(this).contents().unwrap();
		}
	});

	// At this point, translation and substitution for this line is complete.
	// Don't allow further mutations by Google Translate by marking notranslate
	line_elem.addClass('notranslate');

	// Line post-processing + cleanup
	// Remove rogue articles (the + a) often preceding dictionary words
	var remove_articles_regex = new RegExp("(the|a)(\\s*)$", 'gi');
	line_elem.find('.placeholder').each(function(){
		var preceding_text = $(this).prev().text();
		$(this).prev().text(preceding_text.replace(remove_articles_regex, "$2"));
	});

	return word_num;
}

/*
 *  Runs the Tagged Placeholders Algorithm
 */
function tagged_placeholders(){
	var dummies = document.getElementsByClassName('dummy');
	var checkpoint = new Array(dummies.length).fill(false);
	var line_processed = new Array(dummies.length - 1).fill(false);

	// word_num is used for setting the 'w' id of replaced placeholders. Take it
	// as a unique identifier for each postprocessed placeholder
	// IMPORTANT: Does NOT correlate with the meta dictionary ids found in <head>
	var word_num = 1;

	for(let d of dummies){
		var dummy = document.getElementById(d.id);
		// A dummy is "triggered" when it's translated by google translate
		$(dummy).on('DOMSubtreeModified', dummy, function() {
			$(this).unbind();
			var dummy_curr_id = parseInt(this.id.substring(1));
			checkpoint[dummy_curr_id] = true;

			// If D-1 and D are both triggered, then the line between them, L=D
			// should be completely translated and ready to postprocess
			var dummy_prev_id = dummy_curr_id - 1;
			if(dummy_prev_id >= 0 && checkpoint[dummy_prev_id]){
				if(!line_processed[dummy_prev_id]){
					word_num = tp_replace_placeholders(dummy_curr_id, word_num);
					line_processed[dummy_prev_id] = true;
				}
			}

			// If D and D+1 are both triggered, then the line between them, L=D+1
			// should be completely translated and ready to postprocess
			var dummy_next_id = dummy_curr_id + 1;
			if(dummy_next_id < checkpoint.length && checkpoint[dummy_next_id]){
				if(!line_processed[dummy_curr_id]){
					word_num = tp_replace_placeholders(dummy_next_id, word_num);
					line_processed[dummy_curr_id] = true;
				}
			}
		});
	}
}

/*===================================================================*/
/*  Definition Similarity Algorithm
/*===================================================================*/
/*
 *  Runs the Definition Similarity Algorithm
 */
function definition_similarity(){
	return stringSimilarity.compareTwoStrings('paple!', 'apple?');
}

/*===================================================================*/
/*  Route Specific Setup Functions
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
	const edit_novel_action_base = $(edit_novel_form).attr('action').substr(0,
		$(edit_novel_form).attr('action').lastIndexOf("/"));
	// Remove novel components
	const remove_novel_submit = '#remove_novel_submit_btn';
	const remove_novel_modal = '#remove_modal_push';
	const remove_novel_form = '#remove_novel_form';
	const remove_novel_action_base = $(remove_novel_form).attr('action').substr(0,
		$(remove_novel_form).attr('action').lastIndexOf("/"));

	// On show Edit Modal events
	$(edit_novel_modal).on('shown.bs.modal', function (event) {
		var series_entry = $(event.relatedTarget).closest('.library_series_entry');
		var title = series_entry.data('title');
		var abbr = series_entry.data('abbr');
		var id = series_entry.data('id');

		// Set the defaults for the form fields
		$(`${edit_novel_modal} #title`).val(title);
		$(`${edit_novel_modal} #abbr`).val(abbr);

		// Customize the edit form's action and input id to that of the series entry that
		// triggered this modal
		$(`${edit_novel_form} input[name="series_id"]`).val(id)
		$(edit_novel_form).attr('action', `${edit_novel_action_base}/${id}`);
	});

	// On show Remove Modal events
	$(remove_novel_modal).on('shown.bs.modal', function (event) {
		var series_entry = $(event.relatedTarget).closest('.library_series_entry');
		var abbr = series_entry.data('abbr');
		var id = series_entry.data('id');

		// Customize the remove form's action to the specific series
		$(`${remove_novel_form} span[name="series_abbr"]`).text(abbr)
		$(remove_novel_form).attr('action', `${remove_novel_action_base}/${id}`);
	});

	// Update button event sets up an SSE and listens for update progress
	if(!$(update_btn)[0].hasAttribute('disabled')){
		var update_btn_enabled = true;
		var update_error = false;
		$(update_btn).click(function(event){
			// Disable update button while event is finishing up
			if(!update_btn_enabled)	{
				return;
			}
			update_btn_enabled = false;

			// Show the progress bar
			var body_padding_top = $('body').css('padding-top');
			var update_bar_height = $(".library_update_progress_bar_display").css('height');
			if(body_padding_top < update_bar_height){
				$('body').css('padding-top', update_bar_height);
			}
			$('#update_progress_bar').attr("style", "width: 0;");
			$('#update_info_series').attr("style", "display: none;");
			$(".library_update_progress_bar_display").fadeIn()

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
				$('#update_progress_bar').attr("style", width_attr);

				var series_abbr = progress_data['updated'][len_updated-1][ABBR_INDEX];
				$('#update_info_series').removeAttr("style");
				$('#update_info_series').text(series_abbr);

				// Close this connection when all entries have been updated
				if(progress_data['num_series'] == len_updated){
					source.close();
					// Show updates on page
					// progress_data[updated] is packed with info returned from updateSeries() method
					// Each entry should be in the form (abbr, num_chapter_updates, latest_ch)
					$.each(progress_data['updated'], function(index, value){
						var abbr = value[ABBR_INDEX];
						if(value[CH_UPDATES_INDEX] > 0){
							setTimeout(() => {
								$(`#series_${abbr} #num_updates`).text(`${value[CH_UPDATES_INDEX]}`);
								$(`#series_${abbr} .entry_updated`).fadeIn("fast", "swing");
								$(`#series_${abbr} #latest_ch`).text(`${value[CH_LATEST_INDEX]}`);
							}, 1000);
						}
					});

					// Hide progress bar and re-enable this button
					setTimeout(() => {
						$(".library_update_progress_bar_display").fadeOut();
						$('body').css('padding-top', body_padding_top);
						update_btn_enabled = true;
					}, 1000);
					if(!update_error){
						setTimeout(() => {
							createFlashMessage(
								`${SUCCESS_BOLD} Fetched updates for all series in the library!`,
								SUCCESS,
								lib_flashpanel)
						}, 1000);
					}

				}

				// Display errors
				if(progress_data['updated'][len_updated-1][CH_UPDATES_INDEX] < 0){
					update_error = true;
					createFlashMessage(
						"A network error occurred when requesting updates for " + strong(series_abbr),
						CRITICAL,
						lib_flashpanel);
				}
			}
		});
	}

	// When Register Novel Modal's host selection changes, change series code
	$("#series_host").change(function(){
		const opt = $(this).val();
		var placeholder = "";
		switch(opt){
			case '1':{
				placeholder = "https://ncode.syosetu.com/{series_code}";
				break;
			}
			case '2':{
				placeholder = "https://kakuyomu.jp/works/{series_code}";
				break;
			}
		}
		$("#series_code").attr('placeholder', placeholder);
	});

	// Setup the register novel modal
	setupModalForm(reg_novel_submit, reg_novel_modal, reg_novel_form, lib_flashpanel);


	// Setup the edit novel modal
	setupModalForm(edit_novel_submit, edit_novel_modal, edit_novel_form, lib_flashpanel);

	//Setup the remove novel modal
	setupModalForm(remove_novel_submit, remove_novel_modal, remove_novel_form, lib_flashpanel);
}

function setupTableOfContents(){
	const toc_flashpanel = "#toc_flashpanel";
	const jump_to_curr_btn = "#jump_to_curr_btn";
	const update_series_btn = "#update_series_btn";
	const rmv_all_bkmk_btn = "#rmv_all_bkmk_btn";

	// Bookmark events
	$('.toc_chapter_bookmark').click(function(event){
		// Make a post request to the route responsible for handling the form's backend
		var url = $(this).attr('action');
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
				var msg = `${CRITICAL_BOLD} An unexpected error occurred while trying to toggle bookmark`;
				createFlashMessage(msg, CRITICAL, toc_flashpanel);
			}
		});
	});

	// Setcurrent events
	$('.toc_chapter_setcurrent').click(function(event){
		var url = $(this).attr('action');
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
				var msg = `${CRITICAL_BOLD} An unexpected error occurred while trying to set the current chapter`;
				createFlashMessage(msg, CRITICAL, toc_flashpanel);
			}
		});
	});

	// Menu button events
	if(!$(jump_to_curr_btn)[0].hasAttribute('disabled')){
		$(jump_to_curr_btn).click(function() {
			try{
				$('html, body').animate({
					scrollTop: $(".current_chapter").offset().top - document.documentElement.clientHeight/2
				}, 500);
			}
			catch(err){ /* Do nothing */ }
		});
	}

	if(!$(update_series_btn)[0].hasAttribute('disabled')){
		var update_series_btn_enabled = true;
		$(update_series_btn).click(function(){
			if(!update_series_btn_enabled){
				return
			}
			update_series_btn_enabled = false;

			// Make a post request to the route responsible for handling the form's backend
			createFlashMessage(
				"Fetching latest chapters... please wait a few seconds",
				WARNING,
				toc_flashpanel);
			var url = $(this).attr('action');
			$.post(url, function(data) {
				if(data.status == 'ok') {
					update_series_btn_enabled = true;
					if(data.updates > 0){
						createFlashMessage(
							`${SUCCESS_BOLD} Fetched ${data.updates} new chapters!`,
							SUCCESS,
							toc_flashpanel);
					}
					else{
						createFlashMessage(
							`${SUCCESS_BOLD} This series is already up-to-date`,
							SUCCESS,
							toc_flashpanel);
					}
					window.setTimeout(function(){
						location.reload();
					}, 1000);
				}
				else{
					createFlashMessage(
						`${CRITICAL_BOLD} Encountered an error while fetching latest chapters. Try again later`,
						CRITICAL,
						toc_flashpanel);
				}
			});
		});
	}

	if(!$(rmv_all_bkmk_btn)[0].hasAttribute('disabled')){
		$(rmv_all_bkmk_btn).click(function() {
			var url = $(this).attr('action');
			$.post(url, function(data){
				if(data.status == 'ok') {
					location.reload();
				}
			});
		});
	}
}

function setupChapter(){
	const chapter_flashpanel = "#chapter_flashpanel";

	// Fetch chapter information
	const url = this.location.href;
	const base_url = url.substring(0, url.lastIndexOf('/') + 1);
    const ch = parseInt($(`#mdata_ch`).data("value"));
    const latest_ch = parseInt($(`#mdata_latest_ch`).data("value"));

	// Previous chapter
	const ch_prev = ch - 1;
	const ch_prev_href = (ch_prev > 0) ? base_url + ch_prev : null;

	// Next chapter
	const ch_next = ch + 1;
	const ch_next_href = (ch_next <= latest_ch) ? base_url + ch_next : null;

	// Run the postprocessing algorithm
	tagged_placeholders();

	// Padding top = size of floating navbar + 10px so no content is hidden under the top navbar
	$("body").css('padding-top', $("#navbar_top").outerHeight() + 20);
    $(window).resize(function() {
        $("body").css('padding-top', $("#navbar_top").outerHeight() + 20);
    });

    // Chapter progress bar
    const documentStyle = document.documentElement.style;
	$(window).scroll(function() {
		var winTop = $(window).scrollTop();
		var docHeight = $(document).height();
		var winHeight = $(window).height();

		var progress = (winTop / (docHeight - winHeight))*100;
        documentStyle.setProperty('--chapter_progress_var', `${progress}%`);
	});

    // Chapter Navbar show-hide logic
    const navbar_speed = 100;
    $("body").click(function(e){
        if(e.target == this){
            $("#navbar_top, #navbar_bottom").toggleClass("chapter_navbar_hidden");
        }
    });

    // Chapter Navbar to-top button
    $("#chapter_to_top_btn").click(function(){
        document.body.scrollTop = 0;            // For Safari
        document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
    });

	// Bookmark button functionality
	$(".chapter_bookmark_btn").click(function(){
		var url = $(this).attr('action');
		var bookmark_btn = $(this)
		$.post(url, function(data) {
			if(data.status != 'ok') {
				createFlashMessage(
					`${CRITICAL_BOLD} Encountered an error while bookmarking this chapters. Try again later`,
					CRITICAL,
					chapter_flashpanel);
			}
			else{
				$(bookmark_btn).toggleClass("chapter_bookmark_btn_active");
                $(".chapter_sidebar_elem_icon_bookmark").toggle()
			}
		});
	});

	// Chapter Sidebar
	// Start the sidebar in hidden state with current chapter in view
	$("#ch_"+ch).get(0).scrollIntoView({ block: 'center' });

	// Chapter sidebar toggle button funcitonality
	$("#chapter_sidebar_hide_btn").click(function(){
		$(".chapter_sidebar").toggleClass("chapter_sidebar_hidden");
        $(".chapter_sidebar").one("webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend", function() {
            $(this).hide();
        });

        // Fade in the background
        $(".section_chapter").toggleClass("section_chapter_faded");
        // Hide backdrop div
        $(".chapter_sidebar_backdrop").hide();
        // Re-enable page scrolling
        $("html").css("overflow", "unset");
	});
	$("#chapter_sidebar_show_btn").click(function(){
        $(".chapter_sidebar").show().toggleClass("chapter_sidebar_hidden");

        // Fade out the background
        $(".section_chapter").toggleClass("section_chapter_faded");
        // Scroll to current chapter in sidebar
		$("#ch_"+ch).get(0).scrollIntoView({ block: 'center' });
        // Show backdrop div
        $(".chapter_sidebar_backdrop").show();
        // Hook page to temporarily disable scrolling
        $("html").css("overflow", "hidden");
	});

    // Click sidebar backdrop to dismiss sidebar
    $(".chapter_sidebar_backdrop").click(function(){
        $("#chapter_sidebar_hide_btn").click();
    });

	// Chapter sidebar navigation buttions
	$("#navbar_to_first").click(function() {
	    $("#ch_1").get(0).scrollIntoView({ behavior: 'smooth', block: 'center' });
	});
	$("#navbar_to_current").click(function() {
	    $("#ch_"+ch).get(0).scrollIntoView({ behavior: 'smooth', block: 'center' });
	});
	$("#navbar_to_latest").click(function() {
	    $("#ch_"+latest_ch).get(0).scrollIntoView({ behavior: 'smooth', block: 'center' });
	});

	// Chapter Navbar
	// Add functionality of prev, toc, and next buttons
	if(ch_prev_href){
		if(!$('#ch_prev_btn').attr('disabled')){
			$('#ch_prev_btn').click(function(){
				location.href = ch_prev_href;
			});
		}
	    // Empty GET requests on previous chapter to cache it in the background
		fetch(ch_prev_href);
	}
	if(ch_next_href){
		if(!$('#ch_next_btn, .chapter_next_chapter_section').attr('disabled')) {
			$('#ch_next_btn, .chapter_next_chapter_section').click(function(){
				location.href = ch_next_href;
			});
		}
		// Empty GET requests on next chapter to cache it in the background
		fetch(ch_next_href);
	}

	// Chapter keyboard navigation
	document.onkeydown = function(e) {
		switch(e.which) {
			// Left Key
			case 37:
				if(ch_prev_href){
					location.href = ch_prev_href;
				}
				break;
			// Right Key
			case 39:
				if(ch_next_href){
					location.href = ch_next_href;
				}
				break;
			// Exit this handler for other keys
			default:
				return;
		}
		e.preventDefault(); // prevent the default action (scroll / move caret)
	};

    // Line view button functionality
    $("#ch_lineview_btn").click(function(){
        $(".content_maintext_content").toggle();
    })
}

function setupDictionary(){
	const dict_flashpanel = "#dictionary_flashpanel";

	// Dictionary superpanel button functions
	$('#menu_dictionary_dlall_btn').click(function() {
		window.location.href = this.getAttribute('action');
	});
	$('#menu_dictionary_toggleall_btn').click(function() {
		var url = $(this).attr('action');

		$.post(url, function(data) {
			if(data.status == 'ok') {
				const master_toggle = data.toggle;
				$('.dictionary_entry').each(function(index){
					if(($(this).hasClass('dictionary_entry_disabled') && master_toggle) ||
						(!$(this).hasClass('dictionary_entry_disabled') && !master_toggle))
					{
						var toggle = $(this).find(".action_toggle_enable ion-icon").first();
						$(this).toggleClass('dictionary_entry_disabled');
						if(data.toggle){
							toggle.attr("name", "checkbox");
						}else{
							toggle.attr("name", "square-outline");
						}
					}
				});
			}
		});

		// Next click toggles dictionaries to the other state (basically toggle the url between
		// '/dictionary/toggleall/on' and '/dictionary/toggleall/off')
		var url_split = url.split('/');
		if(url_split[url_split.length-1] == 'on'){
			url_split[url_split.length-1] = 'off';
		}
		else{
			url_split[url_split.length-1] = 'on';
		}
		$(this).attr('action', url_split.join('/'));
	});

	// Dictionary searchar functionality
	$("#menu_dictionary_searchbar input").on("input", function(){
		var input = this.value;
		$('.dictionary_entry').each(function(index){

		});
	});

	// Dictionary entry button functions
	$('.action_toggle_enable ion-icon').click(function() {
		var url = $(this).parent().attr("action");
		var dict_entry = $(this).closest('.dictionary_entry');
		const dict_fname = strong(dict_entry.data('fname'));
		const dict_abbr = strong(dict_entry.data('abbr'));

		var toggle = this;
		$.post(url, function(data) {
			if(data.status == 'ok') {
				dict_entry.toggleClass('dictionary_entry_disabled');
				if(data.toggle){
					toggle.setAttribute("name", "checkbox");
				}else{
					toggle.setAttribute("name", "square-outline");
				}
			}
			else if(data.status == 'series_nf'){
				createFlashMessage(data.msg, data.severity, dict_flashpanel);
			}
			else{
				createFlashMessage(
					`${CRITICAL_BOLD} An unexpected error occurred while trying to toggle ${dict_abbr}`,
					CRITICAL,
					dict_flashpanel);
			}
		})
	});

	$('.action_download').click(function() {
		// The following code achieves the same thing by POST request
		var dict_entry = $(this).closest('.dictionary_entry');
		const dict_fname = strong(dict_entry.data('fname'));
		const dict_abbr = strong(dict_entry.data('abbr'));

		var url = this.getAttribute('action');
		$.post(url, function(data){
			if(data.status == 'dict_dne_abort'){
				createFlashMessage(
					`${CRITICAL_BOLD} The requested file ${dict_fname} does not exist. Upload a file or hit Edit under ${dict_abbr} to initialize it.`,
					CRITICAL,
					dict_flashpanel);
			}
			else if(data.status == "dict_download_error"){
				createFlashMessage(
					`${CRITICAL_BOLD} Ran into an unexpected error downloading ${dict_fname}`,
					CRITICAL,
					dict_flashpanel);
			}
			// Success
			else{
				var blob = new Blob([data], {type: "text/plain;charser=utf-8"});
				saveAs(blob, dict_entry.data('fname'));
			}
		})
	});

	$('.action_upload').click(function() {
		var dict_entry = $(this).closest('.dictionary_entry');
		var upload_file_select = dict_entry.find('.upload_file_select');
		upload_file_select.click();
	});
}

function setupDictionaryEdit(){
	const dictionary_edit_toastpanel = "#dictionary_edit_toastpanel";
	var editor_dirty = false;

	// Initialize the correct icon
	var html = document.documentElement;
	var day_night_toggle = "#menu_dictionary_edit_day_night_toggle_btn";
	$(day_night_toggle).each(function(){
		var icon_name = (html.getAttribute('data-theme') == "light") ? 'moon-outline' : 'sunny-outline';
		var icon = $(this)[0].querySelector('ion-icon');
		icon.setAttribute('name', icon_name);
	});

	// Add functionality to toggle day and night UIs
	$(day_night_toggle).click(function(){
		// Toggle the theme
		if(html.getAttribute('data-theme') == "light"){
			html.setAttribute('data-theme', 'dark');
		}
		else{
			html.setAttribute('data-theme', 'light');
		}

		// Change the toggle button
		$(day_night_toggle).each(function(){
			var icon_name = (html.getAttribute('data-theme') == "light") ? 'moon-outline' : 'sunny-outline';
			var icon = $(this)[0].querySelector('ion-icon');
			icon.setAttribute('name', icon_name);
		});

	});

	// Define a simple lexer for the dictionary syntax
	CodeMirror.defineMode("dictionary_mode", function() {
		return {
			startState: function() {
				return {
					validNameTag: false,
					validNameArgs: false,
					validDivLine: false
				};
			},
			token: function(stream, state) {
				// Rule for detecting meta header comments
				if(stream.match(/\s*\/\/\s*series_(?:title|abbr|link)\s*:(?:.*)/)){
					stream.skipToEnd();
					return "dict-meta";
				}

				// Rule for detecting comments '//'
				if(stream.match(/\s*\/\/.*/)) {
					stream.skipToEnd();       // Rest of the line is comment
					return "dict-comment";
				}

				// Rule for detecting the nametag syntax '@name'
				if(stream.match(/@name\{(.*\S.*),(.*\S.*)\}/, false)){
					state.validNameTag = true;
					stream.skipTo("{");
					return "dict-nametag";
				}
				else if(state.validNameTag){
					// First determine if the arguments provided are balanced and valid
					if(!state.nameArgsValidated){
						var matches = stream.match(/\{(.+), (.+)\}/, false);
						if(matches){
							// Same number of splits in both args
							if(matches[1].split('|').length != matches[2].split('|').length){
								stream.next();
								return "line-dict-error";
							}
							// No empty strings in args
							if(matches[1].split('|').includes('') || matches[2].split('|').includes('')){
								stream.next();
								return "line-dict-error";
							}
						}

						state.nameArgsValidated = true;
					}

					if(stream.match(/[,{]/)){
						return null;
					}
					if(stream.match(/\|/)){
						return "dict-namesplit";
					}
					if(stream.match(/}/)){
						// End of the name tag, reset nametag states
						state.validNameTag = false;
						state.nameArgsValidated = false;
						// Eat up the trailing spaces between this nametag and either an inline comment or EOL
						stream.match(/\s*/);
						return null;
					}

					stream.next();
					return null;
				}

				// Rule for detecting individual definition dividers '-->'
				// Note: Regex captures definition up to a potential comment at the end
				var div_match = stream.match(/(.*\S.*)-->([^\/\/]*)/, false);
				if(!state.validDivLine && div_match){
					// Check the RHS of the divider is non-whitespace
					if(div_match[2].match(/.*\S.*/, false)){
						stream.skipTo("-->");
						state.validDivLine = true;
						return null;
					}
				}
				else if(state.validDivLine){
					// If we enter this block, we're right at the divider
					if(stream.match("-->")){
						return "dict-divider";
					}

					// At this point we're at the translated definition
					/* To take into account inline comments, either jump iterator to start of comment
					   if there is one, or jump straight to the end of the line*/
					stream.pos = 0;
					if(stream.match(/(.+)-->(.+)\s*\/\//, false)){
						stream.skipTo("//");
					}
					else{
						stream.skipToEnd();
					}

					// Done, reset divline states
					state.validDivLine = false;
					return null;
				}

				// Skip whitespace lines
				if(stream.match(/^\s*$/)){
					stream.skipToEnd();
					return null;
				}
				// By default a line is an error if it does not fit any of the above rules
				stream.next();
				return "line-dict-error";
			}
		};
	});

	// Create the custom CodeMirror text area
	var dict_editor = CodeMirror.fromTextArea($('#dictionary_editor')[0], {
		mode: "dictionary_mode",
		keyMap: "sublime",
		autoCloseBrackets: true,
		matchBrackets: true,
		showCursorWhenSelecting: true,
		tabSize: 2
	});

	// When user makes changes on the CodeMirror editor, determine if the editor is "dirty"
	dict_editor.on('change', function(){
		curr_content = dict_editor.getDoc().getValue();
		old_content = $('#dictionary_editor').text();
		if(curr_content == old_content){
			editor_dirty = false;
		}
		else {
			editor_dirty = true;
		}
	});

	// On Ctrl-S, if the CodeMirror editor's textarea is in focus, act as an alibi for Save button
	$(".CodeMirror").bind('keydown', function(event) {
		if (event.ctrlKey || event.metaKey) {
			switch (String.fromCharCode(event.which).toLowerCase()) {
				case 's':{
					event.preventDefault();
					$('#menu_dictionary_edit_save_btn').click();
					break;
				}
			}
		}
	});

	// Editor toolbelt button functions
	$('#menu_dictionary_edit_save_btn').click(function(){
		// Send the data to be saved in a POST request
		if(editor_dirty){
			const url = $(this).attr('action');
			const content = dict_editor.getDoc().getValue();

			$.post(url, {"content": content}, function(data){
				if(data.status == 'ok'){
					createToast("Your changes were saved",
						"success",
						"successful_save",
						dictionary_edit_toastpanel);
					$('#dictionary_editor').text(content);
					editor_dirty = false;
				}
				else{
					createToast("Ran into an error! Sorry",
						"danger",
						"error_on_save",
						dictionary_edit_toastpanel);
				}
			});
		}
		else{
			createToast("No changes to save, ignored",
				"warning",
				"warning_on_save",
				dictionary_edit_toastpanel);
		}
	});

	$('#confirm_discard_btn').click(function(){
		// Update CodeMirror to show the old contents
		if(editor_dirty){
			const old_content = $('#dictionary_editor').text();
			dict_editor.getDoc().setValue(old_content);
			createToast("Your changes were discarded",
				"success",
				"successful_discard",
				dictionary_edit_toastpanel);
		}
		else{
			createToast("No changes to discard, ignored",
				"warning",
				"warning_on_discard",
				dictionary_edit_toastpanel);
		}
	});

	$('#menu_dictionary_edit_fullscreen_btn').click(function(){
		$('.dictionary_edit_body').toggleClass('fullscreen');
	});

	/* Editor utilbelt button functions */
	$(".dictionary_edit_utility_btn").click(function(){
		var cm = $(".CodeMirror")[0].CodeMirror;
		var doc = cm.getDoc();
		var cursor = doc.getCursor();
		const line = doc.getLine(cursor.line);

		switch($(this).attr('id')) {
			case "util_new_line":{
				// Insert new line
				doc.replaceRange("\n", {
					line: cursor.line
				});
				break;
			}
			case "util_del_line":{
				// Insert new line
				cm.execCommand("deleteLine");
				break;
			}
			case "util_new_def":{
				// Insert new definition
				const insert_text = "   -->     // ";
				if (line.length === 0) {
					doc.replaceRange(insert_text, {
						line: cursor.line
					});
				} else {
					doc.replaceRange(`\n${insert_text}`, {
						line: cursor.line
					});
				}
				break;
			}
			case "util_new_name":{
				const insert_text = "@name{   ,   }   // ";
				if (line.length === 0) {
					doc.replaceRange(insert_text, {
						line: cursor.line
					});
				} else {
					doc.replaceRange(`\n${insert_text}`, {
						line: cursor.line
					});
				}
				break;
			}
			case "util_insrt_name_div":{
				cm.setSelection(cursor, cursor);
				cm.replaceSelection("|");
				break;
			}
			case "util_insrt_comm_div":{
				const insert_text = "//=============================[  ]==================================";
				if (line.length === 0) {
					doc.replaceRange(insert_text, {
						line: cursor.line
					});
				} else {
					doc.replaceRange(`\n${insert_text}`, {
						line: cursor.line
					});
				}
				break;
			}
			default:
				// No Op
		}
	});
}

function setupHonorifics(){
	$('[data-toggle="tooltip"]').tooltip();

	const honorifics_flashpanel = '#honorifics_flashpanel'
	// Add honorific modal components
	const add_honorific_submit = '#add_honorific_submit_btn';
	const add_honorific_modal = '#add_honorific_modal_push';
	const add_honorific_form = '#add_honorific_form';
	// Edit honorific modal components
	const edit_honorific_submit = '#edit_honorific_submit_btn';
	const edit_honorific_modal = '#edit_honorific_modal_push';
	const edit_honorific_form = '#edit_honorific_form';
	const edit_honorific_action_base = $(edit_honorific_form).attr('action').substr(0,
		$(edit_honorific_form).attr('action').lastIndexOf("/"));
	// Remove honorific modal components
	const remove_honorific_modal = '#remove_honorific_modal';
	const remove_honorific_action_base = $(remove_honorific_modal).attr('action').substr(0,
		$(remove_honorific_modal).attr('action').lastIndexOf("/"));


	// On show Edit Modal events
	$(edit_honorific_modal).on('shown.bs.modal', function (event) {
		var hon_entry = $(event.relatedTarget).closest('.honorific_entry');
		var id = hon_entry.data('id');
		var lang_val = hon_entry.data('lang-val');
		var hraw = hon_entry.data('hraw');
		var htrans = hon_entry.data('htrans');
		var affix_val = hon_entry.data('affix-val');
		var opt_with_dash = (hon_entry.data('opt-with-dash').toLowerCase() == "true");
		var opt_standalone = (hon_entry.data('opt-standalone').toLowerCase() == "true");

		// Set the defaults for the form fields
		$(`${edit_honorific_modal} #lang`).val(lang_val);
		$(`${edit_honorific_modal} #hraw`).val(hraw);
		$(`${edit_honorific_modal} #htrans`).val(htrans);
		$(`${edit_honorific_modal} #affix-${affix_val-1}`).prop('checked', true);
		$(`${edit_honorific_modal} #opt_with_dash`).prop('checked', opt_with_dash);
		$(`${edit_honorific_modal} #opt_standalone`).prop('checked', opt_standalone);

		// Customize the edit form's action and id to that of the honorific entry that triggered
		// the Edit Honorific modal
		$(`${edit_honorific_modal} input[name="hon_id"]`).val(id)
		$(edit_honorific_form).attr('action', `${edit_honorific_action_base}/${id}`);
	});

	// Setup the Add Honorific modal
	setupModalForm(add_honorific_submit, add_honorific_modal, add_honorific_form,
		honorifics_flashpanel);
	// Setup the Edit Honorific modal
	setupModalForm(edit_honorific_submit, edit_honorific_modal, edit_honorific_form,
		honorifics_flashpanel);

	$('#menu_honorifics_toggleall_btn').click(function() {
		var url = $(this).attr('action');

		$.post(url, function(data) {
			if(data.status == 'ok') {
				const master_toggle = data.toggle;
				$('.honorific_entry').each(function(index){
					if(($(this).hasClass('honorific_entry_disabled') && master_toggle) ||
						(!$(this).hasClass('honorific_entry_disabled') && !master_toggle))
					{
						var toggle = $(this).find(".action_toggle_enable ion-icon").first();
						$(this).toggleClass('honorific_entry_disabled');
						if(data.toggle){
							toggle.attr("name", "checkbox");
						}else{
							toggle.attr("name", "square-outline");
						}
					}
				});
			}
		});

		// Next click toggles dictionaries to the other state (basically toggle the url between
		// '/dictionary/toggleall/on' and '/dictionary/toggleall/off')
		var url_split = url.split('/');
		if(url_split[url_split.length-1] == 'on'){
			url_split[url_split.length-1] = 'off';
		}
		else{
			url_split[url_split.length-1] = 'on';
		}
		$(this).attr('action', url_split.join('/'));
	});

	// Honorific entry button functions
	$('.action_toggle_enable ion-icon').click(function() {
		var url = $(this).parent().attr("action");
		var hon_entry = $(this).closest('.honorific_entry');
		const hon_id = strong(hon_entry.data('id'));

		var toggle = this;
		$.post(url, function(data) {
			if(data.status == 'ok') {
				hon_entry.toggleClass('honorific_entry_disabled');
				if(data.toggle){
					toggle.setAttribute("name", "checkbox");
				}else{
					toggle.setAttribute("name", "square-outline");
				}
			}
			else if(data.status == 'hon_nf'){
				createFlashMessage(data.msg, data.severity, honorifics_flashpanel);
			}
			else{
				createFlashMessage(
					`${CRITICAL_BOLD} An unexpected error occurred`,
					CRITICAL,
					honorifics_flashpanel);
			}
		})
	});

	// On show Remove Modal events
	$(remove_honorific_modal).on('shown.bs.modal', function (event) {
		var hon_entry = $(event.relatedTarget).closest('.honorific_entry');
		var id = hon_entry.data('id');
		var hraw = hon_entry.data('hraw');
		var htrans = hon_entry.data('htrans');

		$(remove_honorific_modal).attr('action', `${remove_honorific_action_base}/${id}`);
		$(`${remove_honorific_modal} span[name="hraw"]`).text(hraw);
		$(`${remove_honorific_modal} span[name="htrans"]`).text(htrans);
	});

	$('#confirm_delete_honorific_btn').click(function(){
		var url = $(remove_honorific_modal).attr('action');
		$.post(url, function(data) {
			if(data.status == 'ok') {
				location.reload();
			}
			else{
				createFlashMessage(
					`${CRITICAL_BOLD} ${data.msg}`,
					data.severity,
					honorifics_flashpanel);
			}
		})
	});
}

function setupSettings(){
	// Helper function to create successful setting message
	function showSettingMsgDiv(where_to_show, status, message){
		// Append to "where"
		if($(where_to_show).find('.setting_msg').length !== 0){
			// If the message div already exists, update it
			var msg_div = $(where_to_show).find('.setting_msg');
			msg_div.find('span').text(message);

			msg_div.removeClass();
			msg_div.addClass('setting_msg');
			if(status == "success"){
				msg_div.addClass('setting_success_msg');
				msg_div.addClass('text-success');
				msg_div.find('ion-icon').attr('name', 'checkmark-circle')
			}
			else if(status == "error"){
				msg_div.addClass('setting_error_msg');
				msg_div.addClass('text-danger');
				msg_div.find('ion-icon').attr('name', 'close-circle')
			}
		}
		else{
			// If the message div dne, create it
			var msg_div = document.createElement('div');
			var msg_icon = document.createElement('ion-icon');

			msg_div.classList.add('setting_msg');
			if(status == "success"){
				msg_div.classList.add('setting_success_msg');
				msg_div.classList.add('text-success');
				msg_icon.setAttribute('name', 'checkmark-circle')
			}
			else if(status == "error"){
				msg_div.classList.add('setting_error_msg');
				msg_div.classList.add('text-danger');
				msg_icon.setAttribute('name', 'close-circle')
			}


			var msg_span = document.createElement('span');
			msg_span.innerText = message;

			// Form the HTML tree
			$(msg_div).append(msg_icon);
			$(msg_div).append(msg_span);

			// Add new element to target
			$(where_to_show).append(msg_div);
		}

	}

	// Clear cache functionality
	$("#settings_clear_cache_btn").click(function(){
		var url = $(this).attr('action');
		$.post(url, function(data) {
			if(data.status == 'ok') {
				const msg = "Chapter cache cleared!";
				showSettingMsgDiv("#clear_chapter_cache_setting_opt", "success", msg)

				// Disable this button
				$("#settings_clear_cache_btn").attr("disabled", true);
			}
		})
	});

	// Set chapter theme functionality
	$(".chapter_theme_option").click(function(){
		var url = $(this).attr('action');
		var theme = $(this).data('theme');
		$.post(url, function(data) {
			if(data.status == 'ok') {
				const msg = `Set chapter reader theme to ${theme}`;
				showSettingMsgDiv("#chapter_theme_setting_desc_div", "success", msg);
			}
			else{
				const msg = "Encountered an error setting chapter theme";
				showSettingMsgDiv("#chapter_theme_setting_desc_div", "error", msg);
			}
		})
	});

	// Set dictionary edit theme functionality
	$(".dict_edit_theme_option").click(function(){
		var url = $(this).attr('action');
		var theme = $(this).data('theme');
		$.post(url, function(data) {
			if(data.status == 'ok') {
				const msg = `Set dictionary edit reader theme to ${theme}`;
				showSettingMsgDiv("#dict_edit_theme_setting_desc_div", "success", msg);
			}
			else{
				const msg = "Encountered an error setting dictionary edit theme";
				showSettingMsgDiv("#dict_edit_theme_setting_desc_div", "error", msg)
			}
		})
	});
}