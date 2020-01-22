(function() {
    'use strict';
    $(() => {
        /* click() callbacks AFTER buttons added to the DOM: */
        let make_reset_btn = function(specific_img_src=undefined) {
            let img_src=wizard.icons.option_reset.url_refresh;
            /* Maybe a different icon to reset depending on the context: */
            if (!!specific_img_src) {
                img_src = specific_img_src;
            }
            return $('<div />')
                .css(wizard.icons.option_reset.css)
                .attr('id', 'reset_button')
                .append(
                    $('<i class="fas fa-trash"></i>')
                        .css(wizard.icons.option_reset.css_img)
                        .attr('title', wizard.icons.option_reset.description)
                        .attr('alt', wizard.icons.option_reset.description),
                    /*
                    $('<img src="" alt="" />')
                        .attr('src', img_src)
                        .attr('title', wizard.icons.option_reset.description)
                        .attr('alt', wizard.icons.option_reset.description)
                        .css(wizard.icons.option_reset.css_img)
                    */
                );
        };
        let click_reset_callback = (function (e) {
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            /* TODO Make a better good-looking reset button: */
            if (confirm("Reset the Wizard?\n"+
                "All modifications will be lost")) {
                let final_data = {'reset': true};
                final_data['csrftoken'] = getCookie('csrftoken');
                final_data['csrfmiddlewaretoken'] = getCookie('csrftoken');
                $.ajax({
                    url: wizard.urls.reset,
                    dataType: 'json',
                    method: 'post',
                    data: final_data,
                    cache: false
                }).done(function (data) {
                    window.location.reload(true);
                }).fail(ajax_handle_critical_error);
            }
        });
        let click_cancel_callback = (function (e) {
            if (e && e.preventDefault) {
                e.preventDefault();
            }
            /* TODO Make a better good-looking reset button: */
            if (confirm("Cancel modification?\n"+
                "Current modifications will be lost")) {
                let final_data = {'cancel': true};
                final_data['csrftoken'] = getCookie('csrftoken');
                final_data['csrfmiddlewaretoken'] = getCookie('csrftoken');
                $.ajax({
                    url: wizard.urls.cancel,
                    dataType: 'json',
                    method: 'post',
                    data: final_data,
                    cache: false
                }).done(function (data) {
                    window.location.reload(true);
                }).fail(ajax_handle_critical_error);
            }
        });
        /* override ajax_handle_critical_error to add translation: */
        let old_ajax_handle_critical_error = window.ajax_handle_critical_error;
        window.ajax_handle_critical_error = function () {
            /* ! not same icon for same action (reset): */
            let reset_btn = make_reset_btn(
                wizard.icons.option_reset.url_recycle_bin
            );
            old_ajax_handle_critical_error(
                wizard.error_critical_message + '<br/><br/>' +
                wizard.error_text_for_reset + '&nbsp;' +
                reset_btn.html()
            );
            /* Apply reset click after it's inserted into DOM (~100ms): */
            setTimeout(function () {
                /**
                 * The body is cleared and contains only:
                 * - the message
                 * - the image of the reset button
                 * -> $('#reset_button') doesn't find the button.
                 * -> ugly workaround: assign click() to all imgs
                 *    (there's only one here)
                 */
                $('body').find('img').each(function () {
                    $(this).click(click_reset_callback);
                });
            }, 100);
        };

        /* ! important: never cache Ajax calls */
        $.ajaxSetup({ cache: false });
        let wizard_id = 'wizard',
            reset_btn = make_reset_btn(),
            close_btn = $('<div/>')
                .css(wizard.icons.option_close.css)
                .attr('id', 'close_button')
                .append(
                    $('<i class="fas fa-home"></i>')
                        .css(wizard.icons.option_close.css_img)
                        .attr('title', wizard.icons.option_close.description),
                    /*
                    $('<img />')
                        .attr('src', wizard.icons.option_close.url)
                        .attr('title', wizard.icons.option_close.description)
                        .attr('alt', wizard.icons.option_close.description)
                        .css(wizard.icons.option_close.css_img)

                     */
                ),
            $wizard = $('<div />').addClass('wizard-container');
            $('.container-fluid').append($wizard);
        /**
         * Hack to center an absolute positioned div: stackoverflow :
         * questions/1776915/how-to-center-absolutely-positioned-element-in-div
         */
        $wizard = $('<div />').attr('id', wizard_id).appendTo($wizard);
        $wizard.show();

        /**
         * Test compatibility of "AJAX file sending", thanks stackoverflow:
         * https://stackoverflow.com/questions/7296426/how-can-i-check-
         * if-the-browser-support-html5-file-upload-formdata-object
         */
        let supportAjaxUploadProgressEvents = function () {
            let x = new XMLHttpRequest(),
                r = !! (x && ('upload' in x) && ('onprogress' in x.upload));
            return r && (typeof(window.FormData) !== 'undefined');
        };
        if (!supportAjaxUploadProgressEvents()) {
            /* Show message to upgrade the browser, and immediate return: */
            $('#wizard').append(
                $('<h1>').css({ "text-align": "center", "margin": "10%"})
                         .append(wizard.not_compatible)
            );
            return;
        }
        new WzContentWithButtons(
            undefined,
            {
                /* url to refresh */
                ajax: {
                    url: wizard['urls']['get_step']
                },
                /* CSS: for buttons prev/next: */
                css_buttons: wizard.css_buttons,
                /* CSS: for help buttons: */
                css_help_url: wizard.css_help_url,
                /**
                 * Hard-coded click callbacks
                 * A Django answer could contain 'callback':'reset' to launch
                 * a reset -> we search here:
                 */
                callbacks: {
                    reset: click_reset_callback,
                    cancel: click_cancel_callback
                }
            },
            /* no wrapper = empty string, NOT undefined */
            '',
            /* callback when ajax is done: */
            (wz, data) => {
                $wizard.empty().append(
                    close_btn, reset_btn,
                    wz.render().css(wizard.css_main_div)
                );
                /* click() callbacks AFTER buttons added to the DOM: */
                reset_btn.click(click_reset_callback);
                close_btn.click(function (e) {
                    e.preventDefault();
                    $('#'+wizard_id).remove();
                    window.location = wizard.urls.close;
                });
                wz.after_render();
                /* get might send ('cancel': true) to show 'cancel' button: */
                wz.test_cancel_button(data);

                /**
                 * ! 2018-09-20 Hack to handle when screen is resized:
                 *   sometimes, help elements 'span' are not aligned with
                 *   their input
                 *   -> for each input, check siblings, and if there's a 'span'
                 *      make sure it has the same 'left' property so that they
                 *      are properly aligned
                 */
                let gTimerResize;
                let handleScreenResized = function () {
                    $('#'+wizard_id+' input').each(function () {
                        let left = $(this).position().left;
                        $(this).siblings()
                            .filter('[class*="help"]')
                            /* ! hack in a hack: dont move if css-fixed: */
                            .filter(':not([css-fixed="true"])')
                            .each(function () {
                                if ($(this).position().left !== left) {
                                    $(this).css('left', left + 'px');
                                }
                            });
                    });
                };
                gTimerResize = window.setTimeout(handleScreenResized, 1);
                $(window).resize(function(){
                    if (gTimerResize !== null) {
                        window.clearTimeout(gTimerResize);
                    }
                    gTimerResize = window.setTimeout(handleScreenResized, 150);
                });
            }
        ).ajax_refresh(undefined);


    });

})();
