/**
 * Utils
 *
 * @author Olivier Pons
 * @creation          2017/09/20
 * @last_modification 2017/09/20
 */

/**
 * Equivalent to Python strip() function
 *
 * https://stackoverflow.com/
 * questions/1418050/string-strip-for-javascript
 */
if(typeof(String.prototype.trim) === "undefined")
{
    String.prototype.trim = function() {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}

/**
 * Equivalent to Python format() function
 *
 * Usage '{0} {1}'.format(arg0, arg1)
 * (!) numbers in {} are MANDATORY: this WON'T WORK: '{} {}'.format(arg0, arg1)
 *
 * https://stackoverflow.com/
 * questions/610406/javascript-equivalent-to-printf-string-format
 */
if (!String.prototype.format) {
    String.prototype.format = function() {
        let args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) {
          return typeof(args[number]) !== 'undefined' ? args[number] : match;
        });
    };
}

/**
 * First letter upcase of a word (only first letter all other lowercase)
 */
if (!String.prototype.capitalize) {
    String.prototype.capitalize = function() {
        let args = arguments,
            self = String(this);
        for (let i in args) {
            self = self.split(args[i]).join('|')
        }
        let tab = self.split('|'),
            result = '';
        for (let j in tab) {
            let c = tab[j];
            result += ' ' + c.charAt(0).toUpperCase() + c.slice(1);
        }
        return result.trim();
    };
}

/**
 * Function to call when an AJAX call failed: clear all DOM to make sure the
 * user cant do something, but make sure that the user is warned about a
 * critical problem.
 *
 * This function should never be called (it implies an AJAX critical failure).
 */
function ajax_handle_critical_error (error_message) {
    "use strict";
    let msg = (
        (typeof(error_message) === 'string') && (!!error_message)
        ? error_message
        : 'A critical error has been raised when making an AJAX call');
    $('body').html(
        '<h1 style="text-align: center; ' +
                   'margin-top: 10%; padding-top: 10%; padding-bottom: 10%;">'+
        msg+
        '</h1>'
    );
}

/**
 * Filter by data. As usual, thanks stackoverflow:
 * https://stackoverflow.com/
 * questions/1009485/filter-element-based-on-data-key-value
 *
 * @param key Key to search
 * @param value Value to search
 */
$.fn.filterByData = function(key, value) {
    /* (!) I had to add ".find('*')" which is overkill but works: */
    return this.find('*').filter(function() {
        return $(this).data(key) === value;
    });
};


/**
 * Generates a random name with a max len
 *
 * @param len Int max length of the name
 * @param full_name Bool if the result is a full name or may contain spaces
 * @param with_numbers Bool if the result may contain numbers
 */
let randomName = (len, full_name=false, with_numbers=false) => {
    let rnd = function(a) {
            let result = a.substr(
                Math.floor(Math.random() * (a.length / 2)) * 2, 2
            ).trim();
            return (result !== '' ? result : ' ');
        },
        first = "B C D F G H J K L M N P R S T V W X Z ",
        v = 'a e o u a e i o u a e i o u y eiaiou',
        c = 'b c d f g h k l m n p qur s t v w x z brtrccssttthcrfr'+
            (with_numbers ? '0 1 2 3 4 5 6 7 8 9 _ _ - ' : '')+
            (full_name ? '' : '                            '),
        text = rnd(first).trim()+rnd(v).trim();
    if (full_name) {
        while (text.length<len) {
            text += rnd(c).trim()+rnd(v).trim();
        }
    } else {
        while (text.length<len) {
            text += rnd(c)+rnd(v);
        }
    }
    return text.capitalize(' ', '-', '_');
};

/**
 * Generates a random IP v4 string
 *
 * @returns {string}
 */
let randomIP = () => {
    "use strict";
    let rnd = (mx) => Math.floor(Math.random() * mx);
    return '192.168.'+rnd(10)+'.'+rnd(254);
};


/**
 * Makes Python-like deep copy of an object. As usual, thanks stackoverflow.
 *
 * @param obj
 */
function deepCopy(obj) {
    "use strict";
    return $.extend(true, {}, obj);
}

/**
 * How to read the csrf cookie... well, how to read cookies in general.
 * https://docs.djangoproject.com/fr/1.11/ref/csrf/
 *
 * @param name
 * @returns {*}
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Check if an object has all the properties arguments *after* the obj argument
 *
 * @param obj
 * @returns {*}
 */
function hasOwnProperties(obj) {
    "use strict";
    for (let i=1; i<arguments.length; i++) {
        if (!obj.hasOwnProperty(arguments[i])) {
            return false;
        }
    }
    return true;
}


/**
 * Save and restore events fot the given jquery element
 *
 * Taken from (and re-worked a bit by Olivier Pons):
 * https://github.com/1rosehip/snippets.js.save-restore-events
 *
 * USAGE:
 *
 * - Save events
 * $.srEvents.save($('#test'), 'custom-events');
 *
 * - Remove all events
 * $('#test').off();
 *
 * - Restore events
 * $.srEvents.restore($('#test'), 'custom-events');
 *
 */
(function($){
    'use strict';
    
    /** 
     * Save and Restore Events
     * @type {Object}
     */
    $.srEvents = {};
    
    /**
     * save events
     * @param {object} $elements jQuery elements
     * @param {string} propertyName - property that keeps event data
     *               (in data object)
     */
    $.srEvents.save = function($elements, propertyName) {
                
        if ($elements && $elements.length > 0) {
            $elements.each(function() {
                let $el = $(this), copyOf, events;
                //get events from element
                events = $._data($el.get(0), 'events');
                //create deep copy of the events object
                copyOf = $.extend(true, {}, events);            
                //save events in data
                $el.data(propertyName, copyOf);
            });
        }        
    };
    
    /**
     * restore events 
     * @param {object} $elements jQuery elements
     * @param {string} propertyName - property that keeps event data
     *               (in data object)
     */
    $.srEvents.restore = function($elements, propertyName){

        if ($elements) {
            $elements.each(function() {
                let $el = $(this), events;
                
                //get saved events
                events = $el.data(propertyName);
                if (events) {
                    $.each(events, function(eventName, eventHandler) {
                        if (eventHandler) {
                            $.each(eventHandler, function() {
                                if ($.isFunction(this.handler)) {
                                    $el.on(eventName, this.handler);
                                }
                            });
                        }
                    });
                }
            });
        }
    };
})(jQuery);