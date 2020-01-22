/**
 * Backbone of the Wizard
 *
 * JavaScript interesting free book:
 * https://github.com/getify/You-Dont-Know-JS
 */

'use strict';

class WzData {
    /**
     * constructor
     * @param parent Children often need a reference to their parent
     * @param data   Data object (specific use for each descendant)
     */
    constructor(parent, data)
    {
        this.parent = parent;
        this.data = data;
        if (this.data === undefined) {
            this.get = function () { return undefined; };
        }
        this.set_ajax_data(undefined);
    };
    /**
     * Get the data that was passed when created
     * @param value_default
     * @returns {*}
     */
    get_data(value_default)
    {
        return (this.data ? this.data : value_default);
    };
    /**
     * Set the ajax_data property
     * @param value Value to assign
     * @returns {*}
     */
    set_ajax_data(value)
    {
        this.ajax_data = value;
        return this.ajax_data;
    };
    /**
     * Read the value of a field in this.data
     * @param field Name of the field
     * @param value_default Value to return if field not found
     * @returns {*}
     */
    get(field, value_default=undefined)
    {
        let c = this.data[field];
        if (typeof(c) === 'undefined') {
            return value_default;
        }
        return c;
    }
    /**
     * Uses "ajax_data" object: composed of
     * key = id of and object, value = value to set
     * For each key, if there's a DOM object with that id, set the value.
     * @returns {*}
     */
    refresh_dom_ajax_objects()
    {
        /**
         * Previous callback calls have re-rendered the elements.
         * See there's "ajax_data" and if so, search if there are
         * elements with ids in "ajax_data" that are not set.
         * If so, apply the values so that the concerned elements make
         * ajax call:
         */
        let self = this,
            delay = 100;
        while (self !== undefined) {
            let ajax_data = self.ajax_data;
            for (let key in ajax_data) {
                if (ajax_data.hasOwnProperty(key)) {
                    let value = ajax_data[key],
                        obj = $('#'+key);
                    if (!obj.length) {
                        /* Search by name (= inputs have names, not ids!) */
                        obj = $('[name="'+key+'"]');
                    }
                    if (obj.length && (obj.val() !== value)) {
                        let wz = obj.data('wz'),
                            assigned_later = false;
                        if (wz !== undefined) {
                            if (wz.get('ajax')) {
                                setTimeout(() => {
                                    obj.val(value).change();
                                    delete ajax_data[key];
                                }, delay);
                                assigned_later = true;
                                delay += 10;
                            }
                        }
                        if (!assigned_later) {
                            /* Not to be removed later = remove it now: */
                            obj.val(value).change();
                            delete ajax_data[key];
                        }
                    }
                }
            }
            self = self.parent;
        }
    }
}

/**
 * Class that has a "pointer" to the DOM elements that are created.
 */
class WzDataRender extends WzData {
    /**
     * constructor
     * @param parent Children often need a reference to their parent
     * @param data   Data object (specific use for each descendant)
     * @param wrapper render() wraps the content with this element
     */
    constructor(parent, data, wrapper='<span />') {
        super(parent, data);
        this._root = undefined;
        this._$elements = undefined;
        this._wrapper = wrapper;
        let data_wrapper = this.get('wrapper');
        if (data_wrapper) {
            if (/<[a-z][\s\S]*>/i.test(data_wrapper)) {
                /* it's HTML -> I suppose it's a jQuery tag like "<p />" */
                this._wrapper = data_wrapper;
            } else {
                /* NOT HTML -> I suppose it's a jQuery tag like "p" */
                this._wrapper = '<'+data_wrapper+' />';
            }
        }
    };
    /**
     * Set if render() wraps the content or not.
     * @param wrapper if render() wraps the content with this element
     * @returns void
     */
    set_wrapper(wrapper)
    {
        this._wrapper = wrapper;
    }
    /**
     * Read the root element (= the element that has no parent).
     * This method caches the root at first call.
     *
     * @returns {*}
     */
    get_root()
    {
        if (this._root !== undefined) {
            return this._root;
        }
        /* the "root" can be "this" (if it has not parent), it's normal: */
        this._root = this;
        while (this._root.parent !== undefined) {
            this._root = this._root.parent;
        }
        return this._root;
    }
    /**
     * Read the jQuery elements reference
     *
     * @returns {*}
     */
    get_$elements()
    {
        return this._$elements;
    }
    /**
     * Remember the contents. To use when rendering.
     *
     * @param jquery_elements All jquery elements
     * @returns {* | jQuery}
     */
    set_$elements(jquery_elements)
    {
        this._$elements = jquery_elements;
        return this._$elements;
    };
    /**
     * Return a function to either get from this.data or from the object.
     *
     * @param obj Object to fetch properties (if undefined, read from this.data)
     * @returns function
     */
    fnGetFromObjOrFromData(obj=undefined)
    {
        if (obj===undefined) {
            return this.get;
        }
        return (idx) => {
            return obj.hasOwnProperty(idx) ? obj[idx] : undefined;
        }
    }
    /**
     * Look for properties and apply them to the element parameter.
     *
     * @param element jQuery object
     * @param tab Array of string that are the properties to look for
     * @param src Object to fetch properties (if undefined, read from this.data)
     * @returns {* | jQuery}
     */
    applyProperties(element, tab, src=undefined)
    {
        let fn = this.fnGetFromObjOrFromData(src);
        for (let i=0; i<tab.length; i++) {
            let key= tab[i],
                property = fn.call(this, key);
            if ((property !== undefined) && (property !== '')) {
                element.attr(key, property);
            }
        }
        return element;
    }
    /**
     * Look for a hard-coded callback in the root. If found, apply it.
     *
     * @param element jQuery object
     * @param tab Array of string that are the properties to look for
     * @returns {* | jQuery}
     */
    applyCallback(element, tab)
    {
        /* first try the global callback: */
        let root_callbacks = this.get_root().get('callbacks');
        if (root_callbacks!==undefined) {
            for (let i=0; i<tab.length; i++) {
                let key= tab[i];
                if (root_callbacks.hasOwnProperty(key)) {
                    element.on('click', root_callbacks[key]);
                    return element;
                }
            }
        }
        /* if global callback, try the current object: */
        let callback = this.get('callback');
        if (callback===undefined) {
            return element;
        }
        element.on('click', callback);
        return element;
    }
    /**
     * Look for 'required' property and apply it to the element parameter.
     *
     * @param element jQuery object
     * @param src Object to fetch properties (if undefined, read from this.data)
     * @returns {* | jQuery}
     */
    applyRequired(element, src=undefined)
    {
        let fn = this.fnGetFromObjOrFromData(src);
        if (fn.call(this, 'required')) {
            for (let i=0; i<element.length; i++) {
                $(element[i]).attr('required', 'required').addClass('required');
            }
        }
        return element
    }
    /**
     * Look for properties and apply them to the element parameter.
     * Some specific properties need specific action (see 'visible' below).
     *
     * @param element jQuery object
     * @param src Object to fetch properties (if undefined, read from this.data)
     * @returns {* | jQuery}
     */
    applyUsualProperties(element, src=undefined)
    {
        this.applyProperties(element, ['id', 'name', 'class'], src);
        let fn = this.fnGetFromObjOrFromData(src);
        /* Specific check: visible */
        if (fn.call(this, 'visible') === false) {
            element.hide();
        }
        /* Specific check: required */
        this.applyRequired(element, src);
        /* Specific check: checked */
        if (fn.call(this, 'checked')) {
            element.attr('checked', 'checked');
            element.addClass('checked');
        }
        let attrs = fn.call(this, 'attributes');
        if (typeof(attrs) === "object") {
            for (let k in attrs) {
                if (attrs.hasOwnProperty(k)) {
                    element.attr(k, attrs[k]);
                }
            }
        }
        return element;
    }
    /**
     * Generates a new object based on the information of the obj object.
     *
     * @param obj Object that should have 'type' key + according keys and data
     * @return {Object}
     */
    newWzObject(obj) {
        let cls = WzDumb;
        if (obj.hasOwnProperty('type')) {
            if (obj.type === 'text') {
                cls = WzText;
            } else if (obj.type === 'legend') {
                cls = WzLegend;
            } else if (obj.type === 'image') {
                cls = WzImage;
            } else if (obj.type === 'link') {
                cls = WzLink;
            } else if (obj.type === 'select') {
                cls = WzSelect;
            } else if (obj.type === 'select_radio') {
                cls = WzSelectRadio;
            } else if (obj.type === 'buttons') {
                cls = WzButtons;
            } else if (obj.type === 'input') {
                cls = WzInput;
            } else if (obj.type === 'input_textarea') {
                cls = WzInputTextarea;
            } else if (obj.type === 'input_file') {
                cls = WzInputFile;
            } else if (obj.type === 'fieldset') {
                cls = WzFieldset;
            } else if (obj.type === 'table') {
                cls = WzTable;
            } else if (obj.type === 'sortable') {
                cls = WzSortable;
            } else if (obj.type === 'table_cell_apply_check') {
                cls = WzTableCellApplyCheck;
            } else if (obj.type === 'table_cell_apply_copy') {
                cls = WzTableCellApplyCopy;
            }
        }
        if (obj.hasOwnProperty('data')) {
            /* note: "obj" (last param) is only used by WzText: */
            return new cls(this, obj['data'], this._wrapper, obj);
        }
        if (cls === WzDumb) {
            throw new Error("unknown class / and / or / data property missing");
        }
        return new cls(this);
    }
    /**
     * Renders content.
     *
     * Data is an object with single key 'label' which is the... label.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        let $result;
        if (this._wrapper) {
            $result = $(this._wrapper).append(this.get_$elements());
        } else {
            $result = this.get_$elements();
        }
        return $('<div />').append($result).children();
    };
    /**
     * To be called after elements have been added to the DOM.
     * To bind callback functions (click, hover...)
     *
     * @returns {* | jQuery}
     */
    after_render()
    {
        return this;
    };
    /**
     * Archive CSS properties of a jQuery element
     *
     * @param $obj jQuery element
     * @param tab array of string that are the elements to be archived
     * @param attr_name name of the attribute where to store the archive
     *
     * @returns {* | jQuery}
     */
    static css_archive($obj, tab, attr_name='css-old')
    {
        let old_css = {};
        for (let i=0; i<tab.length; i++) {
            old_css[tab[i]] = $obj.css(tab[i]);
        }
        $obj.data(attr_name, old_css);
    }
    /**
     * Restore CSS properties of a jQuery element that have been saved
     * with css_archive()
     *
     * @param $obj jQuery element
     * @param tab array of string that are the elements to be archived
     * @param attr_name name of the attribute where to store the archive
     *
     * @returns {* | jQuery}
     */
    static css_restore($obj, tab, attr_name='css-old')
    {
        let old_css = $obj.data(attr_name);
        if (typeof(old_css)==='object') {
            for (let key in old_css) {
                if (old_css.hasOwnProperty(key)) {
                    $obj.css(key, old_css[key]);
                }
            }
        }
    }
}

class WzDumb extends WzDataRender {
    /**
     * constructor
     *
     * For this class, generates what's in the data as pure content:
     * just pass a string to data when initializing, and render()
     * will give you that string back.
     *
     * @param parent Children often need a reference to their parent
     * @param data   Data object (specific use for each descendant)
     * @param wrapper render() wraps the content with this element
     */
    constructor(parent, data, wrapper='') {
        super(parent, data, wrapper);
        this.set_$elements([]);
    };
}

class WzText extends WzDataRender {
    /**
     * constructor
     *
     * For this class, set wrapper as <span /> to avoid text changes
     *
     * @param parent Children often need a reference to their parent
     * @param data   Data object (specific use for each descendant)
     * @param wrapper render() wraps the content with this element
     * @param obj Object: original object
     */
    constructor(parent, data, wrapper='<span />', obj=null) {
        super(parent, data, wrapper);
        /* !! usually, for WzText, data is an array -> we can't have custom
         *    properties, but I needed 'line_break'. So exceptionally,
         *    "obj" param is added there: for 'line_break'
         *    (which can't be in the array):
         */
        if (obj.hasOwnProperty('line_break')) {
            this._line_break = !!obj['line_break'];
        } else {
            this._line_break = true;
        }
    };
    /**
     * Renders content.
     *
     * Data is an array of objects. Each object contains information on how
     * to display:
     * - type of the text
     * - the text itself
     *
     * Example:
     * { 'type': 'title_1',
     *   'content': 'What do you want to do?' }
     *
     * @returns {* | jQuery}
     */
    render()
    {
        let container_tags =  {
                'title_1': '<h1 />',
                'title_2': '<h2 />',
                'title_3': '<h3 />',
                'title_4': '<h4 />',
                'title_5': '<h5 />',
                'text': '<span />',
                'code': '<code />',
                'pre': '<pre />',
                'link': '<a />',
            },
            final,
            $result = [];
        if (Array.isArray(this.data)) {
            final = this.data;
        } else if (typeof(this.data) == 'string') {
            final = this.data;
        } else if (typeof(this.data) == 'object') {
            final = this.data;
        } else {
            final = this.get('content', []);
        }
        if (!Array.isArray(final)) {
            final = [final];
        }
        for (let i=0; i<final.length; i++) {
            let c = final[i],
                css_class = c['class'],
                italic = false,
                $container,
                content,
                line_break;
            if (c.hasOwnProperty('italic')) {
                italic=c['italic'];
            }
            /* Handle line_break *inside* the text itself: */
            if (c.hasOwnProperty('line_break')) {
                line_break = !!c['line_break'];
            } else {
                line_break = this._line_break;
            }
            if (c.hasOwnProperty('type') && c.hasOwnProperty('content')) {
                /* build $container based on 'type' () - see container_tags: */
                let container_tag = container_tags[c.type];
                $container = (container_tag ? $(container_tag) : $('<p />'));
                content = c.content;
            } else {
                $container = $('<p />');
                content = c;
            }
            /* 'content' can be an array -> add them separated by <br/>  */
            let localAddContent = function (content_to_add) {
                if (content_to_add===null) {
                    $container.append(this.newWzObject('???').render());
                } else if (typeof(content_to_add)==='object') {
                    $container.append(this.newWzObject(content_to_add).render());
                } else {
                    if (italic) {
                        $container.append('<i>'+content_to_add+'</i>');
                    } else {
                        $container.append(content_to_add);
                    }
                }
            };
            if (Array.isArray(content)) {
                for (let i=0; i<(content.length-1); i++) {
                    localAddContent.call(this, content[i]);
                    if (line_break) {
                        $container.append('<br />');
                    }
                }
                localAddContent.call(this, content[content.length-1]);
            } else {
                localAddContent.call(this, content);
            }
            if (!!css_class) {
                $container.addClass(css_class);
            }
            $result.push($container);
            if (this._line_break && (i<(final.length-1))) {
                $result.push($('<br/>'));
            }
        }
        /* $result is an array. If 'tag' is set, surround with 'tag' */
        let tag = this.get('tag');
        if (tag) {
            $result = $('<' + tag + ' />').append($result);
            /* (!) to have an 'id' or other property, 'tag' MUST be set: */
            this.applyUsualProperties($result);
        }
        this.set_$elements($result);
        return super.render();
    };
}

class WzLegend extends WzDataRender {
    /**
     * constructor
     *
     * For this class, the wrapper is <legend />, don't add another one.
     *
     * @param parent Children often need a reference to their parent
     * @param data   Data object (specific use for each descendant)
     * @param wrapper render() wraps the content with this element
     */
    constructor(parent, data, wrapper=undefined) {
        super(parent, data, wrapper);
    };
    /**
     * Renders content.
     *
     * Data is an object with single key 'label' which is the... label.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        let $legend = $('<legend />').html(this.get('label'));
        this.applyUsualProperties($legend);
        this.set_$elements([$legend]);
        return super.render();
    };
}

class WzImage extends WzDataRender {
    /**
     * constructor
     *
     * @param parent Children often need a reference to their parent
     * @param data   Data object (specific use for each descendant)
     * @param wrapper render() wraps the content with this element
     */
    constructor(parent, data, wrapper=undefined) {
        super(parent, data, wrapper);
    };
    /**
     * Renders content.
     *
     * Data is an object with single key 'label' which is the... label.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        let $img = $('<img src="" />'); /* add src="" to remove PyCharm warn */
        this.applyUsualProperties($img);
        this.applyProperties($img, ['src', 'title', 'alt', 'width', 'height']);
        this.applyCallback($img, ['reset']);
        this.set_$elements($img);
        return super.render();
    };
}

class WzLink extends WzDataRender {
    /**
     * constructor
     *
     * For this class, the wrapper is <a />, don't add another one.
     *
     * @param parent Children often need a reference to their parent
     * @param data   Data object (specific use for each descendant)
     * @param wrapper render() wraps the content with this element
     */
    constructor(parent, data, wrapper=undefined) {
        super(parent, data, wrapper);
    };
    /**
     * Renders content.
     *
     * Data is an object with single key 'label' which is the... label.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        let $link = $('<a />'),
            localAddContent = function (content_to_add) {
                if (typeof(content_to_add)==='object') {
                    $link.append(this.newWzObject(content_to_add).render());
                } else {
                    $link.append(content_to_add);
                }
            };
        this.applyUsualProperties($link);
        this.applyProperties($link, ['href']);
        this.applyCallback($link, ['reset']);
        let content = this.get('content', []);
        for (let i=0; i<content.length; i++) {
            localAddContent.call(this, content[i]);
        }
        this.set_$elements($link);
        return super.render();
    };
}

class WzFieldset extends WzDataRender {
    /**
     * Renders content.
     *
     * Generates a fieldset that is composed of all the elements of the
     * data 'content' key array.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        /* ! input should be wrapped in <p/> -> parent's wrap = <p />: */
        this.set_wrapper('<p />');
        let $result = [];
        if (this.data.hasOwnProperty('content')) {
            for (let idx=0; idx<this.data.content.length; idx++) {
                let obj = this.newWzObject(this.data.content[idx]);
                $result.push(obj.render());
            }
        }
        /* we already have a wrapper: "<fieldset />" -> remove the wrapper: */
        this.set_wrapper('');
        $result = $('<fieldset />').append($result);
        this.applyUsualProperties($result);
        this.set_$elements($result);
        return super.render();
    }
}

class WzSortable extends WzDataRender {
    /**
     * Renders content.
     *
     * Generates a fieldset that is composed of all the elements of the
     * data 'content' key array.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        let $result,
            $mk_div = (cls) => {
                return $('<div />').addClass(cls)
            },
            make_li = (item) => {
                return $('<li />')
                    .attr('to_send', item['to_send'])
                    .attr('name', item['name'])
                    .attr('val', item['val']);
            },
            make_item_src = (item) => {
                return make_li(item).addClass('ui-state-default').append(
                    item.text,
                    $('<span />').html('&raquo;&raquo;&raquo;')
                );
            },
            make_item_dst = (item) => {
                let important = item.important,
                    /* If important = add class important OR greyed + italic: */
                    content = important ?
                        item.text : $('<em />').append(item.text);
                return make_li(item)
                    .addClass('ui-state-default')
                    .addClass(important ? "dst-important" : "dst-not-important")
                    .append(content);
            },
            add_items = (items, $dst, fn_add) => {
                for (let i=0; i<items.length; i++) {
                    let item = items[i];
                    if (hasOwnProperties(item,
                        'name', 'text', 'important', 'to_send', 'val')
                    ) {
                        $dst.append(fn_add(item))
                    }
                }
            },
            c1 = this.get('column1', {}),
            c2 = this.get('column2', {}),
            c1_title = (c1.hasOwnProperty('title') ? c1.title : ''),
            c2_title = (c2.hasOwnProperty('title') ? c2.title : ''),
            c1_items = (c1.hasOwnProperty('items') ? c1.items : []),
            c2_items = (c2.hasOwnProperty('items') ? c2.items : []),
            $s1 =$('<ul />').addClass('sortable1'),
            $s2 =$('<ul />').addClass('sortable2');

        /* Add items */
        add_items(c1_items, $s1, make_item_src);
        add_items(c2_items, $s2, make_item_dst);

        /**
         * ! make containers to separate items from title otherwise
         *   there are CSS drag'n drop problems (offset problems)
         */
        $result = $mk_div('sortable-container').append(
            $mk_div('sortable-container').append(
                $mk_div('sortable-title-container').append(
                    $mk_div('sortable-title-left').append(c1_title),
                    $mk_div('sortable-title-right').append(c2_title)
                )
            ),
            $mk_div('sortable-container').append(
                $mk_div('sortable disable-select').append($s1, $s2)
            )
        );

        this.applyUsualProperties($result);
        this.set_$elements($result);
        return super.render();
    }
}

class WzTable extends WzDataRender {
    /**
     * Renders content.
     *
     * Generates a fieldset that is composed of all the elements of the
     * data 'content' key array.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        let add_btns_select = false,
            make_row = (row, is_selectable) => {
            let $tds = [];
            for (let i = 0; i<row.length; i++) {
                let c = row[i],
                    cls;
                if (c.hasOwnProperty('type') && c.hasOwnProperty('data')) {
                    if (c.type === 'cell_title') {
                        cls = WzTableCellTitle;
                    } else if (c.type === 'cell_selectable_by_col') {
                        cls = WzTableCellSelectableByCol;
                    } else if (c.type === 'cell_apply_check') {
                        cls = WzTableCellApplyCheck;
                        add_btns_select = true;
                    } else if (c.type === 'cell_apply_copy') {
                        cls = WzTableCellApplyCopy;
                        add_btns_select = true;
                    } else { /* Default = Cell */
                        cls = WzTableCell;
                    }
                    $tds.push(new cls(this, c.data).render());
                }
            }
            if (is_selectable) {
                return $('<tr/>').append($tds).addClass('selectable');
            }
            return $('<tr/>').append($tds);
        };
        let make_rows = (idx, is_selectable) => {
            let rows = this.get(idx, [[]]);
            let result = [];
            for (let i = 0; i<rows.length; i++) {
                result.push(make_row(rows[i], is_selectable));
            }
            return result;
        };
        let $result = $('<table />').css('text-align', 'left').append(
            make_rows('titles', false),
            make_rows('rows', true)
        );
        /**
         * Append buttons to make table according to Éric's ergonomic needs,
         * see after_render() which uses the classes of the buttons.
         * Note: using global wizard variable for translated strings:
         */
        let make_btn = (css, txt) => {
                return $('<button />').addClass(css).append(wizard.trans[txt]);
            },
            separator = '&nbsp;&nbsp;&nbsp;';
        if (add_btns_select) {
            $result.prepend(
                $('<tr />').append(
                    $('<td />')
                        .attr('colspan',
                            $($result.find('tr')[0]).find('td, th').length)
                        .append(
                            make_btn('select-all', 'select_all'), separator,
                            make_btn('deselect-all', 'deselect_all')
                        )
                )
            );
        }
        this.applyUsualProperties($result);
        this.set_$elements($result);
        return super.render();
    }
    /**
     * Apply callbacks to elements AFTER content is generated.
     * The content is calculated via render(). render() may not be actually
     * added to the DOM. Applying callbacks to elements *not added* to the DOM
     * doesn't work. Hence this after_render() function.
     *
     * Here I apply stuff according to Éric's ergonomic needs.
     *
     * @returns {* | jQuery}
     */
    after_render() {
        let isMouseDown = false,
            isSelecting = true,
            $table = this.get_$elements(),
            cbSelectableByCol = function () {
                /* callback to un/select same value in the same column */
                let $this = $(this),
                    src_idx = $this.closest('td').index(),
                    src_html = $this.find(':last-child').html().trim();
                $this.closest('table').find('tr').each(function () {
                    $(this).find('td').each(function () {
                        let $this = $(this),
                            dst_idx = $this.index(),
                            dst_html = $this.find(':last-child').html().trim();
                        if (src_idx === dst_idx) {
                            /* We're on the same column */
                            if (src_html === dst_html) {
                                /* Same value -> un/select */
                                let $tr = $this.closest('tr'),
                                    $input_check = $tr.find('input.row-select');
                                if ($tr.hasClass('selected')) {
                                    $tr.removeClass('selected');
                                    $input_check.prop('checked', '');
                                } else {
                                    $tr.addClass('selected');
                                    $input_check.prop('checked', 'checked');
                                }
                            }
                        }
                    });
                });

            };
        $table.on('mousedown', function (e) {
            e.stopPropagation();
        });
        $(document).mouseup(function () {
            isMouseDown = false;
        });

        $table
            .find('td span select').each(function() {
                if ($(this).parent().length === 1) {
                    $(this).css('margin-bottom', '0')
                }
            })
            .end()
            .find('input.row-select')
            .unbind('click')
            .on('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
            }).end()
            .find('td.col-select')
            .on('mousedown', function (e) {
                e.stopPropagation();
                isMouseDown = true;
                let row=$(this).closest('tr');
                isSelecting = !row.hasClass('selected');
                row.toggleClass('selected');
                let check=row.find('input.row-select');
                check.prop('checked', isSelecting);
            })
            .on('mouseover', function () {
                let row=$(this).closest('tr');
                if (isMouseDown) {
                    if (isSelecting) {
                        row.addClass('selected');
                    } else {
                        row.removeClass('selected');
                    }
                    row.find('input.row-select').prop('checked', isSelecting);
                }
            })
            .bind('selectstart', function () {
                return false;
            })
            .end()
            .find('.copy-to-selected')
            .on('click', function (e) {
                let modified = false,
                    $tr = $(this).closest('tr'),
                    wz = undefined,
                    fnApplyValToElements = function(filter, cbAssignValue) {
                        $($tr.find(filter)).each(function () {
                            let $this = $(this),
                                src_idx = $this.closest('td').index(),
                                src_val = $this.val();
                            if (wz === undefined) {
                                wz = $this.data('wz');
                            }
                            $table.find('tr.selected').each(function () {
                                $(this).find(filter).each(function () {
                                    let $this = $(this),
                                        dst_idx = $this.closest('td').index();
                                    if ($this.attr('ignore-copy')) {
                                        return;
                                    }
                                    if (src_idx === dst_idx) {
                                        if (cbAssignValue($this, src_val)) {
                                            modified = true;
                                        }
                                    }
                                });
                            });
                        });
                    };
                /**
                 * for each select of this tr :
                 *  - find all input's in other tr's, and for each of them:
                 *  - if same index, then try to apply the value of the source
                 */
                /* I had to make a callback because you can't apply a val()
                 * to a select if the value doesn't exist -> filter() function:
                 */
                fnApplyValToElements('select', ($el, src_val) => {
                    if ($el.find('option').filter(function () {
                        return this.value === src_val
                    }).length) {
                        /* ok we can assign */
                        if ($el.val() !== src_val) {
                            $el.val(src_val).trigger('change');
                            return true;
                        }
                    }
                    return false;
                });
                /* and here, it's very simple for input elements: */
                fnApplyValToElements('input', ($el, src_val) => {
                    if ($el.val() !== src_val) {
                        $el.val(src_val).trigger('change');
                        return true;
                    }
                    return false;
                });
                /* Use the select reset draft sending: */
                if (modified && wz) {
                    wz.get_root().resetTimerSendDraft();
                }
                e.stopPropagation();

                // Eric : deselect-all after a copy : it is more ergonomic
                $table.find('input.row-select').prop('checked', false);
                $table.find('tr.selectable').removeClass('selected');
            })
            .on('mousedown', function (e) {
                e.stopPropagation();
            })
            .end()
            .find('button.select-all')
            .on('click', function () {
                $table.find('input.row-select').prop('checked', true);
                $table.find('tr.selectable').addClass('selected');
            })
            .end()
            .find('button.deselect-all')
            .on('click', function () {
                $table.find('input.row-select').prop('checked', false);
                $table.find('tr.selectable').removeClass('selected');
            })
            .end()
            .find('a.vendor')
            .click(function(e) {
                let vendor = $(this).text();
                $table.find('tr').each(function () {
                    if (vendor === $(this).find('a.vendor').first().text()) {
                        $(this)
                            .toggleClass('selected')
                            .find('input.row-select')
                            .first()
                            .prop('checked', $(this).hasClass('selected'));
                    }
                });
                e.stopPropagation();
            })
            .on('mousedown', function (e) {
                e.stopPropagation();
            })
            .end()
            .find('td.selectable-by-col').each(function () {
                $(this).click(cbSelectableByCol);
            })
            .end()
            .find('a.selectable')
            .click(function(e) {
                let model = $(this).text();
                $table.find('tr').each(function () {
                    if (model === $(this).find('a.selectable').first().text()) {
                        let selected = $(this).hasClass('selected');
                        $(this).toggleClass('selected')
                            .find('input.row-select')
                            .prop('checked', selected);
                    }
                });
                e.stopPropagation();
            })
            .on('mousedown', function (e) {
                e.stopPropagation();
            });
    }
}

class WzTableCellApplyCheck extends WzDataRender {
    /**
     * Renders content.
     *
     * Generates a cell that contains cells to be able to select the whole row.
     * It applies Éric's ergonomic needs.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        this.set_wrapper('');
        let $result = [];
        for (let idx=0; idx<this.data.length; idx++) {
            let obj = this.newWzObject(this.data[idx]);
            $result.push(obj.render());
        }
        /* !! TODO: clean up if Éric is ok with that: */
        $result=$('<td />').css({'text-decoration': 'none'}).append(
            $('<span />').css({
                'display': 'inline-block',
                'width': '40px',
                'margin': '0',
                'margin-right': '10px',
                'text-align': 'right'
            }).append($result,
                '&nbsp;',
                '<input type="checkbox" class="row-select" ' +
                'style="vertical-align: middle;">'
            )
        ).addClass("col-select");
        /* TODO: end of clean-up ---------- */
        this.applyUsualProperties($result);
        this.set_$elements($result);
        return super.render();
    }
}

class WzTableCellApplyCopy extends WzDataRender {
    /**
     * Renders content.
     *
     * Generates a cell that contains cells to be able to select the whole row.
     * It applies Éric's ergonomic needs.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        this.set_wrapper(undefined);
        let $result = [];
        for (let idx=0; idx<this.data.length; idx++) {
            let obj = this.newWzObject(this.data[idx]);
            $result.push(obj.render());
        }
        /* !! TODO: clean up if Éric is ok with that: */
        $result=$('<td />').css({
            'text-decoration': 'none',
            'margin-top': '0',
            'padding-top': '0'
        }).append(
            $result,
            '<button class="copy-to-selected" ' +
            'style="vertical-align: top; margin-top: 0; padding-top: 0;">' +
            '&#8661;' +
            '</button>'
        ).addClass("col-select");
        /* TODO: end of clean-up ---------- */
        this.applyUsualProperties($result);
        this.set_$elements($result);
        return super.render();
    }
}

class WzTableCellBase extends WzDataRender {
    /**
     * constructor
     * @param parent Children often need a reference to their parent
     * @param is_title if the cell is a title (= th instead of td)
     * @param data   Data object (specific use for each descendant)
     */
    constructor(parent, is_title, data) {
        super(parent, data, '');
        this._is_title = is_title;
    };
    /**
     * Renders content.
     *
     * Generates a fieldset that is composed of all the elements of the
     * data array.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        let $result = [];
        /* ! we put new elements into <th> or <td> -> they are already wrapped
         *   -> we dont need to put them in a wrapper
         *   -> assign 'this._wrapper' to undefined
         *   -> newWzObject() create elements won't not wrap them
         *      wrapper == 'this._wrapper' == undefined:
         */
        for (let idx=0; idx<this.data.length; idx++) {
            let obj = this.newWzObject(this.data[idx]);
            $result.push(obj.render());
        }
        $result = (this._is_title ? $('<th />') : $('<td />')).append($result);
        this.applyUsualProperties($result);
        this.set_$elements($result);
        return super.render();
    }
}

class WzTableCellTitle extends WzTableCellBase {
    /**
     * constructor
     * @param parent Children often need a reference to their parent
     * @param data   Data object (specific use for each descendant)
     */
    constructor(parent, data) {
        /* ! precise to its parent that it's a title = true: */
        super(parent, true, data);
    };
}

class WzTableCell extends WzTableCellBase {
    /**
     * constructor
     * @param parent Children often need a reference to their parent
     * @param data   Data object (specific use for each descendant)
     */
    constructor(parent, data) {
        /* ! precise to its parent that it's not a title = false: */
        super(parent, false, data);
    };
}

class WzTableCellSelectableByCol extends WzTableCell {
    /**
     * Renders content.
     *
     * Generates a fieldset that is composed of all the elements of the
     * data array.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        let $result = super.render();
        $result.addClass('selectable-by-col');
        return $result;
    }
}

class WzButton extends WzDataRender {

    /**
     * constructor
     * @param parent Children often need a reference to their parent
     * @param data   Data object
     * @param label Label of the button
     * @param key Where to get the callback function ('prev', 'next', etc.)
     * @param span_icon The span icon to create
     * @param span_is_first If the span icon is before the text of after
     */
    constructor(parent, data, label, key, span_icon, span_is_first) {
        super(parent, data);
        this._label = label;
        this._key = key;
        this._span_icon = span_icon;
        this._span_is_first = span_is_first;
    };
    /**
     * Renders content. Create dynamically buttons "Prev" and "Next".
     *
     * @returns {*}
     */
    render()
    {
        let $result, goto = this.get(this._key);
        if (goto) {
            $result = $('<a />')
                .attr('href', '') /* need href for css to work (...) */
                .addClass('btn btn-outline-secondary');
            if (!!this._span_icon) {
                /* Add an icon */
                $result.addClass('btn-icon-split'); /* sbadmin2 specific */
                let $icon = $('<span />').addClass('icon').append(
                        $('<i/>').addClass(this._span_icon)
                    ),
                    $text = $('<span />').addClass('text').html(
                        this._label
                    );
                if (!!this._span_is_first) {
                    $result.append($icon, $text);
                } else {
                    $result.append($text, $icon);
                }
            } else {
                $result.html(this._label);
            }
        } else {
            /* No callback = no display */
            $result = $('');
        }
        this.set_$elements($result);
        return super.render();
    };
    /**
     * To be called after elements have been added to the DOM.
     * To bind callback functions (click, hover...)
     *
     * @returns {* | jQuery}
     */
    after_render()
    {
        let elements = this.get_$elements();
        if (elements !== undefined) {
            let self = this;
            elements.click(function(evt) {
                evt.preventDefault();
                self.get_root().stopTimerSendDraft();
                let value = self.get(self._key),
                    new_step = undefined;
                if (value===true) {
                    /* when it's true this means "reload" */
                    window.location.reload(true);
                } else if (typeof(value)==='string') {
                    /* first try to search for a radio that is checked: */
                    $('[name="'+value+'"]').each(function () {
                        if ($(this).is(':checked')) {
                            new_step = $(this).val();
                        }
                    });
                    if (new_step === undefined) {
                        /* not in DOM -> real next step -> send directly: */
                        new_step = value;
                    }
                } else if (typeof(value)==='function') {
                    /* When the server sends "error", with message,
                     * we creates button "back" with function inside
                     */
                    value();
                }
                if (new_step!==undefined) {
                    /* true = refresh (= ask for current step) after: */
                    self.get_root().ajax_send_values(
                        /* self._key = 'prev' or 'next': */
                        self._key, new_step, true
                    );
                }
            });
        }
        return this;
    };
}

class WzButtons extends WzDataRender  {

    /**
     * constructor
     * @param parent Children often need a reference to their parent
     * @param data Data object
     */
    constructor(parent, data) {
        super(parent, data);
        this._prev = null;
        this._next = null;
        this._reload = null;
        this._cancel = null;
    };
    /**
     * Renders content. Create dynamically buttons "Prev" and "Next".
     *
     * @param css_all Css to apply to both buttons
     * @param css_parent Css to apply on parent (for top or bottom buttons)
     * @param css_left Css to apply to left button ('prev')
     * @param css_right Css to apply to right button ('next')
     * @param css_cancel Css to apply to cancel button ('cancel')
     * @returns {* | jQuery}
     */
    apply_css_classes(css_all, css_parent, css_left, css_right, css_cancel)
    {
        let btns=[
            {btn:this._prev, css: css_left, hide: false},
            {btn:this._next, css: css_right, hide: false},
            {btn:this._reload, css: css_left, hide: false},
            {btn:this._cancel, css: css_cancel, hide: true}
        ];
        /* (!) call to render() must have been made before! */
        /* Same for all btns: */
        for (let idx=0; idx<btns.length; idx++) {
            if (btns[idx].btn) {
                btns[idx].btn.get_$elements()
                    .addClass(css_all)
                    .addClass(btns[idx].css).parent().addClass(css_parent);
                if (btns[idx].hide) {
                    btns[idx].btn.get_$elements().hide();
                }
            }
        }
    }
    /**
     * Renders content. Create dynamically buttons "Prev", "Next", "Reload".
     *
     * @returns {* | jQuery}
     */
    render()
    {
        /**
         * Create the div, then add buttons.
         * See @after_render of the WzButton class to see how it's handled.
         */
        this._prev = new WzButton(
            this, this.data, 'Previous', 'prev',
            'fas fa-arrow-left', true  /* span_icon, span_is_first */
        );
        this._next = new WzButton(
            this, this.data, 'Next', 'next',
            'fas fa-arrow-right', false  /* span_icon, span_is_first */
        );
        this._reload = new WzButton(
            this, this.data, 'Ok', 'reload',
            'fas fa-check', true  /* span_icon, span_is_first */
        );
        this._cancel = new WzButton(
            this, this.data, 'Cancel', 'cancel',
            'fas fa-trash', true  /* span_icon, span_is_first */
        );
        let $result = $('<div />')
            .css({'min-height':'50px', 'margin-top':'1em'})
            .append(
                this._prev.render(),
                this._next.render(),
                this._reload.render(),
                this._cancel.render()
            );
        this.set_$elements(this.applyUsualProperties($result));
        return super.render();
    }
    /**
     * To be called after elements have been added to the DOM.
     * To bind callback functions (click, hover...)
     *
     * @returns {* | jQuery}
     */
    after_render()
    {
        /* Apply "clic" callbacks */
        let btns=[this._prev, this._next, this._reload];
        for (let idx=0; idx<btns.length; idx++) {
            if (btns[idx]) {
                btns[idx].after_render();
            }
        }
        /* ! specific 'cancel': after_render() should not be called */
        this.applyCallback(this._cancel.get_$elements(), ['cancel']);
    }
}

class WzInputFile extends WzDataRender {
    /**
     * Renders content.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        let $result = this.applyUsualProperties(
            $('<input />')
                .attr('type', 'file')
                .attr('to_send', this.get('to_send'))
                .attr('id', this.get('id'))
                .attr('name', this.get('id'))
                .attr('value', this.get('value'))
        );
        if (!!this.get('label')) {
            /* Change the result into an array with label as first element */
            $result = $('<div />').append(
                $('<label />').html(this.get('label')),
                $result
            ).children();
        }
        this.set_$elements($result);
        super.render();
        return super.render();
    };
}

class WzDataRenderWithDrafts extends WzDataRender {
    /**
     * constructor
     * @param parent Children often need a reference to their parent
     * @param data   Data object (specific use for each descendant)
     * @param wrapper if render() wraps the content into this element
     */
    constructor(parent, data, wrapper='<p />') {
        /* render that save drafts are almost always wrapped into a <p /> */
        super(parent, data, wrapper);
        /**
         * We need to be able to call resetTimerSendDraft() when a key
         * is released.
         * We can do this on input that are visible.
         * So when input is visible -> link the jQuery element + with 'wz'
         * -> when WzContent.after_render() is called,
         *    it will find this input and call after_render() of this input
         *    -> in after_render() we set the timer to save periodically:
         * (!!) Dont forget assign the input element in render()
         *      (for a sample, see WzInput render() method)
         */
        this._input = undefined;
    }
    /**
     * Hide the error message (if one) on change event.
     *
     * @returns {* | jQuery}
     */
    static hide_error_message($input)
    {
        let $parent = $input.parent(),
            $error = $parent.prevAll('.errorlist');
        if (!$error.length) {
            /* maybe just above in siblings (i.e. in a td, it's above:) */
            $error = $input.prevAll('.errorlist');
        }
        if ($error.length) {
            let $prev=$input.prev();
            $error.slideUp();
            if ($prev.length) {
                /* Bring back original properties (saved with css_archive()) */
                WzDataRender.css_restore($prev, ['color', 'font-weight']);
            }
        }
    }
    /**
     * To bind callback functions (change, click, hover...)
     *
     * @returns {* | jQuery}
     */
    on_change_launch_draft($input)
    {
        let changeCallback = function()  {
                $(this).data('wz').get_root().resetTimerSendDraft();
                WzDataRenderWithDrafts.hide_error_message($input);
            };
        /* Check + select = handle "change", others handle "keyup": */
        if ($input) {
            let prop = $input.prop('type');
            if (prop === 'checkbox' ||
                prop === 'select-one' ||
                prop === 'radio'
            ) {
                $input.change(changeCallback);
            } else {
                $input.keyup(changeCallback);
            }
        }
    }
    /**
     * Create a help_url element
     *
     * @returns {* | jQuery}
     */
    $new_help_url()
    {
        /**
         * ! Added custom attribute "css-fixed" so when the
         *   window is resized, the hack in handleScreenResized()
         *   is *NOT* applied on this element:
         */
        let css_help_url = this.get_root().getCssHelpUrl();
        return  $('<span />')
            .addClass('help-url')
            .attr('css-fixed', true)
            .append(
                $('<img />')
                    .attr('src', css_help_url.img.url)
                    .css(css_help_url.img.css)
            );
    };
    /**
     * To be called after elements have been added to the DOM.
     * To bind callback functions (change, click, hover...)
     *
     * @returns {* | jQuery}
     */
    after_render()
    {
        if (this._input === undefined) {
            /* not a hidden input */
            return super.after_render();
        }
        this.on_change_launch_draft(this._input);
        let $help_url = this._input.siblings().filter('.help-url'),
            $label = this._input.siblings().filter('label');
        if ($help_url.length) {
            let css_help_url = this.get_root().getCssHelpUrl(),
                self = this;
            $help_url.click(function (e) {
                if (e && e.preventDefault) {
                    e.preventDefault();
                }
                let data = {'help-url': self.get('help_url')};
                data['csrftoken'] = getCookie('csrftoken');
                data['csrfmiddlewaretoken'] = getCookie('csrftoken');
                $.ajax({
                    url: css_help_url.json,
                    dataType: 'json',
                    method: 'post',
                    data: data,
                    cache: false
                }).done(function (data) {
                    if (data.hasOwnProperty('result')) {
                        console.log('data', data);
                        let root = self.get_root(),
                            result = data.result.trim(),
                            buttons = {
                                type: 'buttons',
                                data: {
                                    'prev': () => root.ajax_refresh(data)
                                }
                            };
                        let title;
                        if ($label.length) {
                            title = $label.html().trim();
                        } else {
                            title = wizard.css_help_url.default_title;
                        }
                        root.showMessage(title, result, buttons);
                    } else {
                        ajax_handle_critical_error(
                            wizard.error_no_specific_message
                        );
                    }
                }).fail(ajax_handle_critical_error);
            });
        }
        return super.after_render();
    };
}

class WzSelect extends WzDataRenderWithDrafts {
    /**
     * Refresh / reload the options of the select.
     * @param parent_calling: set to true when the parent calls this function
     *                        to refresh a child
     * @param more_data data to add to the ajax
     * @returns {WzSelect}
     */
    refresh_options(parent_calling=false, more_data=false)
    {
        let fnRecurseSearch = function ($el) {
                for (let i=0; i<$el.length; i++) {
                    if ($el[i] instanceof Array) {
                        let result = fnRecurseSearch($el[i]);
                        if (result !== undefined) {
                            return result;
                        }
                    } else if ($el[i].prop('type') === 'select-one') {
                        return $el[i];
                    }
                }
                return undefined;
            },
            $select = fnRecurseSearch(this.get_$elements());
        if ($select === undefined) {
            return this;
        }
        let options = this.get('options', []),
            fill_options = function (data) {
                let data_options = data;
                if (data.hasOwnProperty('options')) {
                    /* All "options" are in the 'options' key */
                    data_options = data['options'];
                }
                $select.find('option').remove();
                for (let idx=0; idx<data_options.length; idx++) {
                    let c=data_options[idx], d = $('<option />');
                    if (typeof(c)==='string') {
                        d.attr('value', idx).html(c)
                    } else if (
                        c.hasOwnProperty('value') &&
                        c.hasOwnProperty('label')
                    ) {
                        d.attr('value', c.value).html(c.label);
                        if (c.hasOwnProperty('selected')) {
                            let sel = c['selected'];
                            if (!!sel) {
                                d.attr('selected', sel);
                            }
                        }
                    } else {
                        d = null;
                    }
                    if (d!==null) {
                        $select.append(d);
                    }
                }
            },
            ajax  = this.get('ajax');

        if (ajax !== undefined) {
            if (parent_calling || typeof(ajax['parent'])==='undefined') {
                $.ajax({
                    method: 'get',
                    url: ajax.url,
                    dataType: 'json',
                    data: (more_data===false ? {} : more_data),
                    cache: false
                }).done(function (data) {
                    fill_options(data);
                }).fail(ajax_handle_critical_error);
            }
        } else {
            fill_options(options);
        }
        return this;
    };
    /**
     * Renders content.
     * For this WzSelect class, generates a select with the parameters
     * in the data object (see code below).
     * @returns {* | jQuery}
     */
    render()
    {
        /* Remove the code "cache" here if it needs full refresh: */
        if (typeof(this.get_$elements()) !== 'undefined') {
            return super.render();
        }

        let $result = [],
            $select = $('<select />')
                .attr('to_send', this.get('to_send', ''))
                .data('wz', this),
            help_text = this.get('help_text'),
            help_url = this.get('help_url'),
            content_replace = this.get('content_replace');
        if (this.get('select-unique', '')) {
            $select.attr('select-unique', true);
        }

        /**
         * NOT USED ANYMORE but 100% working: Handle children property:
        // Gather all children to propagate event on change:
        let child = this.get('child', null),
            children = this.get('children', (child !== null ? [child]: []));
        if (children.length) {
            $select.change(function () {
                for (let i=0; i<children.length; i++) {
                    let child = children[i];
                    let $child = $('body').find('#'+child.id);
                    if ($child.length) {
                        let wz_element = $child.data('wz'),
                            more_data = {};
                        more_data[child['data_param_name']]= $(this).val();
                        if (typeof(wz_element)==='object') {
                            // bool param in refresh_options() below:
                            // true = tell the parent is calling, and more_data
                            // is added to the AJAX params (= filter):
                            wz_element.refresh_options(true, more_data);
                        }
                    }
                }
            });
        }
         */

        /**
         * Handle content_replace property:
         */
        if (content_replace !== undefined) {
            /* content_replace = "when this combo changes, make an Ajax call
             * and put the result into a DOM element":
             */
            if (content_replace.hasOwnProperty('id') &&
                content_replace.hasOwnProperty('ajax')
            ) {
                let id_to_replace = content_replace['id'],
                    ajax = content_replace['ajax'];
                if (ajax.hasOwnProperty('url') &&
                    ajax.hasOwnProperty('data_param_name')
                ) {
                    let ajax_url = ajax['url'],
                        data_param_name = ajax['data_param_name'];
                    /**
                     * - id_to_replace
                     * - ajax_url
                     * - ajax_param_name
                     */
                    $select.change(function () {
                        let data = {},
                            zero_values={'-':true, 'no':true, '0':true },
                            v = $(this).val().toLowerCase();
                        /* if the value is '-', 'no' or 0 (hard-coded) then
                         * dont make the AJAX, just empty() the destination :
                         */
                        if (($(this).prop('selectedIndex') === 0) &&
                            (zero_values[v] === true)) {
                            $('#'+id_to_replace).empty();
                            return;
                        }
                        data[data_param_name] = $(this).val();
                        /* Handle additional data to pass: */
                        if (ajax.hasOwnProperty('data_more')) {
                            for (let i=0; i<ajax['data_more'].length; i++) {
                                let o = ajax['data_more'][i];
                                /* Check for values to get from the inputs: */
                                if (o.hasOwnProperty('id') &&
                                    o.hasOwnProperty('param_name')
                                ) {
                                    data[o['param_name']] = $('#'+o.id).val();
                                }
                                /* Check for hard-coded values to add: */
                                if (o.hasOwnProperty('key') &&
                                    o.hasOwnProperty('value')
                                ) {
                                    data[o['key']] = o['value'];
                                }
                            }
                        }
                        new WzContent(
                            $select.data('wz'),
                            /* data: */
                            {ajax: {
                                url: ajax_url,
                                data: data
                            }},
                            /* no wrapper = empty string, NOT undefined */
                            '',
                            /* callback when ajax is done: */
                            (wz_content) => {
                                $('#'+id_to_replace).empty().append(
                                    wz_content.render()
                                );
                                setTimeout(function () {
                                    wz_content.after_render();
                                }, 100);
                            }
                        ).ajax_refresh();
                    });
                }
            }
        }
        let lbl = this.get('label', '');
        if (lbl) {
            let $lbl = $('<label />').append(lbl);
            /* apply only if the label is not empty
             * hint: convert all html, including &nbsp; to text, then trim():
             */
            if ($('<div />').html(lbl).text().trim()) {
                this.applyRequired($lbl);
            }
            $result.push($lbl);
        }
        this.applyUsualProperties($select);
        /* ! dont forget the link (see big comment in parent constructor) */
        this._input = $select;
        $result.push($select);
        console.log('help_url', help_url);
        if (help_url) {
            $result.push(this.$new_help_url());
        }
        if (help_text) {
            $result.push($('<span />').addClass('helptext').html(help_text));
        }
        if (!this._wrapper) {
            this.set_wrapper('<span />');
        }
        this.set_$elements($result);
        this.refresh_options();
        return super.render();
    };

}

class WzSelectRadio extends WzDataRenderWithDrafts {
    /**
     * Renders content.
     *
     * Generates radios buttons select with the parameters in the data object.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        let $result = [],
            choices=this.get('choices', []);
        for (let idx=0; idx<choices.length; idx++) {
            let c = choices[idx],
                $input = $('<input />')
                    .data('wz', this)
                    .attr('type', 'radio')
                    .attr('to_send', this.get('to_send'))
                    .attr('value', c.value);
            this.applyUsualProperties($input, c);
            let lbl = $('<label />').append($input, c.label);
            this.applyUsualProperties(lbl);
            $result.push(lbl);
        }
        this.set_$elements($result);
        return super.render();
    };
    /**
     * To be called after elements have been added to the DOM.
     * To bind callback functions (change, click, hover...)
     *
     * @returns {* | jQuery}
     */
    after_render()
    {
        /* this element has more than one "input" = loop on all: */
        let self = this;
        $(this.get_$elements()).each(function () {
            self.on_change_launch_draft($(this).find('input[type=radio]'));
        });
        return super.after_render();
    };
}

class WzInput extends WzDataRenderWithDrafts {
    /**
     * Renders content.
     *
     * Generates an input with the parameters in the data object.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        let $result = [],
            id = this.get('id'),
            help_text = this.get('help_text'),
            help_url = this.get('help_url'),
            required = this.get('required'),
            blank = this.get('blank'),
            $input = this.applyUsualProperties($('<input />')),
            input_type = this.get('input_type'),
            initial = this.get('initial'),
            value = this.get('value'),
            is_boolean = this.get('is_boolean');
        /* if required OR blank === "false" -> it's required */
        $input
            .attr('type', input_type)
            .attr('id', id)
            .attr('name', id)
            .attr('to_send', this.get('to_send'))
            .attr('value', value || initial)
            .attr('required', required || (blank === "false"));
        if (is_boolean===true) {
            $input.attr('is_boolean', true);
        }
        if ((input_type === 'checkbox') && ((value==='on') || (value===true))) {
            $input.prop('checked', true);
        }
        if (input_type !== 'hidden') {
            /* ! dont forget the link (see big comment in parent constructor) */
            this._input = $input.data('wz', this);
            if (this.get('label')) {
                console.log('"dmlfkjqsdlkjfdqs"');
                $result.push(
                    $('<label />')
                        .append(this.get('label'))
                        .attr('for', id)
                );
            }
            $result.push($input);
            if (help_url) {
                $result.push(this.$new_help_url());
            }
            if (help_text) {
                $result.push(
                    $('<span />').addClass('helptext').html(help_text)
                );
            }
            $result = $('<div />').append($result).children();
        } else {
            $result = $input;
        }
        this.applyRequired($result);
        this.set_$elements($result);
        return super.render();
    };
}

class WzInputTextarea extends WzDataRenderWithDrafts {
    /**
     * Renders content.
     *
     * Generates an input with the parameters in the data object.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        let $result = [],
            id = this.get('id'),
            help_text = this.get('help_text'),
            help_url = this.get('help_url'),
            required = this.get('required'),
            textarea = this.applyUsualProperties(
                $('<textarea />')
                    .attr('id', id)
                    .attr('name', id)
                    .attr('to_send', this.get('to_send'))
                    .attr('required', required)
                    .html(this.get('value', ''))
            );
        $result.push(
            $('<label />')
                .append(this.get('label'))
                .attr('for', id)
        );
        $result.push(textarea);
        if (help_url) {
            $result.push(this.$new_help_url());
        }
        if (help_text) {
            $result.push($('<span />').addClass('helptext').html(help_text));
        }
        this.applyRequired($result);
        this.set_$elements($result);
        /* ! dont forget -> make link (see big comment in parent constructor) */
        this._input = textarea.data('wz', this);
        return super.render();
    };
}

class WzContent extends WzDataRender {

    /**
     * Constructor
     *
     * @param parent See parent constructor
     * @param data See parent constructor
     * @param wrapper render() wraps the content with this element
     * @param cb_after_ajax_refresh Callback after asking the current step
     */
    constructor(parent, data, wrapper, cb_after_ajax_refresh)
    {
        super(parent, data, wrapper);
        this._cb_after_ajax_refresh = cb_after_ajax_refresh;
        this._breadcrumb = undefined;
        this._step = undefined;
        this._timer_send_draft = null;
        this._draft_sent_callback = false;
        this._css_help_url = undefined;
    };
    /**
     * Add a new WzXxx object to the content ()
     *
     */
    getCssHelpUrl()
    {
        if (this._css_help_url === undefined) {
            this._css_help_url = this.get('css_help_url');
        }
        return this._css_help_url;
    }
    /**
     * Add a new WzXxx object to the content ()
     *
     * @param content
     */
    add(content)
    {
        this._content.push(content);
    }
    /**
     * Get the content (array of WzXxx objects)
     *
     * @return {Array}
     */
    getContent()
    {
        return this._content;
    }
    /**
     * Stop the timer to send draft.
     *
     * @returns WzContent this
     */
    stopTimerSendDraft()
    {
        if (this._timer_send_draft !== null) {
            clearTimeout(this._timer_send_draft);
        }
    }
    /**
     * Launch or re-launch the timer to send draft.
     * Called when key released in inputs, "check" on checkboxes, and so on.
     *
     * @returns WzContent this
     */
    resetTimerSendDraft()
    {
        this.stopTimerSendDraft();
        this._timer_send_draft = setTimeout(() => {
            this.get_root().ajax_send_values(
                'draft', true, this._draft_sent_callback
            );
        }, 1000);
        return this;
    }
    /**
     * Returns the property of the data parameter if is exists
     * OR try to get value in self.data ->
     * The data parameter overrides this.data:
     *
     * @param data Data parameter
     * @param idx Index to get
     * @param default_value Default value
     *
     * @returns {*}
     */
    tryGet(data, idx, default_value)
    {
        if (data.hasOwnProperty(idx)) {
            return data[idx];
        }
        return this.get(idx, default_value);
    };
    /**
     * Refresh content with the param data
     *
     * @param data Result from AJAX call or dynamically generated
     *
     * @return WzContent
     */
    refreshWith(data)
    {
        /**
         * HEART OF GENERATION
         *
         * Analyze + create WzXxx elements
         *
         * data contains the elements:
         *   - *TO BE* generated, displayed and linked
         *   OR
         *   - *ALREADY* generated, linked and displayed
         *   (depending on the context)
         */
        // Debug: console.log('WzContent : refreshWith(', data, ')');
        try {

            this._step = this.tryGet(data, 'step');
            this._title = this.tryGet(data, 'title');
            this._breadcrumb = this.tryGet(data, 'breadcrumb');

            /* Create a fake id to put content into: */
            this.data['id'] = 'wz_' + this._step;

            /* Always clean content to put new content: */
            this._content = [];
            let content = data['content'];
            for (let idx=0; idx<content.length; idx++) {
                this.add(this.newWzObject(content[idx]));
            }
            return this;
        }
        catch(error) {
            /* Should never happen, this means the JSON is not for a Wizard! */
            /* Note - error messages will vary depending on browser */
            console.log("Critical error, technical detail: "+error.toString());
            ajax_handle_critical_error(error.toString());
        }
    }
    /**
     * AJAX call (usually gets current step data) then refresh with result.
     *
     * @param callback_when_done Either the data received
     *                           or function to call back when AJAX is done and
     *                           everything has been built.
     *
     * @return void
     */
    ajax_refresh(callback_when_done)
    {
        let self = this,
            ajax = this.get('ajax'),
            data = (ajax.hasOwnProperty('data') ? ajax.data : {});
        $.ajax({
            method: 'get',
            url: ajax['url'],
            data: data,
            dataType: 'json',
            cache: false
        }).done(function(data) {
            /* ! call refreshWith with context "self" */
            self.refreshWith(data);

            if (typeof(callback_when_done) === 'function') {
                callback_when_done(self);
            } else if (self._cb_after_ajax_refresh !== undefined) {
                self._cb_after_ajax_refresh(self, data);
            }
            if (data.hasOwnProperty('ajax_data')) {
                self.set_ajax_data(data.ajax_data);
            }
            /* Always try to refresh all DOM to change selection if needed: */
            setTimeout(() => {
                self.refresh_dom_ajax_objects();
            }, 1);
        }).fail(ajax_handle_critical_error);
    };

    /**
     * Displays a message.
     *
     * @param title   Title of the message
     * @param message HTML text to be shown
     * @param buttons Object that contains buttons configuration
     *                (search for showMessage() calls to see how to create it)
     * 
     * @return void
     */
    showMessage(title, message, buttons)
    {
        let wzMessageBox = new WzContentWithButtons(
            this.get_root(),
            /* buttons are created now, before calling refreshWith()
             * -> send buttons CSS + visible properties: */
            {
                css_buttons: wizard.css_buttons,
                breadcrumb_visible: false,
                buttons: {
                    visible: {
                        top: false,
                        bottom: true
                    }
                }
            }
        ), wzData = {
            title: title,
            breadcrumb_visible: false,
            content: [{
                type: "text",
                data: {
                    content: [{
                        type: "title_5",
                        content: message
                    }]
                }
            }],
            breadcrumb: this._breadcrumb,
            step: this._step
        };
        if (buttons !== undefined) {
            wzData.content.push(buttons);
        }
        /**
         * Message from the server:
         * -> show an error, and for the next button, just
         *    ask for the current step again:
         */
        wzMessageBox.refreshWith(wzData);
        $('#wizard').empty().append(
            /* access to global css, find a better way later on: */
            wzMessageBox.render().css(wizard.css_main_div)
        );
        /* ! we need to call after_render() AFTER it's been rendered: */
        /*
        TODO: test DOMNodeInserted event instead of timer, maybe safer:
        $(document).on('DOMNodeInserted', function(event) {
            console.log('event', event);
        });
        */
        setTimeout(function () {
            wzMessageBox.after_render();
        }, 100);
    };
    /**
     * Sends the parameters that has been chosen and wait for the answer
     * to refresh (= call to ajax_refresh()).
     *
     * @param step_key Key to add in the AJAX ('prev', 'next' or 'draft')
     * @param step_value Value for the step
     * @param refresh_after Once sent, if we refresh the step (AJAX call)
     *                      or if it's a callback function, call it
     */
    ajax_send_values(step_key, step_value, refresh_after)
    {
        console.log("gathering all values to send...");
        let form_data = new FormData(),
            has_files = false;
        /* add ('prev', 'next' or 'draft') value: */
        form_data.append(step_key, step_value);
        /* add all other elements: */
        this.get_$elements().find('*').each(function() {
            let self = $(this);
            if (self.attr('to_send')==='true') {
                /* (!) TODO read values of other types of input (to send): */
                let input_type = self.get(0).type,
                    input_name = self.attr('name');
                if (input_type === '') {
                    /**
                     * element is not an input element
                     * -> read its 'val' attribute (cf WzSortable with "li")
                     */
                    let val = $(this).attr('val');
                    if (typeof(val) !== 'undefined' && val !== false) {
                        form_data.append(input_name, val);
                    }
                }
                else if (
                    (input_type === 'text') || (input_type === 'password')
                ) {
                    form_data.append(input_name, self.val());
                } else if (input_type === 'textarea') {
                    form_data.append(input_name, self.val());
                } else if (input_type === 'checkbox') {
                    /* Only send 'on' of 'off' : */
                    let value = (self.is(':checked') ? 'on': 'off');
                    if (!!self.attr('is_boolean')) {
                        /* Send true or false, not 'on' or 'off' */
                        value = (value === 'on');
                    }
                    form_data.append(input_name, value);
                } else if (input_type === 'radio') {
                    if (self.is(':checked')) {
                        form_data.append(input_name, self.val());
                    }
                } else if (input_type === 'select-one') {
                    form_data.append(input_name, self.val());
                } else if (input_type === 'file') {
                    has_files = true;
                    form_data.append(input_name, self.get(0).files[0]);
                }
            }
        });
        console.log("...finished");

        let self = this,
            ajax = this.get('ajax'),
            final_data = (ajax.hasOwnProperty('data') ? ajax.data : {});
        console.log('ajax', ajax);
        final_data['csrftoken'] = getCookie('csrftoken');
        final_data['csrfmiddlewaretoken'] = getCookie('csrftoken');
        for (let key in final_data) {
            form_data.append(key, final_data[key]);
        }
        $.ajax({
            url: ajax['url'],
            dataType: (has_files ? false : 'json'),
            method: 'post',
            data: form_data,
            cache: false,
            contentType: false, /* ! dont precise 'json', let browser encode! */
            processData: false /* forbid to processData if files */
        }).done(function(data) {
            console.log('result data', data);
            if (data.hasOwnProperty('success') && (!data.success)) {
                $('.errorlist').slideUp('slow');
                if (data.hasOwnProperty('message_fields')) {
                    let message_fields = data['message_fields'];
                    for (let id in message_fields) {
                        if (message_fields.hasOwnProperty(id)) {
                            let $input = $('[name="'+id+'"]'),
                                $input_parent = $input.parent();
                            if ($input.length) {
                                let $input_error = $('#'+id+'_error'),
                                    message = message_fields[id],
                                    $li = $('<li />').html(
                                        //'<span class="badge badge-warning">'+
                                        message
                                        //'</span>'
                                    );
                                if ($input_error.length===0) {
                                    /* Not found -> create one: */
                                    $input_error = $('<ul />')
                                        .attr('id', id+'_error')
                                        .addClass('errorlist')
                                        .append($li);
                                    $input_error.insertBefore(
                                        ($input_parent.get(0).tagName==='TD'
                                        ? $input
                                        : $input_parent)
                                    );
                                    $input_error.hide();
                                } else {
                                    $input_error.empty().append($li);
                                }
                                $input_error.slideDown('slow');
                            }
                        }
                    }
                    /* wait for DOM insertion -> set a timeout: */
                    setTimeout(function () {
                        /* Take the highest $input (the list is not ordered!) */
                        let $input_top = undefined,
                            $input_offset_top = undefined;
                        for (let id in message_fields) {
                            if (message_fields.hasOwnProperty(id)) {
                                let $input = $('[name="' + id + '"]');
                                if ($input.length) {
                                    let offset_top = $input.offset().top;
                                    if ($input_top===undefined) {
                                        $input_top = $input;
                                        $input_offset_top = offset_top;
                                    } else if (offset_top<$input_offset_top) {
                                        $input_top = $input;
                                        $input_offset_top = offset_top;
                                    }
                                }
                            }
                        }
                        /* Scroll to mid of the highest $input */
                        if ($input_top!==undefined) {
                            /* Hint: xx|0 = rounded value of xx */
                            let mid = $(window.top).height()/2 | 0;
                            $('html, body').animate({
                                scrollTop: $input_top.offset().top - mid
                            }, 750, undefined, function () {
                                $input_top.focus();
                            });
                        }
                    }, 100);
                    return;
                }
                let title, message, buttons;
                /**
                 * Previous step didn't succeed:
                 * -> we're still on the same step
                 * -> create an error message, and only "prev" button
                 * -> when "prev" is clicked, reload with self.ajax_refresh():
                 */
                if (data.hasOwnProperty('message') &&
                    typeof(data['message']) === 'string'
                ) {
                    if (data.hasOwnProperty('title') &&
                            typeof(data['title']) === 'string') {
                        title = data['title'];
                    } else {
                        title = "Error";
                    }
                    message = data['message'].replace(/\n/g, "<br />");
                    /* add prev button which will reload the step: */
                    buttons = {
                        type: 'buttons',
                        data: {
                            'prev': () => self.ajax_refresh(data)
                        }
                    };
                } else {
                    /**
                     * No specific message from the server: show an error,
                     * without "back" buttons. Access global value =
                     * not clean but at least it's translated:
                     */
                    buttons = undefined;
                    message = wizard.error_no_specific_message;
                }
                self.showMessage(title, message, buttons);
            } else if (refresh_after) {
                if (refresh_after===true) {
                    /* Just call refresh = ask for current step + redraw: */
                    self.ajax_refresh(data);
                } else if (typeof(refresh_after)==='function') {
                    refresh_after(data);
                }
            }
        }).fail(ajax_handle_critical_error);
    }
    /**
     * Renders content. Core of the system. That's where everything starts.
     *
     * @returns {* | jQuery}
     */
    render()
    {

        let $elements = this.get_$elements(),
            wz_content = this.getContent();
        if ($elements === undefined) {
            let id = this.get('id'),
                tag = this.get('tag');
            if (tag) {
                $elements = $('<'+tag+' />').attr('id', id);
            } else {
                $elements = $('<div />').attr('id', id);
            }
        } else {
            $elements.empty();
        }
        for (let j in wz_content) {
            let element = wz_content[j];
            $elements.append(element.render());
        }
        this.set_$elements($elements);
        return super.render();
    };
    /**
     * Apply callbacks to elements AFTER content is generated.
     * The content is calculated via render(). render() may not be actually
     * added to the DOM. Applying callbacks to elements *not added* to the DOM
     * doesn't work. Hence this after_render() function: this is where you
     * will be able to apply callbacks to elements AFTER content is generated.
     *
     * @returns {* | jQuery}
     */
    after_render()
    {
        let reOrderValues = function() {
                let idx = 0;
                $(this).find('li').each(function () {
                    $(this).attr('val', idx++);
                });
            },
            call_after_render = function (el) {
                let wz = $(el).data('wz');
                if (wz) {
                    wz.after_render();
                }
            };
        /* Apply sortable + event to reorder values when order changes: */
        $('.sortable1')
            .sortable({ items: 'li:not(.ui-state-disabled)' })
            .on( "sortupdate", reOrderValues );
        $('.sortable2')
            .sortable({ cancel: '.ui-state-disabled' })
            .on( "sortupdate", reOrderValues);

        $('.sortable1 li, .sortable2 li').disableSelection();
        let wz_content = this.getContent();
        for (let i in wz_content) {
            wz_content[i].after_render();
        }
        $(this.get_$elements())
            .find(':input').each(function () { call_after_render(this); })
            .end()
            .find('table').each(function () { call_after_render(this); });
        $('div.breadcrumb_url').unbind('click').on('click', function () {
            let final_data = {'step': $(this).data('step')};
            final_data['csrftoken'] = getCookie('csrftoken');
            final_data['csrfmiddlewaretoken'] = getCookie('csrftoken');
            $.ajax({
                url: wizard.urls.goto,
                dataType: 'json',
                method: 'post',
                data: final_data,
                cache: false
            }).done(function () {
                window.location.reload(true);
            }).fail(ajax_handle_critical_error);
        });

        /*  */
        let filterSelectUnique = function(){
            return $(this).attr('select-unique') === 'true'
        }, fnLoopSelect = function(self, val, cb) {
            $('select').filter(filterSelectUnique).each(function () {
                if ($(this) !== self) {
                    cb($(this).find('option[value="'+val+'"]'));
                }
            });
        }, cbSelectUniqueChange = function () {
            let self = $(this),
                curr = self.val(),
                prev = self.attr('previous-val');
            /* Hide the new val */
            if ((curr !== "-1") && (curr !== "-2")) {
                /* Hide current if not "please choose" or "(no column)"*/
                fnLoopSelect(self, curr, ($select) => $select.hide());
                self.attr('previous-val', curr);
            } else {
                self.attr('previous-val', undefined);
            }
            if (prev !== undefined) {
                /* Show */
                fnLoopSelect(self, prev, ($select) => $select.show());
            }
        };
        let $select = $('select').filter(filterSelectUnique);
        /**
         * (!) if I try $select.change() to apply changes, it launches
         *     the "draft save". -> call manually without $select.change():
        $select.each(function () {
            cbSelectUniqueChange.call(this);
        });
         */
        $select.change(cbSelectUniqueChange);
        return super.after_render();
    }
}

class WzContentWithButtons extends WzContent {

    /**
     * Constructor
     *
     * @param parent See parent constructor
     * @param data See parent constructor
     * @param wrapper render() wraps the content with this element
     * @param cb_after_ajax_refresh Callback after asking the current step
     */
    constructor(parent, data, wrapper, cb_after_ajax_refresh)
    {
        super(parent, data, wrapper, cb_after_ajax_refresh);
        this._breadcrumb_visible = true;
        this._css_buttons = this.get('css_buttons');
        this._cancel_buttons = null;
        this._$_filter_css_cancel = null;
        if (this._css_buttons && this._css_buttons.cancel) {
            /**
             * css class is like 'classX classY classZ'
             * -> explode, add '.' to all element and join them
             * to make jQuery search work like: $('.classX.classY.classZ')
             */
            let css_cancel = this._css_buttons.cancel.split(' ');
            for (let idx=0; idx < css_cancel.length; idx++) {
                css_cancel[idx] = '.' + css_cancel[idx];
            }
            this._$_filter_css_cancel = css_cancel.join('');
        }
        this._buttons = this.tryGetButtonsConfiguration();
    }
    /**
     * Returns the buttons property of the data parameter if is exists
     * OR try to get value in self.data ->
     * The data parameter overrides this.data:
     *
     * @param data Data parameter
     *
     * @returns {*}
     */
    tryGetButtonsConfiguration(data={})
    {
        let buttons = this.tryGet(data, 'buttons');
        if (buttons && buttons.hasOwnProperty('visible')) {
            let buttons_visible = buttons['visible'];
            return {
                visible: {
                    top: !!buttons_visible['top'],
                    bottom: !!buttons_visible['bottom']
                }
            };
        }
        /* By default, buttons are visible on top and bottom */
        return {
            visible: {
                top: true,
                bottom: true
            }
        };
    }
    /**
     * Refresh content with the param data
     *
     * @param data Result from AJAX call or dynamically generated
     *
     * @return WzContent
     */
    refreshWith(data)
    {
        /* Display or not the breadcrumb (ex: for message box, no breadcrumb) */
        this._breadcrumb_visible = this.tryGet(
            data, 'breadcrumb_visible', true /* ! default value = true */
        );
        this._buttons = this.tryGetButtonsConfiguration(data);
        return super.refreshWith(data);
    }
    /**
     * Renders content.
     *
     * @returns {* | jQuery}
     */
    render()
    {
        let $elements = this.get_$elements();
        if ($elements === undefined) {
            $elements = $('<div />').attr('id', this.get('id'));
        } else {
            $elements.empty();
        }
        /* search the buttons + keep them for adding later on: */
        let buttons_top = new WzDumb(this, undefined).render(),
            buttons_bottom = new WzDumb(this, undefined).render(),
            wz_content = this.getContent();
        for (let j in wz_content) {
            let element = wz_content[j];
            if (element instanceof WzButtons) {
                buttons_top = element;
                /* Re-create buttons for the bottom: */
                buttons_bottom = new WzButtons(
                    element.parent, element.data
                );
                /* ! dont forget to add bottom to elements so after_render()
                 *   will call the after_render() of the buttons_bottom too:
                 */
                this.add(buttons_bottom);

                buttons_top.render();
                buttons_top.apply_css_classes(
                    this._css_buttons.all,
                    this._css_buttons.parent.top,
                    this._css_buttons.left,
                    this._css_buttons.right,
                    this._css_buttons.cancel,
                );
                buttons_top = buttons_top.get_$elements();

                buttons_bottom.render();
                buttons_bottom.apply_css_classes(
                    this._css_buttons.all,
                    this._css_buttons.parent.bottom,
                    this._css_buttons.left,
                    this._css_buttons.right,
                    this._css_buttons.cancel,
                );
                buttons_bottom = buttons_bottom.get_$elements();
            }
        }
        if (buttons_top === undefined) {
            buttons_top = new WzDumb(this, undefined).get_$elements();
            buttons_bottom = new WzDumb(this, undefined).get_$elements();
            this.add(buttons_top);
            this.add(buttons_bottom);
        }
        if (this._title) {
            $elements.append($('<h1 />').append(this._title));
        }

        /**
         * Breadcrumb generation
         */
        let $breadcrumb = $('<div />');
        $breadcrumb.attr('id', 'breadcrumbs').addClass('disable-select');

        for (let i = 0; i < this._breadcrumb['generic'].length; i++) {
            let generic = this._breadcrumb['generic'][i],
                detail = this._breadcrumb['detail'][i],
                step = this._breadcrumb['step'][i];
            $breadcrumb.append(
                $('<div />').addClass('breadcrumb_url').append(
                    $('<div />')
                        .addClass('breadcrumbs_step')
                        .append(i+1),
                    $('<div />')
                        .addClass('breadcrumbs_generic')
                        .append(
                            '&nbsp;&nbsp;'+generic,
                            $('<span />').addClass('raquo').css({
                                'display': 'block',
                                'float': 'right'
                            }).html("\u21b3")
                        ),
                    $('<div />')
                        .addClass('breadcrumbs_detail')
                        .css('display', 'inline-block')
                        .append(
                            $('<span />').css({
                                'font-size': 'small'
                            }).html(detail),
                        )
                ).data('step', step)
            );
        }

        /* Only add $breadcrumb if something in it: */
        if (($breadcrumb.html() !== '') && (this._breadcrumb_visible)) {
            $elements.append($breadcrumb);
        }
        /* Add Top buttons: */
        if (this._buttons.visible.top) {
            $elements.append(buttons_top);
        }

        /**
         * Adding all elements except buttons "previous" and "next"
         */
        for (let i in wz_content) {
            let element = wz_content[i];
            /* Everything except WzButtons (we add them after): */
            if (!(element instanceof WzButtons)) {
                $elements.append(element.render());
            }
        }
        /* Add Bottom buttons: */
        if (this._buttons.visible.bottom) {
            $elements.append(buttons_bottom);
        }
        this.set_$elements($elements);
        return $('<div />').append(this.get_$elements()).children();
    };

    /**
     * Renders content.
     *
     * @param data Data of the AJAX call, to look if property 'cancel' is true
     *
     * @returns {* | jQuery}
     */
    test_cancel_button(data) {
        if (data.hasOwnProperty('cancel') && (data.cancel)) {
            /**
             * cancel means: ('draft' != 'real') => we can cancel
             * => show cancel buttons:
             */
            this._cancel_buttons.each(function () {
                $(this).fadeIn();
            });
        } else {
            this._cancel_buttons.each(function () {
                $(this).fadeOut();
            });
        }
        return this;
    }
    /**
     * Apply callbacks to elements AFTER content is generated.
     * The content is calculated via render(). render() may not be actually
     * added to the DOM. Applying callbacks to elements *not added* to the DOM
     * doesn't work. Hence this after_render() function: this is where you
     * will be able to apply callbacks to elements AFTER content is generated.
     *
     * @returns {* | jQuery}
     */
    after_render()
    {
        /**
         * Each time a draft is sent, a jQuery search to show "cancel" button(s)
         * is done. Searching them is overkill.
         * -> pre-calculate where they are, to avoid re-searching:
         */
        if (this._$_filter_css_cancel) {
            this._cancel_buttons = $(this._$_filter_css_cancel);
            if (this._cancel_buttons.length) {
                this._draft_sent_callback = (data) => {
                    /* called when the draft is sent -> re-check: */
                    this.test_cancel_button(data);
                };
            }
        }
        return super.after_render();
    }
}